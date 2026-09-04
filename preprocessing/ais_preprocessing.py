from pathlib import Path
import json
import pickle

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "oilspill_ais_development_dataset.xlsx"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed_ais"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# SEQUENCE CONFIGURATION
# ============================================================

# Number of previous AIS observations given to the LSTM
HISTORY_LENGTH = 12

# We predict the next movement
FUTURE_STEPS = 1

# Maximum allowed time gap between consecutive AIS points
MAX_GAP_MINUTES = 15


# ============================================================
# TRAIN / VALIDATION / TEST SPLIT
# ============================================================

TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15


# ============================================================
# FEATURES
# ============================================================

FEATURE_COLUMNS = [
    "delta_x_km",
    "delta_y_km",
    "sog_knots",
    "cog_sin",
    "cog_cos",
    "heading_sin",
    "heading_cos",
]


TARGET_COLUMNS = [
    "delta_x_km",
    "delta_y_km",
]


# ============================================================
# LOAD DATA
# ============================================================

def load_ais_data():

    print("=" * 70)
    print("LOADING AIS DATA")
    print("=" * 70)

    if not DATA_PATH.exists():

        raise FileNotFoundError(
            f"\nAIS dataset not found:\n{DATA_PATH}"
        )

    df = pd.read_excel(
        DATA_PATH,
        sheet_name="AIS_Track_Points"
    )

    print(
        f"\nDataset shape: {df.shape}"
    )

    print(
        f"Number of columns: {len(df.columns)}"
    )

    return df


# ============================================================
# VALIDATE COLUMNS
# ============================================================

def validate_columns(df):

    print("\n" + "=" * 70)
    print("VALIDATING AIS COLUMNS")
    print("=" * 70)

    required_columns = [
        "case_id",
        "timestamp_utc",
        "mmsi",
        "latitude",
        "longitude",
        "sog_knots",
        "cog_deg",
        "heading_deg",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            "\nMissing required columns:\n"
            + "\n".join(
                f"  - {column}"
                for column in missing_columns
            )
        )

    print("\nAll required AIS columns are present.")

    for column in required_columns:

        print(
            f"  ✓ {column}"
        )


# ============================================================
# CLEAN DATA
# ============================================================

def clean_data(df):

    print("\n" + "=" * 70)
    print("CLEANING AIS DATA")
    print("=" * 70)

    df = df.copy()

    # --------------------------------------------------------
    # Convert timestamp
    # --------------------------------------------------------

    df["timestamp_utc"] = pd.to_datetime(
        df["timestamp_utc"],
        errors="coerce",
        utc=True
    )

    # --------------------------------------------------------
    # Convert numerical columns
    # --------------------------------------------------------

    numeric_columns = [
        "latitude",
        "longitude",
        "sog_knots",
        "cog_deg",
        "heading_deg",
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    before = len(df)

    # --------------------------------------------------------
    # Remove missing critical values
    # --------------------------------------------------------

    df = df.dropna(
        subset=[
            "case_id",
            "timestamp_utc",
            "mmsi",
            "latitude",
            "longitude",
            "sog_knots",
            "cog_deg",
            "heading_deg",
        ]
    )

    print(
        f"\nRows before cleaning : {before}"
    )

    print(
        f"Rows after cleaning  : {len(df)}"
    )

    print(
        f"Rows removed         : "
        f"{before - len(df)}"
    )

    # --------------------------------------------------------
    # Validate geographic coordinates
    # --------------------------------------------------------

    df = df[
        (df["latitude"] >= -90)
        & (df["latitude"] <= 90)
        & (df["longitude"] >= -180)
        & (df["longitude"] <= 180)
    ].copy()

    # --------------------------------------------------------
    # Normalize angles
    # --------------------------------------------------------

    df["cog_deg"] = (
        df["cog_deg"] % 360
    )

    df["heading_deg"] = (
        df["heading_deg"] % 360
    )

    # --------------------------------------------------------
    # Sort trajectory
    # --------------------------------------------------------

    df = df.sort_values(
        [
            "case_id",
            "mmsi",
            "timestamp_utc",
        ]
    ).reset_index(
        drop=True
    )

    # --------------------------------------------------------
    # Remove duplicate timestamps
    # --------------------------------------------------------

    before_duplicates = len(df)

    df = df.drop_duplicates(
        subset=[
            "case_id",
            "mmsi",
            "timestamp_utc",
        ]
    ).reset_index(
        drop=True
    )

    print(
        f"Duplicate observations removed: "
        f"{before_duplicates - len(df)}"
    )

    return df


# ============================================================
# CALCULATE TIME DIFFERENCE
# ============================================================

def calculate_time_difference(df):

    df = df.copy()

    df["time_diff_minutes"] = (
        df
        .groupby(
            ["case_id", "mmsi"]
        )["timestamp_utc"]
        .diff()
        .dt.total_seconds()
        / 60.0
    )

    return df


# ============================================================
# CALCULATE LOCAL DISPLACEMENT
# ============================================================

def calculate_displacement(df):

    print("\n" + "=" * 70)
    print("CALCULATING VESSEL DISPLACEMENT")
    print("=" * 70)

    df = df.copy()

    # --------------------------------------------------------
    # Previous coordinates
    # --------------------------------------------------------

    df["previous_latitude"] = (
        df
        .groupby(
            ["case_id", "mmsi"]
        )["latitude"]
        .shift(1)
    )

    df["previous_longitude"] = (
        df
        .groupby(
            ["case_id", "mmsi"]
        )["longitude"]
        .shift(1)
    )

    # --------------------------------------------------------
    # Latitude movement
    #
    # Approximately:
    #
    # 1 degree latitude ≈ 111.32 km
    # --------------------------------------------------------

    delta_latitude = (
        df["latitude"]
        - df["previous_latitude"]
    )

    delta_y_km = (
        delta_latitude
        * 111.32
    )

    # --------------------------------------------------------
    # Longitude movement
    #
    # Longitude distance depends on latitude.
    # --------------------------------------------------------

    mean_latitude_radians = np.deg2rad(
        (
            df["latitude"]
            + df["previous_latitude"]
        )
        / 2.0
    )

    delta_longitude = (
        df["longitude"]
        - df["previous_longitude"]
    )

    delta_x_km = (
        delta_longitude
        * 111.32
        * np.cos(
            mean_latitude_radians
        )
    )

    df["delta_x_km"] = delta_x_km

    df["delta_y_km"] = delta_y_km

    # --------------------------------------------------------
    # Angular features
    # --------------------------------------------------------

    cog_radians = np.deg2rad(
        df["cog_deg"]
    )

    df["cog_sin"] = np.sin(
        cog_radians
    )

    df["cog_cos"] = np.cos(
        cog_radians
    )

    heading_radians = np.deg2rad(
        df["heading_deg"]
    )

    df["heading_sin"] = np.sin(
        heading_radians
    )

    df["heading_cos"] = np.cos(
        heading_radians
    )

    return df


# ============================================================
# IDENTIFY VALID TRAJECTORY SEGMENTS
# ============================================================

def create_segments(df):

    print("\n" + "=" * 70)
    print("CREATING TRAJECTORY SEGMENTS")
    print("=" * 70)

    df = df.copy()

    # --------------------------------------------------------
    # A new segment starts when the AIS gap is too large.
    # --------------------------------------------------------

    large_gap = (
        df["time_diff_minutes"]
        > MAX_GAP_MINUTES
    )

    # First observation of each vessel
    first_observation = (
        df
        .groupby(
            ["case_id", "mmsi"]
        )
        .cumcount()
        == 0
    )

    df["new_segment"] = (
        large_gap
        | first_observation
    )

    # --------------------------------------------------------
    # Create segment number
    # --------------------------------------------------------

    df["segment_id"] = (
        df
        .groupby(
            ["case_id", "mmsi"]
        )["new_segment"]
        .cumsum()
    )

    print(
        f"\nNumber of trajectory segments: "
        f"{df['segment_id'].nunique()}"
    )

    return df


# ============================================================
# SPLIT EACH TRAJECTORY CHRONOLOGICALLY
# ============================================================

def get_split_indices(n):

    """
    Calculate chronological boundaries.

    Example for 37 observations:

        ~70% → training
        ~15% → validation
        ~15% → test
    """

    train_end = int(
        n * TRAIN_RATIO
    )

    val_end = int(
        n * (TRAIN_RATIO + VAL_RATIO)
    )

    # Ensure enough observations remain
    # for validation and testing.

    train_end = max(
        train_end,
        HISTORY_LENGTH + 1
    )

    val_end = max(
        val_end,
        train_end + 1
    )

    val_end = min(
        val_end,
        n - 1
    )

    return (
        train_end,
        val_end
    )


# ============================================================
# CREATE SLIDING WINDOWS
# ============================================================

def create_sequences(
    df,
    feature_scaler,
    target_scaler
):

    print("\n" + "=" * 70)
    print("CREATING SLIDING-WINDOW SEQUENCES")
    print("=" * 70)

    X_train = []
    y_train = []

    X_val = []
    y_val = []

    X_test = []
    y_test = []

    train_metadata = []
    val_metadata = []
    test_metadata = []

    # --------------------------------------------------------
    # Process each vessel trajectory independently
    # --------------------------------------------------------

    grouped = df.groupby(
        [
            "case_id",
            "mmsi",
            "segment_id",
        ],
        sort=False
    )

    for (
        case_id,
        mmsi,
        segment_id
    ), group in grouped:

        group = group.sort_values(
            "timestamp_utc"
        ).reset_index(
            drop=True
        )

        # ----------------------------------------------------
        # Remove first row because displacement is undefined
        # ----------------------------------------------------

        group = group.dropna(
            subset=[
                "delta_x_km",
                "delta_y_km",
            ]
        ).reset_index(
            drop=True
        )

        n = len(group)

        if n < HISTORY_LENGTH + FUTURE_STEPS:
            continue

        # ----------------------------------------------------
        # Calculate chronological split
        # ----------------------------------------------------

        train_end, val_end = (
            get_split_indices(n)
        )

        # ----------------------------------------------------
        # Transform features and targets
        # ----------------------------------------------------

        feature_values = (
            feature_scaler.transform(
                group[FEATURE_COLUMNS]
            )
        )

        target_values = (
            target_scaler.transform(
                group[TARGET_COLUMNS]
            )
        )

        # ----------------------------------------------------
        # Generate windows
        #
        # Target index determines the split.
        # ----------------------------------------------------

        for target_index in range(
            HISTORY_LENGTH,
            n
        ):

            input_start = (
                target_index
                - HISTORY_LENGTH
            )

            input_end = target_index

            X_window = feature_values[
                input_start:input_end
            ]

            y_window = target_values[
                target_index:
                target_index + FUTURE_STEPS
            ]

            # ------------------------------------------------
            # Determine split
            # ------------------------------------------------

            if target_index < train_end:

                X_train.append(
                    X_window
                )

                y_train.append(
                    y_window
                )

                train_metadata.append({
                    "case_id": case_id,
                    "mmsi": str(mmsi),
                    "segment_id": int(segment_id),
                    "target_time": str(
                        group.loc[
                            target_index,
                            "timestamp_utc"
                        ]
                    )
                })

            elif target_index < val_end:

                X_val.append(
                    X_window
                )

                y_val.append(
                    y_window
                )

                val_metadata.append({
                    "case_id": case_id,
                    "mmsi": str(mmsi),
                    "segment_id": int(segment_id),
                    "target_time": str(
                        group.loc[
                            target_index,
                            "timestamp_utc"
                        ]
                    )
                })

            else:

                X_test.append(
                    X_window
                )

                y_test.append(
                    y_window
                )

                test_metadata.append({
                    "case_id": case_id,
                    "mmsi": str(mmsi),
                    "segment_id": int(segment_id),
                    "target_time": str(
                        group.loc[
                            target_index,
                            "timestamp_utc"
                        ]
                    )
                })

    # --------------------------------------------------------
    # Convert to NumPy
    # --------------------------------------------------------

    X_train = np.asarray(
        X_train,
        dtype=np.float32
    )

    y_train = np.asarray(
        y_train,
        dtype=np.float32
    )

    X_val = np.asarray(
        X_val,
        dtype=np.float32
    )

    y_val = np.asarray(
        y_val,
        dtype=np.float32
    )

    X_test = np.asarray(
        X_test,
        dtype=np.float32
    )

    y_test = np.asarray(
        y_test,
        dtype=np.float32
    )

    return (
        X_train,
        y_train,
        X_val,
        y_val,
        X_test,
        y_test,
        train_metadata,
        val_metadata,
        test_metadata,
    )


# ============================================================
# FIT SCALERS
# ============================================================

def fit_scalers(df):

    print("\n" + "=" * 70)
    print("FITTING SCALERS")
    print("=" * 70)

    # --------------------------------------------------------
    # We need training data only.
    #
    # Split each trajectory and collect the training portion.
    # --------------------------------------------------------

    train_groups = []

    grouped = df.groupby(
        [
            "case_id",
            "mmsi",
            "segment_id",
        ],
        sort=False
    )

    for _, group in grouped:

        group = group.sort_values(
            "timestamp_utc"
        ).reset_index(
            drop=True
        )

        group = group.dropna(
            subset=[
                "delta_x_km",
                "delta_y_km",
            ]
        ).reset_index(
            drop=True
        )

        n = len(group)

        if n < HISTORY_LENGTH + FUTURE_STEPS:
            continue

        train_end, _ = (
            get_split_indices(n)
        )

        train_part = group.iloc[
            :train_end
        ]

        train_groups.append(
            train_part
        )

    if not train_groups:

        raise ValueError(
            "No valid training trajectories found."
        )

    train_df = pd.concat(
        train_groups,
        ignore_index=True
    )

    # --------------------------------------------------------
    # Feature scaler
    # --------------------------------------------------------

    feature_scaler = StandardScaler()

    feature_scaler.fit(
        train_df[
            FEATURE_COLUMNS
        ]
    )

    # --------------------------------------------------------
    # Target scaler
    # --------------------------------------------------------

    target_scaler = StandardScaler()

    target_scaler.fit(
        train_df[
            TARGET_COLUMNS
        ]
    )

    print(
        "\nFeature scaler fitted using "
        f"{len(train_df)} training observations."
    )

    print(
        "Target scaler fitted using "
        f"{len(train_df)} training observations."
    )

    return (
        feature_scaler,
        target_scaler
    )


# ============================================================
# SAVE PROCESSED DATA
# ============================================================

def save_processed_data(
    X_train,
    y_train,
    X_val,
    y_val,
    X_test,
    y_test,
    train_metadata,
    val_metadata,
    test_metadata,
    feature_scaler,
    target_scaler
):

    print("\n" + "=" * 70)
    print("SAVING PROCESSED DATA")
    print("=" * 70)

    # --------------------------------------------------------
    # NumPy arrays
    # --------------------------------------------------------

    np.save(
        OUTPUT_DIR / "X_train.npy",
        X_train
    )

    np.save(
        OUTPUT_DIR / "y_train.npy",
        y_train
    )

    np.save(
        OUTPUT_DIR / "X_val.npy",
        X_val
    )

    np.save(
        OUTPUT_DIR / "y_val.npy",
        y_val
    )

    np.save(
        OUTPUT_DIR / "X_test.npy",
        X_test
    )

    np.save(
        OUTPUT_DIR / "y_test.npy",
        y_test
    )

    # --------------------------------------------------------
    # Scalers
    # --------------------------------------------------------

    with open(
        OUTPUT_DIR / "feature_scaler.pkl",
        "wb"
    ) as file:

        pickle.dump(
            feature_scaler,
            file
        )

    with open(
        OUTPUT_DIR / "target_scaler.pkl",
        "wb"
    ) as file:

        pickle.dump(
            target_scaler,
            file
        )

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    metadata = {
        "history_length":
            HISTORY_LENGTH,

        "future_steps":
            FUTURE_STEPS,

        "max_gap_minutes":
            MAX_GAP_MINUTES,

        "feature_columns":
            FEATURE_COLUMNS,

        "target_columns":
            TARGET_COLUMNS,

        "train_samples":
            int(len(X_train)),

        "validation_samples":
            int(len(X_val)),

        "test_samples":
            int(len(X_test)),

        "train_metadata":
            train_metadata,

        "validation_metadata":
            val_metadata,

        "test_metadata":
            test_metadata,
    }

    with open(
        OUTPUT_DIR / "metadata.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4
        )

    print(
        "\nProcessed data saved to:"
    )

    print(
        OUTPUT_DIR
    )


# ============================================================
# DATASET DIAGNOSTICS
# ============================================================

def print_diagnostics(df):

    print("\n" + "=" * 70)
    print("AIS DATASET DIAGNOSTICS")
    print("=" * 70)

    print(
        f"\nTotal records       : {len(df)}"
    )

    print(
        f"Unique cases        : "
        f"{df['case_id'].nunique()}"
    )

    print(
        f"Unique vessels      : "
        f"{df['mmsi'].nunique()}"
    )

    print(
        f"Latitude range     : "
        f"{df['latitude'].min():.6f} → "
        f"{df['latitude'].max():.6f}"
    )

    print(
        f"Longitude range    : "
        f"{df['longitude'].min():.6f} → "
        f"{df['longitude'].max():.6f}"
    )

    print(
        f"SOG range          : "
        f"{df['sog_knots'].min():.3f} → "
        f"{df['sog_knots'].max():.3f} knots"
    )

    valid_dx = df[
        "delta_x_km"
    ].dropna()

    valid_dy = df[
        "delta_y_km"
    ].dropna()

    if len(valid_dx) > 0:

        displacement = np.sqrt(
            valid_dx ** 2
            +
            valid_dy ** 2
        )

        print(
            f"\nMean displacement  : "
            f"{displacement.mean():.4f} km"
        )

        print(
            f"Median displacement: "
            f"{displacement.median():.4f} km"
        )

        print(
            f"Maximum displacement: "
            f"{displacement.max():.4f} km"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 70)
    print("AIS TRAJECTORY PREPROCESSING")
    print("=" * 70)

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    df = load_ais_data()

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    validate_columns(df)

    # --------------------------------------------------------
    # Clean
    # --------------------------------------------------------

    df = clean_data(df)

    # --------------------------------------------------------
    # Time difference
    # --------------------------------------------------------

    df = calculate_time_difference(
        df
    )

    # --------------------------------------------------------
    # Displacement
    # --------------------------------------------------------

    df = calculate_displacement(
        df
    )

    # --------------------------------------------------------
    # Segments
    # --------------------------------------------------------

    df = create_segments(
        df
    )

    # --------------------------------------------------------
    # Diagnostics
    # --------------------------------------------------------

    print_diagnostics(
        df
    )

    # --------------------------------------------------------
    # Fit scalers using training data
    # --------------------------------------------------------

    (
        feature_scaler,
        target_scaler
    ) = fit_scalers(
        df
    )

    # --------------------------------------------------------
    # Create sequences
    # --------------------------------------------------------

    (
        X_train,
        y_train,
        X_val,
        y_val,
        X_test,
        y_test,
        train_metadata,
        val_metadata,
        test_metadata,
    ) = create_sequences(
        df,
        feature_scaler,
        target_scaler
    )

    # --------------------------------------------------------
    # Print shapes
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("FINAL SEQUENCE SHAPES")
    print("=" * 70)

    print(
        f"\nX_train shape: "
        f"{X_train.shape}"
    )

    print(
        f"y_train shape: "
        f"{y_train.shape}"
    )

    print(
        f"\nX_val shape: "
        f"{X_val.shape}"
    )

    print(
        f"y_val shape: "
        f"{y_val.shape}"
    )

    print(
        f"\nX_test shape: "
        f"{X_test.shape}"
    )

    print(
        f"y_test shape: "
        f"{y_test.shape}"
    )

    # --------------------------------------------------------
    # Check for empty datasets
    # --------------------------------------------------------

    if len(X_train) == 0:

        raise ValueError(
            "Training dataset contains zero sequences."
        )

    if len(X_val) == 0:

        raise ValueError(
            "Validation dataset contains zero sequences."
        )

    if len(X_test) == 0:

        raise ValueError(
            "Test dataset contains zero sequences."
        )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    save_processed_data(
        X_train,
        y_train,
        X_val,
        y_val,
        X_test,
        y_test,
        train_metadata,
        val_metadata,
        test_metadata,
        feature_scaler,
        target_scaler
    )

    # --------------------------------------------------------
    # Complete
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("PREPROCESSING COMPLETE")
    print("=" * 70)

def prepare_rnn_sequence(vessel_df):
    """
    Convert raw AIS observations for one vessel into
    the exact 12 x 7 feature format expected by the LSTM.

    Feature order:
        0 -> delta_x_km
        1 -> delta_y_km
        2 -> sog_knots
        3 -> cog_sin
        4 -> cog_cos
        5 -> heading_sin
        6 -> heading_cos
    """

    required_columns = [
        "latitude",
        "longitude",
        "sog_knots",
        "cog_deg",
        "heading_deg"
    ]

    # --------------------------------------------------------
    # 1. Validate columns
    # --------------------------------------------------------

    missing_columns = [
        column
        for column in required_columns
        if column not in vessel_df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required AIS columns: "
            + ", ".join(missing_columns)
        )

    # --------------------------------------------------------
    # 2. Copy dataframe
    # --------------------------------------------------------

    vessel_df = vessel_df.copy()

    # --------------------------------------------------------
    # 3. Sort chronologically
    # --------------------------------------------------------

    if "timestamp_utc" in vessel_df.columns:

        vessel_df["timestamp_utc"] = pd.to_datetime(
            vessel_df["timestamp_utc"],
            errors="coerce",
            utc=True
        )

        vessel_df = vessel_df.sort_values(
            "timestamp_utc"
        )

    # --------------------------------------------------------
    # 4. Convert numeric columns
    # --------------------------------------------------------

    numeric_columns = [
        "latitude",
        "longitude",
        "sog_knots",
        "cog_deg",
        "heading_deg"
    ]

    for column in numeric_columns:

        vessel_df[column] = pd.to_numeric(
            vessel_df[column],
            errors="coerce"
        )

    # --------------------------------------------------------
    # 5. Remove invalid observations
    # --------------------------------------------------------

    vessel_df = vessel_df.dropna(
        subset=numeric_columns
    )

    # --------------------------------------------------------
    # 6. Need at least 12 observations
    # --------------------------------------------------------

    if len(vessel_df) < 12:

        raise ValueError(
            f"At least 12 valid AIS observations are required. "
            f"Only {len(vessel_df)} available."
        )

    # --------------------------------------------------------
    # 7. Use the latest 12 observations
    # --------------------------------------------------------

    vessel_df = vessel_df.tail(
        12
    ).copy()

    # --------------------------------------------------------
    # 8. Extract coordinates
    # --------------------------------------------------------

    lat = vessel_df[
        "latitude"
    ].to_numpy(
        dtype=np.float64
    )

    lon = vessel_df[
        "longitude"
    ].to_numpy(
        dtype=np.float64
    )

    # --------------------------------------------------------
    # 9. Calculate displacement
    #
    # delta_x = east/west movement
    # delta_y = north/south movement
    # --------------------------------------------------------

    delta_x = np.zeros(
        12,
        dtype=np.float64
    )

    delta_y = np.zeros(
        12,
        dtype=np.float64
    )

    # Latitude:
    # approximately 111.32 km per degree

    delta_y[1:] = (
        np.diff(lat) * 111.32
    )

    # Longitude:
    # longitude degree length depends on latitude

    latitude_radians = np.deg2rad(
        lat[:-1]
    )

    km_per_degree_longitude = (
        111.32
        * np.cos(latitude_radians)
    )

    delta_x[1:] = (
        np.diff(lon)
        * km_per_degree_longitude
    )

    # --------------------------------------------------------
    # 10. Course over ground
    # --------------------------------------------------------

    cog = vessel_df[
        "cog_deg"
    ].to_numpy(
        dtype=np.float64
    )

    cog_radians = np.deg2rad(
        cog
    )

    cog_sin = np.sin(
        cog_radians
    )

    cog_cos = np.cos(
        cog_radians
    )

    # --------------------------------------------------------
    # 11. Vessel heading
    # --------------------------------------------------------

    heading = vessel_df[
        "heading_deg"
    ].to_numpy(
        dtype=np.float64
    )

    heading_radians = np.deg2rad(
        heading
    )

    heading_sin = np.sin(
        heading_radians
    )

    heading_cos = np.cos(
        heading_radians
    )

    # --------------------------------------------------------
    # 12. Construct EXACT 7-feature sequence
    # --------------------------------------------------------

    sequence = np.column_stack([
        delta_x,
        delta_y,
        vessel_df[
            "sog_knots"
        ].to_numpy(
            dtype=np.float64
        ),
        cog_sin,
        cog_cos,
        heading_sin,
        heading_cos
    ])

    # --------------------------------------------------------
    # 13. Validate shape
    # --------------------------------------------------------

    if sequence.shape != (12, 7):

        raise RuntimeError(
            "Unexpected RNN sequence shape: "
            f"{sequence.shape}. "
            "Expected (12, 7)."
        )

    # --------------------------------------------------------
    # 14. Return float32
    # --------------------------------------------------------

    return sequence.astype(
        np.float32
    )
# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
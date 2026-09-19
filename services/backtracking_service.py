from pathlib import Path

import numpy as np
import pandas as pd

from preprocessing.ais_preprocessing import (
    prepare_rnn_sequence
)

from services.rnn_service import (
    get_rnn_service
)

from services.behavior_service import (
    analyze_behaviour
)

from services.evidence_service import (
    fuse_evidence
)

# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = (
    Path(__file__).resolve().parent.parent
)

AIS_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "oilspill_ais_development_dataset.xlsx"
)

SHEET_NAME = "AIS_Track_Points"


# ============================================================
# DISTANCE FUNCTION
# ============================================================

def haversine_distance_km(
    lat1,
    lon1,
    lat2,
    lon2
):
    """
    Calculate great-circle distance between
    two geographic coordinates.
    """

    earth_radius_km = 6371.0

    lat1 = np.radians(lat1)
    lat2 = np.radians(lat2)

    delta_lat = np.radians(
        lat2 - lat1
    )

    delta_lon = np.radians(
        lon2 - lon1
    )

    a = (
        np.sin(delta_lat / 2) ** 2
        +
        np.cos(lat1)
        *
        np.cos(lat2)
        *
        np.sin(delta_lon / 2) ** 2
    )

    c = (
        2
        *
        np.arcsin(
            np.sqrt(a)
        )
    )

    return earth_radius_km * c


# ============================================================
# BACKTRACKING SERVICE
# ============================================================

class BacktrackingService:

    def __init__(self):

        print(
            "\nInitializing "
            "Backtracking Service..."
        )

        # ----------------------------------------------------
        # Initialize RNN
        # ----------------------------------------------------

        self.rnn_service = (
            get_rnn_service()
        )

        self.ais_data = None


    # ========================================================
    # LOAD AIS DATA
    # ========================================================

    def load_ais_data(self):

        if self.ais_data is not None:

            return self.ais_data

        print(
            "Loading AIS dataset..."
        )

        df = pd.read_excel(
            AIS_DATA_PATH,
            sheet_name=SHEET_NAME
        )

        # ----------------------------------------------------
        # Timestamp conversion
        # ----------------------------------------------------

        df["timestamp_utc"] = (
            pd.to_datetime(
                df["timestamp_utc"],
                errors="coerce",
                utc=True
            )
        )

        # ----------------------------------------------------
        # Numeric conversion
        # ----------------------------------------------------

        numeric_columns = [
            "latitude",
            "longitude",
            "sog_knots",
            "cog_deg",
            "heading_deg"
        ]

        for column in numeric_columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

        # ----------------------------------------------------
        # Remove invalid records
        # ----------------------------------------------------

        df = df.dropna(
            subset=[
                "mmsi",
                "timestamp_utc",
                "latitude",
                "longitude",
                "sog_knots",
                "cog_deg",
                "heading_deg"
            ]
        )

        # ----------------------------------------------------
        # Sort
        # ----------------------------------------------------

        df = (
            df
            .sort_values(
                [
                    "mmsi",
                    "timestamp_utc"
                ]
            )
            .reset_index(
                drop=True
            )
        )

        self.ais_data = df

        print(
            f"AIS records loaded: "
            f"{len(df)}"
        )

        print(
            f"Unique vessels: "
            f"{df['mmsi'].nunique()}"
        )

        return df


    # ========================================================
    # GET HISTORICAL VESSEL DATA
    # ========================================================

    def get_candidate_vessels(
        self,
        spill_latitude,
        spill_longitude,
        event_time=None,
        radius_km=50.0,
        lookback_hours=3.0
    ):
        """
        Find vessels with sufficient AIS history before
        the spill event.

        IMPORTANT:

        We do NOT require a vessel to already be inside
        radius_km before running the RNN.

        The RNN predicts the vessel's next position first.
        The predicted position is then compared with the
        spill location.

        radius_km therefore acts as the final spatial
        attribution threshold.
        """

        df = self.load_ais_data().copy()

        # ----------------------------------------------------
        # Event-time filtering
        # ----------------------------------------------------

        if event_time is not None:

            event_time = pd.to_datetime(
                event_time,
                utc=True
            )

            start_time = (
                event_time
                -
                pd.Timedelta(
                    hours=lookback_hours
                )
            )

            end_time = event_time

            df = df[
                (
                    df["timestamp_utc"]
                    >= start_time
                )
                &
                (
                    df["timestamp_utc"]
                    <= end_time
                )
            ].copy()

            print(
                f"\nEvent time: "
                f"{event_time}"
            )

            print(
                f"Historical lookback: "
                f"{start_time} -> "
                f"{end_time}"
            )

            print(
                f"Lookback duration: "
                f"{lookback_hours} hours"
            )

            print(
                f"AIS records in historical "
                f"window: {len(df)}"
            )

        # ----------------------------------------------------
        # No data
        # ----------------------------------------------------

        if df.empty:

            print(
                "No AIS records found "
                "in historical window."
            )

            return pd.DataFrame()

        # ----------------------------------------------------
        # Determine vessels with enough history
        # ----------------------------------------------------

        vessel_counts = (
            df
            .groupby("mmsi")
            .size()
        )

        valid_mmsis = (
            vessel_counts[
                vessel_counts >= 12
            ]
            .index
        )

        candidates = df[
            df["mmsi"].isin(
                valid_mmsis
            )
        ].copy()

        print(
            f"Vessels with >= 12 historical "
            f"observations: "
            f"{len(valid_mmsis)}"
        )

        if candidates.empty:

            print(
                "No vessels have enough "
                "historical observations."
            )

            return pd.DataFrame()

        # ----------------------------------------------------
        # Calculate distance of latest historical position
        # to spill
        # ----------------------------------------------------

        latest_positions = (
            candidates
            .sort_values(
                "timestamp_utc"
            )
            .groupby(
                "mmsi",
                as_index=False
            )
            .tail(1)
            .copy()
        )

        latest_positions[
            "spill_distance_km"
        ] = haversine_distance_km(
            latest_positions[
                "latitude"
            ].to_numpy(),

            latest_positions[
                "longitude"
            ].to_numpy(),

            spill_latitude,

            spill_longitude
        )

        # ----------------------------------------------------
        # Sort by historical distance
        # ----------------------------------------------------

        latest_positions = (
            latest_positions
            .sort_values(
                "spill_distance_km"
            )
            .reset_index(
                drop=True
            )
        )

        print(
            "\nClosest historical vessel "
            "positions:"
        )

        print("-" * 100)

        for _, row in (
            latest_positions.head(10).iterrows()
        ):

            print(
                f"MMSI: {row['mmsi']} | "
                f"Time: {row['timestamp_utc']} | "
                f"Distance: "
                f"{row['spill_distance_km']:.3f} km | "
                f"Position: "
                f"({row['latitude']:.6f}, "
                f"{row['longitude']:.6f})"
            )

        print("-" * 100)

        return latest_positions


    # ========================================================
    # PREDICT VESSEL MOVEMENT
    # ========================================================

    def predict_vessel(
        self,
        vessel_df,
        spill_latitude,
        spill_longitude,
        event_time=None
    ):
        """
        Use the latest 12 AIS observations before the
        spill event to predict the vessel's next position.
        """

        vessel_df = (
            vessel_df
            .sort_values(
                "timestamp_utc"
            )
            .copy()
        )

        # ----------------------------------------------------
        # Restrict to event time
        # ----------------------------------------------------

        if event_time is not None:

            event_time = pd.to_datetime(
                event_time,
                utc=True
            )

            vessel_df = vessel_df[
                vessel_df[
                    "timestamp_utc"
                ]
                <= event_time
            ].copy()

        # ----------------------------------------------------
        # Need 12 observations
        # ----------------------------------------------------

        if len(vessel_df) < 12:

            return None

        # ----------------------------------------------------
        # Latest 12 observations
        # ----------------------------------------------------

        history = (
            vessel_df
            .tail(12)
            .copy()
        )

        # ----------------------------------------------------
        # Prepare RNN sequence
        # ----------------------------------------------------

        try:

            sequence = (
                prepare_rnn_sequence(
                    history
                )
            )

        except Exception as error:

            print(
                f"Could not prepare vessel "
                f"sequence: {error}"
            )

            return None

        # ----------------------------------------------------
        # Current position
        # ----------------------------------------------------

        last_position = (
            history.iloc[-1]
        )

        current_latitude = float(
            last_position[
                "latitude"
            ]
        )

        current_longitude = float(
            last_position[
                "longitude"
            ]
        )

        # ----------------------------------------------------
        # RNN prediction
        # ----------------------------------------------------

        try:

            prediction = (
                self.rnn_service
                .predict_position(
                    sequence=sequence,
                    current_latitude=(
                        current_latitude
                    ),
                    current_longitude=(
                        current_longitude
                    )
                )
            )

        except Exception as error:

            print(
                f"RNN prediction failed "
                f"for vessel "
                f"{last_position['mmsi']}: "
                f"{error}"
            )

            return None

        # ----------------------------------------------------
        # Predicted position
        # ----------------------------------------------------

        predicted_latitude = float(
            prediction[
                "predicted_latitude"
            ]
        )

        predicted_longitude = float(
            prediction[
                "predicted_longitude"
            ]
        )

        # ----------------------------------------------------
        # Distance from predicted position
        # to spill
        # ----------------------------------------------------

        distance_to_spill = (
            haversine_distance_km(
                predicted_latitude,
                predicted_longitude,
                spill_latitude,
                spill_longitude
            )
        )

        # ----------------------------------------------------
        # Predicted movement
        # ----------------------------------------------------

        predicted_movement = float(
            np.sqrt(
                prediction[
                    "delta_x_km"
                ] ** 2
                +
                prediction[
                    "delta_y_km"
                ] ** 2
            )
        )

        # ----------------------------------------------------
        # Result
        # ----------------------------------------------------

        return {

            "mmsi":
                str(
                    last_position[
                        "mmsi"
                    ]
                ),

            "current_timestamp":
                str(
                    last_position[
                        "timestamp_utc"
                    ]
                ),

            "current_latitude":
                current_latitude,

            "current_longitude":
                current_longitude,

            "predicted_latitude":
                predicted_latitude,

            "predicted_longitude":
                predicted_longitude,

            "delta_x_km":
                float(
                    prediction[
                        "delta_x_km"
                    ]
                ),

            "delta_y_km":
                float(
                    prediction[
                        "delta_y_km"
                    ]
                ),

            "distance_to_spill_km":
                float(
                    distance_to_spill
                ),

            "predicted_movement_km":
                predicted_movement
        }


    # ========================================================
    # RANK VESSELS
    # ========================================================

    def rank_vessels(
        self,
        spill_latitude,
        spill_longitude,
        event_time=None,
        radius_km=50.0,
        lookback_hours=3.0
    ):
        """
        Run RNN-based vessel backtracking.

        Ranking is based on the predicted position
        relative to the spill.

        Only vessels whose predicted position is within
        radius_km are retained as final candidates.
        """

        # ----------------------------------------------------
        # Get vessels with enough history
        # ----------------------------------------------------

        candidates = (
            self.get_candidate_vessels(
                spill_latitude=(
                    spill_latitude
                ),

                spill_longitude=(
                    spill_longitude
                ),

                event_time=event_time,

                radius_km=radius_km,

                lookback_hours=lookback_hours
            )
        )

        if candidates.empty:

            return []

        results = []

        # ----------------------------------------------------
        # Evaluate vessels
        # ----------------------------------------------------

        for _, candidate_row in (
            candidates.iterrows()
        ):

            mmsi = candidate_row[
                "mmsi"
            ]

            vessel_df = (
                self.ais_data[
                    self.ais_data[
                        "mmsi"
                    ] == mmsi
                ]
                .copy()
            )

            result = (
                self.predict_vessel(
                    vessel_df=vessel_df,

                    spill_latitude=(
                        spill_latitude
                    ),

                    spill_longitude=(
                        spill_longitude
                    ),

                    event_time=event_time
                )
            )

            if result is None:

                continue
                        # ------------------------------------------------
            # Behaviour analysis
            # ------------------------------------------------
            # IMPORTANT:
            # Use only AIS observations available up to the
            # spill event to avoid future-data leakage.
            behaviour_df = (
                vessel_df
                .sort_values(
                    "timestamp_utc"
                )
                .copy()
            )

            if event_time is not None:

                event_timestamp = (
                    pd.to_datetime(
                        event_time,
                        utc=True
                    )
                )

                behaviour_df = behaviour_df[
                    behaviour_df[
                        "timestamp_utc"
                    ]
                    <= event_timestamp
                ].copy()

            # Focus behaviour analysis on the latest
            # observations before the event.
            behaviour_df = (
                behaviour_df
                .tail(30)
                .copy()
            )

            behaviour_result = (
                analyze_behaviour(
                    behaviour_df
                )
            )

            result[
                "behaviour_score"
            ] = float(
                behaviour_result[
                    "behaviour_score"
                ]
            )

            result[
                "behaviour_anomalies"
            ] = behaviour_result[
                "anomalies"
            ]

            result[
                "behaviour_anomaly_count"
            ] = int(
                behaviour_result[
                    "anomaly_count"
                ]
            )

            result[
                "behaviour_explanations"
            ] = behaviour_result[
                "explanations"
            ]

            # ------------------------------------------------
            # Evidence fusion
            # ------------------------------------------------

            evidence_result = (
                fuse_evidence(
                    {
                        "distance_to_spill_km":
                            result[
                                "distance_to_spill_km"
                            ],

                        "behaviour_score":
                            result[
                                "behaviour_score"
                            ]
                    }
                )
            )

            result[
                "evidence_score"
            ] = float(
                evidence_result[
                    "evidence_score"
                ]
            )

            result[
                "evidence_level"
            ] = evidence_result[
                "evidence_level"
            ]

            result[
                "evidence_signals"
            ] = evidence_result[
                "signals"
            ]

            result[
                "evidence_explanations"
            ] = evidence_result[
                "explanations"
            ]

            # ------------------------------------------------
            # Historical information
            # ------------------------------------------------

            result[
                "candidate_timestamp"
            ] = str(
                candidate_row[
                    "timestamp_utc"
                ]
            )

            result[
                "historical_distance_to_spill_km"
            ] = float(
                candidate_row[
                    "spill_distance_km"
                ]
            )

            # ------------------------------------------------
            # Time before event
            # ------------------------------------------------

            if event_time is not None:

                event_timestamp = (
                    pd.to_datetime(
                        event_time,
                        utc=True
                    )
                )

                candidate_timestamp = (
                    pd.to_datetime(
                        candidate_row[
                            "timestamp_utc"
                        ],
                        utc=True
                    )
                )

                result[
                    "minutes_before_event"
                ] = float(
                    (
                        event_timestamp
                        -
                        candidate_timestamp
                    )
                    .total_seconds()
                    / 60.0
                )

            # ------------------------------------------------
            # Add result
            # ------------------------------------------------

            results.append(
                result
            )

        # ----------------------------------------------------
        # Sort by predicted distance
        # ----------------------------------------------------

        results.sort(
            key=lambda item:
                item[
                    "evidence_score"
                ],
            reverse=True
        )

        # ----------------------------------------------------
        # IMPORTANT:
        # Apply 50 km threshold AFTER RNN prediction
        # ----------------------------------------------------

        filtered_results = [
            result
            for result in results
            if result[
                "distance_to_spill_km"
            ] <= radius_km
        ]

        # ----------------------------------------------------
        # If no vessel is within 50 km after prediction
        # ----------------------------------------------------

        if not filtered_results:

            print(
                f"\nNo predicted vessel position "
                f"was within {radius_km:.1f} km "
                f"of the spill."
            )

            if results:

                print(
                    "\nClosest predicted positions:"
                )

                print("-" * 100)

                for result in results[:10]:

                    print(
                        f"MMSI: "
                        f"{result['mmsi']} | "
                        f"Predicted distance: "
                        f"{result['distance_to_spill_km']:.3f} km | "
                        f"Historical distance: "
                        f"{result['historical_distance_to_spill_km']:.3f} km"
                    )

                print("-" * 100)

            return []

        # ----------------------------------------------------
        # Assign final ranks
        # ----------------------------------------------------

        for index, result in enumerate(
            filtered_results,
            start=1
        ):

            result[
                "rank"
            ] = index

        print(
            f"\nFinal vessels within "
            f"{radius_km:.1f} km: "
            f"{len(filtered_results)}"
        )

        return filtered_results


# ============================================================
# SINGLETON
# ============================================================

_backtracking_service = None


def get_backtracking_service():

    global _backtracking_service

    if _backtracking_service is None:

        _backtracking_service = (
            BacktrackingService()
        )

    return _backtracking_service
from pathlib import Path
import pickle

import numpy as np
import pandas as pd
import torch

from models.rnn.model import create_model


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "rnn"
    / "weights"
    / "rnn_trajectory.pth"
)

FEATURE_SCALER_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed_ais"
    / "feature_scaler.pkl"
)

TARGET_SCALER_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed_ais"
    / "target_scaler.pkl"
)


# ============================================================
# CONFIGURATION
# ============================================================

HISTORY_LENGTH = 12

NUM_FEATURES = 7


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


# ============================================================
# RNN SERVICE
# ============================================================

class RNNService:

    def __init__(self):

        print("=" * 70)
        print("INITIALIZING RNN SERVICE")
        print("=" * 70)

        # ----------------------------------------------------
        # Check required files
        # ----------------------------------------------------

        if not MODEL_PATH.exists():

            raise FileNotFoundError(
                f"RNN model not found:\n{MODEL_PATH}"
            )

        if not FEATURE_SCALER_PATH.exists():

            raise FileNotFoundError(
                f"Feature scaler not found:\n"
                f"{FEATURE_SCALER_PATH}"
            )

        if not TARGET_SCALER_PATH.exists():

            raise FileNotFoundError(
                f"Target scaler not found:\n"
                f"{TARGET_SCALER_PATH}"
            )

        # ----------------------------------------------------
        # Load model
        # ----------------------------------------------------

        self.model = create_model()

        checkpoint = torch.load(
            MODEL_PATH,
            map_location=DEVICE
        )

        self.model.load_state_dict(
            checkpoint["model_state_dict"]
        )

        self.model = self.model.to(
            DEVICE
        )

        self.model.eval()

        # ----------------------------------------------------
        # Load feature scaler
        # ----------------------------------------------------

        with open(
            FEATURE_SCALER_PATH,
            "rb"
        ) as f:

            self.feature_scaler = pickle.load(f)

        # ----------------------------------------------------
        # Load target scaler
        # ----------------------------------------------------

        with open(
            TARGET_SCALER_PATH,
            "rb"
        ) as f:

            self.target_scaler = pickle.load(f)

        # ----------------------------------------------------
        # Recover exact feature names used during training
        # ----------------------------------------------------

        if hasattr(
            self.feature_scaler,
            "feature_names_in_"
        ):

            self.feature_names = list(
                self.feature_scaler.feature_names_in_
            )

        else:

            self.feature_names = [
                "delta_x_km",
                "delta_y_km",
                "sog_knots",
                "cog_sin",
                "cog_cos",
                "heading_sin",
                "heading_cos"
            ]

        # ----------------------------------------------------
        # Validate feature count
        # ----------------------------------------------------

        if len(self.feature_names) != NUM_FEATURES:

            raise ValueError(
                "\nUnexpected number of RNN features.\n"
                f"Expected: {NUM_FEATURES}\n"
                f"Found: {len(self.feature_names)}\n"
                f"Features: {self.feature_names}"
            )

        print(
            f"\nDevice: {DEVICE}"
        )

        print(
            f"History length: {HISTORY_LENGTH}"
        )

        print(
            f"Input features: {NUM_FEATURES}"
        )

        print(
            f"Feature order: {self.feature_names}"
        )

        print(
            "\nRNN service initialized successfully."
        )


    # ========================================================
    # VALIDATE INPUT
    # ========================================================

    def _validate_sequence(
        self,
        sequence
    ):

        sequence = np.asarray(
            sequence,
            dtype=np.float32
        )

        if sequence.shape != (
            HISTORY_LENGTH,
            NUM_FEATURES
        ):

            raise ValueError(
                "\nInvalid AIS sequence shape.\n"
                f"Expected: "
                f"({HISTORY_LENGTH}, {NUM_FEATURES})\n"
                f"Received: {sequence.shape}"
            )

        return sequence


    # ========================================================
    # SCALE FEATURES
    # ========================================================

    def _scale_features(
        self,
        sequence
    ):
        """
        Scale AIS features using the exact feature names
        used when the StandardScaler was fitted.

        This prevents the sklearn feature-name warning.
        """

        sequence_df = pd.DataFrame(
            sequence,
            columns=self.feature_names
        )

        sequence_scaled = (
            self.feature_scaler
            .transform(sequence_df)
        )

        return sequence_scaled.astype(
            np.float32
        )


    # ========================================================
    # PREDICT DISPLACEMENT
    # ========================================================

    def predict_displacement(
        self,
        sequence
    ):
        """
        Predict the next vessel displacement.

        Input:
            sequence -> 12 AIS observations × 7 features

        Output:
            delta_x_km
            delta_y_km
        """

        sequence = self._validate_sequence(
            sequence
        )

        # ----------------------------------------------------
        # Scale features
        # ----------------------------------------------------

        sequence_scaled = (
            self._scale_features(
                sequence
            )
        )

        # ----------------------------------------------------
        # Convert to tensor
        # ----------------------------------------------------

        tensor = torch.tensor(
            sequence_scaled,
            dtype=torch.float32
        )

        tensor = tensor.unsqueeze(
            0
        )

        tensor = tensor.to(
            DEVICE
        )

        # ----------------------------------------------------
        # Prediction
        # ----------------------------------------------------

        with torch.no_grad():

            prediction = self.model(
                tensor
            )

        prediction = (
            prediction
            .cpu()
            .numpy()
        )

        # ----------------------------------------------------
        # Convert prediction back to km
        # ----------------------------------------------------

        displacement = (
            self.target_scaler
            .inverse_transform(
                prediction
            )
        )

        delta_x_km = float(
            displacement[0, 0]
        )

        delta_y_km = float(
            displacement[0, 1]
        )

        return {

            "delta_x_km":
                delta_x_km,

            "delta_y_km":
                delta_y_km
        }


    # ========================================================
    # PREDICT NEXT POSITION
    # ========================================================

    def predict_position(
        self,
        sequence,
        current_latitude,
        current_longitude
    ):
        """
        Predict the vessel's next geographic position.
        """

        result = self.predict_displacement(
            sequence
        )

        delta_x_km = result[
            "delta_x_km"
        ]

        delta_y_km = result[
            "delta_y_km"
        ]

        # ----------------------------------------------------
        # Convert km displacement to degrees
        # ----------------------------------------------------

        km_per_degree_latitude = 111.32

        predicted_latitude = (
            current_latitude
            +
            delta_y_km
            / km_per_degree_latitude
        )

        latitude_radians = np.deg2rad(
            current_latitude
        )

        km_per_degree_longitude = (
            km_per_degree_latitude
            *
            np.cos(latitude_radians)
        )

        km_per_degree_longitude = max(
            abs(km_per_degree_longitude),
            1e-6
        )

        predicted_longitude = (
            current_longitude
            +
            delta_x_km
            / km_per_degree_longitude
        )

        # ----------------------------------------------------
        # Calculate total predicted movement
        # ----------------------------------------------------

        predicted_movement_km = float(
            np.sqrt(
                delta_x_km ** 2
                +
                delta_y_km ** 2
            )
        )

        return {

            "current_latitude":
                float(current_latitude),

            "current_longitude":
                float(current_longitude),

            "delta_x_km":
                delta_x_km,

            "delta_y_km":
                delta_y_km,

            "predicted_movement_km":
                predicted_movement_km,

            "predicted_latitude":
                float(predicted_latitude),

            "predicted_longitude":
                float(predicted_longitude)
        }


# ============================================================
# SINGLETON
# ============================================================

_rnn_service = None


def get_rnn_service():

    global _rnn_service

    if _rnn_service is None:

        _rnn_service = RNNService()

    return _rnn_service
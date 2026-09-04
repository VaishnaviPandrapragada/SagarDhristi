import torch
import torch.nn as nn


class VesselTrajectoryLSTM(nn.Module):
    """
    LSTM model for vessel trajectory prediction.

    Input:
        Sequence of AIS observations.

    Each observation contains:
        1. latitude
        2. longitude
        3. speed over ground
        4. sin(COG)
        5. cos(COG)
        6. sin(heading)
        7. cos(heading)

    Output:
        Predicted future latitude and longitude.
    """

    def __init__(
        self,
        input_size=7,
        hidden_size_1=64,
        hidden_size_2=32,
        output_size=2,
        dropout=0.2
    ):
        super().__init__()

        # ----------------------------------------------------
        # First LSTM layer
        # ----------------------------------------------------

        self.lstm1 = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size_1,
            batch_first=True
        )

        # ----------------------------------------------------
        # Dropout
        # ----------------------------------------------------

        self.dropout = nn.Dropout(dropout)

        # ----------------------------------------------------
        # Second LSTM layer
        # ----------------------------------------------------

        self.lstm2 = nn.LSTM(
            input_size=hidden_size_1,
            hidden_size=hidden_size_2,
            batch_first=True
        )

        # ----------------------------------------------------
        # Fully connected layers
        # ----------------------------------------------------

        self.fc1 = nn.Linear(
            hidden_size_2,
            32
        )

        self.relu = nn.ReLU()

        self.fc2 = nn.Linear(
            32,
            output_size
        )

    def forward(self, x):
        """
        Forward pass.

        x shape:
            (batch_size, sequence_length, input_size)

        Output shape:
            (batch_size, 2)
        """

        # First LSTM
        x, _ = self.lstm1(x)

        x = self.dropout(x)

        # Second LSTM
        x, _ = self.lstm2(x)

        # ----------------------------------------------------
        # Take the final time step
        # ----------------------------------------------------

        x = x[:, -1, :]

        # Fully connected layers
        x = self.fc1(x)

        x = self.relu(x)

        x = self.dropout(x)

        x = self.fc2(x)

        return x


def create_model():
    """
    Create and return the LSTM model.
    """

    model = VesselTrajectoryLSTM(
        input_size=7,
        hidden_size_1=64,
        hidden_size_2=32,
        output_size=2,
        dropout=0.2
    )

    return model


if __name__ == "__main__":

    # --------------------------------------------------------
    # Simple model test
    # --------------------------------------------------------

    model = create_model()

    print("=" * 60)
    print("VESSEL TRAJECTORY LSTM")
    print("=" * 60)

    print(model)

    # Dummy input:
    # batch = 4
    # history = 12
    # features = 7

    dummy_input = torch.randn(
        4,
        12,
        7
    )

    output = model(dummy_input)

    print("\nInput shape:")
    print(dummy_input.shape)

    print("\nOutput shape:")
    print(output.shape)

    print("\nExpected output:")
    print("(4, 2)")

    print("\nModel test complete.")
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

from model import create_model


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed_ais"
)

WEIGHTS_DIR = (
    PROJECT_ROOT
    / "models"
    / "rnn"
    / "weights"
)

WEIGHTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


MODEL_PATH = (
    WEIGHTS_DIR
    / "rnn_trajectory.pth"
)


# ============================================================
# TRAINING CONFIGURATION
# ============================================================

BATCH_SIZE = 32

EPOCHS = 100

LEARNING_RATE = 0.001

PATIENCE = 15

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    print("=" * 70)
    print("LOADING PROCESSED AIS DATA")
    print("=" * 70)

    X_train = np.load(
        DATA_DIR / "X_train.npy"
    )

    y_train = np.load(
        DATA_DIR / "y_train.npy"
    )

    X_val = np.load(
        DATA_DIR / "X_val.npy"
    )

    y_val = np.load(
        DATA_DIR / "y_val.npy"
    )

    print("\nTraining:")
    print("X_train:", X_train.shape)
    print("y_train:", y_train.shape)

    print("\nValidation:")
    print("X_val:", X_val.shape)
    print("y_val:", y_val.shape)

    # --------------------------------------------------------
    # Convert to PyTorch tensors
    # --------------------------------------------------------

    X_train = torch.tensor(
        X_train,
        dtype=torch.float32
    )

    y_train = torch.tensor(
        y_train,
        dtype=torch.float32
    )

    X_val = torch.tensor(
        X_val,
        dtype=torch.float32
    )

    y_val = torch.tensor(
        y_val,
        dtype=torch.float32
    )

    # --------------------------------------------------------
    # Remove FUTURE_STEPS dimension
    #
    # y shape:
    # (samples, 1, 2)
    #
    # becomes:
    # (samples, 2)
    # --------------------------------------------------------

    y_train = y_train.squeeze(1)

    y_val = y_val.squeeze(1)

    return (
        X_train,
        y_train,
        X_val,
        y_val
    )


# ============================================================
# CREATE DATALOADERS
# ============================================================

def create_dataloaders(
    X_train,
    y_train,
    X_val,
    y_val
):

    train_dataset = TensorDataset(
        X_train,
        y_train
    )

    val_dataset = TensorDataset(
        X_val,
        y_val
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False
    )

    return (
        train_loader,
        val_loader
    )


# ============================================================
# TRAIN ONE EPOCH
# ============================================================

def train_one_epoch(
    model,
    loader,
    criterion,
    optimizer
):

    model.train()

    total_loss = 0.0

    for X_batch, y_batch in loader:

        X_batch = X_batch.to(DEVICE)

        y_batch = y_batch.to(DEVICE)

        # ----------------------------------------------------
        # Clear gradients
        # ----------------------------------------------------

        optimizer.zero_grad()

        # ----------------------------------------------------
        # Forward pass
        # ----------------------------------------------------

        predictions = model(
            X_batch
        )

        # ----------------------------------------------------
        # Calculate loss
        # ----------------------------------------------------

        loss = criterion(
            predictions,
            y_batch
        )

        # ----------------------------------------------------
        # Backpropagation
        # ----------------------------------------------------

        loss.backward()

        # ----------------------------------------------------
        # Update weights
        # ----------------------------------------------------

        optimizer.step()

        total_loss += (
            loss.item()
            * X_batch.size(0)
        )

    return (
        total_loss
        / len(loader.dataset)
    )


# ============================================================
# VALIDATION
# ============================================================

def validate(
    model,
    loader,
    criterion
):

    model.eval()

    total_loss = 0.0

    with torch.no_grad():

        for X_batch, y_batch in loader:

            X_batch = X_batch.to(DEVICE)

            y_batch = y_batch.to(DEVICE)

            predictions = model(
                X_batch
            )

            loss = criterion(
                predictions,
                y_batch
            )

            total_loss += (
                loss.item()
                * X_batch.size(0)
            )

    return (
        total_loss
        / len(loader.dataset)
    )


# ============================================================
# MAIN TRAINING
# ============================================================

def main():

    print("\n")
    print("=" * 70)
    print("VESSEL TRAJECTORY LSTM TRAINING")
    print("=" * 70)

    print(
        f"\nDevice: {DEVICE}"
    )

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    (
        X_train,
        y_train,
        X_val,
        y_val
    ) = load_data()

    # --------------------------------------------------------
    # Create loaders
    # --------------------------------------------------------

    (
        train_loader,
        val_loader
    ) = create_dataloaders(
        X_train,
        y_train,
        X_val,
        y_val
    )

    # --------------------------------------------------------
    # Create model
    # --------------------------------------------------------

    model = create_model()

    model = model.to(DEVICE)

    print("\nModel:")
    print(model)

    # --------------------------------------------------------
    # Loss
    # --------------------------------------------------------

    criterion = nn.MSELoss()

    # --------------------------------------------------------
    # Optimizer
    # --------------------------------------------------------

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE
    )

    # --------------------------------------------------------
    # Training variables
    # --------------------------------------------------------

    best_val_loss = float("inf")

    epochs_without_improvement = 0

    # --------------------------------------------------------
    # Training loop
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("STARTING TRAINING")
    print("=" * 70)

    for epoch in range(
        1,
        EPOCHS + 1
    ):

        train_loss = train_one_epoch(
            model,
            train_loader,
            criterion,
            optimizer
        )

        val_loss = validate(
            model,
            val_loader,
            criterion
        )

        print(
            f"Epoch [{epoch:03d}/{EPOCHS}] "
            f"| Train Loss: {train_loss:.6f} "
            f"| Val Loss: {val_loss:.6f}"
        )

        # ----------------------------------------------------
        # Save best model
        # ----------------------------------------------------

        if val_loss < best_val_loss:

            best_val_loss = val_loss

            epochs_without_improvement = 0

            torch.save(
                {
                    "model_state_dict":
                        model.state_dict(),

                    "input_size": 7,

                    "hidden_size_1": 64,

                    "hidden_size_2": 32,

                    "output_size": 2,

                    "dropout": 0.2,

                    "best_val_loss":
                        best_val_loss,
                },
                MODEL_PATH
            )

            print(
                f"  ✓ Best model saved "
                f"→ {MODEL_PATH}"
            )

        else:

            epochs_without_improvement += 1

        # ----------------------------------------------------
        # Early stopping
        # ----------------------------------------------------

        if (
            epochs_without_improvement
            >= PATIENCE
        ):

            print(
                "\nEarly stopping triggered."
            )

            break

    print("\n")
    print("=" * 70)
    print("TRAINING COMPLETE")
    print("=" * 70)

    print(
        f"\nBest validation loss: "
        f"{best_val_loss:.6f}"
    )

    print(
        f"Model saved at:\n"
        f"{MODEL_PATH}"
    )


if __name__ == "__main__":
    main()
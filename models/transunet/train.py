from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import transforms
from sklearn.model_selection import train_test_split

from .model import create_model
from .dataset import TransUNetDataset, collect_samples


# ============================================================
# Configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_DIR = PROJECT_ROOT / "data"

WEIGHTS_DIR = (
    Path(__file__).resolve().parent
    / "weights"
)

BEST_MODEL_PATH = (
    WEIGHTS_DIR
    / "transunet_best.pth"
)

IMG_SIZE = 128
BATCH_SIZE = 16
EPOCHS = 10
LEARNING_RATE = 1e-4
RANDOM_STATE = 42


# ============================================================
# Device
# ============================================================

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("=" * 60)
print("TRANSUNET TRAINING")
print("=" * 60)

print(f"Device: {device}")


# ============================================================
# Prepare directories
# ============================================================

WEIGHTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# Transform
# ============================================================

transform = transforms.Compose([
    transforms.Resize(
        (IMG_SIZE, IMG_SIZE)
    ),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=(0.485, 0.456, 0.406),
        std=(0.229, 0.224, 0.225)
    )
])


# ============================================================
# Load samples
# ============================================================

print("\nLoading dataset...")

samples = collect_samples(
    DATASET_DIR,
    samples_per_class=500
)

print(f"Total samples: {len(samples)}")


# ============================================================
# Labels
# ============================================================

labels = np.array([
    label
    for _, label in samples
])


# ============================================================
# Train / Validation / Test split
# ============================================================

train_samples, temp_samples = train_test_split(
    samples,
    test_size=0.30,
    random_state=RANDOM_STATE,
    stratify=labels
)

temp_labels = np.array([
    label
    for _, label in temp_samples
])

val_samples, test_samples = train_test_split(
    temp_samples,
    test_size=0.50,
    random_state=RANDOM_STATE,
    stratify=temp_labels
)


print("\nDataset split:")
print(f"Train      : {len(train_samples)}")
print(f"Validation : {len(val_samples)}")
print(f"Test       : {len(test_samples)}")


# ============================================================
# Datasets
# ============================================================

train_dataset = TransUNetDataset(
    train_samples,
    transform=transform
)

val_dataset = TransUNetDataset(
    val_samples,
    transform=transform
)

test_dataset = TransUNetDataset(
    test_samples,
    transform=transform
)


# ============================================================
# DataLoaders
# ============================================================

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=0
)

val_loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0
)

test_loader = DataLoader(
    test_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0
)


# ============================================================
# Model
# ============================================================

print("\nCreating TransUNet model...")

model = create_model()

model.to(device)

print("Model created successfully.")


# ============================================================
# Loss and optimizer
# ============================================================

criterion = nn.CrossEntropyLoss()

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=LEARNING_RATE
)


# ============================================================
# Validation function
# ============================================================

def validate():

    model.eval()

    total_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():

        for images, labels_batch in val_loader:

            images = images.to(device)
            labels_batch = labels_batch.to(device)

            outputs = model(images)

            loss = criterion(
                outputs,
                labels_batch
            )

            total_loss += (
                loss.item()
                * images.size(0)
            )

            predictions = torch.argmax(
                outputs,
                dim=1
            )

            correct += (
                predictions == labels_batch
            ).sum().item()

            total += labels_batch.size(0)

    avg_loss = total_loss / total
    accuracy = correct / total

    return avg_loss, accuracy


# ============================================================
# Training
# ============================================================

best_val_accuracy = 0.0


print("\nStarting training...\n")


for epoch in range(EPOCHS):

    model.train()

    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels_batch in train_loader:

        images = images.to(device)
        labels_batch = labels_batch.to(device)

        # Clear gradients
        optimizer.zero_grad()

        # Forward pass
        outputs = model(images)

        # Loss
        loss = criterion(
            outputs,
            labels_batch
        )

        # Backpropagation
        loss.backward()

        # Update weights
        optimizer.step()

        # Statistics
        running_loss += (
            loss.item()
            * images.size(0)
        )

        predictions = torch.argmax(
            outputs,
            dim=1
        )

        correct += (
            predictions == labels_batch
        ).sum().item()

        total += labels_batch.size(0)

    train_loss = running_loss / total
    train_accuracy = correct / total

    val_loss, val_accuracy = validate()

    print(
        f"Epoch [{epoch + 1}/{EPOCHS}] "
        f"| Train Loss: {train_loss:.4f} "
        f"| Train Acc: {train_accuracy:.4f} "
        f"| Val Loss: {val_loss:.4f} "
        f"| Val Acc: {val_accuracy:.4f}"
    )

    # Save best model
    if val_accuracy > best_val_accuracy:

        best_val_accuracy = val_accuracy

        torch.save(
            model.state_dict(),
            BEST_MODEL_PATH
        )

        print(
            f"  ✓ Best model saved "
            f"(Val Acc: {val_accuracy:.4f})"
        )


# ============================================================
# Load best model
# ============================================================

print("\nLoading best model...")

model.load_state_dict(
    torch.load(
        BEST_MODEL_PATH,
        map_location=device
    )
)

model.eval()


# ============================================================
# Final Test
# ============================================================

correct = 0
total = 0

all_predictions = []
all_labels = []


with torch.no_grad():

    for images, labels_batch in test_loader:

        images = images.to(device)
        labels_batch = labels_batch.to(device)

        outputs = model(images)

        predictions = torch.argmax(
            outputs,
            dim=1
        )

        correct += (
            predictions == labels_batch
        ).sum().item()

        total += labels_batch.size(0)

        all_predictions.extend(
            predictions.cpu().numpy()
        )

        all_labels.extend(
            labels_batch.cpu().numpy()
        )


test_accuracy = correct / total


print("\n" + "=" * 60)
print("FINAL TEST RESULT")
print("=" * 60)

print(
    f"Test Accuracy : {test_accuracy:.4f}"
)

print(
    f"Test Accuracy : {test_accuracy * 100:.2f}%"
)

print("\nBest model saved at:")
print(BEST_MODEL_PATH)

print("\n" + "=" * 60)
print("TRANSUNET TRAINING COMPLETED")
print("=" * 60)
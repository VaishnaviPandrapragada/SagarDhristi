from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

import torch
from torch.utils.data import Dataset, DataLoader

import albumentations as A
from albumentations.pytorch import ToTensorV2

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

from .model import create_model


# ============================================================
# PATHS
# ============================================================

# Project root:
# D:\SIH 2026\

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "deeplabv3"
    / "weights"
    / "deeplabv3plus_oilspill.pth"
)


# ============================================================
# CONFIGURATION
# ============================================================

IMG_SIZE = 400

SAMPLES_PER_CLASS = 500

RANDOM_STATE = 42

BATCH_SIZE = 4


# ============================================================
# DEVICE
# ============================================================

device = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


# ============================================================
# TRANSFORMATION
# ============================================================

transform = A.Compose([
    A.Resize(
        IMG_SIZE,
        IMG_SIZE
    ),

    A.Normalize(
        mean=(
            0.485,
            0.456,
            0.406
        ),
        std=(
            0.229,
            0.224,
            0.225
        )
    ),

    ToTensorV2()
])


# ============================================================
# GET IMAGE FILES
# ============================================================

def get_images(folder):

    valid_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".webp"
    }

    paths = []

    for path in folder.rglob("*"):

        if (
            path.is_file()
            and path.suffix.lower()
            in valid_extensions
        ):
            paths.append(path)

    return sorted(
        paths,
        key=lambda path: str(path).lower()
    )


# ============================================================
# BUILD DATAFRAME
# ============================================================

def build_dataframe():

    class_0_dir = DATA_DIR / "Class_0"
    class_1_dir = DATA_DIR / "Class_1"

    class_0_paths = get_images(
        class_0_dir
    )

    class_1_paths = get_images(
        class_1_dir
    )

    print("=" * 60)
    print("DATASET")
    print("=" * 60)

    print(
        f"Class 0 available: "
        f"{len(class_0_paths)}"
    )

    print(
        f"Class 1 available: "
        f"{len(class_1_paths)}"
    )

    # --------------------------------------------------------
    # Select first 500 from each class
    # --------------------------------------------------------

    class_0_paths = (
        class_0_paths[:SAMPLES_PER_CLASS]
    )

    class_1_paths = (
        class_1_paths[:SAMPLES_PER_CLASS]
    )

    records = []

    for path in class_0_paths:

        records.append({
            "path": str(path),
            "label": 0
        })

    for path in class_1_paths:

        records.append({
            "path": str(path),
            "label": 1
        })

    df = pd.DataFrame(
        records
    )

    # --------------------------------------------------------
    # Shuffle exactly like the training pipeline
    # --------------------------------------------------------

    df = df.sample(
        frac=1,
        random_state=RANDOM_STATE
    ).reset_index(
        drop=True
    )

    print()
    print(
        f"Selected total: {len(df)}"
    )

    print(
        "Class distribution:"
    )

    print(
        df["label"]
        .value_counts()
        .sort_index()
        .to_dict()
    )

    return df


# ============================================================
# CREATE EXACT SAME SPLIT
# ============================================================

def create_test_split(df):

    # 70% train / 30% temporary

    train_df, temp_df = train_test_split(
        df,
        test_size=0.30,
        random_state=RANDOM_STATE,
        stratify=df["label"]
    )

    # 15% validation / 15% test

    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        random_state=RANDOM_STATE,
        stratify=temp_df["label"]
    )

    test_df = test_df.reset_index(
        drop=True
    )

    return test_df


# ============================================================
# DATASET
# ============================================================

class OilSpillTestDataset(Dataset):

    def __init__(
        self,
        dataframe,
        transform=None
    ):

        self.dataframe = (
            dataframe
            .reset_index(drop=True)
        )

        self.transform = transform

    def __len__(self):

        return len(
            self.dataframe
        )

    def __getitem__(self, index):

        row = self.dataframe.iloc[
            index
        ]

        image_path = row["path"]

        label = int(
            row["label"]
        )

        image = Image.open(
            image_path
        ).convert("RGB")

        image = np.array(
            image
        )

        if self.transform:

            image = self.transform(
                image=image
            )["image"]

        return (
            image,
            label
        )


# ============================================================
# MAIN EVALUATION
# ============================================================

def main():

    print()
    print("=" * 60)
    print("DEEPLABV3+ LOCAL MODEL EVALUATION")
    print("=" * 60)

    print(
        "Device:",
        device
    )

    print(
        "Model:",
        MODEL_PATH
    )

    # --------------------------------------------------------
    # Check model
    # --------------------------------------------------------

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            f"Model not found:\n{MODEL_PATH}"
        )

    # --------------------------------------------------------
    # Build dataset
    # --------------------------------------------------------

    df = build_dataframe()

    # --------------------------------------------------------
    # Recreate exact test split
    # --------------------------------------------------------

    test_df = create_test_split(
        df
    )

    print()
    print(
        f"Test images: {len(test_df)}"
    )

    print(
        "Test distribution:"
    )

    print(
        test_df["label"]
        .value_counts()
        .sort_index()
        .to_dict()
    )

    # --------------------------------------------------------
    # Dataset + DataLoader
    # --------------------------------------------------------

    test_dataset = OilSpillTestDataset(
        test_df,
        transform
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0
    )

    # --------------------------------------------------------
    # Load model
    # --------------------------------------------------------

    print()
    print("Loading model...")

    model = create_model()

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=device
    )

    # Support either:
    # state_dict directly
    # OR checkpoint containing state_dict

    if (
        isinstance(checkpoint, dict)
        and "state_dict" in checkpoint
    ):

        model.load_state_dict(
            checkpoint["state_dict"]
        )

    else:

        model.load_state_dict(
            checkpoint
        )

    model.to(device)

    model.eval()

    print("Model loaded successfully.")

    # --------------------------------------------------------
    # Predictions
    # --------------------------------------------------------

    all_predictions = []

    all_labels = []

    print()
    print("Running test set...")

    with torch.no_grad():

        for images, labels in test_loader:

            images = images.to(
                device
            )

            outputs = model(
                images
            )

            probabilities = torch.sigmoid(
                outputs
            )

            predictions = (
                probabilities >= 0.5
            ).long()

            all_predictions.extend(
                predictions
                .cpu()
                .numpy()
            )

            all_labels.extend(
                labels
                .numpy()
                .astype(int)
            )

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    accuracy = accuracy_score(
        all_labels,
        all_predictions
    )

    precision = precision_score(
        all_labels,
        all_predictions,
        zero_division=0
    )

    recall = recall_score(
        all_labels,
        all_predictions,
        zero_division=0
    )

    f1 = f1_score(
        all_labels,
        all_predictions,
        zero_division=0
    )

    # --------------------------------------------------------
    # Confusion matrix
    # --------------------------------------------------------

    cm = confusion_matrix(
        all_labels,
        all_predictions
    )

    tn, fp, fn, tp = cm.ravel()

    # Classification IoU
    classification_iou = (
        tp /
        (tp + fp + fn)
        if (tp + fp + fn) > 0
        else 0
    )

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("FINAL TEST RESULTS")
    print("=" * 60)

    print(
        f"Accuracy           : {accuracy:.4f}"
    )

    print(
        f"Precision          : {precision:.4f}"
    )

    print(
        f"Recall             : {recall:.4f}"
    )

    print(
        f"F1 Score           : {f1:.4f}"
    )

    print(
        f"Classification IoU : "
        f"{classification_iou:.4f}"
    )

    # --------------------------------------------------------
    # Confusion matrix
    # --------------------------------------------------------

    print()
    print("Confusion Matrix")
    print("----------------")

    print(
        "             Predicted"
    )

    print(
        "             Class 0  Class 1"
    )

    print(
        f"Actual 0    "
        f"{cm[0][0]:8d} "
        f"{cm[0][1]:8d}"
    )

    print(
        f"Actual 1    "
        f"{cm[1][0]:8d} "
        f"{cm[1][1]:8d}"
    )

    # --------------------------------------------------------
    # Classification report
    # --------------------------------------------------------

    print()
    print("Classification Report")
    print("---------------------")

    print(
        classification_report(
            all_labels,
            all_predictions,
            target_names=[
                "Class 0",
                "Class 1"
            ],
            zero_division=0
        )
    )

    print("=" * 60)
    print("LOCAL EVALUATION COMPLETED")
    print("=" * 60)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()
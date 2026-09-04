from pathlib import Path
import random

import numpy as np
import pandas as pd

from PIL import Image

import torch
import torch.nn as nn

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

# Current dataset location
DATASET_DIR = PROJECT_ROOT / "data"

# DeepLab weights directory
WEIGHTS_DIR = (
    Path(__file__).resolve().parent
    / "weights"
)

# Training output directory
OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "deeplabv3"
)

WEIGHTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# CONFIGURATION
# ============================================================

IMG_SIZE = 400

BATCH_SIZE = 4

# Reduced from 30 because we are training on CPU
EPOCHS = 10

LEARNING_RATE = 1e-3

RANDOM_STATE = 42

BEST_MODEL_PATH = (
    WEIGHTS_DIR
    / "deeplabv3plus_best.pth"
)


# ============================================================
# REPRODUCIBILITY
# ============================================================

random.seed(
    RANDOM_STATE
)

np.random.seed(
    RANDOM_STATE
)

torch.manual_seed(
    RANDOM_STATE
)


# ============================================================
# DEVICE
# ============================================================

device = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


print("=" * 60)
print("DEEPLABV3+ TRAINING")
print("=" * 60)

print(
    "Device:",
    device
)

print(
    "Epochs:",
    EPOCHS
)


# ============================================================
# TRANSFORMS
# ============================================================

train_transform = A.Compose([

    A.Resize(
        IMG_SIZE,
        IMG_SIZE
    ),

    A.HorizontalFlip(
        p=0.5
    ),

    A.VerticalFlip(
        p=0.5
    ),

    A.RandomRotate90(
        p=0.5
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


val_test_transform = A.Compose([

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
# DATASET CLASS
# ============================================================

class OilSpillDataset(Dataset):

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


    def __getitem__(
        self,
        index
    ):

        row = self.dataframe.iloc[
            index
        ]

        image_path = row[
            "path"
        ]

        label = int(
            row["label"]
        )

        image = Image.open(
            image_path
        ).convert(
            "RGB"
        )

        image = np.array(
            image
        )

        if self.transform:

            image = self.transform(
                image=image
            )["image"]

        label = torch.tensor(
            label,
            dtype=torch.float32
        )

        return (
            image,
            label
        )


# ============================================================
# GET IMAGE FILES
# ============================================================

def get_images(
    folder
):

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
            and
            path.suffix.lower()
            in valid_extensions
        ):

            paths.append(
                path
            )

    return sorted(
        paths,
        key=lambda path: str(path).lower()
    )


# ============================================================
# LOAD IMAGES
# ============================================================

class_0_paths = get_images(
    DATASET_DIR / "Class_0"
)

class_1_paths = get_images(
    DATASET_DIR / "Class_1"
)


print()
print("=" * 60)
print("DATASET")
print("=" * 60)

print(
    "Class 0 available:",
    len(class_0_paths)
)

print(
    "Class 1 available:",
    len(class_1_paths)
)


# ============================================================
# SELECT 500 FROM EACH CLASS
# ============================================================

class_0_paths = class_0_paths[
    :500
]

class_1_paths = class_1_paths[
    :500
]


print()
print(
    "Selected Class 0:",
    len(class_0_paths)
)

print(
    "Selected Class 1:",
    len(class_1_paths)
)


# ============================================================
# CREATE DATAFRAME
# ============================================================

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


# ============================================================
# SHUFFLE
# ============================================================

df = df.sample(

    frac=1,

    random_state=RANDOM_STATE

).reset_index(
    drop=True
)


# ============================================================
# TRAIN / VALIDATION / TEST SPLIT
# ============================================================

train_df, temp_df = train_test_split(

    df,

    test_size=0.30,

    random_state=RANDOM_STATE,

    stratify=df["label"]
)


val_df, test_df = train_test_split(

    temp_df,

    test_size=0.50,

    random_state=RANDOM_STATE,

    stratify=temp_df["label"]
)


print()
print("=" * 60)
print("DATASET SPLIT")
print("=" * 60)

print(
    "Training:",
    len(train_df)
)

print(
    "Validation:",
    len(val_df)
)

print(
    "Testing:",
    len(test_df)
)


print()
print(
    "Training distribution:",
    train_df["label"]
    .value_counts()
    .sort_index()
    .to_dict()
)

print(
    "Validation distribution:",
    val_df["label"]
    .value_counts()
    .sort_index()
    .to_dict()
)

print(
    "Testing distribution:",
    test_df["label"]
    .value_counts()
    .sort_index()
    .to_dict()
)


# ============================================================
# SAVE SPLITS
# ============================================================

SPLITS_DIR = (
    PROJECT_ROOT
    / "splits"
)

SPLITS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


train_df.to_csv(
    SPLITS_DIR / "train.csv",
    index=False
)

val_df.to_csv(
    SPLITS_DIR / "validation.csv",
    index=False
)

test_df.to_csv(
    SPLITS_DIR / "test.csv",
    index=False
)


# ============================================================
# CREATE DATASETS
# ============================================================

train_dataset = OilSpillDataset(

    train_df,

    train_transform

)


val_dataset = OilSpillDataset(

    val_df,

    val_test_transform

)


test_dataset = OilSpillDataset(

    test_df,

    val_test_transform

)


# ============================================================
# DATA LOADERS
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
# CREATE MODEL
# ============================================================

print()
print("Creating model...")

model = create_model().to(
    device
)


print(
    "Model created successfully."
)


# ============================================================
# LOSS FUNCTION
# ============================================================

criterion = nn.BCEWithLogitsLoss()


# ============================================================
# OPTIMIZER
# ============================================================

optimizer = torch.optim.Adam(

    filter(
        lambda p: p.requires_grad,
        model.parameters()
    ),

    lr=LEARNING_RATE

)


# ============================================================
# TRAINING HISTORY
# ============================================================

train_losses = []

val_losses = []

train_accuracies = []

val_accuracies = []


# ============================================================
# BEST MODEL
# ============================================================

best_val_loss = float(
    "inf"
)


# ============================================================
# TRAINING LOOP
# ============================================================

for epoch in range(
    EPOCHS
):

    # ========================================================
    # TRAINING
    # ========================================================

    model.train()

    running_train_loss = 0.0

    train_predictions = []

    train_labels = []


    for images, labels in train_loader:

        images = images.to(
            device
        )

        labels = labels.to(
            device
        )


        optimizer.zero_grad()


        outputs = model(
            images
        )


        loss = criterion(

            outputs,

            labels

        )


        loss.backward()


        optimizer.step()


        running_train_loss += (

            loss.item()
            *
            images.size(0)

        )


        probabilities = torch.sigmoid(
            outputs
        )


        predictions = (

            probabilities >= 0.5

        ).long()


        train_predictions.extend(

            predictions
            .detach()
            .cpu()
            .numpy()

        )


        train_labels.extend(

            labels
            .detach()
            .cpu()
            .numpy()
            .astype(int)

        )


    train_loss = (

        running_train_loss
        /
        len(train_dataset)

    )


    train_accuracy = accuracy_score(

        train_labels,

        train_predictions

    )


    # ========================================================
    # VALIDATION
    # ========================================================

    model.eval()

    running_val_loss = 0.0

    val_predictions = []

    val_labels = []


    with torch.no_grad():

        for images, labels in val_loader:

            images = images.to(
                device
            )

            labels = labels.to(
                device
            )


            outputs = model(
                images
            )


            loss = criterion(

                outputs,

                labels

            )


            running_val_loss += (

                loss.item()
                *
                images.size(0)

            )


            probabilities = torch.sigmoid(
                outputs
            )


            predictions = (

                probabilities >= 0.5

            ).long()


            val_predictions.extend(

                predictions
                .cpu()
                .numpy()

            )


            val_labels.extend(

                labels
                .cpu()
                .numpy()
                .astype(int)

            )


    val_loss = (

        running_val_loss
        /
        len(val_dataset)

    )


    val_accuracy = accuracy_score(

        val_labels,

        val_predictions

    )


    # ========================================================
    # STORE HISTORY
    # ========================================================

    train_losses.append(
        train_loss
    )

    val_losses.append(
        val_loss
    )

    train_accuracies.append(
        train_accuracy
    )

    val_accuracies.append(
        val_accuracy
    )


    # ========================================================
    # PRINT RESULTS
    # ========================================================

    print()
    print(
        "=" * 60
    )

    print(
        f"Epoch [{epoch + 1}/{EPOCHS}]"
    )

    print(
        f"Train Loss     : {train_loss:.4f}"
    )

    print(
        f"Train Accuracy : {train_accuracy:.4f}"
    )

    print(
        f"Val Loss       : {val_loss:.4f}"
    )

    print(
        f"Val Accuracy   : {val_accuracy:.4f}"
    )


    # ========================================================
    # SAVE BEST MODEL
    # ========================================================

    if val_loss < best_val_loss:

        best_val_loss = val_loss

        torch.save(

            model.state_dict(),

            BEST_MODEL_PATH

        )

        print(
            "✓ Best model saved."
        )


# ============================================================
# SAVE TRAINING HISTORY
# ============================================================

history = pd.DataFrame({

    "epoch":
        range(
            1,
            EPOCHS + 1
        ),

    "train_loss":
        train_losses,

    "val_loss":
        val_losses,

    "train_accuracy":
        train_accuracies,

    "val_accuracy":
        val_accuracies

})


history.to_csv(

    OUTPUT_DIR
    / "training_history.csv",

    index=False

)


# ============================================================
# LOAD BEST MODEL
# ============================================================

print()
print(
    "Loading best model..."
)


model.load_state_dict(

    torch.load(

        BEST_MODEL_PATH,

        map_location=device

    )

)


model.eval()


print(
    "Best model loaded."
)


# ============================================================
# FINAL TEST
# ============================================================

all_predictions = []

all_labels = []


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


# ============================================================
# FINAL METRICS
# ============================================================

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


cm = confusion_matrix(

    all_labels,

    all_predictions

)


# ============================================================
# CLASSIFICATION IoU
# ============================================================

tn, fp, fn, tp = cm.ravel()


classification_iou = (

    tp
    /
    (tp + fp + fn)

    if
    (tp + fp + fn) > 0

    else 0

)


# ============================================================
# FINAL RESULTS
# ============================================================

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
    f"Classification IoU : {classification_iou:.4f}"
)


# ============================================================
# CONFUSION MATRIX
# ============================================================

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


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

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


# ============================================================
# SAVE RESULTS
# ============================================================

results = pd.DataFrame({

    "Metric": [

        "Accuracy",

        "Precision",

        "Recall",

        "F1 Score",

        "Classification IoU"

    ],

    "Value": [

        accuracy,

        precision,

        recall,

        f1,

        classification_iou

    ]

})


results.to_csv(

    OUTPUT_DIR
    / "test_results.csv",

    index=False

)


# ============================================================
# COMPLETION
# ============================================================

print()
print("=" * 60)
print("DEEPLABV3+ TRAINING COMPLETED")
print("=" * 60)


print()
print(
    "Best model saved at:"
)


print(
    BEST_MODEL_PATH
)


print()
print(
    "Training outputs saved at:"
)


print(
    OUTPUT_DIR
)
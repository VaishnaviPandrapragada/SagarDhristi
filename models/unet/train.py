import sys
from pathlib import Path

import torch
import torch.nn as nn
from torch.optim import Adam
from torch.utils.data import DataLoader, Subset
from tqdm import tqdm

# Allow imports from project root
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from preprocessing.sar_dataset import SARDataset
from models.unet.model import UNet


# ============================================================
# CONFIG
# ============================================================

TRAIN_SAMPLES = 2000
VAL_SAMPLES = 400

BATCH_SIZE = 8
EPOCHS = 10
LEARNING_RATE = 1e-4

IMAGE_SIZE = 128

MODEL_PATH = (
    ROOT
    / "models"
    / "unet"
    / "weights"
    / "unet_segmentation.pth"
)


# ============================================================
# DICE LOSS
# ============================================================

class DiceLoss(nn.Module):

    def __init__(self, smooth=1.0):
        super().__init__()
        self.smooth = smooth

    def forward(self, predictions, targets):

        predictions = torch.sigmoid(predictions)

        predictions = predictions.contiguous().view(-1)
        targets = targets.contiguous().view(-1)

        intersection = (predictions * targets).sum()

        dice = (
            (2.0 * intersection + self.smooth)
            /
            (
                predictions.sum()
                + targets.sum()
                + self.smooth
            )
        )

        return 1.0 - dice


# ============================================================
# COMBINED LOSS
# ============================================================

class CombinedLoss(nn.Module):

    def __init__(self):
        super().__init__()

        self.bce = nn.BCEWithLogitsLoss()
        self.dice = DiceLoss()

    def forward(self, predictions, targets):

        bce_loss = self.bce(predictions, targets)
        dice_loss = self.dice(predictions, targets)

        return bce_loss + dice_loss


# ============================================================
# METRICS
# ============================================================

def calculate_dice(predictions, targets, threshold=0.5):

    predictions = torch.sigmoid(predictions)

    predictions = (predictions > threshold).float()

    predictions = predictions.contiguous().view(-1)
    targets = targets.contiguous().view(-1)

    intersection = (predictions * targets).sum()

    dice = (
        (2.0 * intersection + 1.0)
        /
        (
            predictions.sum()
            + targets.sum()
            + 1.0
        )
    )

    return dice.item()


def calculate_iou(predictions, targets, threshold=0.5):

    predictions = torch.sigmoid(predictions)

    predictions = (predictions > threshold).float()

    predictions = predictions.contiguous().view(-1)
    targets = targets.contiguous().view(-1)

    intersection = (predictions * targets).sum()

    union = (
        predictions.sum()
        + targets.sum()
        - intersection
    )

    iou = (intersection + 1.0) / (union + 1.0)

    return iou.item()


# ============================================================
# TRAINING
# ============================================================

def train_one_epoch(
    model,
    loader,
    criterion,
    optimizer,
    device
):

    model.train()

    running_loss = 0.0
    running_dice = 0.0
    running_iou = 0.0

    for images, masks in tqdm(
        loader,
        desc="Training"
    ):

        images = images.to(device)
        masks = masks.to(device)

        optimizer.zero_grad()

        outputs = model(images)

        loss = criterion(outputs, masks)

        loss.backward()

        optimizer.step()

        running_loss += loss.item()
        running_dice += calculate_dice(
            outputs,
            masks
        )
        running_iou += calculate_iou(
            outputs,
            masks
        )

    batches = len(loader)

    return (
        running_loss / batches,
        running_dice / batches,
        running_iou / batches
    )


# ============================================================
# VALIDATION
# ============================================================

def validate(
    model,
    loader,
    criterion,
    device
):

    model.eval()

    running_loss = 0.0
    running_dice = 0.0
    running_iou = 0.0

    with torch.no_grad():

        for images, masks in tqdm(
            loader,
            desc="Validation"
        ):

            images = images.to(device)
            masks = masks.to(device)

            outputs = model(images)

            loss = criterion(
                outputs,
                masks
            )

            running_loss += loss.item()

            running_dice += calculate_dice(
                outputs,
                masks
            )

            running_iou += calculate_iou(
                outputs,
                masks
            )

    batches = len(loader)

    return (
        running_loss / batches,
        running_dice / batches,
        running_iou / batches
    )


# ============================================================
# MAIN
# ============================================================

def main():

    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    print("=" * 60)
    print("SagarDhristi - U-Net Segmentation Training")
    print("=" * 60)

    print("Device:", device)
    print("Image size:", IMAGE_SIZE)
    print("Training samples:", TRAIN_SAMPLES)
    print("Validation samples:", VAL_SAMPLES)
    print("Batch size:", BATCH_SIZE)
    print("Epochs:", EPOCHS)
    print("Learning rate:", LEARNING_RATE)

    # --------------------------------------------------------
    # DATASET
    # --------------------------------------------------------

    train_dataset = SARDataset(
        image_dir=r"D:\images\train",
        mask_dir=r"D:\masks\train",
        image_size=IMAGE_SIZE
                        )

    val_dataset = SARDataset(
        image_dir=r"D:\images\val",
        mask_dir=r"D:\masks\val",
        image_size=IMAGE_SIZE
        )

    print(
        "Full training dataset:",
        len(train_dataset)
    )

    print(
        "Full validation dataset:",
        len(val_dataset)
    )

    # Use subset for faster prototype training
    train_count = min(
        TRAIN_SAMPLES,
        len(train_dataset)
    )

    val_count = min(
        VAL_SAMPLES,
        len(val_dataset)
    )

    train_dataset = Subset(
        train_dataset,
        range(train_count)
    )

    val_dataset = Subset(
        val_dataset,
        range(val_count)
    )

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

    # --------------------------------------------------------
    # MODEL
    # --------------------------------------------------------

    model = UNet(
        in_channels=1,
        out_channels=1
    ).to(device)

    criterion = CombinedLoss()

    optimizer = Adam(
        model.parameters(),
        lr=LEARNING_RATE
    )

    print("Model ready.")
    print()

    # --------------------------------------------------------
    # TRAIN
    # --------------------------------------------------------

    best_dice = 0.0

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    for epoch in range(EPOCHS):

        print(
            f"\nEpoch {epoch + 1}/{EPOCHS}"
        )

        train_loss, train_dice, train_iou = (
            train_one_epoch(
                model,
                train_loader,
                criterion,
                optimizer,
                device
            )
        )

        val_loss, val_dice, val_iou = (
            validate(
                model,
                val_loader,
                criterion,
                device
            )
        )

        print(
            f"Train Loss: {train_loss:.4f}"
        )

        print(
            f"Train Dice: {train_dice:.4f}"
        )

        print(
            f"Train IoU : {train_iou:.4f}"
        )

        print(
            f"Val Loss  : {val_loss:.4f}"
        )

        print(
            f"Val Dice  : {val_dice:.4f}"
        )

        print(
            f"Val IoU   : {val_iou:.4f}"
        )

        # ----------------------------------------------------
        # SAVE BEST MODEL
        # ----------------------------------------------------

        if val_dice > best_dice:

            best_dice = val_dice

            torch.save(
                model.state_dict(),
                MODEL_PATH
            )

            print(
                f"✓ Saved best model → {MODEL_PATH}"
            )

    print()
    print("=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    print(
        f"Best validation Dice: {best_dice:.4f}"
    )
    print(
        f"Model saved at: {MODEL_PATH}"
    )


if __name__ == "__main__":
    main()
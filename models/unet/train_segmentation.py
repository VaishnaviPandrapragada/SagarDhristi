from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Subset
from torch.optim import Adam
from tqdm import tqdm

from preprocessing.sar_dataset import SARDataset
from models.unet.model import create_model


# ============================================================
# CONFIG
# ============================================================

TRAIN_IMAGE_DIR = r"D:\images\train"
TRAIN_MASK_DIR = r"D:\masks\train"

VAL_IMAGE_DIR = r"D:\images\val"
VAL_MASK_DIR = r"D:\masks\val"

TRAIN_SAMPLES = 300
VAL_SAMPLES = 100

BATCH_SIZE = 8
EPOCHS = 2
LEARNING_RATE = 1e-4

MODEL_PATH = Path("models/unet/weights/unet_segmentation.pth")


# ============================================================
# DICE LOSS
# ============================================================

def dice_loss(pred, target):

    pred = torch.sigmoid(pred)

    smooth = 1e-6

    intersection = (pred * target).sum()

    dice = (
        (2 * intersection + smooth)
        /
        (pred.sum() + target.sum() + smooth)
    )

    return 1 - dice


# ============================================================
# COMBINED LOSS
# ============================================================

def combined_loss(pred, target):

    bce = nn.functional.binary_cross_entropy_with_logits(
        pred,
        target
    )

    dice = dice_loss(pred, target)

    return bce + dice


# ============================================================
# DICE SCORE
# ============================================================

def dice_score(pred, target):

    pred = (torch.sigmoid(pred) > 0.5).float()

    smooth = 1e-6

    intersection = (pred * target).sum()

    dice = (
        (2 * intersection + smooth)
        /
        (pred.sum() + target.sum() + smooth)
    )

    return dice.item()


# ============================================================
# IOU SCORE
# ============================================================

def iou_score(pred, target):

    pred = (torch.sigmoid(pred) > 0.5).float()

    smooth = 1e-6

    intersection = (pred * target).sum()

    union = pred.sum() + target.sum() - intersection

    iou = (intersection + smooth) / (union + smooth)

    return iou.item()


# ============================================================
# MAIN
# ============================================================

def main():

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    print("=" * 60)
    print("U-NET OIL SPILL SEGMENTATION TRAINING")
    print("=" * 60)

    print("Device:", device)

    # --------------------------------------------------------
    # DATASET
    # --------------------------------------------------------

    train_dataset = SARDataset(
        TRAIN_IMAGE_DIR,
        TRAIN_MASK_DIR
    )

    val_dataset = SARDataset(
        VAL_IMAGE_DIR,
        VAL_MASK_DIR
    )

    # Use subset for fast development
    train_dataset = Subset(
        train_dataset,
        range(min(TRAIN_SAMPLES, len(train_dataset)))
    )

    val_dataset = Subset(
        val_dataset,
        range(min(VAL_SAMPLES, len(val_dataset)))
    )

    print()
    print("Training samples  :", len(train_dataset))
    print("Validation samples:", len(val_dataset))

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

    model = create_model().to(device)

    optimizer = Adam(
        model.parameters(),
        lr=LEARNING_RATE
    )

    # --------------------------------------------------------
    # TRAINING
    # --------------------------------------------------------

    best_dice = 0.0

    for epoch in range(EPOCHS):

        model.train()

        total_loss = 0.0

        progress = tqdm(
            train_loader,
            desc=f"Epoch {epoch + 1}/{EPOCHS}"
        )

        for images, masks in progress:

            images = images.to(device)
            masks = masks.to(device)

            optimizer.zero_grad()

            outputs = model(images)

            loss = combined_loss(
                outputs,
                masks
            )

            loss.backward()

            optimizer.step()

            total_loss += loss.item()

            progress.set_postfix(
                loss=f"{loss.item():.4f}"
            )

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        model.eval()

        val_dice = 0.0
        val_iou = 0.0

        with torch.no_grad():

            for images, masks in val_loader:

                images = images.to(device)
                masks = masks.to(device)

                outputs = model(images)

                val_dice += dice_score(
                    outputs,
                    masks
                )

                val_iou += iou_score(
                    outputs,
                    masks
                )

        val_dice /= len(val_loader)
        val_iou /= len(val_loader)

        avg_loss = total_loss / len(train_loader)

        print()
        print(
            f"Epoch {epoch + 1}/{EPOCHS} | "
            f"Loss: {avg_loss:.4f} | "
            f"Dice: {val_dice:.4f} | "
            f"IoU: {val_iou:.4f}"
        )

        # ----------------------------------------------------
        # SAVE BEST MODEL
        # ----------------------------------------------------

        if val_dice > best_dice:

            best_dice = val_dice

            MODEL_PATH.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            torch.save(
                model.state_dict(),
                MODEL_PATH
            )

            print(
                f"Saved best model → {MODEL_PATH}"
            )

    print()
    print("=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)

    print(f"Best validation Dice: {best_dice:.4f}")
    print(f"Model saved at       : {MODEL_PATH}")


if __name__ == "__main__":
    main()
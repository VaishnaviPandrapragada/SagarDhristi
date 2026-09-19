from pathlib import Path
import random

import numpy as np
from PIL import Image

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from models.transunet.model import create_model


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Local training dataset location
IMAGE_ROOT = Path(r"D:\images")
MASK_ROOT = Path(r"D:\masks")

# Portable fallback if dataset is placed inside the project
if not (IMAGE_ROOT / "train").exists():
    IMAGE_ROOT = PROJECT_ROOT / "images"
    MASK_ROOT = PROJECT_ROOT / "masks"


# ============================================================
# TRAINING CONFIGURATION
# Same dataset scale as U-Net / DeepLabV3+
# ============================================================

IMG_SIZE = 128
BATCH_SIZE = 8

EPOCHS = 10
TRAIN_LIMIT = 2000
VAL_LIMIT = 400

LEARNING_RATE = 1e-4
RANDOM_STATE = 42


# ============================================================
# OUTPUT
# ============================================================

WEIGHTS_DIR = (
    Path(__file__).resolve().parent / "weights"
)

BEST_MODEL_PATH = (
    WEIGHTS_DIR / "transunet_segmentation_best.pth"
)

WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# DEVICE
# ============================================================

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ============================================================
# REPRODUCIBILITY
# ============================================================

random.seed(RANDOM_STATE)
np.random.seed(RANDOM_STATE)
torch.manual_seed(RANDOM_STATE)

if torch.cuda.is_available():
    torch.cuda.manual_seed_all(RANDOM_STATE)


# ============================================================
# DATASET PAIR COLLECTION
# ============================================================

def collect_pairs(image_dir, mask_dir):
    pairs = []

    for path in sorted(image_dir.iterdir()):
        if (
            path.is_file()
            and path.suffix.lower()
            in {".png", ".jpg", ".jpeg", ".bmp", ".webp"}
        ):
            mask_path = mask_dir / path.name

            if mask_path.exists():
                pairs.append((path, mask_path))

    return pairs


# ============================================================
# DATASET
# ============================================================

class SegmentationDataset(Dataset):

    def __init__(self, pairs):
        self.pairs = pairs

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, index):

        image_path, mask_path = self.pairs[index]

        # ----------------------------------------------------
        # Image
        # ----------------------------------------------------

        image = (
            Image.open(image_path)
            .convert("RGB")
            .resize(
                (IMG_SIZE, IMG_SIZE),
                Image.Resampling.BILINEAR,
            )
        )

        # ----------------------------------------------------
        # Mask
        # ----------------------------------------------------

        mask = (
            Image.open(mask_path)
            .convert("L")
            .resize(
                (IMG_SIZE, IMG_SIZE),
                Image.Resampling.NEAREST,
            )
        )

        # ----------------------------------------------------
        # Convert image to float [0, 1]
        # ----------------------------------------------------

        image = (
            np.asarray(
                image,
                dtype=np.float32,
            )
            / 255.0
        )

        # ----------------------------------------------------
        # Convert mask to binary {0, 1}
        # ----------------------------------------------------

        mask = (
            np.asarray(
                mask,
                dtype=np.float32,
            )
            > 127
        ).astype(np.float32)

        # ----------------------------------------------------
        # ImageNet normalization
        # ----------------------------------------------------

        mean = np.array(
            [0.485, 0.456, 0.406],
            dtype=np.float32,
        )

        std = np.array(
            [0.229, 0.224, 0.225],
            dtype=np.float32,
        )

        image = (image - mean) / std

        # ----------------------------------------------------
        # Convert to tensors
        # ----------------------------------------------------

        image = (
            torch.from_numpy(image)
            .permute(2, 0, 1)
            .float()
        )

        mask = (
            torch.from_numpy(mask)
            .unsqueeze(0)
            .float()
        )

        return image, mask


# ============================================================
# DICE LOSS
# ============================================================

def dice_loss(logits, target):

    probabilities = torch.sigmoid(logits)

    intersection = (
        probabilities * target
    ).sum(dim=(1, 2, 3))

    denominator = (
        probabilities.sum(dim=(1, 2, 3))
        + target.sum(dim=(1, 2, 3))
    )

    dice = (
        (2.0 * intersection + 1.0)
        / (denominator + 1.0)
    )

    return 1.0 - dice.mean()


# ============================================================
# TRAIN / VALIDATION LOOP
# ============================================================

def run_epoch(model, loader, optimizer=None):

    training = optimizer is not None

    model.train(training)

    loss_sum = 0.0
    dice_sum = 0.0
    iou_sum = 0.0

    context = (
        torch.enable_grad()
        if training
        else torch.no_grad()
    )

    with context:

        for batch_index, (images, masks) in enumerate(loader):

            images = images.to(device)
            masks = masks.to(device)

            if training:
                optimizer.zero_grad(
                    set_to_none=True
                )

            logits = model(images)

            bce = nn.functional.binary_cross_entropy_with_logits(
                logits,
                masks,
            )

            dice = dice_loss(
                logits,
                masks,
            )

            loss = (
                0.5 * bce
                + 0.5 * dice
            )

            if training:

                loss.backward()

                optimizer.step()

            # ------------------------------------------------
            # Metrics
            # ------------------------------------------------

            predictions = (
                torch.sigmoid(logits) >= 0.5
            ).float()

            intersection = (
                predictions * masks
            ).sum().item()

            union = (
                (predictions + masks) > 0
            ).float().sum().item()

            prediction_pixels = (
                predictions.sum().item()
            )

            mask_pixels = (
                masks.sum().item()
            )

            batch_dice = (
                2.0 * intersection
                / (
                    prediction_pixels
                    + mask_pixels
                    + 1e-8
                )
            )

            batch_iou = (
                intersection
                / (union + 1e-8)
            )

            loss_sum += loss.item()
            dice_sum += batch_dice
            iou_sum += batch_iou

            # ------------------------------------------------
            # Progress
            # ------------------------------------------------

            if training and (
                batch_index == 0
                or (batch_index + 1) % 25 == 0
            ):
                print(
                    f"    batch {batch_index + 1}/"
                    f"{len(loader)} | "
                    f"loss {loss.item():.4f}"
                )

    count = max(len(loader), 1)

    return (
        loss_sum / count,
        dice_sum / count,
        iou_sum / count,
    )


# ============================================================
# MAIN
# ============================================================

def main():

    train_pairs = collect_pairs(
        IMAGE_ROOT / "train",
        MASK_ROOT / "train",
    )[:TRAIN_LIMIT]

    validation_pairs = collect_pairs(
        IMAGE_ROOT / "val",
        MASK_ROOT / "val",
    )[:VAL_LIMIT]

    if not train_pairs or not validation_pairs:

        raise FileNotFoundError(
            "Paired dataset not found.\n"
            f"Images: {IMAGE_ROOT}\n"
            f"Masks: {MASK_ROOT}"
        )

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    print("=" * 70)
    print("TRANSUNET SEGMENTATION TRAINING")
    print("=" * 70)

    print("Device:", device)
    print("Training pairs:", len(train_pairs))
    print("Validation pairs:", len(validation_pairs))
    print("Image size:", f"{IMG_SIZE}x{IMG_SIZE}")
    print("Batch size:", BATCH_SIZE)
    print("Epochs:", EPOCHS)
    print("Learning rate:", LEARNING_RATE)

    # --------------------------------------------------------
    # DataLoaders
    # --------------------------------------------------------

    train_loader = DataLoader(
        SegmentationDataset(train_pairs),
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0,
    )

    validation_loader = DataLoader(
        SegmentationDataset(validation_pairs),
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
    )

    # --------------------------------------------------------
    # Model
    # --------------------------------------------------------

    print("\nCreating TransUNet model...")

    model = create_model().to(device)

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
    )

    # --------------------------------------------------------
    # Training
    # --------------------------------------------------------

    best_validation_dice = -1.0

    for epoch in range(1, EPOCHS + 1):

        print()
        print(f"Epoch {epoch}/{EPOCHS}")

        train_loss, train_dice, train_iou = run_epoch(
            model,
            train_loader,
            optimizer,
        )

        validation_loss, validation_dice, validation_iou = run_epoch(
            model,
            validation_loader,
        )

        print(
            f"Epoch {epoch}/{EPOCHS} | "
            f"Train Loss {train_loss:.4f} | "
            f"Train Dice {train_dice:.4f} | "
            f"Train IoU {train_iou:.4f} | "
            f"Val Loss {validation_loss:.4f} | "
            f"Val Dice {validation_dice:.4f} | "
            f"Val IoU {validation_iou:.4f}"
        )

        # ----------------------------------------------------
        # Save best checkpoint
        # ----------------------------------------------------

        if validation_dice > best_validation_dice:

            best_validation_dice = validation_dice

            torch.save(
                model.state_dict(),
                BEST_MODEL_PATH,
            )

            print(
                "  ✓ Best segmentation model saved"
            )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print(
        "Best validation Dice:",
        f"{best_validation_dice:.4f}",
    )
    print("Saved:", BEST_MODEL_PATH)
    print("=" * 70)


if __name__ == "__main__":
    main()
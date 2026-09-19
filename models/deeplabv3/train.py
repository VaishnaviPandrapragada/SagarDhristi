from pathlib import Path
import random
import time
import numpy as np
from PIL import Image

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from models.deeplabv3.model import create_model


# ============================================================
# DeepLabV3+ SEGMENTATION TRAINING
# Same dataset scale/epoch count as the U-Net run
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

IMAGE_ROOT = Path(r"D:\images")
MASK_ROOT = Path(r"D:\masks")

if not (IMAGE_ROOT / "train").exists():
    IMAGE_ROOT = PROJECT_ROOT / "images"
    MASK_ROOT = PROJECT_ROOT / "masks"

# Match the U-Net training scale.
TRAIN_LIMIT = 2000
VAL_LIMIT = 400
EPOCHS = 10

# Smaller spatial size keeps CPU training practical.
# The original images/masks are still used; only the training
# resolution is resized.
IMG_SIZE = 128
BATCH_SIZE = 4

LEARNING_RATE = 1e-4
RANDOM_STATE = 42

WEIGHTS_DIR = Path(__file__).resolve().parent / "weights"
BEST_MODEL_PATH = WEIGHTS_DIR / "deeplabv3plus_segmentation_best.pth"
WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

random.seed(RANDOM_STATE)
np.random.seed(RANDOM_STATE)
torch.manual_seed(RANDOM_STATE)

if device.type == "cpu":
    # Avoid excessive thread oversubscription on a laptop CPU.
    torch.set_num_threads(min(8, max(1, torch.get_num_threads())))


def collect_pairs(image_dir, mask_dir):
    pairs = []

    for image_path in sorted(image_dir.iterdir()):
        if (
            image_path.is_file()
            and image_path.suffix.lower()
            in {".png", ".jpg", ".jpeg", ".bmp", ".webp"}
        ):
            mask_path = mask_dir / image_path.name

            if mask_path.exists():
                pairs.append((image_path, mask_path))

    return pairs


class OilSpillSegmentationDataset(Dataset):
    def __init__(self, pairs):
        self.pairs = pairs

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, index):
        image_path, mask_path = self.pairs[index]

        image = (
            Image.open(image_path)
            .convert("RGB")
            .resize((IMG_SIZE, IMG_SIZE), Image.Resampling.BILINEAR)
        )

        mask = (
            Image.open(mask_path)
            .convert("L")
            .resize((IMG_SIZE, IMG_SIZE), Image.Resampling.NEAREST)
        )

        image = np.asarray(image, dtype=np.float32) / 255.0
        mask = (
            np.asarray(mask, dtype=np.float32) > 127
        ).astype(np.float32)

        # ImageNet normalization for the pretrained ResNet encoder.
        image = (
            image
            - np.array([0.485, 0.456, 0.406], dtype=np.float32)
        ) / np.array([0.229, 0.224, 0.225], dtype=np.float32)

        image_tensor = (
            torch.from_numpy(image)
            .permute(2, 0, 1)
            .float()
        )

        mask_tensor = (
            torch.from_numpy(mask)
            .unsqueeze(0)
            .float()
        )

        return image_tensor, mask_tensor


def dice_loss(logits, target):
    probability = torch.sigmoid(logits)

    intersection = (
        probability * target
    ).sum(dim=(1, 2, 3))

    denominator = (
        probability.sum(dim=(1, 2, 3))
        + target.sum(dim=(1, 2, 3))
    )

    dice = (
        (2.0 * intersection + 1.0)
        / (denominator + 1.0)
    )

    return 1.0 - dice.mean()


def metrics(logits, target):
    prediction = (
        torch.sigmoid(logits) >= 0.5
    ).float()

    intersection = (
        prediction * target
    ).sum().item()

    union = (
        (prediction + target) > 0
    ).float().sum().item()

    pred_area = prediction.sum().item()
    target_area = target.sum().item()

    dice = (
        2.0 * intersection
        / (pred_area + target_area + 1e-8)
    )

    iou = intersection / (union + 1e-8)

    return dice, iou


def run_epoch(model, loader, optimizer=None):
    training = optimizer is not None

    model.train(training)

    total_loss = 0.0
    total_dice = 0.0
    total_iou = 0.0

    context = (
        torch.enable_grad()
        if training
        else torch.no_grad()
    )

    with context:
        for batch_index, (images, masks) in enumerate(loader, start=1):
            images = images.to(device)
            masks = masks.to(device)

            if training:
                optimizer.zero_grad(set_to_none=True)

            logits = model(images)

            bce = nn.functional.binary_cross_entropy_with_logits(
                logits,
                masks,
            )

            dice = dice_loss(logits, masks)

            loss = 0.5 * bce + 0.5 * dice

            if training:
                loss.backward()
                optimizer.step()

            batch_dice, batch_iou = metrics(
                logits.detach(),
                masks,
            )

            total_loss += loss.item()
            total_dice += batch_dice
            total_iou += batch_iou

            # Progress output so a CPU run doesn't look frozen.
            if training and (
                batch_index == 1
                or batch_index % 25 == 0
                or batch_index == len(loader)
            ):
                print(
                    f"    batch {batch_index}/{len(loader)}"
                    f" | loss {loss.item():.4f}",
                    flush=True,
                )

    count = max(len(loader), 1)

    return (
        total_loss / count,
        total_dice / count,
        total_iou / count,
    )


def main():
    train_pairs = collect_pairs(
        IMAGE_ROOT / "train",
        MASK_ROOT / "train",
    )[:TRAIN_LIMIT]

    val_pairs = collect_pairs(
        IMAGE_ROOT / "val",
        MASK_ROOT / "val",
    )[:VAL_LIMIT]

    if not train_pairs or not val_pairs:
        raise FileNotFoundError(
            "Paired dataset not found. "
            f"Images: {IMAGE_ROOT} | Masks: {MASK_ROOT}"
        )

    print("=" * 70)
    print("DEEPLABV3+ SEGMENTATION TRAINING")
    print("=" * 70)
    print("Device:", device)
    print("Training pairs:", len(train_pairs))
    print("Validation pairs:", len(val_pairs))
    print("Image size:", f"{IMG_SIZE}x{IMG_SIZE}")
    print("Batch size:", BATCH_SIZE)
    print("Epochs:", EPOCHS)
    print("Best model:", BEST_MODEL_PATH)
    print("=" * 70)

    train_loader = DataLoader(
        OilSpillSegmentationDataset(train_pairs),
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0,
    )

    val_loader = DataLoader(
        OilSpillSegmentationDataset(val_pairs),
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
    )

    print("Creating DeepLabV3+ model...", flush=True)

    model = create_model().to(device)

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
    )

    best_dice = -1.0

    for epoch in range(1, EPOCHS + 1):
        start_time = time.time()

        print(
            f"\nEpoch {epoch}/{EPOCHS}",
            flush=True,
        )

        train_loss, train_dice, train_iou = run_epoch(
            model,
            train_loader,
            optimizer,
        )

        val_loss, val_dice, val_iou = run_epoch(
            model,
            val_loader,
        )

        elapsed = time.time() - start_time

        print(
            f"Epoch {epoch}/{EPOCHS} | "
            f"Train Loss {train_loss:.4f} | "
            f"Train Dice {train_dice:.4f} | "
            f"Train IoU {train_iou:.4f} | "
            f"Val Loss {val_loss:.4f} | "
            f"Val Dice {val_dice:.4f} | "
            f"Val IoU {val_iou:.4f} | "
            f"Time {elapsed / 60:.1f} min",
            flush=True,
        )

        if val_dice > best_dice:
            best_dice = val_dice

            torch.save(
                model.state_dict(),
                BEST_MODEL_PATH,
            )

            print(
                "  ✓ Best segmentation model saved",
                flush=True,
            )

    print("\n" + "=" * 70)
    print(
        "Best validation Dice:",
        f"{best_dice:.4f}",
    )
    print("Saved:", BEST_MODEL_PATH)
    print("=" * 70)


if __name__ == "__main__":
    main()

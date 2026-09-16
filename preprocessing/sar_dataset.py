from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset


class SARDataset(Dataset):
    """
    Paired SAR image + oil-spill segmentation mask dataset.

    Expected structure:

        D:/images/
            train/
            val/

        D:/masks/
            train/
            val/

    Image and mask filenames must match.
    """

    def __init__(self, image_dir, mask_dir, image_size=128):

        self.image_dir = Path(image_dir)
        self.mask_dir = Path(mask_dir)
        self.image_size = image_size

        if not self.image_dir.exists():
            raise FileNotFoundError(
                f"Image directory not found: {self.image_dir}"
            )

        if not self.mask_dir.exists():
            raise FileNotFoundError(
                f"Mask directory not found: {self.mask_dir}"
            )

        self.samples = []

        image_files = sorted(
            self.image_dir.glob("*.png")
        )

        for image_path in image_files:

            mask_path = self.mask_dir / image_path.name

            if not mask_path.exists():
                raise FileNotFoundError(
                    f"Mask not found for image: {image_path.name}"
                )

            self.samples.append(
                (image_path, mask_path)
            )

        if not self.samples:
            raise RuntimeError(
                f"No PNG images found in {self.image_dir}"
            )

        print(
            f"Loaded {len(self.samples)} image-mask pairs"
        )

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):

        image_path, mask_path = self.samples[index]

        # ----------------------------------------------------
        # SAR IMAGE
        # ----------------------------------------------------

        image = Image.open(
            image_path
        ).convert("L")

        image = image.resize(
            (self.image_size, self.image_size),
            Image.Resampling.BILINEAR
        )

        image = np.array(
            image,
            dtype=np.float32
        )

        # Normalize 0-255 → 0-1
        image = image / 255.0

        image = torch.from_numpy(
            image
        ).unsqueeze(0)

        # ----------------------------------------------------
        # SEGMENTATION MASK
        # ----------------------------------------------------

        mask = Image.open(
            mask_path
        ).convert("L")

        # IMPORTANT:
        # Nearest-neighbour keeps mask binary.
        mask = mask.resize(
            (self.image_size, self.image_size),
            Image.Resampling.NEAREST
        )

        mask = np.array(
            mask,
            dtype=np.float32
        )

        # 0 = background
        # 255 = oil
        mask = (
            mask > 127
        ).astype(np.float32)

        mask = torch.from_numpy(
            mask
        ).unsqueeze(0)

        return image, mask


if __name__ == "__main__":

    print("=" * 60)
    print("TESTING SAR DATASET")
    print("=" * 60)

    train_dataset = SARDataset(
        r"D:\images\train",
        r"D:\masks\train",
        image_size=128
    )

    val_dataset = SARDataset(
        r"D:\images\val",
        r"D:\masks\val",
        image_size=128
    )

    image, mask = train_dataset[0]

    print()

    print(
        "Training samples :",
        len(train_dataset)
    )

    print(
        "Validation samples:",
        len(val_dataset)
    )

    print()

    print("Sample:")

    print(
        "  Image shape :",
        image.shape
    )

    print(
        "  Image dtype :",
        image.dtype
    )

    print(
        "  Image range :",
        image.min().item(),
        image.max().item()
    )

    print()

    print(
        "  Mask shape  :",
        mask.shape
    )

    print(
        "  Mask dtype  :",
        mask.dtype
    )

    print(
        "  Mask values :",
        torch.unique(mask).tolist()
    )

    print()

    print(
        "Dataset test completed successfully!"
    )
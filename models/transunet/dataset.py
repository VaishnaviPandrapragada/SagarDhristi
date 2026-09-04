from pathlib import Path

import torch
from torch.utils.data import Dataset
from PIL import Image


class TransUNetDataset(Dataset):

    def __init__(self, samples, transform=None):

        self.samples = samples
        self.transform = transform

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):

        image_path, label = self.samples[index]

        image = Image.open(image_path).convert("RGB")

        if self.transform:
            image = self.transform(image)

        label = torch.tensor(
            label,
            dtype=torch.long
        )

        return image, label


def collect_samples(root_dir, samples_per_class=500):

    root_dir = Path(root_dir)

    class_0_dir = root_dir / "Class_0"
    class_1_dir = root_dir / "Class_1"

    if not class_0_dir.exists():
        raise FileNotFoundError(
            f"Directory not found: {class_0_dir}"
        )

    if not class_1_dir.exists():
        raise FileNotFoundError(
            f"Directory not found: {class_1_dir}"
        )

    class_0_images = sorted(
        class_0_dir.glob("*.jpg")
    )[:samples_per_class]

    class_1_images = sorted(
        class_1_dir.glob("*.jpg")
    )[:samples_per_class]

    if len(class_0_images) < samples_per_class:
        raise RuntimeError(
            f"Not enough Class_0 images. "
            f"Found {len(class_0_images)}"
        )

    if len(class_1_images) < samples_per_class:
        raise RuntimeError(
            f"Not enough Class_1 images. "
            f"Found {len(class_1_images)}"
        )

    samples = []

    for image_path in class_0_images:
        samples.append((image_path, 0))

    for image_path in class_1_images:
        samples.append((image_path, 1))

    return samples
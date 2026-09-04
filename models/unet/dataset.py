from pathlib import Path

import torch
from torch.utils.data import Dataset
from PIL import Image


class OilSpillDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = Path(root_dir)
        self.transform = transform

        self.samples = []

        class_mapping = {
            "Class_0": 0,
            "Class_1": 1
        }

        for class_name, label in class_mapping.items():
            class_dir = self.root_dir / class_name

            if not class_dir.exists():
                raise FileNotFoundError(
                    f"Directory not found: {class_dir}"
                )

            for image_path in class_dir.glob("*.jpg"):
                self.samples.append((image_path, label))

        if not self.samples:
            raise RuntimeError(
                f"No JPG images found in {self.root_dir}"
            )

        print(f"Loaded {len(self.samples)} images")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        image_path, label = self.samples[index]

        image = Image.open(image_path).convert("L")

        if self.transform:
            image = self.transform(image)

        label = torch.tensor(label, dtype=torch.long)

        return image, label
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torchvision import transforms

from models.unet.model import create_model


DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "unet"
    / "weights"
    / "unet_segmentation.pth"
)


transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.ToTensor()
])


def load_segmentation_model():

    model = create_model()

    model.load_state_dict(
        torch.load(
            MODEL_PATH,
            map_location=DEVICE
        )
    )

    model.to(DEVICE)
    model.eval()

    return model


def predict_segmentation(image_path):

    model = load_segmentation_model()

    image = Image.open(image_path).convert("L")

    original_size = image.size

    image_tensor = transform(image)

    image_tensor = image_tensor.unsqueeze(0)
    image_tensor = image_tensor.to(DEVICE)

    with torch.no_grad():

        logits = model(image_tensor)

        probabilities = torch.sigmoid(logits)

        mask = (
            probabilities > 0.5
        ).float()

    mask = mask.squeeze().cpu().numpy()

    return {
        "mask": mask,
        "confidence": float(
            probabilities.mean().item()
        ),
        "original_size": original_size
    }
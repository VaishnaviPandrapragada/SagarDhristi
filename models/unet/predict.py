from pathlib import Path

import torch
from torchvision import transforms
from PIL import Image

from .model import UNet


# Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# Model path
MODEL_PATH = Path(__file__).resolve().parent / "weights" / "unet_segmentation.pth"


# Image preprocessing
transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor()
])


def load_model():
    model = UNet(
        in_channels=1,
        out_channels=1
    )

    model.load_state_dict(
        torch.load(MODEL_PATH, map_location=device)
    )

    model.to(device)
    model.eval()

    return model


def predict(image_path):
    model = load_model()

    image = Image.open(image_path).convert("L")
    image_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        output = model(image_tensor)
        probabilities = torch.sigmoid(output)
        mask = (probabilities > 0.5).float()

    # Determine whether the model detected any spill pixels
    spill_pixels = mask.sum().item()
    oil_spill_detected = spill_pixels > 0

    prediction_class = 1 if oil_spill_detected else 0

    return {
        "class": prediction_class,
        "oil_spill_detected": oil_spill_detected,
        "mask": mask.squeeze().cpu().numpy(),
        "spill_pixels": int(spill_pixels)
    }


if __name__ == "__main__":

    image_path = input("Enter image path: ").strip()

    result = predict(image_path)

    print("\nPrediction:")
    print(f"Class: {result['class']}")
    print(f"Oil spill detected: {result['oil_spill_detected']}")
    print(f"Spill pixels: {result['spill_pixels']}")

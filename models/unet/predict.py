from pathlib import Path

import torch
from torchvision import transforms
from PIL import Image

from .model import UNetClassifier


# Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# Model path
MODEL_PATH = Path(__file__).resolve().parent / "weights" / "unet_classifier.pth"


# Image preprocessing
transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor()
])

def load_model():
    model = UNetClassifier(
        in_channels=1,
        num_classes=2
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
        prediction = output.argmax(dim=1).item()

    return {
        "class": prediction,
        "oil_spill_detected": prediction == 1
    }


if __name__ == "__main__":

    image_path = input("Enter image path: ").strip()

    result = predict(image_path)

    print("\nPrediction:")
    print(f"Class: {result['class']}")
    print(f"Oil spill detected: {result['oil_spill_detected']}")
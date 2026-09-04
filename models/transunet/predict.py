from pathlib import Path

import torch
from PIL import Image
from torchvision import transforms

from .model import TransUNetClassifier


MODEL_PATH = (
    Path(__file__).resolve().parent
    / "weights"
    / "transunet_best.pth"
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=(0.485, 0.456, 0.406),
        std=(0.229, 0.224, 0.225)
    )
])


def load_model():
    model = TransUNetClassifier()

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=device
    )

    if isinstance(checkpoint, dict) and "state_dict" in checkpoint:
        model.load_state_dict(checkpoint["state_dict"])
    else:
        model.load_state_dict(checkpoint)

    model.to(device)
    model.eval()

    return model


def predict(image_path):
    model = load_model()

    image = Image.open(image_path).convert("RGB")

    image_tensor = transform(image)
    image_tensor = image_tensor.unsqueeze(0).to(device)

    with torch.no_grad():
        output = model(image_tensor)

        probabilities = torch.softmax(output, dim=1)

        prediction = torch.argmax(
            probabilities,
            dim=1
        ).item()

        confidence = probabilities[0][prediction].item()

    return {
        "class": prediction,
        "oil_spill_detected": prediction == 1,
        "confidence": confidence
    }


if __name__ == "__main__":

    image_path = input("Enter image path: ").strip()

    result = predict(image_path)

    print("\n" + "=" * 50)
    print("TRANSUNET PREDICTION")
    print("=" * 50)

    print(f"Class: {result['class']}")
    print(f"Oil Spill Detected: {result['oil_spill_detected']}")
    print(f"Confidence: {result['confidence'] * 100:.2f}%")

    print("=" * 50)
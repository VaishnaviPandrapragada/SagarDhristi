from pathlib import Path

import torch
import numpy as np
from PIL import Image

import albumentations as A
from albumentations.pytorch import ToTensorV2

from .model import DeepLabV3PlusClassifier


# --------------------------------------------------
# Device
# --------------------------------------------------

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print(f"Using device: {device}")


# --------------------------------------------------
# Model path
# --------------------------------------------------

MODEL_PATH = (
    Path(__file__).resolve().parent
    / "weights"
    / "deeplabv3plus_best.pth"
)


# --------------------------------------------------
# Image preprocessing
# --------------------------------------------------

transform = A.Compose([
    A.Resize(400, 400),

    A.Normalize(
        mean=(0.485, 0.456, 0.406),
        std=(0.229, 0.224, 0.225)
    ),

    ToTensorV2()
])


# --------------------------------------------------
# Load model
# --------------------------------------------------

def load_model():

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model weights not found:\n{MODEL_PATH}"
        )

    model = DeepLabV3PlusClassifier()

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=device
    )

    # Handle checkpoint dictionary
    if isinstance(checkpoint, dict) and "state_dict" in checkpoint:
        model.load_state_dict(checkpoint["state_dict"])

    else:
        model.load_state_dict(checkpoint)

    model.to(device)
    model.eval()

    return model


# --------------------------------------------------
# Prediction
# --------------------------------------------------

def predict(image_path):

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found:\n{image_path}"
        )

    # Load image
    image = Image.open(image_path).convert("RGB")

    # PIL → NumPy
    image = np.array(image)

    # Apply preprocessing
    transformed = transform(image=image)

    image_tensor = transformed["image"]

    # Add batch dimension
    image_tensor = image_tensor.unsqueeze(0)

    # Move to device
    image_tensor = image_tensor.to(device)

    # Load model
    model = load_model()

    # Inference
    with torch.no_grad():

        output = model(image_tensor)

        # Convert logits → probability
        probability = torch.sigmoid(output).item()

    # Binary classification
    prediction = int(probability >= 0.5)

    # Confidence
    confidence = (
        probability
        if prediction == 1
        else 1.0 - probability
    )

    return {
        "class": prediction,
        "oil_spill_detected": prediction == 1,
        "confidence": confidence
    }


# --------------------------------------------------
# Command-line testing
# --------------------------------------------------

if __name__ == "__main__":

    print("\n" + "=" * 50)
    print("DeepLabV3+ Oil Spill Prediction")
    print("=" * 50)

    image_path = input(
        "\nEnter image path: "
    ).strip()

    try:

        result = predict(image_path)

        print("\nPrediction")
        print("-" * 30)

        print(
            f"Class: {result['class']}"
        )

        print(
            f"Oil spill detected: "
            f"{result['oil_spill_detected']}"
        )

        print(
            f"Confidence: "
            f"{result['confidence'] * 100:.2f}%"
        )

        print("=" * 50)

    except Exception as e:

        print("\nPrediction failed:")
        print(e)
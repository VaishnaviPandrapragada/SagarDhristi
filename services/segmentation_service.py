from __future__ import annotations

import base64
import io
from pathlib import Path
from typing import Any, Dict

import numpy as np
import torch
from PIL import Image
from torchvision import transforms

from models.unet.model import UNet


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

MODEL_INPUT_SIZE = 128
MASK_THRESHOLD = 0.5

TRANSFORM = transforms.Compose([
    transforms.Resize(
        (MODEL_INPUT_SIZE, MODEL_INPUT_SIZE)
    ),
    transforms.ToTensor(),
])

_MODEL: UNet | None = None


def _load_model() -> UNet:
    global _MODEL

    if _MODEL is not None:
        return _MODEL

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"U-Net weights not found: {MODEL_PATH}"
        )

    model = UNet(
        in_channels=1,
        out_channels=1,
    )

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=DEVICE,
    )

    if isinstance(checkpoint, dict) and "state_dict" in checkpoint:
        checkpoint = checkpoint["state_dict"]

    if not isinstance(checkpoint, dict):
        raise ValueError(
            "Unsupported U-Net checkpoint format."
        )

    cleaned_checkpoint = {
        key.replace("module.", "", 1): value
        for key, value in checkpoint.items()
    }

    model.load_state_dict(
        cleaned_checkpoint,
        strict=True,
    )

    model.to(DEVICE)
    model.eval()

    _MODEL = model

    return model


def _mask_to_data_url(mask: np.ndarray) -> str:
    mask_uint8 = (
        (mask > 0).astype(np.uint8) * 255
    )

    buffer = io.BytesIO()

    Image.fromarray(
        mask_uint8,
        mode="L",
    ).save(
        buffer,
        format="PNG",
        optimize=True,
    )

    encoded = base64.b64encode(
        buffer.getvalue()
    ).decode("ascii")

    return f"data:image/png;base64,{encoded}"


def _calculate_geometry(
    mask: np.ndarray,
) -> Dict[str, Any]:

    height, width = mask.shape

    positive_y, positive_x = np.where(
        mask > 0
    )

    area_pixels = int(len(positive_x))

    total_pixels = height * width

    coverage_ratio = (
        area_pixels / total_pixels
        if total_pixels
        else 0.0
    )

    if area_pixels == 0:
        return {
            "spill_present": False,
            "area_pixels": 0,
            "coverage_ratio": 0.0,
            "mask_width": 0,
            "mask_height": 0,
            "bounding_box": None,
            "centroid": None,
            "geometry_source": "u_net_binary_mask",
        }

    x_min = int(positive_x.min())
    x_max = int(positive_x.max())
    y_min = int(positive_y.min())
    y_max = int(positive_y.max())

    return {
        "spill_present": True,
        "area_pixels": area_pixels,
        "coverage_ratio": float(coverage_ratio),
        "mask_width": int(x_max - x_min + 1),
        "mask_height": int(y_max - y_min + 1),
        "bounding_box": {
            "x_min": x_min,
            "y_min": y_min,
            "x_max": x_max,
            "y_max": y_max,
            "width": int(x_max - x_min + 1),
            "height": int(y_max - y_min + 1),
        },
        "centroid": {
            "x": float(positive_x.mean()),
            "y": float(positive_y.mean()),
        },
        "geometry_source": "u_net_binary_mask",
    }


def predict_segmentation(
    image_path: str,
) -> Dict[str, Any]:

    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Image not found: {path}"
        )

    image = Image.open(path).convert("L")

    original_width, original_height = image.size

    tensor = TRANSFORM(
        image
    ).unsqueeze(0).to(DEVICE)

    model = _load_model()

    with torch.no_grad():
        logits = model(tensor)
        probabilities = torch.sigmoid(logits)

    probability_map = (
        probabilities[0, 0]
        .detach()
        .cpu()
        .numpy()
    )

    mask = (
        probability_map >= MASK_THRESHOLD
    ).astype(np.uint8)

    geometry = _calculate_geometry(mask)

    positive_probabilities = probability_map[
        mask > 0
    ]

    if positive_probabilities.size:
        model_confidence = float(
            positive_probabilities.mean()
        )
    else:
        model_confidence = float(
            probability_map.max()
        )

    return {
        "mask_available": True,

        "mask": mask,

        "mask_shape": [
            int(mask.shape[0]),
            int(mask.shape[1]),
        ],

        "model_confidence": model_confidence,

        "spill_pixels": geometry["area_pixels"],

        "coverage_ratio": geometry["coverage_ratio"],

        "mask_image": _mask_to_data_url(mask),

        "geometry": geometry,

        "original_image_size": {
            "width": int(original_width),
            "height": int(original_height),
        },

        "model": "U-Net",

        "model_input_size": [
            MODEL_INPUT_SIZE,
            MODEL_INPUT_SIZE,
        ],

        "mask_threshold": MASK_THRESHOLD,
    }

def unload_model():
    global _MODEL
    _MODEL = None
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
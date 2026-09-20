from pathlib import Path
import base64, io
import numpy as np
import torch
from PIL import Image
from .model import create_model

DEVICE=torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_PATH=Path(__file__).resolve().parent/"weights"/"deeplabv3plus_segmentation_best.pth"
_model = None

def load_model():
    global _model
    if _model is None:
        model=create_model()
        model.load_state_dict(torch.load(MODEL_PATH,map_location=DEVICE))
        model.to(DEVICE).eval()
        _model=model
    return _model

def predict(image_path):
    image=Image.open(image_path).convert("RGB")
    original_size=image.size
    resized=image.resize((256,256),Image.Resampling.BILINEAR)
    array=np.asarray(resized,dtype=np.float32)/255.0
    array=(array-np.array([0.485,0.456,0.406]))/np.array([0.229,0.224,0.225])
    tensor=torch.from_numpy(array).permute(2,0,1).unsqueeze(0).float().to(DEVICE)
    with torch.no_grad():
        probability=torch.sigmoid(load_model()(tensor))[0,0]
    binary=probability>=0.5
    mask=binary.cpu().numpy().astype(np.uint8)
    spill_pixels=int(mask.sum())
    coverage=float(mask.mean())
    confidence=float(probability[binary].mean().item()) if spill_pixels else float((1.0-probability).mean().item())
    out=io.BytesIO()
    Image.fromarray(mask*255,mode="L").save(out,format="PNG")
    encoded=base64.b64encode(out.getvalue()).decode("ascii")
    return {
        "class":1 if spill_pixels else 0,
        "oil_spill_detected":bool(spill_pixels),
        "confidence":confidence,
        "mask":mask,
        "mask_shape":list(mask.shape),
        "spill_pixels":spill_pixels,
        "coverage_ratio":coverage,
        "mask_image":f"data:image/png;base64,{encoded}",
        "original_image_size":list(original_size),
        "model_input_size":[256,256],
    }

def unload_model():
    global _model
    _model = None
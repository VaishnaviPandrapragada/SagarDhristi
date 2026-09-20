from pathlib import Path
import base64,io
import numpy as np
import torch
from PIL import Image
from .model import create_model

DEVICE=torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_PATH=Path(__file__).resolve().parent/"weights"/"transunet_segmentation_best.pth"
_model = None

def load_model():
    global _model
    if _model is None:
        model=create_model()
        model.load_state_dict(torch.load(MODEL_PATH,map_location=DEVICE))
        model.to(DEVICE).eval(); _model=model
    return _model

def predict(image_path):
    image=Image.open(image_path).convert("RGB")
    original_size=image.size
    im=image.resize((128,128),Image.Resampling.BILINEAR)
    a=np.asarray(im,dtype=np.float32)/255.0
    a=(a-np.array([.485,.456,.406]))/np.array([.229,.224,.225])
    x=torch.from_numpy(a).permute(2,0,1).unsqueeze(0).float().to(DEVICE)
    with torch.no_grad(): p=torch.sigmoid(load_model()(x))[0,0]
    b=p>=.5; mask=b.cpu().numpy().astype(np.uint8); pixels=int(mask.sum())
    cov=float(mask.mean())
    conf=float(p[b].mean().item()) if pixels else float((1-p).mean().item())
    out=io.BytesIO(); Image.fromarray(mask*255,mode="L").save(out,format="PNG")
    encoded=base64.b64encode(out.getvalue()).decode("ascii")
    return {"class":1 if pixels else 0,"oil_spill_detected":bool(pixels),"confidence":conf,
            "mask":mask,"mask_shape":list(mask.shape),"spill_pixels":pixels,
            "coverage_ratio":cov,"mask_image":f"data:image/png;base64,{encoded}",
            "original_image_size":list(original_size),"model_input_size":[128,128]}

def unload_model():
    global _model
    _model = None
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
import torch.nn as nn
import segmentation_models_pytorch as smp

class DeepLabV3PlusSegmenter(nn.Module):
    """DeepLabV3+ binary segmentation model for oil-spill masks."""
    def __init__(self):
        super().__init__()
        self.deeplab = smp.DeepLabV3Plus(
            encoder_name="resnet18",
            encoder_weights="imagenet",
            in_channels=3,
            classes=1,
        )
    def forward(self, x):
        return self.deeplab(x)

def create_model():
    return DeepLabV3PlusSegmenter()

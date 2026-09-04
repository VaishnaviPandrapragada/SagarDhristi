import torch
import torch.nn as nn
import segmentation_models_pytorch as smp


class DeepLabV3PlusClassifier(nn.Module):

    def __init__(self):
        super().__init__()

        # DeepLabV3+ with ResNet50 encoder
        self.deeplab = smp.DeepLabV3Plus(
            encoder_name="resnet50",
            encoder_weights="imagenet",
            in_channels=3,
            classes=1
        )

        # Convert spatial feature maps into one feature vector
        self.pool = nn.AdaptiveAvgPool2d((1, 1))

        # Binary classification head
        self.classifier = nn.Sequential(
            nn.Flatten(),

            nn.Linear(256, 128),

            nn.ReLU(inplace=True),

            nn.Dropout(0.3),

            nn.Linear(128, 1)
        )

    def forward(self, x):

        # Extract encoder features
        features = self.deeplab.encoder(x)

        # Decode DeepLabV3+ features
        decoder_output = self.deeplab.decoder(features)

        # Global average pooling
        pooled = self.pool(decoder_output)

        # Classification
        logits = self.classifier(pooled)

        return logits.squeeze(1)


def create_model():

    model = DeepLabV3PlusClassifier()

    # Freeze ResNet50 encoder
    for param in model.deeplab.encoder.parameters():
        param.requires_grad = False

    return model


# ============================================================
# MODEL TEST
# ============================================================

if __name__ == "__main__":

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    print("=" * 60)
    print("TESTING DEEPLABV3+ MODEL")
    print("=" * 60)

    print("Device:", device)

    if torch.cuda.is_available():
        print("GPU:", torch.cuda.get_device_name(0))

    model = create_model().to(device)

    # Test input
    x = torch.randn(
        2,
        3,
        400,
        400
    ).to(device)

    with torch.no_grad():

        output = model(x)

    print("Input shape:", x.shape)

    print("Output shape:", output.shape)

    print("Model test completed successfully!")
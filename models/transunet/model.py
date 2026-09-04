import torch
import torch.nn as nn


# ============================================================
# Convolutional Block
# ============================================================

class ConvBlock(nn.Module):

    def __init__(self, in_channels, out_channels):

        super().__init__()

        self.block = nn.Sequential(
            nn.Conv2d(
                in_channels,
                out_channels,
                kernel_size=3,
                padding=1
            ),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),

            nn.Conv2d(
                out_channels,
                out_channels,
                kernel_size=3,
                padding=1
            ),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.block(x)


# ============================================================
# TransUNet Classifier
# ============================================================

class TransUNetClassifier(nn.Module):

    def __init__(
        self,
        num_classes=2,
        img_size=128,
        embed_dim=256,
        num_heads=8,
        num_layers=2
    ):

        super().__init__()

        # ----------------------------------------------------
        # CNN Encoder
        # ----------------------------------------------------

        self.encoder1 = ConvBlock(3, 32)
        self.pool1 = nn.MaxPool2d(2)

        self.encoder2 = ConvBlock(32, 64)
        self.pool2 = nn.MaxPool2d(2)

        self.encoder3 = ConvBlock(64, 128)
        self.pool3 = nn.MaxPool2d(2)

        self.encoder4 = ConvBlock(128, embed_dim)

        # ----------------------------------------------------
        # Transformer
        # ----------------------------------------------------

        # After 3 pooling operations:
        # 128x128 → 64x64 → 32x32 → 16x16

        feature_size = img_size // 8
        num_patches = feature_size * feature_size

        self.positional_embedding = nn.Parameter(
            torch.randn(
                1,
                num_patches,
                embed_dim
            )
        )

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=num_heads,
            dim_feedforward=embed_dim * 2,
            dropout=0.1,
            batch_first=True,
            activation="gelu"
        )

        self.transformer = nn.TransformerEncoder(
            encoder_layer,
            num_layers=num_layers
        )

        # ----------------------------------------------------
        # Lightweight Decoder
        # ----------------------------------------------------

        self.decoder3 = ConvBlock(embed_dim, 128)
        self.decoder2 = ConvBlock(128, 64)
        self.decoder1 = ConvBlock(64, 32)

        # ----------------------------------------------------
        # Classification Head
        # ----------------------------------------------------

        self.global_pool = nn.AdaptiveAvgPool2d(1)

        self.classifier = nn.Sequential(
            nn.Flatten(),

            nn.Linear(32, 32),
            nn.ReLU(inplace=True),

            nn.Dropout(0.3),

            nn.Linear(32, num_classes)
        )


    # ========================================================
    # Forward Pass
    # ========================================================

    def forward(self, x):

        # ----------------------------------------------------
        # CNN Encoder
        # ----------------------------------------------------

        x = self.encoder1(x)
        x = self.pool1(x)

        x = self.encoder2(x)
        x = self.pool2(x)

        x = self.encoder3(x)
        x = self.pool3(x)

        x = self.encoder4(x)

        # ----------------------------------------------------
        # Convert feature map → Transformer sequence
        # ----------------------------------------------------

        batch_size, channels, height, width = x.shape

        x = x.flatten(2)

        x = x.transpose(1, 2)

        # ----------------------------------------------------
        # Positional information
        # ----------------------------------------------------

        x = x + self.positional_embedding[:, :x.size(1), :]

        # ----------------------------------------------------
        # Transformer
        # ----------------------------------------------------

        x = self.transformer(x)

        # ----------------------------------------------------
        # Convert sequence → feature map
        # ----------------------------------------------------

        x = x.transpose(1, 2)

        x = x.reshape(
            batch_size,
            channels,
            height,
            width
        )

        # ----------------------------------------------------
        # Lightweight decoder
        # ----------------------------------------------------

        x = nn.functional.interpolate(
            x,
            scale_factor=2,
            mode="bilinear",
            align_corners=False
        )

        x = self.decoder3(x)

        x = nn.functional.interpolate(
            x,
            scale_factor=2,
            mode="bilinear",
            align_corners=False
        )

        x = self.decoder2(x)

        x = nn.functional.interpolate(
            x,
            scale_factor=2,
            mode="bilinear",
            align_corners=False
        )

        x = self.decoder1(x)

        # ----------------------------------------------------
        # Classification
        # ----------------------------------------------------

        x = self.global_pool(x)

        logits = self.classifier(x)

        return logits


# ============================================================
# Model Factory
# ============================================================

def create_model():

    model = TransUNetClassifier(
        num_classes=2,
        img_size=128,
        embed_dim=256,
        num_heads=8,
        num_layers=2
    )

    return model


# ============================================================
# Quick Model Test
# ============================================================

if __name__ == "__main__":

    model = create_model()

    dummy_input = torch.randn(
        2,
        3,
        128,
        128
    )

    output = model(dummy_input)

    print("Model test successful!")
    print("Input shape :", dummy_input.shape)
    print("Output shape:", output.shape)
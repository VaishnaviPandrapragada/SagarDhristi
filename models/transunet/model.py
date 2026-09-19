import torch
import torch.nn as nn
import torch.nn.functional as F

class ConvBlock(nn.Module):
    def __init__(self,in_channels,out_channels):
        super().__init__()
        self.block=nn.Sequential(
            nn.Conv2d(in_channels,out_channels,3,padding=1,bias=False),
            nn.BatchNorm2d(out_channels),nn.ReLU(inplace=True),
            nn.Conv2d(out_channels,out_channels,3,padding=1,bias=False),
            nn.BatchNorm2d(out_channels),nn.ReLU(inplace=True),
        )
    def forward(self,x): return self.block(x)

class TransUNetSegmenter(nn.Module):
    def __init__(self,img_size=128,embed_dim=256,num_heads=8,num_layers=2):
        super().__init__()
        self.encoder1=ConvBlock(3,32); self.pool1=nn.MaxPool2d(2)
        self.encoder2=ConvBlock(32,64); self.pool2=nn.MaxPool2d(2)
        self.encoder3=ConvBlock(64,128); self.pool3=nn.MaxPool2d(2)
        self.encoder4=ConvBlock(128,embed_dim)
        feature_size=img_size//8
        self.positional_embedding=nn.Parameter(torch.zeros(1,feature_size*feature_size,embed_dim))
        layer=nn.TransformerEncoderLayer(
            d_model=embed_dim,nhead=num_heads,dim_feedforward=embed_dim*2,
            dropout=0.1,batch_first=True,activation="gelu",norm_first=True
        )
        self.transformer=nn.TransformerEncoder(layer,num_layers=num_layers)
        self.decoder3=ConvBlock(embed_dim,128)
        self.decoder2=ConvBlock(128,64)
        self.decoder1=ConvBlock(64,32)
        self.segmentation_head=nn.Conv2d(32,1,1)
        nn.init.trunc_normal_(self.positional_embedding,std=0.02)

    def forward(self,x):
        x=self.pool1(self.encoder1(x))
        x=self.pool2(self.encoder2(x))
        x=self.pool3(self.encoder3(x))
        x=self.encoder4(x)
        b,c,h,w=x.shape
        tokens=x.flatten(2).transpose(1,2)
        tokens=self.transformer(tokens+self.positional_embedding[:,:tokens.size(1),:])
        x=tokens.transpose(1,2).reshape(b,c,h,w)
        x=self.decoder3(F.interpolate(x,scale_factor=2,mode="bilinear",align_corners=False))
        x=self.decoder2(F.interpolate(x,scale_factor=2,mode="bilinear",align_corners=False))
        x=self.decoder1(F.interpolate(x,scale_factor=2,mode="bilinear",align_corners=False))
        return self.segmentation_head(x)

def create_model():
    return TransUNetSegmenter()

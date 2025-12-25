"""
Model architecture definition for MultiTaskResNet.
Extracted from the notebook for reuse in the backend.
"""
import torch
import torch.nn as nn
import torchvision.models as models


class MultiTaskResNet(nn.Module):
    """
    Multi-task neural network with a shared ResNet18 backbone.

    Outputs:
    - logits: raw classification scores (used with CrossEntropyLoss)
    - nutr: normalized nutrition predictions (used with MSELoss)
    """
    def __init__(self, num_classes=101, nutrition_dim=6):
        super().__init__()

        # Load pretrained ResNet18 and remove its final classification layer
        self.resnet = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        self.resnet.fc = nn.Identity()  # output is a 512-dim feature vector
        self.backbone_out = 512

        # Task-specific heads
        # Classification head outputs raw logits (softmax applied inside CrossEntropyLoss)
        self.classifier = nn.Linear(self.backbone_out, num_classes)

        # Regression head outputs continuous values (no activation for MSE loss)
        self.regressor = nn.Linear(self.backbone_out, nutrition_dim)

    def backbone(self, x):
        # Shared feature extractor
        return self.resnet(x)

    def forward(self, x):
        # Forward pass through backbone and both heads
        feat = self.backbone(x)
        logits = self.classifier(feat)
        nutr = self.regressor(feat)
        return logits, nutr


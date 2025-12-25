"""
Image preprocessing utilities for model inference.
"""
from PIL import Image
import torch
from torchvision import transforms


def get_test_transform():
    """
    Get image transform for inference (no augmentation).
    """
    return transforms.Compose([
        transforms.Resize((224, 224)),  # ResNet standard input size
        transforms.ToTensor(),          # convert PIL -> torch tensor
    ])


def preprocess_image(image: Image.Image) -> torch.Tensor:
    """
    Preprocess an image for model inference.
    
    Args:
        image: PIL Image (RGB)
        
    Returns:
        Preprocessed tensor ready for model input [1, 3, 224, 224]
    """
    transform = get_test_transform()
    tensor = transform(image)
    return tensor.unsqueeze(0)  # Add batch dimension


def load_image_from_bytes(image_bytes: bytes) -> Image.Image:
    """
    Load PIL Image from bytes.
    
    Args:
        image_bytes: Image file bytes
        
    Returns:
        PIL Image in RGB mode
    """
    from io import BytesIO
    image = Image.open(BytesIO(image_bytes))
    if image.mode != 'RGB':
        image = image.convert('RGB')
    return image


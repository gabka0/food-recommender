"""
Model loading and inference utilities.
"""
import os
import torch
from typing import Dict, Tuple, List
try:
    from .model_architecture import MultiTaskResNet
    from .nutrition_loader import load_nutrition_mapping, TARGET_COLS
except ImportError:
    from model_architecture import MultiTaskResNet
    from nutrition_loader import load_nutrition_mapping, TARGET_COLS


def load_model_checkpoint(checkpoint_path: str, device: str = 'cpu') -> Dict:
    """
    Load model checkpoint from saved .pt file.
    
    Args:
        checkpoint_path: Path to food101_multitask_resnet18.pt
        device: Device to load model on ('cpu' or 'cuda')
        
    Returns:
        Dictionary with model_state_dict, y_mean, y_std, classes, history
    """
    checkpoint = torch.load(checkpoint_path, map_location=device)
    return checkpoint


def create_model_from_checkpoint(checkpoint: Dict, device: str = 'cpu') -> MultiTaskResNet:
    """
    Create and load model from checkpoint.
    
    Args:
        checkpoint: Loaded checkpoint dictionary
        device: Device to load model on
        
    Returns:
        Loaded model in evaluation mode
    """
    num_classes = len(checkpoint['classes'])
    nutrition_dim = 6  # Fixed based on TARGET_COLS
    
    model = MultiTaskResNet(num_classes=num_classes, nutrition_dim=nutrition_dim)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()
    
    return model


def unnormalize_nutr(
    nutr_norm: torch.Tensor,
    y_mean: torch.Tensor,
    y_std: torch.Tensor
) -> torch.Tensor:
    """
    Convert normalized nutrition vectors back to original units (per 100g).
    
    Args:
        nutr_norm: Normalized nutrition tensor
        y_mean: Mean values used for normalization
        y_std: Std values used for normalization
        
    Returns:
        Unnormalized nutrition tensor (per 100g)
    """
    return nutr_norm * y_std + y_mean


def format_nutr(vec: torch.Tensor, cols: List[str] = None) -> Dict[str, float]:
    """
    Format a nutrition tensor as a readable dictionary.
    
    Args:
        vec: Nutrition tensor
        cols: Column names (defaults to TARGET_COLS)
        
    Returns:
        Dictionary mapping column names to values
    """
    if cols is None:
        cols = TARGET_COLS
    vec = vec.detach().cpu().numpy().tolist()
    return {c: float(v) for c, v in zip(cols, vec)}


def predict(
    model: MultiTaskResNet,
    image_tensor: torch.Tensor,
    device: str = 'cpu'
) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Run model inference on an image.
    
    Args:
        model: Loaded MultiTaskResNet model
        image_tensor: Preprocessed image tensor [1, 3, 224, 224]
        device: Device to run inference on
        
    Returns:
        Tuple of (logits, nutr_pred_norm)
        - logits: Classification logits [1, 101]
        - nutr_pred_norm: Normalized nutrition predictions [1, 6]
    """
    model.eval()
    with torch.no_grad():
        image_tensor = image_tensor.to(device)
        logits, nutr_pred_norm = model(image_tensor)
    return logits, nutr_pred_norm


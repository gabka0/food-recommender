"""
Alternative food recommendation logic using prototype-based similarity.
"""
import torch
import torch.nn.functional as F
from typing import List, Dict


def suggest_similar_lower_calorie(
    image_tensor: torch.Tensor,
    model,  # Changed from model_backbone to model
    prototypes: torch.Tensor,
    calories_per100: torch.Tensor,
    classes: List[str],
    device: str = 'cpu',
    topk_sim: int = 15,
    topk_out: int = 5,
    min_calorie_drop: float = 20.0
) -> Dict:
    """
    Suggest visually similar food classes with lower calorie density.
    
    Args:
        image_tensor: Preprocessed image tensor [1, 3, 224, 224]
        model: The full model object (to access model.backbone)
        prototypes: Class prototype embeddings [C, D] (L2-normalized)
        calories_per100: Calories per 100g for each class [C]
        classes: List of class names
        device: Device to run on
        topk_sim: Number of visually similar classes to consider
        topk_out: Number of final suggestions to return
        min_calorie_drop: Minimum calorie reduction (kcal/100g)
        
    Returns:
        Dictionary with:
        - pred_class: Predicted class name
        - pred_calories_per_100g: Predicted calories per 100g
        - suggestions: List of alternative suggestions with similarity, calories, and drop
    """
    # Ensure model is in eval mode
    model.eval()
    
    # Extract normalized embedding for query image
    x = image_tensor.to(device)
    with torch.no_grad():
        emb = model.backbone(x)  # [1, D] - call backbone method on model
        emb = F.normalize(emb, dim=1)  # normalize for cosine similarity
    
    # Ensure prototypes are on the same device as embedding
    prototypes_device = prototypes.to(device)
    calories_device = calories_per100.to(device)
    
    # Cosine similarity with all class prototypes
    sims = (prototypes_device @ emb.squeeze(0))  # [C]
    
    # Predicted class based on nearest prototype (embedding space)
    pred_idx = int(torch.argmax(sims).item())
    pred_class = classes[pred_idx]
    pred_cal = float(calories_device[pred_idx].item())
    
    # Move sims to CPU for easier indexing
    sims = sims.cpu()
    
    print(f"Recommendation: Predicted class={pred_class}, calories={pred_cal:.1f}, min_drop={min_calorie_drop}")
    
    # Retrieve top visually similar candidate classes
    top_sim_idx = torch.topk(sims, k=min(topk_sim, len(classes))).indices.tolist()
    
    suggestions = []
    candidates_checked = 0
    for j in top_sim_idx:
        if j == pred_idx:
            continue
        
        cal = float(calories_per100[j].item())  # Use original CPU tensor for indexing
        candidates_checked += 1
        
        # Only keep candidates with sufficiently lower calories
        if cal < pred_cal - min_calorie_drop:  # Changed <= to < to ensure actual drop
            suggestions.append({
                "class": classes[j],
                "similarity": float(sims[j].item()),
                "calories_per_100g": cal,
                "calorie_drop": pred_cal - cal
            })
            print(f"  Added: {classes[j]} (cal={cal:.1f}, drop={pred_cal-cal:.1f}, sim={sims[j].item():.3f})")
        
        if len(suggestions) >= topk_out:
            break
    
    print(f"Found {len(suggestions)} suggestions after checking {candidates_checked} candidates")
    
    # If no suggestions found, try with lower threshold
    if len(suggestions) == 0 and min_calorie_drop > 5.0:
        # Retry with half the calorie drop requirement
        for j in top_sim_idx:
            if j == pred_idx:
                continue
            
            cal = float(calories_per100[j].item())  # Use original CPU tensor for indexing
            
            if cal < pred_cal - (min_calorie_drop / 2):
                suggestions.append({
                    "class": classes[j],
                    "similarity": float(sims[j].item()),
                    "calories_per_100g": cal,
                    "calorie_drop": pred_cal - cal
                })
            
            if len(suggestions) >= topk_out:
                break
    
    return {
        "pred_class": pred_class,
        "pred_calories_per_100g": pred_cal,
        "suggestions": suggestions
    }


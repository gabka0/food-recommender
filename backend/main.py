"""
FastAPI application for food recommendation system.
"""
import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import torch
from typing import Dict

try:
    from .model_loader import (
        load_model_checkpoint,
        create_model_from_checkpoint,
        predict,
        unnormalize_nutr,
        format_nutr
    )
    from .nutrition_loader import load_nutrition_mapping
    from .image_utils import load_image_from_bytes, preprocess_image
    from .recommendation import suggest_similar_lower_calorie
except ImportError:
    # For running directly with python main.py
    from model_loader import (
        load_model_checkpoint,
        create_model_from_checkpoint,
        predict,
        unnormalize_nutr,
        format_nutr
    )
    from nutrition_loader import load_nutrition_mapping
    from image_utils import load_image_from_bytes, preprocess_image
    from recommendation import suggest_similar_lower_calorie

# Initialize FastAPI app
app = FastAPI(title="Food Recommender API", version="1.0.0")

# Configure CORS
FRONTEND_URL = os.getenv("FRONTEND_URL", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL] if FRONTEND_URL != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for loaded model and artifacts
model = None
classes = None
y_mean = None
y_std = None
prototypes = None
calories_per100 = None
nutrition_mapping = None
device = 'cpu'


@app.on_event("startup")
async def load_artifacts():
    """Load all model artifacts on startup."""
    global model, classes, y_mean, y_std, prototypes, calories_per100, nutrition_mapping, device
    
    # Set device
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")
    
    # Paths to model artifacts
    # In Docker/Cloud Run: models are at /app/models
    # In local dev: models are at ../models (parent directory)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(os.path.join(current_dir, "models")):
        models_dir = os.path.join(current_dir, "models")
    else:
        # Fallback to parent directory structure (local development)
        base_dir = os.path.dirname(current_dir)
        models_dir = os.path.join(base_dir, "models")
    
    model_path = os.path.join(models_dir, "food101_multitask_resnet18.pt")
    prototypes_path = os.path.join(models_dir, "food101_class_prototypes.pt")
    calories_path = os.path.join(models_dir, "calories_per100.pt")
    nutrition_csv_path = os.path.join(models_dir, "nutrition.csv")
    
    # Check if files exist
    for path in [model_path, prototypes_path, calories_path, nutrition_csv_path]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Required file not found: {path}")
    
    print("Loading model checkpoint...")
    checkpoint = load_model_checkpoint(model_path, device=device)
    classes = checkpoint['classes']
    y_mean = checkpoint['y_mean'].to(device)
    y_std = checkpoint['y_std'].to(device)
    
    print("Creating model...")
    model = create_model_from_checkpoint(checkpoint, device=device)
    
    print("Loading prototypes...")
    prototypes = torch.load(prototypes_path, map_location=device)
    
    print("Loading calories vector...")
    calories_per100 = torch.load(calories_path, map_location=device)
    
    print("Loading nutrition mapping...")
    nutrition_mapping, _, _ = load_nutrition_mapping(nutrition_csv_path, classes)
    
    print("All artifacts loaded successfully!")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "device": device
    }


@app.post("/predict")
async def predict_food(file: UploadFile = File(...)):
    """
    Predict food class and nutrition from uploaded image.
    
    Returns:
        - predicted_class: Food class name
        - confidence: Classification confidence (softmax probability)
        - nutrition: Nutrition values per 100g
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Read image file
        image_bytes = await file.read()
        image = load_image_from_bytes(image_bytes)
        
        # Preprocess image
        image_tensor = preprocess_image(image)
        
        # Run prediction
        logits, nutr_pred_norm = predict(model, image_tensor, device=device)
        
        # Get top 5 predictions
        probs = torch.softmax(logits, dim=1)
        top5_probs, top5_indices = torch.topk(probs[0], k=min(5, len(classes)))
        
        # Get predicted class (top 1)
        pred_idx = int(top5_indices[0].item())
        predicted_class = classes[pred_idx]
        confidence = float(top5_probs[0].item())
        
        # Get top 5 predictions with classes and confidences
        top5_predictions = [
            {
                "class": classes[int(idx.item())],
                "confidence": float(prob.item())
            }
            for prob, idx in zip(top5_probs, top5_indices)
        ]
        
        # Unnormalize nutrition predictions
        nutr_pred = unnormalize_nutr(nutr_pred_norm[0], y_mean, y_std)
        nutrition = format_nutr(nutr_pred)
        
        return {
            "predicted_class": predicted_class,
            "confidence": confidence,
            "top5_predictions": top5_predictions,
            "nutrition": nutrition
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")


@app.post("/recommend")
async def recommend_alternatives(
    file: UploadFile = File(...),
    topk_sim: int = 20,
    topk_out: int = 6,
    min_calorie_drop: float = 15.0
):
    """
    Get lower-calorie alternative suggestions for uploaded food image.
    
    Args:
        file: Image file
        topk_sim: Number of visually similar classes to consider (default: 20)
        topk_out: Number of suggestions to return (default: 6)
        min_calorie_drop: Minimum calorie reduction in kcal/100g (default: 15.0)
    
    Returns:
        Dictionary with predicted class, calories, and alternative suggestions
    """
    print(f"\n=== RECOMMENDATION REQUEST ===")
    print(f"Parameters: topk_sim={topk_sim}, topk_out={topk_out}, min_calorie_drop={min_calorie_drop}")
    
    if model is None or prototypes is None or calories_per100 is None:
        print("ERROR: Model artifacts not loaded!")
        raise HTTPException(status_code=503, detail="Model artifacts not loaded")
    
    try:
        # Read and preprocess image
        image_bytes = await file.read()
        image = load_image_from_bytes(image_bytes)
        image_tensor = preprocess_image(image)
        
        print("Image preprocessed, calling suggest_similar_lower_calorie...")
        
        # Get recommendations (pass the model, not just backbone method)
        result = suggest_similar_lower_calorie(
            image_tensor=image_tensor,
            model=model,  # Pass the full model
            prototypes=prototypes,
            calories_per100=calories_per100,
            classes=classes,
            device=device,
            topk_sim=topk_sim,
            topk_out=topk_out,
            min_calorie_drop=min_calorie_drop
        )
        
        print(f"Result: {len(result.get('suggestions', []))} suggestions found")
        print(f"=== END RECOMMENDATION ===\n")
        
        return result
    
    except Exception as e:
        import traceback
        error_detail = f"Recommendation failed: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)
        raise HTTPException(status_code=400, detail=f"Recommendation failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)


"""
Load and process nutrition CSV with alias mapping.
Replicates the logic from notebook Cell 9.
"""
import os
import pandas as pd
import torch
import difflib
from typing import Dict, List, Tuple


TARGET_COLS = ["calories", "protein", "fat", "carbs", "sugars", "sodium"]
RAW_TARGETS = ["calories", "protein", "carbohydrates", "fats", "sugars", "sodium"]


def load_nutrition_mapping(
    csv_path: str,
    classes: List[str]
) -> Tuple[Dict[str, torch.Tensor], torch.Tensor, torch.Tensor]:
    """
    Load nutrition CSV and create mapping dictionary with alias handling.
    
    Args:
        csv_path: Path to nutrition.csv
        classes: List of Food-101 class names (101 classes)
        
    Returns:
        Tuple of (nutrition_mapping, y_mean, y_std)
        - nutrition_mapping: Dict mapping class_name -> nutrition tensor (per 100g)
        - y_mean: Mean values for normalization
        - y_std: Std values for normalization
    """
    # Load CSV
    nutr_df = pd.read_csv(csv_path)
    
    # Normalize label formatting
    nutr_df["label"] = nutr_df["label"].astype(str).str.strip().str.lower().str.replace(" ", "_")
    
    # Convert "per portion weight" -> per 100g
    for c in RAW_TARGETS:
        nutr_df[c] = nutr_df[c].astype(float) / nutr_df["weight"].astype(float) * 100.0
    
    # Average multiple rows per class
    nutr_per100 = nutr_df.groupby("label")[RAW_TARGETS].mean().reset_index()
    
    # Rename for convenience
    nutr_per100 = nutr_per100.rename(columns={"label": "class_name", "carbohydrates": "carbs", "fats": "fat"})
    
    # Check what nutrition labels exist
    nutr_labels = set(nutr_per100["class_name"].tolist())
    missing = sorted(list(set(classes) - nutr_labels))
    
    if missing:
        print(f"Missing before alias: {missing}")
    
    # Aliases: Food-101 -> nutrition label
    # These 3 almost always appear without underscores or with slightly different wording in the CSV file
    ALIASES = {
        "cup_cakes": "cupcakes",
        "grilled_cheese_sandwich": "grilled cheese sandwich",
        "lobster_roll_sandwich": "lobster roll",
    }
    
    # Try to map aliases to something that actually exists
    resolved_aliases = {}
    for k, v in ALIASES.items():
        if v in nutr_labels:
            resolved_aliases[k] = v
        else:
            # If exact alias not found, try closest match
            close = difflib.get_close_matches(v, nutr_labels, n=3, cutoff=0.6)
            if close:
                print(f"Alias '{k}' -> '{v}' not found. Closest: {close}")
                resolved_aliases[k] = close[0]
    
    if resolved_aliases:
        print(f"Resolved aliases: {resolved_aliases}")
    
    # Apply aliases by duplicating rows under Food-101 class_name
    for food101_name, nutr_name in resolved_aliases.items():
        row = nutr_per100[nutr_per100["class_name"] == nutr_name]
        if len(row) == 1:
            new_row = row.copy()
            new_row.loc[:, "class_name"] = food101_name
            nutr_per100 = pd.concat([nutr_per100, new_row], ignore_index=True)
    
    # Refresh label set
    nutr_labels = set(nutr_per100["class_name"].tolist())
    missing = sorted(list(set(classes) - nutr_labels))
    
    if missing:
        print(f"Missing after alias: {missing}")
    
    # Create nutrition mapping dictionary
    nutrition_mapping = {
        row["class_name"]: torch.tensor([row[c] for c in TARGET_COLS], dtype=torch.float32)
        for _, row in nutr_per100.iterrows()
    }
    
    # Sanity check
    missing = sorted(list(set(classes) - set(nutrition_mapping.keys())))
    if missing:
        print(f"Warning: {len(missing)} classes still missing from nutrition mapping")
        print(f"Missing list: {missing[:30]}")
    
    # Compute normalization stats
    Y = torch.stack([nutrition_mapping[c] for c in classes], dim=0)  # in Food-101 class order
    y_mean = Y.mean(dim=0)
    y_std = Y.std(dim=0).clamp(min=1e-6)
    
    return nutrition_mapping, y_mean, y_std


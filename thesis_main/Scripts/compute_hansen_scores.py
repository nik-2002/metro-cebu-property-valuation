"""
Compute Hansen Gravity accessibility scores for properties.

For each property, computes 6 category-specific Hansen scores (education, finance,
grocery, health, security, transport) and a weighted composite score.

Uses vectorized haversine distance with numpy for performance.
"""

import numpy as np
import pandas as pd
from pathlib import Path


def haversine_km(lat1, lon1, lat2_arr, lon2_arr):
    """
    Compute haversine distance in km from (lat1, lon1) to arrays (lat2_arr, lon2_arr).
    
    Args:
        lat1, lon1: scalars, property coordinates
        lat2_arr, lon2_arr: 1D numpy arrays, amenity coordinates
    
    Returns:
        1D numpy array of distances in km
    """
    R = 6371.0
    dlat = np.radians(lat2_arr - lat1)
    dlon = np.radians(lon2_arr - lon1)
    a = np.sin(dlat / 2) ** 2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2_arr)) * np.sin(dlon / 2) ** 2
    return R * 2 * np.arcsin(np.sqrt(a))


def compute_hansen_score(lat, lon, amenity_lats, amenity_lons, radius_km=5.0, beta=2.0):
    """
    Compute Hansen accessibility score for a property.
    
    Args:
        lat, lon: property coordinates
        amenity_lats, amenity_lons: 1D numpy arrays of amenity coordinates
        radius_km: only consider amenities within this distance (default 5.0 km)
        beta: decay parameter for 1/d^beta (default 2.0)
    
    Returns:
        Hansen score (float)
    """
    # Handle case where amenity arrays are empty
    if len(amenity_lats) == 0 or len(amenity_lons) == 0:
        return 0.0
    
    # Compute distances to all amenities in this category
    distances = haversine_km(lat, lon, amenity_lats, amenity_lons)
    
    # Filter to those within radius
    within_radius = distances <= radius_km
    distances_within = distances[within_radius]
    
    # If none within radius, score is 0
    if len(distances_within) == 0:
        return 0.0
    
    # Apply 0.5 km floor
    distances_within = np.maximum(distances_within, 0.5)
    
    # Compute Hansen score
    score = np.sum(1.0 / (distances_within ** beta))
    
    return score


def main():
    # Setup paths
    base_dir = Path(__file__).resolve().parents[1]
    abt_path = base_dir / "Data" / "processed" / "abt_clean.csv"
    amenities_dir = base_dir / "Data" / "amenities"
    
    # Load ABT
    print(f"Loading ABT from {abt_path}")
    abt = pd.read_csv(abt_path)
    print(f"ABT shape before: {abt.shape}")
    
    # Check required columns
    if 'latitude' not in abt.columns or 'longitude' not in abt.columns:
        raise ValueError("ABT must have 'latitude' and 'longitude' columns")
    
    # Load amenity CSVs
    amenity_categories = ['education', 'finance', 'grocery', 'health', 'security', 'transport']
    amenities = {}
    
    for category in amenity_categories:
        path = amenities_dir / f"{category}.csv"
        if not path.exists():
            raise FileNotFoundError(f"Amenity file not found: {path}")
        df = pd.read_csv(path)
        amenities[category] = df
        print(f"Loaded {len(df)} {category} amenities")
    
    # Initialize new columns
    for category in amenity_categories:
        abt[f'hansen_{category}'] = 0.0
    
    # Compute Hansen scores for each category
    for category in amenity_categories:
        print(f"Computing hansen_{category}...")
        
        amenity_df = amenities[category]
        amenity_lats = amenity_df['lat'].values
        amenity_lons = amenity_df['lon'].values
        
        # Compute score for each property
        scores = []
        for idx, row in abt.iterrows():
            score = compute_hansen_score(
                row['latitude'],
                row['longitude'],
                amenity_lats,
                amenity_lons
            )
            scores.append(score)
        
        abt[f'hansen_{category}'] = scores
    
    # Compute composite score with weights
    print("Computing hansen_composite...")
    weights = {
        'transport': 0.25,
        'grocery': 0.20,
        'education': 0.20,
        'health': 0.15,
        'finance': 0.15,
        'security': 0.05
    }
    
    abt['hansen_composite'] = (
        weights['transport'] * abt['hansen_transport'] +
        weights['grocery'] * abt['hansen_grocery'] +
        weights['education'] * abt['hansen_education'] +
        weights['health'] * abt['hansen_health'] +
        weights['finance'] * abt['hansen_finance'] +
        weights['security'] * abt['hansen_security']
    )
    
    # Round all Hansen columns to 4 decimal places
    hansen_cols = [col for col in abt.columns if col.startswith('hansen_')]
    for col in hansen_cols:
        abt[col] = abt[col].round(4)
    
    # Print statistics before saving
    print(f"\nABT shape after: {abt.shape}")
    print("\nHansen score statistics:")
    for col in hansen_cols:
        zero_count = (abt[col] == 0.0).sum()
        print(f"\n{col}:")
        print(f"  Mean: {abt[col].mean():.4f}")
        print(f"  Std:  {abt[col].std():.4f}")
        print(f"  Zero scores: {zero_count} rows")
    
    # Overwrite ABT
    print(f"\nSaving ABT to {abt_path}")
    abt.to_csv(abt_path, index=False)
    print("Done.")


if __name__ == "__main__":
    main()

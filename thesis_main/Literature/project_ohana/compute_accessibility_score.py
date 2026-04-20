import geopy
import geopy.distance as dist
import numpy as np
import fire
import pandas as pd
from tqdm import tqdm

# Multi-processing setup (optional)
PANDAS_MP = False

if PANDAS_MP:
    try:
        import os
        os.environ["MODIN_ENGINE"] = "ray"
        import modin.pandas as mpd
        from modin.config import ProgressBar
        ProgressBar.enable()
        import ray
        ray.init(ignore_reinit_error=True)
    except ImportError:
        print("Modin/Ray not found. Falling back to standard pandas.")
        PANDAS_MP = False

def get_distance_in_km_gc(pointA, pointB):
    """Calculate distance between pointA and pointB using Great Circle."""
    return dist.great_circle(pointA, pointB).km

def calculate_hansen_grav_score(distances, coeff=2.0, self_distance_floor=0.5):
    """
    Calculates Hansen Gravitational Score.
    Implements a self_distance_floor (default 0.5km) to prevent divide-by-zero 
    and match the project methodology.
    """
    if len(distances) == 0:
        return 0

    distances = np.array(distances)
    # Apply floor to distances (self-distance fix)
    distances = np.maximum(distances, self_distance_floor)

    # Formula: Σ (1 / d^β)
    scores = 1.0 / (distances ** coeff)
    return np.sum(scores)

def get_accessibility_score(row, amenities_tuples, max_study_area, coeff, self_distance_floor):
    """Calculates score for a single row (property/centroid)."""
    # Flexible column names
    lat = row.get('latitude', row.get('lat'))
    lon = row.get('longitude', row.get('lon'))

    if lat is None or lon is None:
        return row

    distances = []
    pointA = (lat, lon)
    for pointB in amenities_tuples:
        distance = get_distance_in_km_gc(pointA, pointB)
        if distance <= max_study_area:
            distances.append(distance)

    score = calculate_hansen_grav_score(distances, coeff, self_distance_floor)
    
    # Store results
    row['num_amenities'] = len(distances)
    row['ave_amenity_distance'] = np.mean(distances) if len(distances) > 0 else 0
    row['accessibility_score'] = score
    return row

def compute_accessibility_score(
        amenities_file, centroids_file, 
        coeff=2.0, max_study_area=14.2, 
        self_distance_floor=0.5,
        output_file='scores.csv'):
    """
    Calculates accessibility scores for all points in centroids_file based on amenities_file.
    
    Args:
        amenities_file: CSV with 'lat', 'lon' of amenities
        centroids_file: CSV with 'latitude'/'longitude' (or lat/lon) of target properties
        coeff: Friction coefficient (beta). Default 2.0 for urban areas.
        max_study_area: Search radius in km. Default 14.2km.
        self_distance_floor: Minimum distance in km. Default 0.5km.
    """
    print(f"Reading files: {amenities_file}, {centroids_file}...")
    amenities_df = pd.read_csv(amenities_file)
    centroids_df = pd.read_csv(centroids_file)

    # Prepare amenities as a list of tuples for speed
    amenities_tuples = list(zip(amenities_df['lat'], amenities_df['lon']))
    print(f"Total amenities to process: {len(amenities_tuples)}")

    print(f"Calculating scores (beta={coeff}, radius={max_study_area}km)...")

    if PANDAS_MP:
        # Using Modin for parallelized apply
        m_centroids_df = mpd.DataFrame(centroids_df)
        results = m_centroids_df.apply(
            get_accessibility_score, axis=1, 
            args=(amenities_tuples, max_study_area, coeff, self_distance_floor)
        )
        scores_df = results.to_pandas()
    else:
        # Standard pandas with progress bar
        tqdm.pandas()
        scores_df = centroids_df.progress_apply(
            get_accessibility_score, axis=1, 
            args=(amenities_tuples, max_study_area, coeff, self_distance_floor)
        )

    scores_df.to_csv(output_file, index=False)
    print(f"Saved results to {output_file}")
    
    if PANDAS_MP:
        ray.shutdown()

if __name__ == "__main__":
    fire.Fire(compute_accessibility_score)

"""
Phase 1: Region & Label Setup Module
- Saves starter known manganese deposit dataset (from GSI/IBM records)
- Generates random negative/control sample points within the region bounding box
- Enforces buffer zone (>= 2 km) from any positive deposit location
"""

import math
import random
import pandas as pd
import numpy as np
from pathlib import Path
import config

def haversine_km(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance between two points in kilometers."""
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def save_known_deposits():
    """Save initial positive deposit coordinates to CSV."""
    df_positives = pd.DataFrame(config.STARTER_DEPOSITS)
    df_positives["label"] = 1
    df_positives["type"] = "Positive (Known Deposit)"
    
    config.DEPOSITS_CSV.parent.mkdir(parents=True, exist_ok=True)
    df_positives.to_csv(config.DEPOSITS_CSV, index=False)
    print(f" Saved {len(df_positives)} known manganese deposit points to '{config.DEPOSITS_CSV}'")
    return df_positives

def generate_negative_control_points(positives_df, num_negatives=config.NUM_NEGATIVE_SAMPLES, buffer_km=config.BUFFER_KM, seed=config.SEED):
    """
    Generate negative control sample points randomly within the region bounding box,
    ensuring points are sampled both INSIDE and OUTSIDE the Sausar Gondite Belt polygon
    with at least `buffer_km` separation from known deposits.
    """
    random.seed(seed)
    np.random.seed(seed)
    from src.geology_layer import is_point_in_polygon
    
    min_lon, min_lat, max_lon, max_lat = config.BBOX
    pos_coords = positives_df[["lat", "lon"]].values
    
    negatives = []
    attempts = 0
    max_attempts = num_negatives * 300
    
    target_inside = num_negatives // 2  # 50% inside gondite belt, 50% outside
    count_inside = 0
    count_outside = 0
    
    while len(negatives) < num_negatives and attempts < max_attempts:
        attempts += 1
        cand_lat = random.uniform(min_lat, max_lat)
        cand_lon = random.uniform(min_lon, max_lon)
        
        # Check distance to all positive deposits
        too_close = False
        for pos_lat, pos_lon in pos_coords:
            dist = haversine_km(cand_lat, cand_lon, pos_lat, pos_lon)
            if dist < buffer_km:
                too_close = True
                break
        
        if not too_close:
            in_belt = is_point_in_polygon(cand_lon, cand_lat)
            if in_belt and count_inside < target_inside:
                count_inside += 1
                negatives.append({
                    "name": f"Control_Point_Belt_{count_inside}",
                    "lat": round(cand_lat, 5),
                    "lon": round(cand_lon, 5),
                    "district": "Gondite Belt Control",
                    "state": "N/A",
                    "label": 0,
                    "type": "Negative (Intra-Belt Control Point)"
                })
            elif not in_belt and count_outside < (num_negatives - target_inside):
                count_outside += 1
                negatives.append({
                    "name": f"Control_Point_Outer_{count_outside}",
                    "lat": round(cand_lat, 5),
                    "lon": round(cand_lon, 5),
                    "district": "Outer Region Control",
                    "state": "N/A",
                    "label": 0,
                    "type": "Negative (Outer Region Control Point)"
                })
            
    df_negatives = pd.DataFrame(negatives)
    print(f" Generated {len(df_negatives)} negative control points ({count_inside} inside Gondite belt, {count_outside} outer region) with >={buffer_km}km buffer.")
    return df_negatives

def prepare_labeled_dataset():
    """
    Combines positive manganese deposits and negative control points into a single labeled dataset.
    """
    df_positives = save_known_deposits()
    df_negatives = generate_negative_control_points(df_positives)
    
    df_combined = pd.concat([df_positives, df_negatives], ignore_index=True)
    
    print("\n--- PHASE 1 DIAGNOSTIC SUMMARY ---")
    print(f"Target Bounding Box: [Lon: {config.BBOX[0]} to {config.BBOX[2]}, Lat: {config.BBOX[1]} to {config.BBOX[3]}]")
    print(f"Total Labeled Locations: {len(df_combined)}")
    print(f"  - Positive Samples (Known Mn Ore Deposits): {len(df_positives)}")
    print(f"  - Negative Control Samples: {len(df_negatives)}")
    print(f"  - Buffer Zone Constraint: >= {config.BUFFER_KM} km from any positive deposit")
    print("-----------------------------------\n")
    
    return df_combined

if __name__ == "__main__":
    df = prepare_labeled_dataset()

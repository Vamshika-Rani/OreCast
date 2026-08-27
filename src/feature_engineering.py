"""
Phase 3: Feature Engineering Module
- Computes standard mineral-indicative spectral indices from Sentinel-2 bands
- Combines spectral indices with DEM terrain features (elevation, slope, aspect)
- Outputs tabular dataset (CSV) and displays diagnostic statistics
"""

import pandas as pd
import numpy as np
import config
from src.data_prep import prepare_labeled_dataset
from src.gee_acquisition import fetch_satellite_data_for_points

def compute_spectral_indices(df):
    """
    Computes standard remote sensing spectral indices for mineral exploration & vegetation filtering:
    1. Iron Oxide Index = Red / Blue (B4 / B2)
    2. SWIR / NIR Ratio = SWIR1 / NIR (B11 / B8)
    3. Clay / Alteration Index = SWIR1 / SWIR2 (B11 / B12)
    4. Ferrous Iron Index = SWIR2 / NIR (B12 / B8)
    5. NDVI = (NIR - Red) / (NIR + Red) ((B8 - B4) / (B8 + B4))
    """
    df = df.copy()
    
    # 1. Iron Oxide Index (Ferric Iron Fe3+)
    df["iron_oxide_index"] = np.where(df["B2"] > 0, df["B4"] / df["B2"], 0.0)
    
    # 2. SWIR / NIR Ratio (Mineral Alteration)
    df["swir_nir_ratio"] = np.where(df["B8"] > 0, df["B11"] / df["B8"], 0.0)
    
    # 3. Clay / Hydrothermal Alteration Index (Al-OH absorption at 2.2 um)
    df["clay_alteration_idx"] = np.where(df["B12"] > 0, df["B11"] / df["B12"], 0.0)
    
    # 4. Ferrous Iron Index (Fe2+)
    df["ferrous_iron_idx"] = np.where(df["B8"] > 0, df["B12"] / df["B8"], 0.0)
    
    # 5. NDVI (Normalized Difference Vegetation Index)
    denom = df["B8"] + df["B4"]
    df["ndvi"] = np.where(denom != 0, (df["B8"] - df["B4"]) / denom, 0.0)
    
    # 6. Sub-surface Proxy: Sausar Group Gondite Geological Formation Membership & Distance
    from src.geology_layer import add_geology_features
    df = add_geology_features(df)
    
    # Round all floating point columns to 4 decimals
    for col in config.FEATURE_COLUMNS:
        if col in df.columns:
            df[col] = df[col].round(4)
            
    return df

def build_feature_dataset(force_rebuild=False):
    """
    Executes Phase 1, Phase 2, and Phase 3 to generate the full tabular feature dataset.
    Caches output to config.SAMPLES_CSV.
    """
    if not force_rebuild and config.SAMPLES_CSV.exists():
        print(f" Loading existing tabular feature dataset from '{config.SAMPLES_CSV}'...")
        df_dataset = pd.read_csv(config.SAMPLES_CSV)
        print_dataset_statistics(df_dataset)
        return df_dataset
        
    print("\n Building Tabular Feature Dataset (Phases 1-3)...")
    df_points = prepare_labeled_dataset()
    df_raw = fetch_satellite_data_for_points(df_points)
    df_dataset = compute_spectral_indices(df_raw)
    
    # Save to disk
    df_dataset.to_csv(config.SAMPLES_CSV, index=False)
    print(f" Saved clean feature dataset with {len(df_dataset)} rows to '{config.SAMPLES_CSV}'")
    
    print_dataset_statistics(df_dataset)
    return df_dataset

def print_dataset_statistics(df):
    """
    Prints diagnostic dataset statistics: class balance, feature summary statistics, missing values.
    """
    print("\n=======================================================")
    print("           PHASE 3 FEATURE DATASET STATISTICS          ")
    print("=======================================================")
    print(f"Total Rows (Sample Locations): {len(df)}")
    print("Class Balance:")
    print(df["label"].value_counts().to_string())
    print("\nMissing Values Check:")
    missing_sum = df[config.FEATURE_COLUMNS].isnull().sum().sum()
    print(f"Total NaN/Null values in feature columns: {missing_sum}")
    
    print("\nFeature Distribution Summary:")
    summary = df[config.FEATURE_COLUMNS].describe().T[["mean", "std", "min", "50%", "max"]]
    print(summary.to_string())
    print("=======================================================\n")

if __name__ == "__main__":
    df = build_feature_dataset(force_rebuild=True)

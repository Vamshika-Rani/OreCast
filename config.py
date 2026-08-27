"""
Global Configuration for Manganese Reserve Detection Pipeline
Region: Central India Manganese Belt (Balaghat - Bhandara - Nagpur)
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Target Region Bounding Box (WGS84: [min_lon, min_lat, max_lon, max_lat])
# Covers Balaghat (MP), Bhandara & Nagpur (Maharashtra) manganese belt
BBOX = [79.20, 21.10, 80.50, 22.05]

# Load environment variables from .env if present (prevents committing secrets)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Google Earth Engine Project Configuration (read cleanly from environment, no hardcoded secrets)
GEE_PROJECT_ID = os.getenv("GEE_PROJECT_ID", "")

# Date range for satellite composite (dry season preferred for low cloud/vegetation cover)
DATE_START = "2024-01-01"
DATE_END = "2024-05-31"

# Negative Point Sampling Parameters
BUFFER_KM = 2.0  # Minimum distance in km from any known deposit for negative control points
NUM_NEGATIVE_SAMPLES = 60  # ~2:1 or 1.5:1 ratio of negative to positive points
SEED = 42

# Feature Constants
SENTINEL2_BANDS = {
    "B2": "Blue",
    "B3": "Green",
    "B4": "Red",
    "B8": "NIR",
    "B11": "SWIR1",
    "B12": "SWIR2"
}

FEATURE_COLUMNS = [
    "B2", "B3", "B4", "B8", "B11", "B12",
    "iron_oxide_index",    # Red / Blue (B4 / B2)
    "swir_nir_ratio",      # SWIR1 / NIR (B11 / B8)
    "clay_alteration_idx", # SWIR1 / SWIR2 (B11 / B12)
    "ferrous_iron_idx",    # SWIR2 / NIR (B12 / B8)
    "ndvi",                # (NIR - Red) / (NIR + Red)
    "elevation",           # SRTM DEM elevation in meters
    "slope",               # DEM slope in degrees
    "aspect",              # DEM aspect in degrees
    "in_gondite_formation",# GSI Sub-surface proxy: Inside Sausar Gondite Belt (1/0)
    "dist_to_gondite_km"   # GSI Sub-surface proxy: Distance to Gondite boundary in km
]

# File Paths - Module 1 (Reserve Mapping)
DEPOSITS_CSV = RAW_DATA_DIR / "known_manganese_deposits.csv"
SAMPLES_CSV = PROCESSED_DATA_DIR / "labeled_samples_dataset.csv"
MODEL_FILE = PROCESSED_DATA_DIR / "manganese_model.pkl"
GRID_PREDICTIONS_CSV = PROCESSED_DATA_DIR / "region_grid_predictions.csv"
PREDICTION_RASTER_TIF = PROCESSED_DATA_DIR / "manganese_probability_map.tif"

# File Paths - Module 2 (Production Shortfall & Operational Planning)
SYNTHETIC_PRODUCTION_CSV = RAW_DATA_DIR / "synthetic_moil_production_history.csv"
SHORTFALL_MODEL_FILE = PROCESSED_DATA_DIR / "shortfall_model.pkl"
SHORTFALL_PREDICTIONS_CSV = PROCESSED_DATA_DIR / "shortfall_site_predictions.csv"

# Key MOIL Mine Operations for Production Shortfall Tracking
MOIL_MINES = [
    {"mine_id": "M01", "name": "Bharweli Mine", "district": "Balaghat", "type": "Underground", "monthly_target_mt": 30000, "lat": 21.800, "lon": 80.220},
    {"mine_id": "M02", "name": "Dongri Buzurg Mine", "district": "Bhandara", "type": "Opencast", "monthly_target_mt": 25000, "lat": 21.530, "lon": 79.700},
    {"mine_id": "M03", "name": "Tirodi Mine", "district": "Balaghat", "type": "Opencast", "monthly_target_mt": 18000, "lat": 21.620, "lon": 80.180},
    {"mine_id": "M04", "name": "Chikla Mine", "district": "Bhandara", "type": "Underground", "monthly_target_mt": 15000, "lat": 21.550, "lon": 79.650},
    {"mine_id": "M05", "name": "Mansar Mine", "district": "Nagpur", "type": "Underground", "monthly_target_mt": 12000, "lat": 21.390, "lon": 79.250}
]

# Shortfall Feature Definitions (Combining Real Environmental + Synthetic Operational Inputs)
SHORTFALL_FEATURES = [
    "equipment_uptime_pct",      # Synthetic: Fleet availability %
    "maintenance_downtime_hrs",  # Synthetic: Breakdown / repair hours
    "blasting_delays_count",     # Synthetic: Explosive/weather blasting delays
    "haul_road_flooding_days",   # Synthetic: Pit access/haul road blockage days
    "monthly_rainfall_mm",       # Real GEE / Satellite Environmental: Monthly rainfall
    "soil_moisture_index",       # Real GEE / Satellite Environmental: Soil moisture
    "mean_ndvi",                 # Real Sentinel-2: Surrounding vegetation index
    "land_surface_temp_c",       # Real MODIS/GEE: Mean surface temperature
    "hist_3m_avg_production_mt"  # Synthetic: 3-month moving average production run-rate
]

# Initial Starter Dataset: 30 Documented Manganese Deposits from GSI / IBM Records
STARTER_DEPOSITS = [
    {"name": "Tirodi Mine", "lat": 21.620, "lon": 80.180, "district": "Balaghat", "state": "Madhya Pradesh"},
    {"name": "Bharweli Mine", "lat": 21.800, "lon": 80.220, "district": "Balaghat", "state": "Madhya Pradesh"},
    {"name": "Sakoli Deposit", "lat": 21.210, "lon": 79.750, "district": "Bhandara", "state": "Maharashtra"},
    {"name": "Chikla Mine", "lat": 21.550, "lon": 79.650, "district": "Bhandara", "state": "Maharashtra"},
    {"name": "Sitasaongi Mine", "lat": 21.560, "lon": 79.640, "district": "Bhandara", "state": "Maharashtra"},
    {"name": "Dongri Buzurg Mine", "lat": 21.530, "lon": 79.700, "district": "Bhandara", "state": "Maharashtra"},
    {"name": "Mansar Deposit", "lat": 21.390, "lon": 79.250, "district": "Nagpur", "state": "Maharashtra"},
    {"name": "Kandri Mine", "lat": 21.420, "lon": 79.280, "district": "Nagpur", "state": "Maharashtra"},
    {"name": "Miragpur Deposit", "lat": 21.640, "lon": 79.820, "district": "Balaghat", "state": "Madhya Pradesh"},
    {"name": "Katangi Mine", "lat": 21.700, "lon": 79.800, "district": "Balaghat", "state": "Madhya Pradesh"},
    {"name": "Garra Deposit", "lat": 21.810, "lon": 80.170, "district": "Balaghat", "state": "Madhya Pradesh"},
    {"name": "Sukli / Ramrama", "lat": 21.780, "lon": 79.880, "district": "Balaghat", "state": "Madhya Pradesh"},
    {"name": "Ukwa Mine", "lat": 21.960, "lon": 80.470, "district": "Balaghat", "state": "Madhya Pradesh"},
    {"name": "Jamrapani Mine", "lat": 21.730, "lon": 79.850, "district": "Balaghat", "state": "Madhya Pradesh"},
    {"name": "Jarah Mohgaon", "lat": 21.660, "lon": 79.800, "district": "Balaghat", "state": "Madhya Pradesh"},
    {"name": "Netra Deposit", "lat": 21.720, "lon": 79.830, "district": "Balaghat", "state": "Madhya Pradesh"},
    {"name": "Gowari Wadhona", "lat": 21.520, "lon": 79.520, "district": "Nagpur", "state": "Maharashtra"},
    {"name": "Parsoda Deposit", "lat": 21.360, "lon": 79.350, "district": "Nagpur", "state": "Maharashtra"},
    {"name": "Kurmura Mine", "lat": 21.520, "lon": 79.610, "district": "Bhandara", "state": "Maharashtra"},
    {"name": "Junawani Deposit", "lat": 21.550, "lon": 79.350, "district": "Nagpur", "state": "Maharashtra"},
    {"name": "Kaolkasa Deposit", "lat": 21.600, "lon": 80.050, "district": "Balaghat", "state": "Madhya Pradesh"},
    {"name": "Jagantola Deposit", "lat": 21.900, "lon": 80.350, "district": "Balaghat", "state": "Madhya Pradesh"},
    {"name": "Gudma Deposit", "lat": 21.920, "lon": 80.400, "district": "Balaghat", "state": "Madhya Pradesh"},
    {"name": "Laugur Deposit", "lat": 21.850, "lon": 80.300, "district": "Balaghat", "state": "Madhya Pradesh"},
    {"name": "Selwa Deposit", "lat": 21.480, "lon": 79.750, "district": "Bhandara", "state": "Maharashtra"},
    {"name": "Pauni Mn Belt", "lat": 21.150, "lon": 79.650, "district": "Bhandara", "state": "Maharashtra"},
    {"name": "Wandara Deposit", "lat": 21.400, "lon": 79.700, "district": "Bhandara", "state": "Maharashtra"},
    {"name": "Asolpani Deposit", "lat": 21.350, "lon": 79.680, "district": "Bhandara", "state": "Maharashtra"},
    {"name": "Pardhi Mine", "lat": 21.750, "lon": 79.920, "district": "Balaghat", "state": "Madhya Pradesh"},
    {"name": "Ghatkurti Deposit", "lat": 21.680, "lon": 80.120, "district": "Balaghat", "state": "Madhya Pradesh"}
]


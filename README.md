# OreCast

> **Satellite Intelligence for Manganese Reserve Discovery and Production Planning**  
> Smart India Hackathon (SIH) 2026 • Ministry of Steel Problem Statement Prototype  

OreCast is a satellite-driven decision platform built for manganese mineral exploration and mine production risk management in Central India (Balaghat, Bhandara, and Nagpur mining belts).

---

## System Overview

OreCast brings together satellite remote sensing, terrain analysis, sub-surface geological proxy modeling, and operational forecasting into a single plain-language interface:

1. **Where to Find Manganese**: Combines **Sentinel-2 multispectral satellite imagery**, **SRTM land elevation data**, and **GSI Sub-Surface Geological Formation Proxies** to map areas with a high chance of containing manganese deposits across unexplored terrain.
2. **Production Trends & Forecast**: Combines regional satellite climate conditions (rainfall, soil moisture, land temperature) with mine operational data to forecast next-month ore production volumes.
3. **Shortfall Risk by Mine**: Evaluates monthly risk levels across key active mine sites (Bharweli, Dongri Buzurg, Tirodi, Chikla, and Mansar) to flag potential production drops before they occur.
4. **Recommended Actions**: Automatically identifies primary risk drivers and generates actionable directives across the 3 problem statement categories: **Mine Schedule Adjustment**, **Equipment Redeployment**, and **Blasting Optimization**.
5. **Data Sources**: A transparent breakdown showing which inputs use real satellite measurements versus geological proxies and estimated placeholder data.

---

## Scientific & Geological Foundation

### 1. Geological Setting (Sausar Group Gondite Belt)
In Central India's primary manganese belts (Balaghat in Madhya Pradesh, Bhandara and Nagpur in Maharashtra), manganese ores (pyrolusite $MnO_2$, psilomelane, braunite) occur within metamorphosed gondite rock formations (Sausar Group metasediments) and weathered lateritic crusts. These mineral zones co-exist with ferric iron oxides (hematite $Fe_2O_3$, goethite) and clay alteration minerals.

### 2. Satellite Spectral Physics & Geological Proxies

| Feature / Index | Type | Physical / Absorption Basis | Geological Significance |
| :--- | :--- | :--- | :--- |
| **Iron Oxide Index** | Surface Spectral | Ferric iron ($Fe^{3+}$) absorbs Blue light and reflects Red light. | Identifies iron oxide mineral zones co-existing with manganese ore. |
| **SWIR / NIR Ratio** | Surface Spectral | Shortwave Infrared reflects strongly off altered rock. | Detects hydrothermally altered host rock formations. |
| **Clay Index** | Surface Spectral | Hydroxyl (Al-OH) bending causes absorption at 2.2 $\mu$m (Band 12). | Highlights weathered alteration clay haloes around mineral deposits. |
| **NDVI (Vegetation Mask)** | Surface Spectral | Chlorophyll absorbs Red light and reflects Near-Infrared. | Filters out dense vegetation to focus on exposed rock and soil. |
| **Elevation & Slope** | Terrain Physical | Upland gondites form resistant structural ridges (350m–520m). | Discriminates resistant metamorphic ridges from low plains. |
| **Sausar Gondite Belt (GSI)** | Sub-Surface Proxy | Polygons from GSI Quadrangle Maps (55 O, 55 K, 64 C). | Encodes rock formation membership and boundary proximity as a proxy for ore host rock. |

---

## System Architecture & User Views

```
+-----------------------------------------------------------------------------------+
|                                     ORECAST                                       |
|      Satellite Intelligence for Reserve Discovery & Production Planning           |
+-----------------------------------------------------------------------------------+
                                         |
     +-------------------+---------------+-------------------+-------------------+
     |                   |                                   |                   |
     v                   v                                   v                   v
+-----------------+ +-------------------------------+ +-------------------+ +-------------------+
|  WHERE TO FIND  | |     PRODUCTION TRENDS         | |  SHORTFALL RISK   | |    RECOMMENDED    |
|    MANGANESE    | |         & FORECAST            | |     BY MINE       | |      ACTIONS      |
| (Satellite/GSI) | |   (Climate + Ops Signals)     | | (Risk Diagnosis)| | (Schedule/Eq/Blast)|
+-----------------+ +-------------------------------+ +-------------------+ +-------------------+
```

### 1. Where to Find Manganese
- Evaluates 5,568 grid areas (~1.5 km resolution) across the Balaghat-Bhandara manganese belt.
- Integrates surface spectral bands, DEM terrain features, and **GSI Sub-Surface Geological Formation Proxies** (`in_gondite_formation`, `dist_to_gondite_km`).
- Achieves **95.0% Spatial Accuracy (Recall)** and **0.924 ROC-AUC**.
- **High Prospect Markers**: High-probability areas ($\ge 0.80$ chance) are displayed as **prominent purple markers** (`#A855F7`) alongside toggleable **GSI Geological Formation Boundaries**.

### 2. Production Trends & Forecast
- Tracks monthly operational trends for key mine sites: Bharweli, Dongri Buzurg, Tirodi, Chikla, and Mansar.
- Forecasts next-month ore production volume and shortfall probability below expected targets.

### 3. Shortfall Risk by Mine
- Diagnoses current mine-level risk levels (High Risk, Moderate Risk, Low Risk).
- Highlights key contributing risk drivers (equipment uptime, maintenance hours, rainfall, blasting delays).

### 4. Recommended Actions
Translates shortfall risk drivers into concrete directives across 3 filterable categories:
- **Mine Schedule Adjustment**: Reallocates extraction quotas to lower-risk sister mines (e.g. shift 2,300 MT target from Bharweli to Tirodi Mine), front-loads Q1 production ahead of monsoon onset, and adjusts shift work schedules.
- **Equipment Redeployment**: Redeploys standby dumpers/loaders from low-risk underground sites and dispatches mobile mechanics.
- **Blasting Optimization**: Transitions to waterproof emulsion explosives for wet bench conditions and pre-drills upper bench blasting patterns.

### 5. Data Sources & Transparency
- Clearly separates real satellite measurements, geological map proxies, and estimated operational placeholders.

---

## Data Sources & Transparency Audit

| Application Section | Information / Variable | Data Status | Data Provider |
| :--- | :--- | :--- | :--- |
| **Where to Find Manganese** | Sentinel-2 Bands & Mineral Scores | Real satellite data | Google Earth Engine (`COPERNICUS/S2_SR_HARMONIZED`) |
| **Where to Find Manganese** | Elevation & Land Slope | Real satellite data | NASA / USGS SRTM 30m DEM (`USGS/SRTMGL1_003`) |
| **Where to Find Manganese** | Geological Formation Boundaries (Sub-surface Proxy) | Geological map proxy (GSI) | GSI Quadrangle Literature (55 O, 55 K, 64 C) — *Geological formation boundaries (GSI public maps) — used as a surface-mappable proxy for sub-surface rock type. This is NOT drilling or geophysical subsurface data, which MOIL would need to provide for volumetric reserve estimation.* |
| **Production Trends & Forecast** | Monthly Rainfall & Soil Water | Real satellite data | GEE CHIRPS Daily Rainfall & ERA5-Land Soil Moisture |
| **Production Trends & Forecast** | Land Surface Temperature | Real satellite data | GEE MODIS LST (`MODIS/061/MOD11A2`) |
| **Production Trends & Forecast** | Historical Production Figures | Real public data | Compiled from MOIL Investor Relations, PIB, IBM Yearbook ([Template CSV](file:///c:/Users/amoli/OneDrive/Desktop/Manganese%20Reserve%20detection/data/raw/moil_real_production_template.csv)) |
| **Production Trends & Forecast** | Equipment Uptime & Repair Hours | Estimated placeholder data | Calibrated operational breakdown generator ([`src/synthetic_production_gen.py`](file:///c:/Users/amoli/OneDrive/Desktop/Manganese%20Reserve%20detection/src/synthetic_production_gen.py)) |
| **Production Trends & Forecast** | Blasting Delays & Road Flooding | Estimated placeholder data | Calibrated operational delay log generator |

---

## Repository Structure

```
Manganese Reserve detection/
├── .gitignore                 # Excludes secrets, credentials, logs, and caches
├── .env.example               # Environment variables configuration template
├── config.py                 # Region boundaries, GEE settings, feature constants, file paths
├── data/
│   ├── raw/                   # Known deposit coordinates & production CSVs
│   │   ├── known_manganese_deposits.csv
│   │   ├── moil_real_production_template.csv
│   │   └── synthetic_moil_production_history.csv
│   └── processed/             # Machine learning models, feature datasets, GeoTIFF rasters
│       ├── manganese_model.pkl
│       ├── manganese_probability_map.tif
│       ├── region_grid_predictions.csv
│       ├── shortfall_model.pkl
│       └── shortfall_site_predictions.csv
├── src/
│   ├── data_prep.py           # Deposit coordinate loading & negative control sampling
│   ├── gee_acquisition.py     # Earth Engine satellite data collection & processing
│   ├── geology_layer.py       # Sausar Group Gondite geological formation & distance calculator
│   ├── feature_engineering.py # Spectral index, terrain & geological feature extraction
│   ├── model_training.py      # Spatial cross-validation & reserve model training
│   ├── predict_region.py      # Region grid scoring & high-potential hotspot analysis
│   ├── synthetic_production_gen.py # Time-series operational data generator
│   ├── shortfall_model.py     # Production volume forecaster & shortfall classifier
│   └── corrective_engine.py   # Rule-based operational recommendation engine
├── app.py                     # OreCast Interactive Streamlit Dashboard
├── requirements.txt           # Python dependencies
└── README.md                  # System documentation & scientific rationale
```

---

### 1. One-Click Launch (Recommended)
You only need **ONE command** to run the app:
```bash
streamlit run app.py
```
*Or on Windows, simply double-click **[`run_app.bat`](file:///c:/Users/amoli/OneDrive/Desktop/Manganese%20Reserve%20detection/run_app.bat)**.*

`app.py` automatically detects pre-computed models and data, loading everything instantly!

---

### 2. Security & Environment Setup
This repository is configured to keep API keys and environment credentials safe:
1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```
2. (Optional) If your Google Earth Engine setup requires a specific GCP Project ID, set it in `.env`:
   ```env
   GEE_PROJECT_ID=your-gcp-project-id
   ```
3. A `.gitignore` file is included to prevent `.env` and credentials from being committed to GitHub.

### 3. Step-by-Step Pipeline Execution

#### Reserve Exploration Pipeline
```bash
# 1. Prepare labeled deposit locations
python -m src.data_prep

# 2. Extract Sentinel-2 spectral indices, SRTM terrain & GSI geology features
python -m src.feature_engineering

# 3. Train reserve detection model with spatial cross-validation
python -m src.model_training

# 4. Generate region-wide probability predictions & GeoTIFF raster
python -m src.predict_region
```

#### Production Forecasting & Actions Pipeline
```bash
# 5. Generate calibrated operational history
python -m src.synthetic_production_gen

# 6. Train production volume & shortfall prediction models
python -m src.shortfall_model

# 7. Run operational recommendation engine
python -m src.corrective_engine
```

### 4. Launch Interactive Dashboard
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501` to access OreCast.

---

## Model Performance & Validation Summary

### Reserve Detection Classifier (Integrated Surface + Sub-Surface Proxy)
- **Detection Accuracy (Recall)**: **95.0%** (Minimizes missed deposit areas)
- **Spatial ROC-AUC**: **0.924** (Evaluated on unseen sub-regions)
- **Sub-Surface Feature Importance Contribution**:
  - Distance to Gondite Boundary (`dist_to_gondite_km`): **4.13%**
  - Gondite Belt Membership (`in_gondite_formation`): **2.31%**
  - Combined Geological Contribution: **6.44%** total model importance.

### Production Shortfall Forecaster
- **Shortfall Detection Recall**: **100.0%** on out-of-time test data
- **Production Forecast Error (MAE)**: **2,471 MT / month**
- **Main Risk Factors**:
  1. Machinery Availability: **34.58%**
  2. Soil Moisture: **22.84%**
  3. Monthly Rainfall: **13.22%**
  4. Maintenance Downtime: **8.97%**

---

## Operational Scope & Data Notes

1. **Sub-surface Geological Proxy**: Geological formation boundaries (Sausar Group gondite metasediments from GSI public quadrangle maps) provide a legitimate surface-mappable proxy for ore-bearing host rock type. Actual volumetric reserve estimation requires private MOIL/GSI drilling cores.
2. **Operational Log Scope**: Machinery uptime and breakdown logs use estimated historical placeholders calibrated to regional rainfall patterns due to the private nature of internal mine records. Real public production figures can be loaded directly into `data/raw/moil_real_production_input.csv`.

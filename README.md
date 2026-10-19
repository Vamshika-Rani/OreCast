Cast

> **Satellite Intelligence for Manganese Reserve Discovery and Production Planning**  
> Smart India Hackathon (SIH) 2026 • Ministry of Steel Problem Statement Prototype  

OreCast is a satellite-driven AI decision platform built for manganese mineral exploration and mine production risk management in Central India (**Balaghat**, **Bhandara**, and **Nagpur** mining belts).

![Data Source](https://img.shields.io/badge/Data_Source-Google_Earth_Engine_(Sentinel--2_L2A_%26_SRTM)-22c55e?style=for-the-badge)
![Model](https://img.shields.io/badge/Classifier-Calibrated_Random_Forest-0284c7?style=for-the-badge)
![UI](https://img.shields.io/badge/Dashboard-Streamlit_Dark_Glassmorphism-8b5cf6?style=for-the-badge)

---

## System Overview

OreCast brings together live satellite remote sensing, terrain landform analysis, sub-surface geological proxy modeling, and operational forecasting into a single plain-language interface:

1. **Where to Find Manganese**: Integrates live **Sentinel-2 multispectral satellite images** (Band 2, 3, 4, 8, 11, 12), **SRTM 30m land elevation data**, and **GSI Sub-Surface Geological Formation Proxies** to map unexplored terrain with high manganese ore prospectivity.
2. **Production Trends & Forecast**: Combines regional satellite climate conditions (CHIRPS rainfall, ERA5-Land soil moisture, MODIS land surface temperature) with mine operational metrics to forecast next-month ore production volumes.
3. **Shortfall Risk by Mine**: Evaluates monthly shortfall risk levels across key active MOIL mine sites (**Bharweli**, **Dongri Buzurg**, **Tirodi**, **Chikla**, and **Mansar**) to flag potential production drops before they occur.
4. **Recommended Actions**: Automatically identifies primary risk drivers and generates actionable directives across 3 core operational categories: **Mine Schedule Adjustment**, **Equipment Redeployment**, and **Blasting Optimization**.
5. **Data Sources & Transparency Audit**: A transparent breakdown showing which inputs use live satellite measurements versus geological proxies and estimated operational logs.

---

## Scientific & Geological Foundation

### 1. Geological Setting (Sausar Group Gondite Belt)
In Central India's primary manganese belts (Balaghat in Madhya Pradesh, Bhandara and Nagpur in Maharashtra), manganese ores (pyrolusite $MnO_2$, psilomelane, braunite) occur within metamorphosed gondite rock formations (Sausar Group metasediments) and weathered lateritic crusts. These mineral zones co-exist with ferric iron oxides (hematite $Fe_2O_3$, goethite) and clay alteration minerals.

### 2. Live Satellite Spectral Physics & Feature Importance

| Feature / Index | Data Source | Physical / Absorption Basis | Live Model Importance |
| :--- | :--- | :--- | :---: |
| **Clay Alteration Index** | Sentinel-2 SWIR1/SWIR2 | Al-OH hydroxyl bending causes strong absorption at 2.2 $\mu$m (Band 12). Highlights alteration haloes. | **14.07%** |
| **B12 (SWIR2)** | Sentinel-2 | Shortwave Infrared 2 surface reflectance band. | **9.17%** |
| **SWIR / NIR Ratio** | Sentinel-2 | Shortwave Infrared reflects strongly off altered host rock. | **7.34%** |
| **Ferrous Iron Index** | Sentinel-2 | B12 / B8 ratio measuring ferrous iron absorption. | **7.15%** |
| **Distance to Gondite Boundary** | GSI Map Layer | Distance (km) to Sausar Group Gondite host rock boundary. | **7.02%** |
| **Iron Oxide Index** | Sentinel-2 | Ferric iron ($Fe^{3+}$) absorbs Blue (B2) and reflects Red (B4). | **6.89%** |
| **SRTM Elevation & Slope** | USGS SRTM 30m DEM | Metamorphic gondites form resistant structural ridges (350m–520m). | **9.56%** |
| **Gondite Formation Proxy** | GSI Literature | Sausar Gondite Belt polygon membership (1/0). | **1.05%** |

---

## System Architecture & Modules

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
| (Sentinel-2/DEM)| |   (Climate + Ops Signals)     | | (Risk Diagnosis)| | (Schedule/Eq/Blast)|
+-----------------+ +-------------------------------+ +-------------------+ +-------------------+
```

### 1. Where to Find Manganese
- Evaluates **5,568 regional grid areas** (~1.5 km resolution) across the Balaghat-Bhandara manganese belt.
- Powered by live Google Earth Engine Sentinel-2 L2A & SRTM 30m DEM rasters.
- **Recalibrated Probability Thresholds**:
  - **Grid Filter Threshold (Default: 0.50)**: Renders 532 prospective grid cells (~9.5% of the target region).
  - **Hotspot Cutoff (Default: 0.60)**: Highlights **93 high-confidence target hotspots** (~1.6% of the grid) in bold Royal Purple markers (`#A855F7`).

### 2. Production Trends & Forecast
- Tracks monthly operational trends for key MOIL mine sites: Bharweli, Dongri Buzurg, Tirodi, Chikla, and Mansar.
- Forecasts next-month ore production volume and shortfall probability below expected targets.

### 3. Shortfall Risk by Mine
- Diagnoses current mine-level risk levels (High Risk, Moderate Risk, Low Risk).
- Highlights key contributing risk drivers (equipment uptime, maintenance hours, rainfall, blasting delays).

### 4. Recommended Actions
Translates shortfall risk drivers into concrete directives across 3 filterable categories:
- **Mine Schedule Adjustment**: Reallocates extraction quotas to lower-risk sister mines (e.g. shift 2,300 MT target from Bharweli to Tirodi Mine), front-loads Q1 production ahead of monsoon onset, and adjusts shift work schedules.
- **Equipment Redeployment**: Redeploys standby dumpers/loaders from low-risk underground sites and dispatches mobile mechanics.
- **Blasting Optimization**: Transitions to waterproof emulsion explosives for wet bench conditions and pre-drills upper bench blasting patterns.

---

## Data Sources & Transparency Audit

| Application Section | Information / Variable | Data Status | Data Provider / Source |
| :--- | :--- | :--- | :--- |
| **Where to Find Manganese** | Sentinel-2 Bands & Spectral Indices | **Live Satellite Data** | Google Earth Engine (`COPERNICUS/S2_SR_HARMONIZED`) |
| **Where to Find Manganese** | Elevation & Land Slope | **Live Satellite Data** | NASA / USGS SRTM 30m DEM (`USGS/SRTMGL1_003`) |
| **Where to Find Manganese** | Geological Formation Boundaries (Sub-surface Proxy) | Geological Map Proxy (GSI) | GSI Quadrangle Literature (55 O, 55 K, 64 C) |
| **Production Trends & Forecast** | Monthly Rainfall & Soil Water | **Live Satellite Data** | GEE CHIRPS Daily Rainfall & ERA5-Land Soil Moisture |
| **Production Trends & Forecast** | Land Surface Temperature | **Live Satellite Data** | GEE MODIS LST (`MODIS/061/MOD11A2`) |
| **Production Trends & Forecast** | Historical Production Figures | Real Public Data | MOIL Investor Relations, PIB & IBM Yearbook |
| **Production Trends & Forecast** | Equipment Uptime & Repair Hours | Operational Log Proxy | Calibrated operational log generator ([`src/synthetic_production_gen.py`](file:///c:/Users/amoli/OneDrive/Desktop/Manganese%20Reserve%20detection/src/synthetic_production_gen.py)) |

---

## Quick Start & Installation

### 1. One-Click Launch (Recommended)
Run the Streamlit application with a single command:
```bash
streamlit run app.py
```
*Or on Windows, simply double-click **[`run_app.bat`](file:///c:/Users/amoli/OneDrive/Desktop/Manganese%20Reserve%20detection/run_app.bat)**.*

### 2. Environment & Google Earth Engine Setup
This repository uses `.env` configuration to manage credentials securely:
1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```
2. Set your Google Cloud Project ID in `.env`:
   ```env
   GEE_PROJECT_ID=orecast-507007
   ```
3. Register your GCP Project for free Earth Engine access at: [console.cloud.google.com/earth-engine/configuration](https://console.cloud.google.com/earth-engine/configuration?project=orecast-507007).

---

## Repository Structure

```
Manganese Reserve detection/
├── .gitignore                 # Excludes secrets, credentials, logs, and caches
├── .env.example               # Environment configuration template
├── config.py                 # Region boundaries, GEE settings, feature constants, file paths
├── data/
│   ├── raw/                   # Known deposit coordinates & starter CSVs
│   │   ├── known_manganese_deposits.csv
│   │   └── synthetic_moil_production_history.csv
│   └── processed/             # Machine learning models, feature datasets, GeoTIFF rasters
│       ├── manganese_model.pkl
│       ├── manganese_probability_map.tif
│       ├── region_grid_predictions.csv
│       ├── shortfall_model.pkl
│       └── shortfall_site_predictions.csv
├── src/
│   ├── data_prep.py           # Deposit coordinate loading & intra-belt negative control sampling
│   ├── gee_acquisition.py     # Live Google Earth Engine satellite data acquisition
│   ├── geology_layer.py       # Sausar Group Gondite geological formation boundary polygon
│   ├── feature_engineering.py # Spectral index, terrain & geological feature extraction
│   ├── model_training.py      # Spatial cross-validation & calibrated model training
│   ├── predict_region.py      # Region grid scoring & high-potential hotspot analysis
│   ├── synthetic_production_gen.py # Operational time-series log generator
│   ├── shortfall_model.py     # Production volume forecaster & shortfall classifier
│   └── corrective_engine.py   # Rule-based operational recommendation engine
├── app.py                     # OreCast Interactive Streamlit Dashboard
├── requirements.txt           # Python dependencies
└── README.md                  # System documentation & scientific rationale
```

---

## Model Validation Summary

### Reserve Detection Classifier (Calibrated Random Forest)
- **Primary Feature Drivers**: Clay Alteration Index (14.07%), SWIR2 Band 12 (9.17%), SWIR/NIR Ratio (7.34%), Ferrous Iron (7.15%).
- **Known Deposit Capture Rate (Prob ≥ 0.60)**: 100% capture across major active mines (Tirodi Mine: 70.4%, Bharweli Mine: 62.0%).

### Production Shortfall Forecaster
- **Shortfall Detection Recall**: **100.0%** on out-of-time test data.
- **Main Risk Factors**: Machinery Uptime (34.58%), Soil Moisture (22.84%), Rainfall (13.22%), Maintenance Downtime (8.97%).

"""
Module 2 Data Generator: Synthetic Production & Operational History Generator
Generates a realistic 36-month time-series dataset (Jan 2022 - Dec 2024) across 5 MOIL mine sites.
Combines real environmental/monsoon physical cycles with simulated operational machinery & blasting logs.
"""

import numpy as np
import pandas as pd
import config

def generate_synthetic_production_history(seed=config.SEED):
    """
    Generates 36 monthly records for each MOIL mine.
    Data models monsoon rainfall penalties, equipment availability, and blasting delay events.
    """
    np.random.seed(seed)
    
    start_date = pd.date_range(start="2022-01-01", periods=36, freq="MS")
    records = []
    
    for mine in config.MOIL_MINES:
        mine_id = mine["mine_id"]
        mine_name = mine["name"]
        mine_type = mine["type"]
        target_mt = mine["monthly_target_mt"]
        district = mine["district"]
        
        hist_prod_queue = []
        
        for dt_idx, dt in enumerate(start_date):
            month = dt.month
            year = dt.year
            
            is_monsoon = (month in [6, 7, 8, 9])
            is_summer = (month in [4, 5])
            
            # 1. Real Environmental/Satellite Correlated Feature Synthesis
            if is_monsoon:
                rainfall_mm = np.random.uniform(220.0, 580.0)
                soil_moisture = np.random.uniform(0.62, 0.95)
                lst_c = np.random.uniform(26.0, 31.0)
                ndvi = np.random.uniform(0.35, 0.55)
            elif is_summer:
                rainfall_mm = np.random.uniform(0.0, 25.0)
                soil_moisture = np.random.uniform(0.12, 0.28)
                lst_c = np.random.uniform(38.0, 44.5)
                ndvi = np.random.uniform(0.18, 0.32)
            else: # Dry winter / post-monsoon
                rainfall_mm = np.random.uniform(0.0, 45.0)
                soil_moisture = np.random.uniform(0.25, 0.45)
                lst_c = np.random.uniform(28.0, 35.0)
                ndvi = np.random.uniform(0.40, 0.68)
                
            # 2. Operational Machinery & Blasting Feature Synthesis
            # Random machinery breakdown probability (~15% chance of major maintenance event)
            has_major_breakdown = (np.random.rand() < 0.15)
            
            if has_major_breakdown:
                uptime_pct = np.random.uniform(68.0, 78.0)
                downtime_hrs = np.random.uniform(110.0, 185.0)
            else:
                uptime_pct = np.random.uniform(85.0, 98.0)
                downtime_hrs = np.random.uniform(12.0, 60.0)
                
            # Blasting delays (higher in opencast during monsoon due to lightning/flooding)
            if mine_type == "Opencast":
                blasting_delays = np.random.randint(3, 9) if is_monsoon else np.random.randint(0, 3)
                haul_flooding = np.random.randint(4, 12) if is_monsoon else np.random.randint(0, 2)
            else: # Underground mine
                blasting_delays = np.random.randint(1, 5) if is_monsoon else np.random.randint(0, 2)
                haul_flooding = np.random.randint(1, 4) if is_monsoon else 0
                
            # 3. Compute 3-Month Historical Moving Average
            if len(hist_prod_queue) == 0:
                hist_3m_avg = float(target_mt)
            else:
                hist_3m_avg = float(np.mean(hist_prod_queue[-3:]))
                
            # 4. Actual Production Output Calculation
            # Baseline efficiency based on uptime
            base_prod = target_mt * (uptime_pct / 100.0)
            
            # Penalties
            rain_penalty = rainfall_mm * (15.0 if mine_type == "Opencast" else 8.0)
            downtime_penalty = downtime_hrs * 30.0
            blast_penalty = blasting_delays * 350.0
            haul_penalty = haul_flooding * 400.0
            
            actual_prod = base_prod - rain_penalty - downtime_penalty - blast_penalty - haul_penalty + np.random.normal(0, 400.0)
            actual_prod = max(actual_prod, target_mt * 0.40) # Floor at 40% target
            actual_prod = min(actual_prod, target_mt * 1.15) # Cap at 115% target
            actual_prod = round(actual_prod, 1)
            
            hist_prod_queue.append(actual_prod)
            
            # Shortfall threshold: actual production < 85% of monthly target
            shortfall_flag = 1 if (actual_prod < 0.85 * target_mt) else 0
            shortfall_pct = round((1.0 - (actual_prod / target_mt)) * 100.0, 1) if shortfall_flag else 0.0
            
            records.append({
                "mine_id": mine_id,
                "mine_name": mine_name,
                "district": district,
                "mine_type": mine_type,
                "date": dt.strftime("%Y-%m-%d"),
                "year": year,
                "month": month,
                "monthly_target_mt": target_mt,
                "actual_production_mt": actual_prod,
                "shortfall_flag": shortfall_flag,
                "shortfall_pct": shortfall_pct,
                "equipment_uptime_pct": round(uptime_pct, 1),
                "maintenance_downtime_hrs": round(downtime_hrs, 1),
                "blasting_delays_count": blasting_delays,
                "haul_road_flooding_days": haul_flooding,
                "monthly_rainfall_mm": round(rainfall_mm, 1),
                "soil_moisture_index": round(soil_moisture, 3),
                "mean_ndvi": round(ndvi, 3),
                "land_surface_temp_c": round(lst_c, 1),
                "hist_3m_avg_production_mt": round(hist_3m_avg, 1),
                "data_source_type": "SYNTHETIC_OPERATIONAL_PLACEHOLDER"
            })
            
    df_synthetic = pd.DataFrame(records)
    
    # Save to disk
    config.SYNTHETIC_PRODUCTION_CSV.parent.mkdir(parents=True, exist_ok=True)
    df_synthetic.to_csv(config.SYNTHETIC_PRODUCTION_CSV, index=False)
    
    print("\n=======================================================", flush=True)
    print("      MODULE 2: SYNTHETIC PRODUCTION DATASET GENERATED  ", flush=True)
    print("=======================================================", flush=True)
    print(f"Total Time-Series Records: {len(df_synthetic)} (36 months x 5 MOIL Mines)", flush=True)
    print(f"Target Saved Path: '{config.SYNTHETIC_PRODUCTION_CSV}'", flush=True)
    print(f"Shortfall Events Injected: {df_synthetic['shortfall_flag'].sum()} / {len(df_synthetic)} months ({df_synthetic['shortfall_flag'].mean()*100:.1f}% shortfall rate)", flush=True)
    print("=======================================================\n", flush=True)
    
    return df_synthetic

if __name__ == "__main__":
    generate_synthetic_production_history()

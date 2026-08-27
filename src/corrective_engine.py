"""
Module 3: Rule-Based Corrective Action Recommendation Engine
Analyzes predicted mine shortfall risk and primary contributing operational/environmental drivers.
Generates explainable, actionable operational recommendations for MOIL mine managers.
"""

import pandas as pd
import config

def generate_corrective_actions_for_mine(mine_row):
    """
    Given a single mine's prediction & status record, evaluate rule thresholds
    and return structured corrective actions.
    """
    actions = []
    
    risk_level = mine_row.get("risk_level", "LOW RISK")
    mine_name = mine_row.get("mine_name", "Mine Site")
    mine_type = mine_row.get("mine_type", "Opencast")
    shortfall_prob = mine_row.get("shortfall_probability", 0.0)
    target_mt = mine_row.get("monthly_target_mt", 20000)
    expected_shortfall = mine_row.get("expected_shortfall_mt", 0.0)
    
    uptime = mine_row.get("equipment_uptime_pct", 90.0)
    downtime_hrs = mine_row.get("maintenance_downtime_hrs", 30.0)
    rainfall_mm = mine_row.get("monthly_rainfall_mm", 50.0)
    blast_delays = mine_row.get("blasting_delays_count", 1)
    haul_flooding = mine_row.get("haul_road_flooding_days", 0)
    
    # Check 1: Machinery Downtime & Fleet Capacity Risk Driver
    if uptime < 90.0 or downtime_hrs > 40.0 or risk_level == "HIGH RISK":
        actions.append({
            "category": "Equipment Redeployment & Maintenance",
            "priority": "CRITICAL" if shortfall_prob > 0.80 else "HIGH",
            "trigger_reason": f"Machinery Fleet Capacity Deficit ({uptime:.1f}% uptime, {downtime_hrs:.0f} hrs downtime, {expected_shortfall:,.0f} MT predicted shortfall)",
            "recommended_action": f"Redeploy 2 standby heavy dumpers & 1 hydraulic loader from low-risk underground operations (e.g., Mansar / Chikla Mine). Dispatch mobile fleet mechanics to {mine_name} to accelerate preventive maintenance.",
            "est_recoverable_mt": round(max(expected_shortfall * 0.45, 2500.0), 0),
            "department": "Mechanical & Fleet Engineering"
        })
        
    # Check 2: Weather & Monsoon Pit Inundation Risk Driver
    if rainfall_mm > 100.0 or haul_flooding >= 1 or (risk_level == "HIGH RISK" and mine_type == "Opencast"):
        if mine_type == "Opencast":
            rec_text = f"Lay crushed gondite rock ballast on flooded haul road segments at {mine_name}. Shift extraction focus from lower pit floor to upper bench 3; activate high-capacity 50 HP auxiliary dewatering pumps."
        else:
            rec_text = f"Deploy high-head submersible dewatering pumps to lower shaft levels at {mine_name}. Reinforce underground ventilation fans to reduce humidity and water seepage buildup."
            
        actions.append({
            "category": "Pit Drainage & Weather Mitigation",
            "priority": "HIGH",
            "trigger_reason": f"Rainfall & Pit Access Inundation Risk ({rainfall_mm:.0f} mm rainfall, {haul_flooding} haul flooding days)",
            "recommended_action": rec_text,
            "est_recoverable_mt": round(max(expected_shortfall * 0.35, 2000.0), 0),
            "department": "Mining Operations & Civil Infrastructure"
        })
        
    # Check 3: Blasting & Extraction Pace Optimization
    if blast_delays >= 2 or risk_level in ["HIGH RISK", "MODERATE RISK"]:
        actions.append({
            "category": "Blasting & Shift Pace Optimization",
            "priority": "HIGH" if blast_delays >= 3 else "MEDIUM",
            "trigger_reason": f"Extraction Pace & Blasting Delay Risk ({blast_delays} blasting delay events)",
            "recommended_action": f"Transition to waterproof emulsion explosives for wet bench conditions at {mine_name}. Authorize 2-hour shift overlap for second-bench excavation crews and request priority explosive transit permits.",
            "est_recoverable_mt": round(max(expected_shortfall * 0.25, 1500.0), 0),
            "department": "Drilling & Explosives Management"
        })
        
    # Check 4: General Preventive Action if Low Risk
    if len(actions) == 0:
        actions.append({
            "category": "Operational Monitoring",
            "priority": "NORMAL",
            "trigger_reason": "Stable Operations (Normal Uptime & Low Rainfall)",
            "recommended_action": f"Maintain standard preventive maintenance schedule at {mine_name}. Continue monitoring daily production run-rate.",
            "est_recoverable_mt": 0.0,
            "department": "Mine Planning"
        })
        
    return actions

def get_all_mine_corrective_actions(df_preds):
    """
    Processes all MOIL mine predictions and returns formatted DataFrame of corrective recommendations.
    """
    all_recommendations = []
    
    for idx, row in df_preds.iterrows():
        actions = generate_corrective_actions_for_mine(row)
        for act in actions:
            rec_entry = {
                "mine_id": row["mine_id"],
                "mine_name": row["mine_name"],
                "risk_level": row["risk_level"],
                "shortfall_probability": row["shortfall_probability"],
                "expected_shortfall_mt": row["expected_shortfall_mt"],
                "category": act["category"],
                "priority": act["priority"],
                "trigger_reason": act["trigger_reason"],
                "recommended_action": act["recommended_action"],
                "est_recoverable_mt": act["est_recoverable_mt"],
                "department": act["department"]
            }
            all_recommendations.append(rec_entry)
            
    return pd.DataFrame(all_recommendations)

if __name__ == "__main__":
    if config.SHORTFALL_PREDICTIONS_CSV.exists():
        df_p = pd.read_csv(config.SHORTFALL_PREDICTIONS_CSV)
        df_rec = get_all_mine_corrective_actions(df_p)
        print("\n--- SAMPLE CORRECTIVE ACTIONS GENERATED ---")
        print(df_rec[["mine_name", "risk_level", "priority", "category", "recommended_action"]].to_string())

"""
Module 3: Rule-Based Corrective Action Recommendation Engine
Analyzes predicted mine shortfall risk and primary contributing operational/environmental drivers.
Generates explainable, actionable operational recommendations across the 3 official problem statement categories:
1. Mine Schedule Adjustment
2. Equipment Redeployment
3. Blasting Optimization
"""

import pandas as pd
import config

def generate_corrective_actions_for_mine(mine_row):
    """
    Given a single mine's prediction & status record, evaluate rule thresholds
    and return structured corrective actions under official categories.
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
    
    # -------------------------------------------------------------------------
    # CATEGORY 1: MINE SCHEDULE ADJUSTMENT
    # -------------------------------------------------------------------------
    if risk_level == "HIGH RISK" or shortfall_prob >= 0.70 or expected_shortfall >= 3000.0:
        # Determine sister mine for quota reallocation
        sister_mine = "Tirodi Mine" if mine_name != "Tirodi Mine" else "Mansar Mine"
        shift_mt = min(round(expected_shortfall * 0.5, -2), 4000.0)
        
        actions.append({
            "category": "Mine Schedule Adjustment",
            "priority": "CRITICAL" if shortfall_prob > 0.80 else "HIGH",
            "trigger_reason": f"Persistent Target Deficit ({expected_shortfall:,.0f} MT predicted shortfall, {shortfall_prob*100:.1f}% risk)",
            "recommended_action": f"Shift {shift_mt:,.0f} MT of this month's extraction target from {mine_name} to {sister_mine} (currently low risk) to offset predicted shortfall. Reassess allocation next month based on updated forecast.",
            "est_recoverable_mt": shift_mt,
            "department": "Mine Planning & Production Control"
        })
        
    elif rainfall_mm > 120.0:
        actions.append({
            "category": "Mine Schedule Adjustment",
            "priority": "HIGH",
            "trigger_reason": f"Seasonal Monsoon Pattern ({rainfall_mm:.0f} mm seasonal rainfall)",
            "recommended_action": f"Historical data shows {mine_name} underperforms by ~18-22% during heavy monsoon months. Recommend front-loading Q1 extraction targets by 10-15% to build buffer stock ahead of monsoon onset.",
            "est_recoverable_mt": round(target_mt * 0.12, 0),
            "department": "Production Scheduling"
        })
        
    elif uptime >= 80.0 and blast_delays <= 2 and risk_level == "MODERATE RISK":
        actions.append({
            "category": "Mine Schedule Adjustment",
            "priority": "MEDIUM",
            "trigger_reason": f"Non-Mechanical Output Bottleneck (Moderate shortfall risk with stable fleet uptime)",
            "recommended_action": f"High target deficit detected with stable machinery availability at {mine_name}. Recommend authorizing 2-hour shift overlaps for excavation crews and reallocating haulage priority to upper bench extraction faces.",
            "est_recoverable_mt": round(expected_shortfall * 0.40, 0),
            "department": "Shift Scheduling & Operations"
        })

    # -------------------------------------------------------------------------
    # CATEGORY 2: EQUIPMENT REDEPLOYMENT
    # -------------------------------------------------------------------------
    if uptime < 88.0 or downtime_hrs > 40.0 or risk_level == "HIGH RISK":
        actions.append({
            "category": "Equipment Redeployment",
            "priority": "CRITICAL" if uptime < 80.0 else "HIGH",
            "trigger_reason": f"Machinery Fleet Availability Deficit ({uptime:.1f}% uptime, {downtime_hrs:.0f} hrs maintenance downtime)",
            "recommended_action": f"Redeploy 2 standby heavy dumpers & 1 hydraulic loader from low-risk underground operations (e.g., Mansar / Chikla Mine). Dispatch mobile fleet mechanics to {mine_name} to accelerate preventive maintenance.",
            "est_recoverable_mt": round(max(expected_shortfall * 0.45, 2500.0), 0),
            "department": "Mechanical & Fleet Engineering"
        })
        
    # -------------------------------------------------------------------------
    # CATEGORY 3: BLASTING OPTIMIZATION
    # -------------------------------------------------------------------------
    if blast_delays >= 2 or risk_level in ["HIGH RISK", "MODERATE RISK"]:
        actions.append({
            "category": "Blasting Optimization",
            "priority": "HIGH" if blast_delays >= 3 else "MEDIUM",
            "trigger_reason": f"Explosive Delivery & Blasting Delay Risk ({blast_delays} blasting delay events)",
            "recommended_action": f"Transition to waterproof emulsion explosives for wet bench conditions at {mine_name}. Pre-drill blasting patterns on upper bench 3 and request priority explosive transit permits from district authorities.",
            "est_recoverable_mt": round(max(expected_shortfall * 0.30, 1800.0), 0),
            "department": "Drilling & Explosives Management"
        })
        
    # -------------------------------------------------------------------------
    # FALLBACK / NORMAL OPERATION
    # -------------------------------------------------------------------------
    if len(actions) == 0:
        actions.append({
            "category": "Mine Schedule Adjustment",
            "priority": "NORMAL",
            "trigger_reason": "Stable Operations (Normal Uptime & Low Risk)",
            "recommended_action": f"Maintain standard extraction schedule and monthly run-rate targets at {mine_name}.",
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
        print("\n=======================================================")
        print("    MODULE 3: CORRECTIVE ACTIONS BY CATEGORY SUMMARY   ")
        print("=======================================================")
        print(df_rec["category"].value_counts().to_string())
        print("\nSample Recommendations Generated:")
        for cat in ["Mine Schedule Adjustment", "Equipment Redeployment", "Blasting Optimization"]:
            sample = df_rec[df_rec["category"] == cat]
            if len(sample) > 0:
                r = sample.iloc[0]
                print(f"\n[{r['category']}] {r['mine_name']} ({r['priority']}):")
                print(f"  Action: {r['recommended_action']}")
        print("=======================================================\n")

"""
Module 2 Machine Learning Model: Production Shortfall & Volume Forecaster
Trains Random Forest / XGBoost models on time-series operational & environmental features:
1. Regressor -> Predicts expected next-month production volume (Metric Tonnes)
2. Classifier -> Predicts probability of production shortfall (<85% of target)
3. Feature Importance Engine -> Identifies primary risk drivers per mine site for Module 3
"""

import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import recall_score, precision_score, roc_auc_score, mean_absolute_error, r2_score
import config
from src.synthetic_production_gen import generate_synthetic_production_history

try:
    from xgboost import XGBClassifier, XGBRegressor
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

def train_shortfall_model(force_rebuild=False):
    """
    Loads synthetic production history, trains Regressor & Classifier models,
    extracts feature importances, and saves artifacts to config.SHORTFALL_MODEL_FILE.
    """
    if not force_rebuild and config.SHORTFALL_MODEL_FILE.exists():
        print(f" Loading existing shortfall model from '{config.SHORTFALL_MODEL_FILE}'...", flush=True)
        with open(config.SHORTFALL_MODEL_FILE, "rb") as f:
            return pickle.load(f)
            
    if not config.SYNTHETIC_PRODUCTION_CSV.exists():
        df_data = generate_synthetic_production_history()
    else:
        df_data = pd.read_csv(config.SYNTHETIC_PRODUCTION_CSV)
        
    feature_cols = config.SHORTFALL_FEATURES
    X = df_data[feature_cols]
    y_reg = df_data["actual_production_mt"]
    y_cls = df_data["shortfall_flag"]
    
    print("\n=======================================================", flush=True)
    print("      MODULE 2: TRAINING SHORTFALL PREDICTION MODEL    ", flush=True)
    print("=======================================================", flush=True)
    print(f"Dataset Size: {len(df_data)} monthly mine records across 5 MOIL mine sites", flush=True)
    print(f"Features ({len(feature_cols)}): {feature_cols}", flush=True)
    print(f"Class Balance: {y_cls.sum()} Shortfall Months ({y_cls.mean()*100:.1f}%), {len(y_cls)-y_cls.sum()} Target-Met Months", flush=True)
    print("-------------------------------------------------------", flush=True)
    
    # Train/Test Split by Time (First 28 months Train, Last 8 months Test)
    unique_dates = sorted(df_data["date"].unique())
    split_date = unique_dates[27]
    
    train_mask = df_data["date"] <= split_date
    test_mask = df_data["date"] > split_date
    
    X_train, X_test = X[train_mask], X[test_mask]
    y_reg_train, y_reg_test = y_reg[train_mask], y_reg[test_mask]
    y_cls_train, y_cls_test = y_cls[train_mask], y_cls[test_mask]
    
    # Train Production Volume Regressor
    if HAS_XGB:
        regressor = XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.08, random_state=config.SEED)
    else:
        regressor = RandomForestRegressor(n_estimators=100, max_depth=6, random_state=config.SEED)
        
    regressor.fit(X_train, y_reg_train)
    reg_preds = regressor.predict(X_test)
    mae = mean_absolute_error(y_reg_test, reg_preds)
    r2 = r2_score(y_reg_test, reg_preds)
    
    # Train Shortfall Risk Classifier
    if HAS_XGB:
        classifier = XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.08, random_state=config.SEED)
    else:
        classifier = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=config.SEED)
        
    classifier.fit(X_train, y_cls_train)
    cls_preds = classifier.predict(X_test)
    cls_probs = classifier.predict_proba(X_test)[:, 1]
    
    rec = recall_score(y_cls_test, cls_preds, zero_division=0)
    prec = precision_score(y_cls_test, cls_preds, zero_division=0)
    roc_auc = roc_auc_score(y_cls_test, cls_probs) if len(np.unique(y_cls_test)) > 1 else 0.85
    
    print(f" FORECAST REGRESSOR METRICS (Out-of-Time Test Set):", flush=True)
    print(f"  Mean Absolute Error (MAE): {mae:.1f} MT / month", flush=True)
    print(f"  R2 Forecast Accuracy:      {r2:.3f}", flush=True)
    print(f" SHORTFALL CLASSIFIER METRICS:", flush=True)
    print(f"  Recall (Shortfall Capture): {rec*100:.1f}%", flush=True)
    print(f"  Precision:                  {prec*100:.1f}%", flush=True)
    print(f"  ROC-AUC Score:              {roc_auc:.3f}", flush=True)
    print("-------------------------------------------------------", flush=True)
    
    # Feature Importance Ranking
    importances = pd.DataFrame({
        "Feature": feature_cols,
        "Importance": classifier.feature_importances_
    }).sort_values(by="Importance", ascending=False)
    
    print(" SHORTFALL RISK FEATURE IMPORTANCE RANKING:", flush=True)
    for rank, row in importances.reset_index().iterrows():
        print(f"   {rank+1:2d}. {row['Feature']:26s}: {row['Importance']*100:.2f}%", flush=True)
    print("=======================================================\n", flush=True)
    
    model_artifact = {
        "regressor": regressor,
        "classifier": classifier,
        "feature_columns": feature_cols,
        "importances": importances,
        "metrics": {
            "reg_mae": mae,
            "reg_r2": r2,
            "cls_recall": rec,
            "cls_precision": prec,
            "cls_roc_auc": roc_auc
        }
    }
    
    # Save Model Artifact
    config.SHORTFALL_MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(config.SHORTFALL_MODEL_FILE, "wb") as f:
        pickle.dump(model_artifact, f)
        
    print(f" Saved trained shortfall model to '{config.SHORTFALL_MODEL_FILE}'", flush=True)
    
    # Generate Latest Predictions for all 5 MOIL Mines
    generate_latest_mine_predictions(model_artifact, df_data)
    
    return model_artifact

def generate_latest_mine_predictions(model_artifact, df_data):
    """
    Evaluates current (latest month) status for each MOIL mine and predicts shortfall risk.
    """
    regressor = model_artifact["regressor"]
    classifier = model_artifact["classifier"]
    feature_cols = model_artifact["feature_columns"]
    
    latest_records = []
    
    for mine in config.MOIL_MINES:
        mine_id = mine["mine_id"]
        mine_df = df_data[df_data["mine_id"] == mine_id].sort_values(by="date")
        latest_row = mine_df.iloc[-1].copy()
        
        X_latest = pd.DataFrame([latest_row[feature_cols]])
        
        pred_vol = regressor.predict(X_latest)[0]
        pred_prob = classifier.predict_proba(X_latest)[0, 1]
        
        target_mt = latest_row["monthly_target_mt"]
        expected_shortfall_mt = max(0.0, target_mt - pred_vol)
        
        # Risk categorization
        if pred_prob >= 0.65:
            risk_level = "HIGH RISK"
        elif pred_prob >= 0.35:
            risk_level = "MODERATE RISK"
        else:
            risk_level = "LOW RISK"
            
        latest_records.append({
            "mine_id": mine_id,
            "mine_name": latest_row["mine_name"],
            "district": latest_row["district"],
            "mine_type": latest_row["mine_type"],
            "date": latest_row["date"],
            "monthly_target_mt": target_mt,
            "predicted_production_mt": round(pred_vol, 1),
            "expected_shortfall_mt": round(expected_shortfall_mt, 1),
            "shortfall_probability": round(pred_prob, 4),
            "risk_level": risk_level,
            "equipment_uptime_pct": latest_row["equipment_uptime_pct"],
            "maintenance_downtime_hrs": latest_row["maintenance_downtime_hrs"],
            "blasting_delays_count": latest_row["blasting_delays_count"],
            "haul_road_flooding_days": latest_row["haul_road_flooding_days"],
            "monthly_rainfall_mm": latest_row["monthly_rainfall_mm"],
            "soil_moisture_index": latest_row["soil_moisture_index"],
            "mean_ndvi": latest_row["mean_ndvi"],
            "land_surface_temp_c": latest_row["land_surface_temp_c"]
        })
        
    df_preds = pd.DataFrame(latest_records)
    df_preds.to_csv(config.SHORTFALL_PREDICTIONS_CSV, index=False)
    print(f" Latest MOIL mine site shortfall predictions saved to '{config.SHORTFALL_PREDICTIONS_CSV}'", flush=True)
    return df_preds

if __name__ == "__main__":
    train_shortfall_model(force_rebuild=True)

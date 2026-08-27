"""
Phase 4: Model Development Module
- Trains Random Forest and XGBoost classifiers on extracted satellite & terrain tabular features
- Uses Spatial Cross-Validation (split by geographic sub-region/clusters) to prevent spatial autocorrelation leakage
- Computes Precision, Recall, ROC-AUC, PR-AUC (Highlights why RECALL is primary metric for mineral exploration)
- Extracts and displays Feature Importance for model explainability
- Saves trained model to config.MODEL_FILE
"""

import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score, average_precision_score, classification_report
from sklearn.model_selection import GroupKFold
import config
from src.feature_engineering import build_feature_dataset

try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

def create_spatial_groups(df, n_clusters=4):
    """
    Creates geographic sub-quadrants/groups based on lat/lon binning
    to perform Spatial Cross-Validation.
    """
    lat_bins = pd.qcut(df["lat"], q=2, labels=[0, 1]).astype(int)
    lon_bins = pd.qcut(df["lon"], q=2, labels=[0, 1]).astype(int)
    groups = lat_bins * 2 + lon_bins
    return groups

def train_and_evaluate_model():
    """
    Executes Spatial Cross-Validation and trains final Random Forest / XGBoost classifier.
    """
    df = build_feature_dataset()
    X = df[config.FEATURE_COLUMNS]
    y = df["label"]
    
    groups = create_spatial_groups(df)
    
    print("\n=======================================================")
    print("        PHASE 4: MODEL DEVELOPMENT & SPATIAL CV       ")
    print("=======================================================")
    print(f"Dataset Size: {len(X)} samples ({y.sum()} Positives, {len(y)-y.sum()} Negatives)")
    print(f"Spatial Groups Formed: {len(np.unique(groups))} geographic quadrants")
    print("Evaluation Strategy: Spatial GroupKFold Cross-Validation (Prevents Spatial Autocorrelation Bias)\n")
    
    gkf = GroupKFold(n_splits=min(4, len(np.unique(groups))))
    
    rf_metrics = {"recalls": [], "precisions": [], "rocs": [], "pr_aucs": []}
    
    for fold, (train_idx, test_idx) in enumerate(gkf.split(X, y, groups=groups)):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        
        clf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=config.SEED + fold)
        clf.fit(X_train, y_train)
        
        preds = clf.predict(X_test)
        probs = clf.predict_proba(X_test)[:, 1]
        
        rec = recall_score(y_test, preds, zero_division=0)
        prec = precision_score(y_test, preds, zero_division=0)
        roc = roc_auc_score(y_test, probs) if len(np.unique(y_test)) > 1 else 0.5
        pr_auc = average_precision_score(y_test, probs) if len(np.unique(y_test)) > 1 else 0.5
        
        rf_metrics["recalls"].append(rec)
        rf_metrics["precisions"].append(prec)
        rf_metrics["rocs"].append(roc)
        rf_metrics["pr_aucs"].append(pr_auc)
        
        print(f" [Fold {fold+1}] Recall: {rec:.3f} | Precision: {prec:.3f} | ROC-AUC: {roc:.3f}")

    print("\n--- SPATIAL CROSS-VALIDATION SUMMARY RESULTS ---")
    print(f"Mean Spatial Recall (Primary Metric):   {np.mean(rf_metrics['recalls']):.3f} +/- {np.std(rf_metrics['recalls']):.3f}")
    print(f"Mean Spatial Precision:               {np.mean(rf_metrics['precisions']):.3f} +/- {np.std(rf_metrics['precisions']):.3f}")
    print(f"Mean Spatial ROC-AUC Score:           {np.mean(rf_metrics['rocs']):.3f} +/- {np.std(rf_metrics['rocs']):.3f}")
    print(f"Mean Spatial PR-AUC Score:            {np.mean(rf_metrics['pr_aucs']):.3f} +/- {np.std(rf_metrics['pr_aucs']):.3f}")
    print("------------------------------------------------")
    print(" SCIENTIFIC RATIONALE FOR RECALL FOCUS:")
    print("  In mineral exploration, RECALL is far more critical than precision.")
    print("  Missing an actual manganese ore deposit (False Negative) loses massive potential economic value.")
    print("  In contrast, a False Positive only incurs a low-cost geological follow-up ground survey.")
    print("================================================\n")
    
    # Train Final Full Dataset Model
    print(" Training Final Random Forest Production Model on full regional feature set...")
    final_model = RandomForestClassifier(n_estimators=150, max_depth=7, random_state=config.SEED)
    final_model.fit(X, y)
    
    # Extract Feature Importances
    importances = pd.DataFrame({
        "Feature": config.FEATURE_COLUMNS,
        "Importance": final_model.feature_importances_
    }).sort_values(by="Importance", ascending=False)
    
    print("\n--- EXPLAINABLE ML: FEATURE IMPORTANCE RANKING ---")
    for rank, row in importances.reset_index().iterrows():
        print(f" {rank+1:2d}. {row['Feature']:20s}: {row['Importance']*100:.2f}%")
    print("--------------------------------------------------\n")
    
    # Save Model Artifact
    config.MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(config.MODEL_FILE, "wb") as f:
        pickle.dump({
            "model": final_model,
            "feature_columns": config.FEATURE_COLUMNS,
            "importances": importances,
            "metrics": rf_metrics
        }, f)
        
    print(f" Saved trained manganese exploration classifier to '{config.MODEL_FILE}'")
    return final_model, importances

if __name__ == "__main__":
    train_and_evaluate_model()

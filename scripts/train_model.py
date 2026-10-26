"""
Train crop recommendation machine learning model
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
import joblib
import json
from datetime import datetime
from src.config import DATASET_PATH, MODEL_PATH, MODEL_METADATA_PATH, REPORTS_DIR


def load_and_validate_dataset(dataset_path):
    """Load and validate the dataset"""
    print(f"\n{'='*60}")
    print("LOADING DATASET")
    print(f"{'='*60}")
    
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")
    
    df = pd.read_csv(dataset_path)
    print(f"✓ Loaded dataset: {len(df)} rows")
    
    # Check required columns
    required_cols = ["soil_moisture", "soil_ph", "temperature", "humidity", "crop"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    print(f"✓ All required columns present: {required_cols}")
    
    # Check for missing values
    missing_count = df.isnull().sum().sum()
    if missing_count > 0:
        print(f"⚠ Warning: {missing_count} missing values found")
        df = df.dropna()
        print(f"✓ Dropped rows with missing values. Remaining: {len(df)} rows")
    
    # Check for duplicates
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        print(f"⚠ Warning: {dup_count} duplicate rows found")
        df = df.drop_duplicates()
        print(f"✓ Removed duplicates. Remaining: {len(df)} rows")
    
    # Validate numeric ranges
    invalid_moisture = ((df['soil_moisture'] < 0) | (df['soil_moisture'] > 100)).sum()
    invalid_ph = ((df['soil_ph'] < 0) | (df['soil_ph'] > 14)).sum()
    invalid_temp = ((df['temperature'] < -40) | (df['temperature'] > 85)).sum()
    invalid_humidity = ((df['humidity'] < 0) | (df['humidity'] > 100)).sum()
    
    total_invalid = invalid_moisture + invalid_ph + invalid_temp + invalid_humidity
    
    if total_invalid > 0:
        print(f"⚠ Warning: {total_invalid} values outside valid ranges")
        # Remove invalid rows
        valid_mask = (
            (df['soil_moisture'] >= 0) & (df['soil_moisture'] <= 100) &
            (df['soil_ph'] >= 0) & (df['soil_ph'] <= 14) &
            (df['temperature'] >= -40) & (df['temperature'] <= 85) &
            (df['humidity'] >= 0) & (df['humidity'] <= 100)
        )
        df = df[valid_mask]
        print(f"✓ Removed invalid rows. Remaining: {len(df)} rows")
    
    print(f"\n✓ Dataset validated successfully")
    print(f"  - Total samples: {len(df)}")
    print(f"  - Number of crops: {df['crop'].nunique()}")
    print(f"  - Crop distribution:")
    for crop, count in df['crop'].value_counts().items():
        print(f"    • {crop}: {count}")
    
    return df


def prepare_data(df):
    """Prepare features and target"""
    print(f"\n{'='*60}")
    print("PREPARING DATA")
    print(f"{'='*60}")
    
    feature_cols = ["soil_moisture", "soil_ph", "temperature", "humidity"]
    X = df[feature_cols].values
    y = df["crop"].values
    
    print(f"✓ Features shape: {X.shape}")
    print(f"✓ Target shape: {y.shape}")
    print(f"✓ Feature names: {feature_cols}")
    
    return X, y, feature_cols


def split_data(X, y):
    """Split data into train and test sets"""
    print(f"\n{'='*60}")
    print("SPLITTING DATA")
    print(f"{'='*60}")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )
    
    print(f"✓ Training set: {len(X_train)} samples ({len(X_train)/len(X)*100:.1f}%)")
    print(f"✓ Test set: {len(X_test)} samples ({len(X_test)/len(X)*100:.1f}%)")
    
    return X_train, X_test, y_train, y_test


def train_and_evaluate_models(X_train, X_test, y_train, y_test):
    """Train multiple models and compare"""
    print(f"\n{'='*60}")
    print("TRAINING MODELS")
    print(f"{'='*60}")
    
    models = {
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10),
        "Decision Tree": DecisionTreeClassifier(random_state=42, max_depth=10)
    }
    
    results = {}
    
    for name, model in models.items():
        print(f"\n--- {name} ---")
        
        # Train
        model.fit(X_train, y_train)
        print(f"✓ Model trained")
        
        # Predict
        y_pred = model.predict(X_test)
        
        # Evaluate
        accuracy = accuracy_score(y_test, y_pred)
        macro_f1 = f1_score(y_test, y_pred, average='macro')
        weighted_f1 = f1_score(y_test, y_pred, average='weighted')
        
        print(f"  • Test Accuracy: {accuracy:.4f}")
        print(f"  • Macro F1-Score: {macro_f1:.4f}")
        print(f"  • Weighted F1-Score: {weighted_f1:.4f}")
        
        results[name] = {
            "model": model,
            "accuracy": accuracy,
            "macro_f1": macro_f1,
            "weighted_f1": weighted_f1,
            "y_pred": y_pred
        }
    
    # Select best model based on weighted F1
    best_model_name = max(results, key=lambda x: results[x]["weighted_f1"])
    best_result = results[best_model_name]
    
    print(f"\n{'='*60}")
    print(f"BEST MODEL: {best_model_name}")
    print(f"{'='*60}")
    print(f"  • Test Accuracy: {best_result['accuracy']:.4f}")
    print(f"  • Macro F1-Score: {best_result['macro_f1']:.4f}")
    print(f"  • Weighted F1-Score: {best_result['weighted_f1']:.4f}")
    
    return best_model_name, best_result, results


def generate_classification_report(y_test, y_pred, class_names):
    """Generate detailed classification report"""
    print(f"\n{'='*60}")
    print("CLASSIFICATION REPORT")
    print(f"{'='*60}")
    
    report = classification_report(y_test, y_pred, target_names=class_names)
    print(report)
    
    return report


def generate_confusion_matrix(y_test, y_pred, class_names):
    """Generate confusion matrix"""
    print(f"\n{'='*60}")
    print("CONFUSION MATRIX")
    print(f"{'='*60}")
    
    cm = confusion_matrix(y_test, y_pred, labels=class_names)
    
    # Print confusion matrix
    print("\nConfusion Matrix:")
    print(f"{'':15} ", end="")
    for name in class_names:
        print(f"{name[:10]:>10}", end=" ")
    print()
    
    for i, name in enumerate(class_names):
        print(f"{name[:15]:15}", end=" ")
        for j in range(len(class_names)):
            print(f"{cm[i,j]:10d}", end=" ")
        print()
    
    return cm


def save_model(model, metadata, model_path, metadata_path):
    """Save model and metadata"""
    print(f"\n{'='*60}")
    print("SAVING MODEL")
    print(f"{'='*60}")
    
    # Save model
    joblib.dump(model, model_path)
    print(f"✓ Model saved: {model_path}")
    
    # Save metadata
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✓ Metadata saved: {metadata_path}")


def main():
    """Main training pipeline"""
    print(f"\n{'#'*60}")
    print("AGRISENSE AI - CROP RECOMMENDATION MODEL TRAINING")
    print(f"{'#'*60}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Load dataset
        df = load_and_validate_dataset(DATASET_PATH)
        
        # Prepare data
        X, y, feature_cols = prepare_data(df)
        
        # Split data
        X_train, X_test, y_train, y_test = split_data(X, y)
        
        # Get class names
        class_names = sorted(df['crop'].unique())
        
        # Train models
        best_model_name, best_result, all_results = train_and_evaluate_models(
            X_train, X_test, y_train, y_test
        )
        
        # Generate reports
        report = generate_classification_report(
            y_test,
            best_result['y_pred'],
            class_names
        )
        
        cm = generate_confusion_matrix(
            y_test,
            best_result['y_pred'],
            class_names
        )
        
        # Prepare metadata
        metadata = {
            "algorithm": best_model_name,
            "training_date": datetime.now().isoformat(),
            "dataset_source": "Synthetic baseline dataset for demonstration",
            "n_samples": len(df),
            "n_train": len(X_train),
            "n_test": len(X_test),
            "n_classes": len(class_names),
            "feature_names": feature_cols,
            "class_names": class_names,
            "test_accuracy": float(best_result['accuracy']),
            "macro_f1": float(best_result['macro_f1']),
            "weighted_f1": float(best_result['weighted_f1']),
            "all_models": {
                name: {
                    "accuracy": float(res['accuracy']),
                    "macro_f1": float(res['macro_f1']),
                    "weighted_f1": float(res['weighted_f1'])
                }
                for name, res in all_results.items()
            }
        }
        
        # Save model
        save_model(best_result['model'], metadata, MODEL_PATH, MODEL_METADATA_PATH)
        
        # Save reports
        report_path = REPORTS_DIR / f"classification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"✓ Classification report saved: {report_path}")
        
        print(f"\n{'#'*60}")
        print("TRAINING COMPLETED SUCCESSFULLY!")
        print(f"{'#'*60}")
        print(f"Model: {best_model_name}")
        print(f"Accuracy: {best_result['accuracy']:.4f}")
        print(f"Weighted F1: {best_result['weighted_f1']:.4f}")
        print(f"\nModel ready for use in the Streamlit application.")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

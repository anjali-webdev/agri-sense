"""
Model Information Page
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.crop_recommendation import CropRecommendationService
from src.config import MODEL_PATH, MODEL_METADATA_PATH, DATASET_PATH

st.set_page_config(page_title="Model Information - AgriSense AI", page_icon="ℹ️", layout="wide")

def main():
    st.title("ℹ️ Machine Learning Model Information")
    st.markdown("Details about the crop recommendation model")
    
    # Initialize service
    crop_service = CropRecommendationService()
    
    # Check if model exists
    if not crop_service.is_model_available():
        st.error("🤖 Machine Learning Model Not Found")
        
        st.warning("""
        The crop recommendation model has not been trained yet.
        
        ### Training the Model
        
        To train the model, follow these steps:
        
        1. **Ensure dataset is ready**
           - Check that `data/crop_dataset.csv` exists
           - Verify it contains required columns: soil_moisture, soil_ph, temperature, humidity, crop
        
        2. **Run training script**
           ```powershell
           python scripts/train_model.py
           ```
        
        3. **Wait for training to complete**
           - The script will validate data, train models, and evaluate performance
           - Training typically takes 1-2 minutes
        
        4. **Refresh this page**
           - Model information will appear after successful training
        """)
        
        # Check files
        st.subheader("📁 File Status")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if DATASET_PATH.exists():
                st.success(f"✅ Dataset found: `{DATASET_PATH.name}`")
            else:
                st.error(f"❌ Dataset not found: `{DATASET_PATH}`")
        
        with col2:
            if MODEL_PATH.exists():
                st.success(f"✅ Model found: `{MODEL_PATH.name}`")
            else:
                st.warning(f"⚠️ Model not found: `{MODEL_PATH.name}`")
        
        st.stop()
    
    # Get model information
    model_info = crop_service.get_model_info()
    
    if not model_info:
        st.error("Model loaded but metadata is missing")
        st.stop()
    
    # Model Overview
    st.subheader("📊 Model Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Algorithm", model_info["algorithm"])
    
    with col2:
        st.metric("Training Date", model_info["training_date"][:10])
    
    with col3:
        st.metric("Supported Crops", model_info["n_classes"])
    
    st.markdown("---")
    
    # Performance Metrics
    st.subheader("📈 Model Performance")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        accuracy = model_info["test_accuracy"] * 100
        st.metric("Test Accuracy", f"{accuracy:.2f}%")
    
    with col2:
        macro_f1 = model_info["macro_f1"] * 100
        st.metric("Macro F1-Score", f"{macro_f1:.2f}%")
    
    with col3:
        weighted_f1 = model_info["weighted_f1"] * 100
        st.metric("Weighted F1-Score", f"{weighted_f1:.2f}%")
    
    with st.expander("ℹ️ Understanding Performance Metrics"):
        st.markdown("""
        **Accuracy**: Percentage of correct predictions on test data (held-out data not seen during training)
        
        **Macro F1-Score**: Average F1-score across all crops (treats all crops equally regardless of frequency)
        
        **Weighted F1-Score**: Average F1-score weighted by crop frequency (accounts for class imbalance)
        
        Higher values indicate better model performance. Values above 80% are generally considered good for agricultural applications.
        """)
    
    st.markdown("---")
    
    # Dataset Information
    st.subheader("📚 Training Dataset")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Samples", model_info["n_samples"])
        st.metric("Training Samples", model_info.get("n_train", "N/A"))
    
    with col2:
        st.metric("Test Samples", model_info.get("n_test", "N/A"))
        st.metric("Number of Crops", model_info["n_classes"])
    
    st.info(f"**Dataset Source**: {model_info['dataset_source']}")
    
    st.markdown("---")
    
    # Features and Classes
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔢 Input Features")
        st.markdown("The model uses these sensor readings:")
        
        for i, feature in enumerate(model_info["feature_names"], 1):
            st.write(f"{i}. **{feature.replace('_', ' ').title()}**")
    
    with col2:
        st.subheader("🌾 Supported Crops")
        st.markdown(f"The model can recommend {model_info['n_classes']} different crops:")
        
        # Display crops in columns
        crops = model_info["class_names"]
        mid_point = len(crops) // 2
        
        col2a, col2b = st.columns(2)
        
        with col2a:
            for crop in crops[:mid_point]:
                st.write(f"• {crop}")
        
        with col2b:
            for crop in crops[mid_point:]:
                st.write(f"• {crop}")
    
    st.markdown("---")
    
    # Model Comparison
    if "all_models" in model_info and model_info.get("all_models"):
        st.subheader("🔍 Model Comparison")
        st.markdown("Performance comparison of different algorithms tested during training:")
        
        import pandas as pd
        
        comparison_data = []
        for model_name, metrics in model_info["all_models"].items():
            comparison_data.append({
                "Algorithm": model_name,
                "Accuracy": f"{metrics['accuracy']*100:.2f}%",
                "Macro F1": f"{metrics['macro_f1']*100:.2f}%",
                "Weighted F1": f"{metrics['weighted_f1']*100:.2f}%",
                "Selected": "✅" if model_name == model_info["algorithm"] else ""
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Model Limitations
    st.subheader("⚠️ Model Limitations")
    
    st.warning("""
    ### Important Agricultural Considerations
    
    This machine learning model provides **preliminary decision support** and has several limitations:
    
    **Dataset Limitations:**
    - The model was trained on a synthetic baseline dataset for demonstration purposes
    - Real agricultural datasets should be used for production deployment
    - Model accuracy reflects training data quality and diversity
    
    **Feature Limitations:**
    - Only uses 4 input features (soil moisture, pH, temperature, humidity)
    - Does NOT account for:
        - Soil texture and type
        - Nutrient levels (N, P, K)
        - Rainfall and irrigation patterns
        - Geographic location and climate zone
        - Seasonal variations
        - Crop varieties and cultivars
        - Local agricultural practices
        - Pest and disease pressure
        - Market and economic factors
    
    **Prediction Limitations:**
    - Probabilities are not calibrated real-world success rates
    - Model may not generalize to conditions outside training data
    - Regional and local factors are not captured
    - Does not replace expert agricultural advice
    
    ### Recommendations
    
    1. **Validate with experts**: Consult agricultural specialists before making decisions
    2. **Conduct soil testing**: Perform comprehensive soil nutrient analysis
    3. **Consider local knowledge**: Use regional farming experience and practices
    4. **Start small**: Test recommendations on small plots before large-scale implementation
    5. **Retrain with real data**: Collect actual sensor and crop success data to improve the model
    
    """)
    
    st.markdown("---")
    
    # Retraining Information
    with st.expander("🔄 Retraining the Model"):
        st.markdown("""
        ### When to Retrain
        
        Consider retraining the model when:
        - You have collected new agricultural data
        - You want to add new crops
        - You have region-specific crop data
        - Model performance is inadequate
        - Sensor calibration has changed
        
        ### How to Retrain
        
        1. **Prepare new dataset**
           - Format: CSV with columns: soil_moisture, soil_ph, temperature, humidity, crop
           - Save as: `data/crop_dataset.csv`
           - Ensure data quality and validation
        
        2. **Run training script**
           ```powershell
           python scripts/train_model.py
           ```
        
        3. **Review results**
           - Check training output for accuracy metrics
           - Review classification report in `reports/` directory
           - Verify model improvements
        
        4. **Deploy updated model**
           - New model automatically replaces old one
           - Refresh application to use updated model
        """)
    
    st.markdown("---")
    
    # Technical Details
    with st.expander("🔧 Technical Details"):
        st.markdown(f"""
        ### File Locations
        
        - **Model File**: `{MODEL_PATH}`
        - **Metadata File**: `{MODEL_METADATA_PATH}`
        - **Dataset File**: `{DATASET_PATH}`
        - **Reports Directory**: `reports/`
        
        ### Model Architecture
        
        - **Algorithm**: {model_info['algorithm']}
        - **Framework**: scikit-learn
        - **Input Features**: 4 numerical features
        - **Output**: Multi-class classification
        - **Classes**: {model_info['n_classes']} crop types
        
        ### Training Configuration
        
        - **Test Split**: 20% of data
        - **Random Seed**: 42 (for reproducibility)
        - **Stratification**: Enabled (maintains class distribution)
        - **Cross-validation**: Not implemented (future enhancement)
        """)


if __name__ == "__main__":
    main()

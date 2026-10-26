"""
Crop Recommendation Page
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.sensor_processing import SensorDataManager
from src.crop_recommendation import CropRecommendationService
from src.data_validation import SensorValidator

st.set_page_config(page_title="Crop Recommendation - AgriSense AI", page_icon="🌾", layout="wide")

def main():
    st.title("🌾 AI-Powered Crop Recommendation")
    st.markdown("Get intelligent crop suggestions based on soil and environmental conditions")
    
    # Initialize services
    sensor_manager = SensorDataManager()
    crop_service = CropRecommendationService()
    validator = SensorValidator()
    
    # Check if model is available
    if not crop_service.is_model_available():
        st.error("🤖 Machine Learning model not found!")
        st.warning("""
        The crop recommendation model has not been trained yet.
        
        **To train the model:**
        1. Open a terminal in the project directory
        2. Activate your virtual environment
        3. Run: `python scripts/train_model.py`
        4. Wait for training to complete
        5. Refresh this page
        """)
        st.stop()
    
    # Model info banner
    model_info = crop_service.get_model_info()
    if model_info:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Model Algorithm", model_info["algorithm"])
        with col2:
            st.metric("Test Accuracy", f"{model_info['test_accuracy']*100:.1f}%")
        with col3:
            st.metric("Supported Crops", model_info["n_classes"])
    
    st.markdown("---")
    
    # Input mode selection
    st.subheader("📥 Select Input Mode")
    
    input_mode = st.radio(
        "Choose how to provide sensor data:",
        options=["Use Latest IoT Sensor Data", "Manual Input"],
        horizontal=True
    )
    
    st.markdown("---")
    
    # Initialize session state
    if "prediction_result" not in st.session_state:
        st.session_state.prediction_result = None
    if "input_values" not in st.session_state:
        st.session_state.input_values = None
    
    # Input collection
    if input_mode == "Use Latest IoT Sensor Data":
        st.subheader("📡 Latest IoT Sensor Readings")
        
        # Fetch latest data
        with st.spinner("Fetching latest sensor data..."):
            latest_data = sensor_manager.fetch_latest_data()
        
        if not latest_data["success"]:
            st.error(f"❌ Cannot fetch sensor data: {latest_data['message']}")
            st.stop()
        
        # Check validation
        validation = latest_data["validation"]
        sensor_data = latest_data["data"]
        
        # Display readings
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💧 Soil Moisture", f"{sensor_data['soil_moisture']:.1f}%")
        with col2:
            st.metric("🌍 Soil pH", f"{sensor_data['soil_ph']:.2f}")
        with col3:
            st.metric("🌡️ Temperature", f"{sensor_data['temperature']:.1f}°C")
        with col4:
            st.metric("💨 Humidity", f"{sensor_data['humidity']:.1f}%")
        
        # Show validation status
        if not validation["is_valid"]:
            st.error("❌ Sensor data validation failed!")
            for error in validation["errors"]:
                st.error(f"• {error}")
            st.stop()
        
        if validation["warnings"]:
            with st.expander("⚠️ Validation Warnings"):
                for warning in validation["warnings"]:
                    st.warning(warning)
        
        # Check freshness
        if not latest_data["is_fresh"]:
            st.warning(f"⚠️ {latest_data['message']}")
            proceed = st.checkbox("Proceed with stale data?")
            if not proceed:
                st.stop()
        
        st.success("✅ Sensor data is valid and ready for prediction")
        
        # Store values
        input_values = sensor_data
        source = "IoT Sensors"
    
    else:  # Manual Input
        st.subheader("✏️ Enter Sensor Values Manually")
        
        col1, col2 = st.columns(2)
        
        with col1:
            soil_moisture = st.number_input(
                "💧 Soil Moisture (%)",
                min_value=0.0,
                max_value=100.0,
                value=50.0,
                step=1.0,
                help="Enter soil moisture percentage (0-100)"
            )
            
            soil_ph = st.number_input(
                "🌍 Soil pH",
                min_value=0.0,
                max_value=14.0,
                value=6.5,
                step=0.1,
                help="Enter soil pH value (0-14)"
            )
        
        with col2:
            temperature = st.number_input(
                "🌡️ Temperature (°C)",
                min_value=-40.0,
                max_value=85.0,
                value=25.0,
                step=0.5,
                help="Enter air temperature in Celsius"
            )
            
            humidity = st.number_input(
                "💨 Humidity (%)",
                min_value=0.0,
                max_value=100.0,
                value=65.0,
                step=1.0,
                help="Enter relative humidity percentage"
            )
        
        input_values = {
            "soil_moisture": soil_moisture,
            "soil_ph": soil_ph,
            "temperature": temperature,
            "humidity": humidity
        }
        source = "Manual Input"
        
        # Validate manual input
        validation = validator.validate_sensor_data(input_values)
        
        if not validation["is_valid"]:
            st.error("❌ Invalid input values!")
            for error in validation["errors"]:
                st.error(f"• {error}")
        elif validation["warnings"]:
            with st.expander("⚠️ Input Warnings"):
                for warning in validation["warnings"]:
                    st.warning(warning)
    
    st.markdown("---")
    
    # Prediction buttons
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if st.button("🌱 Recommend Crops", type="primary", use_container_width=True):
            with st.spinner("Analyzing soil conditions..."):
                prediction = crop_service.predict_crop(
                    input_values["soil_moisture"],
                    input_values["soil_ph"],
                    input_values["temperature"],
                    input_values["humidity"]
                )
                st.session_state.prediction_result = prediction
                st.session_state.input_values = input_values
    
    with col2:
        if input_mode == "Use Latest IoT Sensor Data":
            if st.button("🔄 Refresh Sensor Data", use_container_width=True):
                sensor_manager.thingspeak.clear_cache()
                st.rerun()
    
    with col3:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.prediction_result = None
            st.session_state.input_values = None
            st.rerun()
    
    # Display prediction results
    if st.session_state.prediction_result:
        st.markdown("---")
        st.subheader("🎯 Crop Recommendation Results")
        
        prediction = st.session_state.prediction_result
        
        if prediction["success"]:
            # Main recommendation
            st.success(f"### 🌱 Recommended Crop: **{prediction['predicted_crop']}**")
            
            # Input summary
            with st.expander("📊 Input Conditions"):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Soil Moisture", f"{st.session_state.input_values['soil_moisture']:.1f}%")
                with col2:
                    st.metric("Soil pH", f"{st.session_state.input_values['soil_ph']:.2f}")
                with col3:
                    st.metric("Temperature", f"{st.session_state.input_values['temperature']:.1f}°C")
                with col4:
                    st.metric("Humidity", f"{st.session_state.input_values['humidity']:.1f}%")
                
                st.caption(f"Data Source: {source}")
            
            # Probabilities
            if prediction["probabilities"]:
                st.markdown("#### 📈 Crop Suitability Scores")
                st.info("""
                These scores represent the model's confidence for each crop based on the input conditions.
                Higher scores indicate better suitability according to the training data.
                """)
                
                # Show top 5 crops
                top_crops = list(prediction["probabilities"].items())[:5]
                
                for i, (crop, prob) in enumerate(top_crops, 1):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{i}. {crop}**")
                    with col2:
                        st.progress(prob, text=f"{prob*100:.1f}%")
            
            # Important disclaimer
            st.warning("""
            ⚠️ **Important Agricultural Disclaimer**
            
            This recommendation is based on **preliminary decision support** and should NOT be considered 
            as a guarantee of crop yield or profitability.
            
            Factors not captured by this model include:
            - Soil texture and type
            - Nutrient levels (N, P, K)
            - Rainfall and irrigation
            - Season and location
            - Crop variety
            - Local agricultural practices
            - Disease and pest pressure
            
            **Always consult agricultural experts and conduct proper soil testing before making final crop decisions.**
            """)
            
        else:
            st.error(f"❌ Prediction failed: {prediction['error']}")
    
    st.markdown("---")
    
    # Additional information
    with st.expander("ℹ️ How Crop Recommendation Works"):
        st.markdown("""
        ### Machine Learning Process
        
        1. **Data Collection**: Sensor readings are collected (soil moisture, pH, temperature, humidity)
        2. **Validation**: Data is validated for accuracy and completeness
        3. **Model Prediction**: A trained machine learning model analyzes the conditions
        4. **Recommendation**: The model suggests the most suitable crop(s)
        
        ### Model Training
        
        The model was trained on historical agricultural data with known crop-condition relationships.
        It learns patterns between environmental conditions and successful crop cultivation.
        
        ### Limitations
        
        - The model's accuracy depends on the quality and diversity of training data
        - Probabilities are not calibrated real-world success rates
        - Regional variations and specific crop varieties are not captured
        - Many agricultural factors beyond the four sensor readings affect crop success
        """)


if __name__ == "__main__":
    main()

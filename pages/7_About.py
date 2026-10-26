"""
About Page
"""
import streamlit as st

st.set_page_config(page_title="About - AgriSense AI", page_icon="📖", layout="wide")

def main():
    st.title("📖 About AgriSense AI")
    st.markdown("Smart Agriculture IoT System with AI-Based Crop Recommendation")
    
    # Project Overview
    st.subheader("🌱 Project Overview")
    
    st.markdown("""
    **AgriSense AI** is a comprehensive smart agriculture system that combines IoT sensor technology 
    with artificial intelligence to help farmers monitor their soil conditions and make informed crop decisions.
    
    The system provides real-time monitoring of critical agricultural parameters and uses machine learning 
    to recommend suitable crops based on current environmental conditions.
    """)
    
    st.markdown("---")
    
    # Key Features
    st.subheader("✨ Key Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **IoT Sensor Monitoring**
        - 💧 Real-time soil moisture tracking
        - 🌍 Continuous soil pH monitoring
        - 🌡️ Air temperature measurement
        - 💨 Relative humidity tracking
        - ☁️ Cloud data storage via ThingSpeak
        """)
        
        st.markdown("""
        **Data Analytics**
        - 📊 Interactive data visualization
        - 📈 Historical trend analysis
        - 🔗 Sensor correlation analysis
        - 💾 CSV data export
        - 📉 Statistical summaries
        """)
    
    with col2:
        st.markdown("""
        **AI Crop Recommendation**
        - 🤖 Machine learning-powered predictions
        - 🌾 Multiple crop support
        - 📊 Confidence scores
        - ⚙️ Manual input mode
        - 🔄 Real-time predictions
        """)
        
        st.markdown("""
        **Alert System**
        - ⚠️ Configurable thresholds
        - 🔔 Real-time notifications
        - 🏥 Sensor health monitoring
        - 📊 Data freshness checks
        - ⚙️ Custom alert rules
        """)
    
    st.markdown("---")
    
    # System Architecture
    st.subheader("🏗️ System Architecture")
    
    st.markdown("""
    ### Data Flow
    
    1. **Sensors** → Measure soil moisture, pH, temperature, and humidity
    2. **ESP32** → Reads sensor data and uploads to ThingSpeak via Wi-Fi
    3. **ThingSpeak** → Stores time-series data in the cloud
    4. **Streamlit Dashboard** → Fetches data via REST API
    5. **Python Backend** → Validates and processes sensor readings
    6. **ML Model** → Predicts suitable crops
    7. **Visualization** → Displays insights through interactive charts
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Hardware Components**
        - ESP32 microcontroller
        - Soil moisture sensor
        - Soil pH sensor
        - DHT22 temperature/humidity sensor
        - Wi-Fi connectivity
        """)
    
    with col2:
        st.markdown("""
        **Software Stack**
        - Python 3
        - Streamlit web framework
        - Scikit-learn ML library
        - Pandas & NumPy
        - Plotly visualization
        - ThingSpeak IoT platform
        """)
    
    st.markdown("---")
    
    # Machine Learning Workflow
    st.subheader("🤖 Machine Learning Workflow")
    
    st.markdown("""
    ### Training Pipeline
    
    1. **Data Collection** - Gather labeled agricultural data with sensor readings and crop outcomes
    2. **Data Validation** - Check for missing values, outliers, and invalid readings
    3. **Data Preprocessing** - Clean and normalize sensor measurements
    4. **Model Training** - Train multiple classification algorithms (Random Forest, Decision Tree)
    5. **Model Evaluation** - Test on held-out data and calculate performance metrics
    6. **Model Selection** - Choose best-performing model based on F1-score
    7. **Model Deployment** - Save model and integrate with Streamlit dashboard
    
    ### Prediction Process
    
    1. **Input Collection** - Receive sensor readings (live or manual)
    2. **Input Validation** - Ensure values are within physical ranges
    3. **Feature Preparation** - Format inputs for model
    4. **Prediction** - Run ML model to predict suitable crop
    5. **Result Presentation** - Display recommendation with confidence scores
    """)
    
    st.markdown("---")
    
    # Agricultural Limitations
    st.subheader("⚠️ Agricultural Limitations")
    
    st.warning("""
    **Important**: This system provides **preliminary decision support** and should not be the sole basis 
    for agricultural decisions.
    
    ### Factors Not Captured by the Model
    
    - **Soil Characteristics**: Texture, structure, organic matter, drainage
    - **Nutrient Levels**: Nitrogen (N), Phosphorus (P), Potassium (K), micronutrients
    - **Water Availability**: Rainfall patterns, irrigation systems, water quality
    - **Climate**: Seasonal variations, frost dates, growing degree days
    - **Location**: Geographic zone, elevation, local weather patterns
    - **Economic Factors**: Market prices, labor availability, input costs
    - **Agricultural Practices**: Crop rotation, pest management, fertilization
    - **Crop Varieties**: Specific cultivars adapted to local conditions
    
    ### Recommendations
    
    - Consult with local agricultural extension services
    - Conduct comprehensive soil testing
    - Consider regional farming practices
    - Start with small test plots
    - Monitor crop performance and adjust
    """)
    
    st.markdown("---")
    
    # Future Enhancements
    st.subheader("🚀 Future Enhancements")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Hardware Improvements**
        - Additional soil nutrient sensors (NPK)
        - Rainfall measurement
        - Light intensity sensors
        - Multiple sensor node support
        - Solar-powered operation
        """)
        
        st.markdown("""
        **Data Features**
        - Local SQLite database
        - Long-term data retention
        - Data backup and export
        - Multi-location support
        - Weather API integration
        """)
    
    with col2:
        st.markdown("""
        **ML Enhancements**
        - Deep learning models
        - Yield prediction
        - Pest and disease detection
        - Irrigation recommendations
        - Fertilizer optimization
        """)
        
        st.markdown("""
        **User Features**
        - Email/SMS alerts
        - Mobile app
        - User authentication
        - Farm management tools
        - Report generation
        """)
    
    st.markdown("---")
    
    # Technical Information
    with st.expander("🔧 Technical Information"):
        st.markdown("""
        ### Project Structure
        
        ```
        agrisense-ai/
        ├── app.py                      # Main Streamlit application
        ├── pages/                      # Multi-page Streamlit pages
        │   ├── 1_Dashboard.py
        │   ├── 2_Live_Monitoring.py
        │   ├── 3_Crop_Recommendation.py
        │   ├── 4_Historical_Analytics.py
        │   ├── 5_Alerts_Health.py
        │   ├── 6_Model_Information.py
        │   └── 7_About.py
        ├── src/                        # Python backend modules
        │   ├── config.py
        │   ├── thingspeak_service.py
        │   ├── sensor_processing.py
        │   ├── crop_recommendation.py
        │   ├── data_validation.py
        │   ├── alert_service.py
        │   └── visualization.py
        ├── scripts/                    # Utility scripts
        │   └── train_model.py
        ├── data/                       # Dataset directory
        ├── models/                     # Trained ML models
        ├── firmware/                   # ESP32 firmware
        └── requirements.txt            # Python dependencies
        ```
        
        ### Configuration
        
        - Environment variables via `.env` file
        - Streamlit configuration in `.streamlit/config.toml`
        - Alert thresholds configurable via UI
        - Demo mode for testing without hardware
        
        ### Data Privacy
        
        - Sensor data stored in your ThingSpeak account
        - No data transmitted to third parties
        - API keys stored locally only
        - Open-source and auditable code
        """)
    
    st.markdown("---")
    
    # Credits and License
    st.subheader("👥 Project Information")
    
    st.markdown("""
    **Version**: 1.0.0
    
    **Purpose**: College final-year engineering project demonstrating IoT and AI integration 
    for smart agriculture applications.
    
    **Technology**: Built with Python, Streamlit, Scikit-learn, and ThingSpeak IoT platform.
    
    **Note**: This is an educational project. For production agricultural use, please consult 
    with agricultural experts and conduct thorough field testing.
    """)
    
    st.markdown("---")
    
    # Footer
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem 0;">
        <p style="font-size: 1.2rem; font-weight: bold; color: #2E7D32;">🌱 AgriSense AI</p>
        <p style="font-size: 0.9rem;">Measure Your Soil. Understand Your Farm. Choose the Right Crop.</p>
        <p style="font-size: 0.8rem; margin-top: 1rem;">Built with ❤️ using Streamlit</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

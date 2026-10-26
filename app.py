"""
AgriSense AI - Main Streamlit Application
Smart Agriculture IoT System with AI-Based Crop Recommendation
"""
import streamlit as st
from src.config import DEMO_MODE_ENABLED

# Page configuration
st.set_page_config(
    page_title="AgriSense AI",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E7D32;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .kpi-card {
        background-color: #f5f5f5;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2E7D32;
        margin-bottom: 1rem;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: bold;
        color: #2E7D32;
    }
    .kpi-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
    .status-badge {
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: bold;
    }
    .status-demo {
        background-color: #FFF3E0;
        color: #E65100;
    }
    .status-live {
        background-color: #E8F5E9;
        color: #2E7D32;
    }
    .alert-warning {
        background-color: #FFF3E0;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #FF9800;
        margin: 1rem 0;
    }
    .alert-info {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #2196F3;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Main page
def main():
    # Header
    st.markdown('<div class="main-header">🌱 AgriSense AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Smart Agriculture IoT System with AI-Based Crop Recommendation</div>',
        unsafe_allow_html=True
    )
    
    # Mode indicator
    mode = "DEMO MODE" if DEMO_MODE_ENABLED else "LIVE IOT MODE"
    badge_class = "status-demo" if DEMO_MODE_ENABLED else "status-live"
    st.markdown(
        f'<div style="text-align: center;"><span class="status-badge {badge_class}">{mode}</span></div>',
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    
    # Welcome message
    st.markdown("""
    ### Welcome to AgriSense AI
    
    **AgriSense AI** is a comprehensive Smart Agriculture system that combines:
    - 🌡️ **Real-time IoT Sensor Monitoring** - Track soil moisture, pH, temperature, and humidity
    - 🤖 **AI-Powered Crop Recommendation** - Get intelligent crop suggestions based on your soil conditions
    - 📊 **Historical Data Analytics** - Visualize trends and patterns in your sensor data
    - ⚠️ **Smart Alerts** - Receive notifications when sensor readings fall outside optimal ranges
    
    #### Quick Start Guide
    
    1. **📊 Dashboard** - View your current sensor readings and overall system status
    2. **📡 Live Sensor Monitoring** - Monitor individual sensors with detailed charts
    3. **🌾 Crop Recommendation** - Get AI-powered crop recommendations
    4. **📈 Historical Analytics** - Analyze historical sensor data and trends
    5. **🔔 Alerts & Health** - Check sensor health and configure alert thresholds
    6. **ℹ️ Model Information** - View machine learning model details
    
    #### Current Mode
    """)
    
    if DEMO_MODE_ENABLED:
        st.info("""
        **DEMO MODE** is currently active. The application is using synthetic sensor data for demonstration purposes.
        
        To switch to **LIVE IOT MODE**:
        1. Set up your ThingSpeak channel
        2. Configure your ESP32 with sensors
        3. Update the `.env` file with your ThingSpeak credentials
        4. Set `ENABLE_DEMO_MODE=false` in your `.env` file
        """)
    else:
        st.success("""
        **LIVE IOT MODE** is active. The application is connected to your ThingSpeak channel and receiving real sensor data.
        """)
    
    st.markdown("---")
    
    # Navigation
    st.markdown("### 🧭 Navigation")
    st.markdown("""
    Use the **sidebar** on the left to navigate between different pages:
    - Click on any page to view detailed information
    - All pages update automatically based on your sensor data
    """)
    
    # Important notes
    with st.expander("⚠️ Important Agricultural Limitations"):
        st.warning("""
        **Please Note:** The crop recommendations provided by this system are based on **preliminary decision support** 
        and should not be considered as guarantees of crop yield or profitability.
        
        Soil moisture, pH, temperature, and humidity alone do not capture all factors affecting crop suitability, including:
        - Soil texture and soil type
        - Nutrient levels (Nitrogen, Phosphorus, Potassium)
        - Rainfall and irrigation availability
        - Season and geographic location
        - Crop variety and local agricultural practices
        - Disease pressure and pest management
        
        **Always consult with agricultural experts and conduct proper soil testing before making final crop decisions.**
        """)
    
    # System requirements
    with st.expander("🔧 System Requirements"):
        st.markdown("""
        **Hardware Components:**
        - ESP32 development board
        - Soil moisture sensor
        - Soil pH sensor (with signal conditioning)
        - DHT22 temperature and humidity sensor
        - Wi-Fi connection
        
        **Software Components:**
        - Python 3.8+
        - Streamlit web framework
        - ThingSpeak IoT platform
        - Scikit-learn machine learning library
        - Pandas, NumPy, Plotly for data processing and visualization
        """)
    
    st.markdown("---")
    
    # Footer
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem 0;">
        <p>AgriSense AI v1.0 | Built with Streamlit 🚀</p>
        <p style="font-size: 0.9rem;">Measure Your Soil. Understand Your Farm. Choose the Right Crop.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

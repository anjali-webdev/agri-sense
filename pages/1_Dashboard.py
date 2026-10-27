"""
Dashboard - Main overview page
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.sensor_processing import SensorDataManager
from src.crop_recommendation import CropRecommendationService
from src.alert_service import AlertService
from src.visualization import create_multi_sensor_chart
from datetime import datetime

st.set_page_config(page_title="Dashboard - AgriSense AI", page_icon="📊", layout="wide")

# Auto-refresh every 30 seconds
import time
st_autorefresh = st.empty()
with st_autorefresh:
    st.markdown("""
        <script>
            setTimeout(function() {
                window.location.reload();
            }, 30000);
        </script>
    """, unsafe_allow_html=True)

# Custom CSS
st.markdown("""
<style>
    .kpi-card {
        background-color: #f5f5f5;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2E7D32;
        text-align: center;
    }
    .kpi-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E7D32;
    }
    .kpi-label {
        font-size: 1rem;
        color: #666;
        margin-top: 0.5rem;
    }
    .kpi-unit {
        font-size: 1.2rem;
        color: #999;
    }
    .status-healthy { color: #2E7D32; }
    .status-warning { color: #FF9800; }
    .status-critical { color: #F44336; }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("📊 Dashboard")
    st.markdown("Real-time overview of your agricultural monitoring system")
    
    # Initialize services
    sensor_manager = SensorDataManager()
    crop_service = CropRecommendationService()
    alert_service = AlertService()
    
    # Mode indicator
    mode = sensor_manager.get_data_source()
    if sensor_manager.is_demo_mode():
        st.warning(f"⚠️ Running in {mode} - Using synthetic data for demonstration")
    else:
        st.info(f"✅ Running in {mode} - Connected to ThingSpeak")
    
    # Fetch latest data
    with st.spinner("Fetching latest sensor data..."):
        latest_data = sensor_manager.fetch_latest_data()
    
    if not latest_data["success"]:
        st.error(f"❌ Error fetching data: {latest_data['message']}")
        st.stop()
    
    sensor_data = latest_data["data"]
    timestamp = latest_data["timestamp"]
    validation = latest_data["validation"]
    
    # System status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_color = "🟢" if latest_data["success"] else "🔴"
        st.metric("System Status", f"{status_color} Online" if latest_data["success"] else "Offline")
    
    with col2:
        freshness = "🟢 Fresh" if latest_data["is_fresh"] else "🟡 Stale"
        st.metric("Data Freshness", freshness)
    
    with col3:
        if timestamp:
            # Display in local timezone with date and time
            st.metric("Last Update", timestamp.strftime("%d %b, %I:%M:%S %p"))
        else:
            st.metric("Last Update", "N/A")
    
    st.markdown("---")
    
    # KPI Cards - Sensor Readings
    st.subheader("Current Sensor Readings")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        if sensor_data and "soil_moisture" in sensor_data:
            value = sensor_data["soil_moisture"]
            st.markdown(f'<div class="kpi-value">{value:.1f}<span class="kpi-unit">%</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="kpi-value">--</div>', unsafe_allow_html=True)
        st.markdown('<div class="kpi-label">💧 Soil Moisture</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        if sensor_data and "soil_ph" in sensor_data:
            value = sensor_data["soil_ph"]
            st.markdown(f'<div class="kpi-value">{value:.1f}<span class="kpi-unit"> pH</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="kpi-value">--</div>', unsafe_allow_html=True)
        st.markdown('<div class="kpi-label">🌍 Soil pH</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        if sensor_data and "temperature" in sensor_data:
            value = sensor_data["temperature"]
            st.markdown(f'<div class="kpi-value">{value:.1f}<span class="kpi-unit">°C</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="kpi-value">--</div>', unsafe_allow_html=True)
        st.markdown('<div class="kpi-label">🌡️ Temperature</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        if sensor_data and "humidity" in sensor_data:
            value = sensor_data["humidity"]
            st.markdown(f'<div class="kpi-value">{value:.1f}<span class="kpi-unit">%</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="kpi-value">--</div>', unsafe_allow_html=True)
        st.markdown('<div class="kpi-label">💨 Humidity</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Alerts
    if sensor_data:
        alerts = alert_service.check_all_sensors(sensor_data)
        freshness_alert = alert_service.check_data_freshness(timestamp, max_age_minutes=30)
        
        if freshness_alert["has_alert"]:
            alerts.append(freshness_alert)
        
        if alerts:
            st.subheader("⚠️ Active Alerts")
            alert_summary = alert_service.get_alert_summary(alerts)
            
            for alert in alerts[:3]:  # Show top 3 alerts
                if alert["severity"] == "critical":
                    st.error(f"🔴 {alert['message']}")
                else:
                    st.warning(f"🟡 {alert['message']}")
    
    st.markdown("---")
    
    # Historical Chart
    st.subheader("📈 Recent Sensor Trends")
    
    with st.spinner("Loading historical data..."):
        historical_df = sensor_manager.get_historical_data(days=1)
    
    if historical_df is not None and not historical_df.empty:
        fig = create_multi_sensor_chart(historical_df)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No historical data available yet")
    
    st.markdown("---")
    
    # Crop Recommendation Preview
    st.subheader("🌾 Latest Crop Recommendation")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if crop_service.is_model_available() and sensor_data:
            if validation["is_valid"]:
                prediction = crop_service.predict_crop(
                    sensor_data["soil_moisture"],
                    sensor_data["soil_ph"],
                    sensor_data["temperature"],
                    sensor_data["humidity"]
                )
                
                if prediction["success"]:
                    st.success(f"🌱 Recommended Crop: **{prediction['predicted_crop']}**")
                    
                    if prediction["probabilities"]:
                        st.write("Top 3 Recommendations:")
                        top_3 = list(prediction["probabilities"].items())[:3]
                        for i, (crop, prob) in enumerate(top_3, 1):
                            st.write(f"{i}. {crop}: {prob*100:.1f}%")
                else:
                    st.warning(f"Cannot predict: {prediction['error']}")
            else:
                st.warning("⚠️ Current sensor readings have validation issues. Cannot provide recommendation.")
        else:
            if not crop_service.is_model_available():
                st.info("🤖 Model not trained yet. Run `python scripts/train_model.py` to train the model.")
            else:
                st.info("No sensor data available for prediction")
    
    with col2:
        if st.button("🔍 View Detailed Recommendations", use_container_width=True):
            st.switch_page("pages/3_Crop_Recommendation.py")
    
    st.markdown("---")
    
    # Validation Warnings
    if validation and validation["warnings"]:
        with st.expander("⚠️ Sensor Validation Warnings"):
            for warning in validation["warnings"]:
                st.warning(warning)
    
    # Refresh button
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()
    
    # Footer
    import pytz
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist)
    st.markdown(f"<div style='text-align: center; color: #999; padding: 1rem;'>Last refreshed: {current_time.strftime('%d %b %Y, %I:%M:%S %p IST')}</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()

"""
Alerts and Sensor Health Page
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.sensor_processing import SensorDataManager
from src.alert_service import AlertService
from src.config import ALERT_THRESHOLDS, SENSOR_RANGES

st.set_page_config(page_title="Alerts & Health - AgriSense AI", page_icon="🔔", layout="wide")

def main():
    st.title("🔔 Alerts & Sensor Health")
    st.markdown("Monitor sensor health and configure alert thresholds")
    
    # Initialize services
    sensor_manager = SensorDataManager()
    
    # Initialize session state for thresholds
    if "alert_thresholds" not in st.session_state:
        st.session_state.alert_thresholds = ALERT_THRESHOLDS.copy()
    
    alert_service = AlertService(st.session_state.alert_thresholds)
    
    # Fetch latest data
    with st.spinner("Checking sensor status..."):
        latest_data = sensor_manager.fetch_latest_data()
    
    # System health overview
    st.subheader("🏥 System Health Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if latest_data["success"]:
            st.success("✅ System Online")
        else:
            st.error("🔴 System Offline")
    
    with col2:
        if latest_data["is_fresh"]:
            st.success("✅ Data Fresh")
        else:
            st.warning("⚠️ Data Stale")
    
    with col3:
        if latest_data["timestamp"]:
            age_minutes = (sensor_manager.validator.check_data_freshness(latest_data["timestamp"])[1])
            st.info(f"📅 {age_minutes}")
        else:
            st.error("🔴 No Timestamp")
    
    st.markdown("---")
    
    # Active Alerts
    st.subheader("⚠️ Active Alerts")
    
    if latest_data["success"] and latest_data["data"]:
        sensor_data = latest_data["data"]
        
        # Check all sensors for alerts
        alerts = alert_service.check_all_sensors(sensor_data)
        
        # Check data freshness
        freshness_alert = alert_service.check_data_freshness(
            latest_data["timestamp"],
            max_age_minutes=30
        )
        
        if freshness_alert["has_alert"]:
            alerts.append(freshness_alert)
        
        # Display alerts
        if alerts:
            alert_summary = alert_service.get_alert_summary(alerts)
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Alerts", alert_summary["total_alerts"])
            with col2:
                st.metric("Critical", alert_summary["critical"], delta=None)
            with col3:
                st.metric("Warnings", alert_summary["warning"], delta=None)
            
            st.markdown("#### Alert Details")
            
            for alert in alerts:
                if alert["severity"] == "critical":
                    st.error(f"🔴 **{alert['sensor'].upper()}**: {alert['message']}")
                else:
                    st.warning(f"🟡 **{alert['sensor'].upper()}**: {alert['message']}")
        else:
            st.success("✅ No active alerts - All sensors are within configured thresholds")
    else:
        st.error("Cannot check alerts - No sensor data available")
    
    st.markdown("---")
    
    # Sensor Status
    st.subheader("📊 Sensor Status")
    
    if latest_data["success"] and latest_data["data"]:
        validation = latest_data["validation"]
        
        sensor_status = []
        
        for sensor_type in ["soil_moisture", "soil_ph", "temperature", "humidity"]:
            if sensor_type in latest_data["data"]:
                value = latest_data["data"][sensor_type]
                is_valid, status, _ = sensor_manager.validator.validate_reading(sensor_type, value)
                
                sensor_status.append({
                    "Sensor": sensor_type.replace("_", " ").title(),
                    "Value": f"{value:.2f}",
                    "Status": "✅ Valid" if is_valid and status == "valid" else ("⚠️ Warning" if status == "warning" else "❌ Invalid"),
                    "Range": f"{SENSOR_RANGES[sensor_type]['min']}-{SENSOR_RANGES[sensor_type]['max']} {SENSOR_RANGES[sensor_type]['unit']}"
                })
        
        if sensor_status:
            import pandas as pd
            status_df = pd.DataFrame(sensor_status)
            st.dataframe(status_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Alert Configuration
    st.subheader("⚙️ Configure Alert Thresholds")
    st.markdown("Set custom thresholds for each sensor. Alerts will trigger when readings go outside these ranges.")
    
    tabs = st.tabs(["💧 Soil Moisture", "🌍 Soil pH", "🌡️ Temperature", "💨 Humidity"])
    
    # Soil Moisture
    with tabs[0]:
        col1, col2 = st.columns(2)
        
        with col1:
            moisture_min = st.number_input(
                "Minimum Threshold (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(st.session_state.alert_thresholds["soil_moisture"]["min"]),
                step=1.0,
                key="moisture_min"
            )
        
        with col2:
            moisture_max = st.number_input(
                "Maximum Threshold (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(st.session_state.alert_thresholds["soil_moisture"]["max"]),
                step=1.0,
                key="moisture_max"
            )
        
        if st.button("Update Soil Moisture Thresholds", key="update_moisture"):
            st.session_state.alert_thresholds["soil_moisture"]["min"] = moisture_min
            st.session_state.alert_thresholds["soil_moisture"]["max"] = moisture_max
            st.success("✅ Thresholds updated!")
            st.rerun()
        
        st.info(f"Current: Alert if < {moisture_min}% or > {moisture_max}%")
    
    # Soil pH
    with tabs[1]:
        col1, col2 = st.columns(2)
        
        with col1:
            ph_min = st.number_input(
                "Minimum Threshold",
                min_value=0.0,
                max_value=14.0,
                value=float(st.session_state.alert_thresholds["soil_ph"]["min"]),
                step=0.1,
                key="ph_min"
            )
        
        with col2:
            ph_max = st.number_input(
                "Maximum Threshold",
                min_value=0.0,
                max_value=14.0,
                value=float(st.session_state.alert_thresholds["soil_ph"]["max"]),
                step=0.1,
                key="ph_max"
            )
        
        if st.button("Update Soil pH Thresholds", key="update_ph"):
            st.session_state.alert_thresholds["soil_ph"]["min"] = ph_min
            st.session_state.alert_thresholds["soil_ph"]["max"] = ph_max
            st.success("✅ Thresholds updated!")
            st.rerun()
        
        st.info(f"Current: Alert if < {ph_min} or > {ph_max}")
    
    # Temperature
    with tabs[2]:
        col1, col2 = st.columns(2)
        
        with col1:
            temp_min = st.number_input(
                "Minimum Threshold (°C)",
                min_value=-40.0,
                max_value=85.0,
                value=float(st.session_state.alert_thresholds["temperature"]["min"]),
                step=1.0,
                key="temp_min"
            )
        
        with col2:
            temp_max = st.number_input(
                "Maximum Threshold (°C)",
                min_value=-40.0,
                max_value=85.0,
                value=float(st.session_state.alert_thresholds["temperature"]["max"]),
                step=1.0,
                key="temp_max"
            )
        
        if st.button("Update Temperature Thresholds", key="update_temp"):
            st.session_state.alert_thresholds["temperature"]["min"] = temp_min
            st.session_state.alert_thresholds["temperature"]["max"] = temp_max
            st.success("✅ Thresholds updated!")
            st.rerun()
        
        st.info(f"Current: Alert if < {temp_min}°C or > {temp_max}°C")
    
    # Humidity
    with tabs[3]:
        col1, col2 = st.columns(2)
        
        with col1:
            humidity_min = st.number_input(
                "Minimum Threshold (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(st.session_state.alert_thresholds["humidity"]["min"]),
                step=1.0,
                key="humidity_min"
            )
        
        with col2:
            humidity_max = st.number_input(
                "Maximum Threshold (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(st.session_state.alert_thresholds["humidity"]["max"]),
                step=1.0,
                key="humidity_max"
            )
        
        if st.button("Update Humidity Thresholds", key="update_humidity"):
            st.session_state.alert_thresholds["humidity"]["min"] = humidity_min
            st.session_state.alert_thresholds["humidity"]["max"] = humidity_max
            st.success("✅ Thresholds updated!")
            st.rerun()
        
        st.info(f"Current: Alert if < {humidity_min}% or > {humidity_max}%")
    
    st.markdown("---")
    
    # Reset thresholds
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("**Reset all thresholds to default values**")
    
    with col2:
        if st.button("🔄 Reset to Defaults", use_container_width=True):
            st.session_state.alert_thresholds = ALERT_THRESHOLDS.copy()
            st.success("✅ Thresholds reset to defaults!")
            st.rerun()
    
    st.markdown("---")
    
    # Important notes
    with st.expander("ℹ️ About Alert Thresholds"):
        st.markdown("""
        ### Configuring Thresholds
        
        Alert thresholds define the acceptable operating range for each sensor. When a sensor reading 
        falls outside this range, an alert is triggered.
        
        ### Threshold Guidelines
        
        **Default thresholds are examples only!** You should configure thresholds based on:
        - Your specific crop requirements
        - Local climate conditions
        - Soil type and characteristics
        - Seasonal variations
        - Agricultural best practices for your region
        
        ### Alert Severity
        
        - **Warning (🟡)**: Reading is outside configured threshold but within physical limits
        - **Critical (🔴)**: System error, no data, or physically impossible reading
        
        ### Limitations
        
        - Thresholds are currently stored in session state (reset on page refresh)
        - Email/SMS notifications are not yet implemented
        - Consider consulting agricultural experts for optimal threshold values
        """)


if __name__ == "__main__":
    main()

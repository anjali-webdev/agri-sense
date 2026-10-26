"""
Live Sensor Monitoring Page
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.sensor_processing import SensorDataManager
from src.visualization import create_time_series_chart
from src.config import SENSOR_RANGES

st.set_page_config(page_title="Live Monitoring - AgriSense AI", page_icon="📡", layout="wide")

def main():
    st.title("📡 Live Sensor Monitoring")
    st.markdown("Real-time monitoring of individual sensors with historical trends")
    
    # Initialize
    sensor_manager = SensorDataManager()
    
    # Mode indicator
    if sensor_manager.is_demo_mode():
        st.warning(f"⚠️ {sensor_manager.get_data_source()} - Using synthetic data")
    else:
        st.info(f"✅ {sensor_manager.get_data_source()} - Live data from ThingSpeak")
    
    # Time range selection
    col1, col2 = st.columns([3, 1])
    with col1:
        time_range = st.selectbox(
            "Select Time Range",
            options=[1, 3, 7, 14, 30],
            format_func=lambda x: f"Last {x} day{'s' if x > 1 else ''}",
            index=2
        )
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            sensor_manager.thingspeak.clear_cache()
            st.rerun()
    
    # Fetch data
    with st.spinner(f"Loading {time_range} day(s) of sensor data..."):
        df = sensor_manager.get_historical_data(days=time_range, force_refresh=False)
        latest_data = sensor_manager.fetch_latest_data()
    
    if df is None or df.empty:
        st.error("No sensor data available")
        st.stop()
    
    # Summary statistics
    stats = sensor_manager.get_summary_statistics(df)
    
    st.markdown("---")
    
    # Soil Moisture Section
    st.subheader("💧 Soil Moisture")
    
    col1, col2, col3, col4 = st.columns(4)
    
    if "soil_moisture" in stats:
        with col1:
            st.metric("Current", f"{stats['soil_moisture']['current']:.1f}%")
        with col2:
            st.metric("Minimum", f"{stats['soil_moisture']['min']:.1f}%")
        with col3:
            st.metric("Maximum", f"{stats['soil_moisture']['max']:.1f}%")
        with col4:
            st.metric("Average", f"{stats['soil_moisture']['mean']:.1f}%")
        
        fig = create_time_series_chart(
            df, "soil_moisture",
            "Soil Moisture Over Time",
            "Moisture (%)",
            "#795548"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("ℹ️ About Soil Moisture"):
            st.info(f"""
            **Soil Moisture** measures the water content in the soil as a percentage.
            
            - **Valid Range:** {SENSOR_RANGES['soil_moisture']['min']}-{SENSOR_RANGES['soil_moisture']['max']}%
            - **Optimal Range:** Varies by crop (typically 40-80% for most crops)
            - **Low Moisture:** May indicate need for irrigation
            - **High Moisture:** May indicate over-watering or poor drainage
            
            **Note:** Accuracy depends on sensor calibration and soil type.
            """)
    
    st.markdown("---")
    
    # Soil pH Section
    st.subheader("🌍 Soil pH")
    
    col1, col2, col3, col4 = st.columns(4)
    
    if "soil_ph" in stats:
        with col1:
            st.metric("Current", f"{stats['soil_ph']['current']:.2f}")
        with col2:
            st.metric("Minimum", f"{stats['soil_ph']['min']:.2f}")
        with col3:
            st.metric("Maximum", f"{stats['soil_ph']['max']:.2f}")
        with col4:
            st.metric("Average", f"{stats['soil_ph']['mean']:.2f}")
        
        fig = create_time_series_chart(
            df, "soil_ph",
            "Soil pH Over Time",
            "pH",
            "#FF9800"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("ℹ️ About Soil pH"):
            st.info(f"""
            **Soil pH** measures the acidity or alkalinity of the soil.
            
            - **Valid Range:** {SENSOR_RANGES['soil_ph']['min']}-{SENSOR_RANGES['soil_ph']['max']} pH
            - **Acidic:** pH < 7
            - **Neutral:** pH = 7
            - **Alkaline:** pH > 7
            - **Optimal Range:** Varies by crop (typically 6.0-7.5)
            
            pH affects nutrient availability and microbial activity in soil.
            """)
    
    st.markdown("---")
    
    # Temperature Section
    st.subheader("🌡️ Air Temperature")
    
    col1, col2, col3, col4 = st.columns(4)
    
    if "temperature" in stats:
        with col1:
            st.metric("Current", f"{stats['temperature']['current']:.1f}°C")
        with col2:
            st.metric("Minimum", f"{stats['temperature']['min']:.1f}°C")
        with col3:
            st.metric("Maximum", f"{stats['temperature']['max']:.1f}°C")
        with col4:
            st.metric("Average", f"{stats['temperature']['mean']:.1f}°C")
        
        fig = create_time_series_chart(
            df, "temperature",
            "Air Temperature Over Time",
            "Temperature (°C)",
            "#F44336"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("ℹ️ About Temperature"):
            st.info(f"""
            **Air Temperature** measures the ambient temperature around the sensors.
            
            - **Valid Range:** {SENSOR_RANGES['temperature']['min']}-{SENSOR_RANGES['temperature']['max']}°C
            - **Optimal Range:** Varies by crop (typically 15-35°C for growth)
            - **Affects:** Plant growth rate, water requirements, pest activity
            
            Temperature variations throughout the day are normal.
            """)
    
    st.markdown("---")
    
    # Humidity Section
    st.subheader("💨 Relative Humidity")
    
    col1, col2, col3, col4 = st.columns(4)
    
    if "humidity" in stats:
        with col1:
            st.metric("Current", f"{stats['humidity']['current']:.1f}%")
        with col2:
            st.metric("Minimum", f"{stats['humidity']['min']:.1f}%")
        with col3:
            st.metric("Maximum", f"{stats['humidity']['max']:.1f}%")
        with col4:
            st.metric("Average", f"{stats['humidity']['mean']:.1f}%")
        
        fig = create_time_series_chart(
            df, "humidity",
            "Relative Humidity Over Time",
            "Humidity (% RH)",
            "#2196F3"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("ℹ️ About Humidity"):
            st.info(f"""
            **Relative Humidity** measures the moisture content in the air.
            
            - **Valid Range:** {SENSOR_RANGES['humidity']['min']}-{SENSOR_RANGES['humidity']['max']}% RH
            - **Low Humidity:** May increase plant water stress and evaporation
            - **High Humidity:** May increase disease risk
            - **Optimal Range:** Varies by crop (typically 50-70%)
            
            Humidity often correlates inversely with temperature.
            """)
    
    st.markdown("---")
    
    # Data quality information
    st.subheader("📊 Data Quality")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Records", len(df))
    with col2:
        valid_count = len(df[df["validation_status"] == "valid"])
        st.metric("Valid Records", valid_count)
    with col3:
        invalid_count = len(df[df["validation_status"] != "valid"])
        st.metric("Invalid Records", invalid_count)
    
    if latest_data["timestamp"]:
        st.info(f"📅 Latest reading: {latest_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()

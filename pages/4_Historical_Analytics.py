"""
Historical Data and Analytics Page
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.sensor_processing import SensorDataManager
from src.visualization import create_time_series_chart, create_correlation_heatmap
import pandas as pd

st.set_page_config(page_title="Historical Analytics - AgriSense AI", page_icon="📈", layout="wide")

def main():
    st.title("📈 Historical Data & Analytics")
    st.markdown("Analyze trends, patterns, and correlations in your sensor data")
    
    # Initialize
    sensor_manager = SensorDataManager()
    
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
    
    # Load data
    with st.spinner(f"Loading {time_range} day(s) of historical data..."):
        df = sensor_manager.get_historical_data(days=time_range, force_refresh=False)
    
    if df is None or df.empty:
        st.error("No historical data available")
        st.info("Data will become available once sensors start sending readings to ThingSpeak")
        st.stop()
    
    # Summary statistics
    stats = sensor_manager.get_summary_statistics(df)
    
    # Overview metrics
    st.subheader("📊 Data Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records", len(df))
    with col2:
        valid_count = len(df[df["validation_status"] == "valid"])
        st.metric("Valid Records", valid_count)
    with col3:
        if len(df) > 0:
            time_span = (df["timestamp"].max() - df["timestamp"].min()).days
            st.metric("Time Span", f"{time_span} days")
        else:
            st.metric("Time Span", "0 days")
    with col4:
        if len(df) > 1:
            avg_interval = (df["timestamp"].max() - df["timestamp"].min()) / (len(df) - 1)
            st.metric("Avg Interval", f"{avg_interval.total_seconds() / 60:.0f} min")
        else:
            st.metric("Avg Interval", "N/A")
    
    st.markdown("---")
    
    # Individual sensor charts
    st.subheader("📉 Sensor Trends")
    
    tabs = st.tabs(["💧 Soil Moisture", "🌍 Soil pH", "🌡️ Temperature", "💨 Humidity"])
    
    with tabs[0]:
        if "soil_moisture" in stats:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Average", f"{stats['soil_moisture']['mean']:.1f}%")
            with col2:
                st.metric("Min", f"{stats['soil_moisture']['min']:.1f}%")
            with col3:
                st.metric("Max", f"{stats['soil_moisture']['max']:.1f}%")
            
            fig = create_time_series_chart(
                df, "soil_moisture",
                "Soil Moisture Historical Trend",
                "Moisture (%)",
                "#795548"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tabs[1]:
        if "soil_ph" in stats:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Average", f"{stats['soil_ph']['mean']:.2f}")
            with col2:
                st.metric("Min", f"{stats['soil_ph']['min']:.2f}")
            with col3:
                st.metric("Max", f"{stats['soil_ph']['max']:.2f}")
            
            fig = create_time_series_chart(
                df, "soil_ph",
                "Soil pH Historical Trend",
                "pH",
                "#FF9800"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tabs[2]:
        if "temperature" in stats:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Average", f"{stats['temperature']['mean']:.1f}°C")
            with col2:
                st.metric("Min", f"{stats['temperature']['min']:.1f}°C")
            with col3:
                st.metric("Max", f"{stats['temperature']['max']:.1f}°C")
            
            fig = create_time_series_chart(
                df, "temperature",
                "Temperature Historical Trend",
                "Temperature (°C)",
                "#F44336"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tabs[3]:
        if "humidity" in stats:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Average", f"{stats['humidity']['mean']:.1f}%")
            with col2:
                st.metric("Min", f"{stats['humidity']['min']:.1f}%")
            with col3:
                st.metric("Max", f"{stats['humidity']['max']:.1f}%")
            
            fig = create_time_series_chart(
                df, "humidity",
                "Humidity Historical Trend",
                "Humidity (% RH)",
                "#2196F3"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Correlation analysis
    st.subheader("🔗 Sensor Correlations")
    st.markdown("Correlation measures how sensor readings relate to each other (-1 to +1)")
    
    fig = create_correlation_heatmap(df)
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("ℹ️ Understanding Correlations"):
        st.markdown("""
        **Correlation values:**
        - **+1.0**: Perfect positive correlation (both increase together)
        - **0.0**: No correlation (independent)
        - **-1.0**: Perfect negative correlation (one increases, other decreases)
        
        **Common patterns:**
        - Temperature and humidity often show negative correlation (hot air holds less relative humidity)
        - Soil moisture may correlate with humidity (moist conditions)
        - pH typically shows weak correlation with other sensors (relatively stable)
        
        ⚠️ **Note:** Correlation does NOT imply causation!
        """)
    
    st.markdown("---")
    
    # Data export
    st.subheader("💾 Export Data")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("Download the current dataset as CSV for further analysis")
    
    with col2:
        # Prepare export dataframe
        export_df = df[["timestamp", "soil_moisture", "soil_ph", "temperature", "humidity", "source", "validation_status"]].copy()
        csv = export_df.to_csv(index=False)
        
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"agrisense_data_{time_range}days.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    st.markdown("---")
    
    # Statistical summary table
    with st.expander("📋 Detailed Statistics Table"):
        summary_data = []
        
        for sensor in ["soil_moisture", "soil_ph", "temperature", "humidity"]:
            if sensor in stats:
                summary_data.append({
                    "Sensor": sensor.replace("_", " ").title(),
                    "Current": f"{stats[sensor]['current']:.2f}",
                    "Mean": f"{stats[sensor]['mean']:.2f}",
                    "Median": f"{stats[sensor]['median']:.2f}",
                    "Std Dev": f"{stats[sensor]['std']:.2f}",
                    "Min": f"{stats[sensor]['min']:.2f}",
                    "Max": f"{stats[sensor]['max']:.2f}"
                })
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    # Raw data viewer
    with st.expander("📄 View Raw Data"):
        st.dataframe(df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()

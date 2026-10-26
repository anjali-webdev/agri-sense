"""
Visualization utilities for sensor data using Plotly
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Optional


def create_time_series_chart(
    df: pd.DataFrame,
    y_column: str,
    title: str,
    y_label: str,
    color: str = "#2E7D32"
) -> go.Figure:
    """
    Create a time series line chart.
    
    Args:
        df: DataFrame with timestamp and sensor data
        y_column: Column name for y-axis
        title: Chart title
        y_label: Y-axis label
        color: Line color
        
    Returns:
        Plotly figure
    """
    if df is None or df.empty:
        # Return empty chart with message
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title=title,
            xaxis_title="Time",
            yaxis_title=y_label,
            height=400
        )
        return fig
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df[y_column],
        mode='lines+markers',
        name=y_label,
        line=dict(color=color, width=2),
        marker=dict(size=4)
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Time",
        yaxis_title=y_label,
        hovermode='x unified',
        height=400,
        template="plotly_white"
    )
    
    return fig


def create_multi_sensor_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create a multi-line chart for all sensors (normalized).
    
    Args:
        df: DataFrame with all sensor data
        
    Returns:
        Plotly figure
    """
    if df is None or df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        return fig
    
    fig = go.Figure()
    
    # Add each sensor as a trace
    sensors = {
        "soil_moisture": {"name": "Soil Moisture (%)", "color": "#795548"},
        "soil_ph": {"name": "Soil pH", "color": "#FF9800"},
        "temperature": {"name": "Temperature (°C)", "color": "#F44336"},
        "humidity": {"name": "Humidity (% RH)", "color": "#2196F3"}
    }
    
    for col, props in sensors.items():
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df["timestamp"],
                y=df[col],
                mode='lines',
                name=props["name"],
                line=dict(color=props["color"], width=2)
            ))
    
    fig.update_layout(
        title="All Sensors - Historical Trends",
        xaxis_title="Time",
        yaxis_title="Sensor Readings",
        hovermode='x unified',
        height=500,
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def create_gauge_chart(
    value: float,
    title: str,
    min_val: float,
    max_val: float,
    unit: str = "",
    color: str = "#2E7D32"
) -> go.Figure:
    """
    Create a gauge chart for a single sensor reading.
    
    Args:
        value: Current sensor value
        title: Chart title
        min_val: Minimum value for gauge
        max_val: Maximum value for gauge
        unit: Unit of measurement
        color: Gauge color
        
    Returns:
        Plotly figure
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        number={'suffix': f" {unit}"},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': color},
            'steps': [
                {'range': [min_val, (max_val - min_val) * 0.33 + min_val], 'color': "lightgray"},
                {'range': [(max_val - min_val) * 0.33 + min_val, (max_val - min_val) * 0.66 + min_val], 'color': "gray"},
                {'range': [(max_val - min_val) * 0.66 + min_val, max_val], 'color': "darkgray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    fig.update_layout(height=300)
    
    return fig


def create_correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    """
    Create a correlation heatmap for sensor data.
    
    Args:
        df: DataFrame with sensor data
        
    Returns:
        Plotly figure
    """
    if df is None or df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        return fig
    
    # Select numeric columns
    sensor_cols = ["soil_moisture", "soil_ph", "temperature", "humidity"]
    available_cols = [col for col in sensor_cols if col in df.columns]
    
    if not available_cols:
        fig = go.Figure()
        fig.add_annotation(
            text="No sensor data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        return fig
    
    # Calculate correlation matrix
    corr_matrix = df[available_cols].corr()
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=available_cols,
        y=available_cols,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 12},
        colorbar=dict(title="Correlation")
    ))
    
    fig.update_layout(
        title="Sensor Correlation Matrix",
        height=500,
        template="plotly_white"
    )
    
    return fig


def create_distribution_chart(
    df: pd.DataFrame,
    column: str,
    title: str,
    x_label: str
) -> go.Figure:
    """
    Create a histogram for sensor data distribution.
    
    Args:
        df: DataFrame with sensor data
        column: Column to plot
        title: Chart title
        x_label: X-axis label
        
    Returns:
        Plotly figure
    """
    if df is None or df.empty or column not in df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        return fig
    
    fig = go.Figure(data=[go.Histogram(
        x=df[column],
        nbinsx=30,
        marker_color='#2E7D32',
        opacity=0.75
    )])
    
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title="Frequency",
        height=400,
        template="plotly_white"
    )
    
    return fig

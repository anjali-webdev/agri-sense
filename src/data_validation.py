"""
Data validation and processing for sensor readings
"""
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from src.config import SENSOR_RANGES, EXPECTED_RANGES


class SensorValidator:
    """Validates sensor readings against physical and expected ranges"""
    
    @staticmethod
    def validate_reading(
        sensor_type: str,
        value: float,
        timestamp: Optional[datetime] = None
    ) -> Tuple[bool, str, str]:
        """
        Validate a single sensor reading.
        
        Args:
            sensor_type: Type of sensor (soil_moisture, soil_ph, temperature, humidity)
            value: Sensor reading value
            timestamp: Optional timestamp for staleness check
            
        Returns:
            Tuple of (is_valid, status, message)
            status can be: 'valid', 'warning', 'invalid'
        """
        if pd.isna(value):
            return False, "invalid", f"{sensor_type}: Missing value"
        
        if not isinstance(value, (int, float)):
            return False, "invalid", f"{sensor_type}: Non-numeric value"
        
        # Check if value is infinite
        if np.isinf(value):
            return False, "invalid", f"{sensor_type}: Infinite value"
        
        # Get sensor ranges
        if sensor_type not in SENSOR_RANGES:
            return False, "invalid", f"Unknown sensor type: {sensor_type}"
        
        sensor_range = SENSOR_RANGES[sensor_type]
        expected_range = EXPECTED_RANGES[sensor_type]
        
        # Check physical limits
        if value < sensor_range["min"] or value > sensor_range["max"]:
            return False, "invalid", (
                f"{sensor_type}: Value {value:.2f} outside physical range "
                f"[{sensor_range['min']}, {sensor_range['max']}]"
            )
        
        # Check expected operating range (warning, not error)
        if value < expected_range["min"] or value > expected_range["max"]:
            return True, "warning", (
                f"{sensor_type}: Value {value:.2f} outside expected range "
                f"[{expected_range['min']}, {expected_range['max']}] but within physical limits"
            )
        
        return True, "valid", f"{sensor_type}: Valid reading"
    
    @staticmethod
    def validate_sensor_data(data: Dict[str, float]) -> Dict[str, any]:
        """
        Validate all sensor readings in a data dictionary.
        
        Args:
            data: Dictionary with sensor readings
            
        Returns:
            Dictionary with validation results
        """
        results = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "validated_data": {}
        }
        
        sensor_types = ["soil_moisture", "soil_ph", "temperature", "humidity"]
        
        for sensor_type in sensor_types:
            if sensor_type not in data:
                results["errors"].append(f"Missing {sensor_type}")
                results["is_valid"] = False
                continue
            
            value = data[sensor_type]
            is_valid, status, message = SensorValidator.validate_reading(
                sensor_type, value
            )
            
            if status == "invalid":
                results["errors"].append(message)
                results["is_valid"] = False
            elif status == "warning":
                results["warnings"].append(message)
                results["validated_data"][sensor_type] = value
            else:
                results["validated_data"][sensor_type] = value
        
        return results
    
    @staticmethod
    def check_data_freshness(
        timestamp: datetime,
        max_age_minutes: int = 30
    ) -> Tuple[bool, str]:
        """
        Check if data is fresh enough.
        
        Args:
            timestamp: Data timestamp
            max_age_minutes: Maximum age in minutes
            
        Returns:
            Tuple of (is_fresh, message)
        """
        if timestamp is None:
            return False, "No timestamp available"
        
        # Get current time in IST (Asia/Kolkata timezone)
        from datetime import timezone
        import pytz
        
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        # Ensure timestamp is timezone-aware
        if hasattr(timestamp, 'tzinfo'):
            if timestamp.tzinfo is None:
                # If naive, assume UTC and convert to IST
                timestamp = pytz.utc.localize(timestamp).astimezone(ist)
            else:
                # Convert to IST if different timezone
                timestamp = timestamp.astimezone(ist)
        
        age = now - timestamp
        
        if age > timedelta(minutes=max_age_minutes):
            return False, (
                f"Data is stale: {age.total_seconds() / 60:.1f} minutes old "
                f"(max: {max_age_minutes} minutes)"
            )
        
        return True, f"Data is fresh: {age.total_seconds() / 60:.1f} minutes old"
    
    @staticmethod
    def clean_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
        """
        Clean and validate a dataframe of sensor readings.
        
        Args:
            df: DataFrame with sensor readings
            
        Returns:
            Tuple of (cleaned_df, cleaning_stats)
        """
        stats = {
            "original_rows": len(df),
            "missing_values": 0,
            "invalid_values": 0,
            "duplicates": 0,
            "final_rows": 0
        }
        
        if df.empty:
            return df, stats
        
        # Remove duplicates
        initial_len = len(df)
        df = df.drop_duplicates()
        stats["duplicates"] = initial_len - len(df)
        
        # Check for missing values
        stats["missing_values"] = df.isnull().sum().sum()
        
        # Validate each sensor column
        sensor_cols = ["soil_moisture", "soil_ph", "temperature", "humidity"]
        valid_mask = pd.Series([True] * len(df), index=df.index)
        
        for col in sensor_cols:
            if col in df.columns:
                for idx, value in df[col].items():
                    is_valid, status, _ = SensorValidator.validate_reading(col, value)
                    if status == "invalid":
                        valid_mask[idx] = False
                        stats["invalid_values"] += 1
        
        # Filter to valid rows
        df = df[valid_mask].copy()
        stats["final_rows"] = len(df)
        
        return df, stats


def get_demo_data(num_records: int = 100) -> pd.DataFrame:
    """
    Generate synthetic sensor data for demo mode.
    
    Args:
        num_records: Number of demo records to generate
        
    Returns:
        DataFrame with synthetic sensor data
    """
    np.random.seed(42)
    
    # Generate timestamps for the last 24 hours in IST
    import pytz
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    timestamps = [now - timedelta(hours=24 - i * 24 / num_records) for i in range(num_records)]
    
    # Generate realistic sensor patterns
    # Soil moisture: varies with time (watering cycles)
    base_moisture = 50 + 15 * np.sin(np.linspace(0, 4 * np.pi, num_records))
    soil_moisture = base_moisture + np.random.normal(0, 5, num_records)
    soil_moisture = np.clip(soil_moisture, 20, 80)
    
    # Soil pH: relatively stable with small variations
    soil_ph = 6.5 + np.random.normal(0, 0.3, num_records)
    soil_ph = np.clip(soil_ph, 5.5, 7.5)
    
    # Temperature: varies throughout the day
    base_temp = 25 + 8 * np.sin(np.linspace(0, 2 * np.pi, num_records))
    temperature = base_temp + np.random.normal(0, 2, num_records)
    temperature = np.clip(temperature, 15, 40)
    
    # Humidity: inversely correlated with temperature
    humidity = 70 - 0.5 * (temperature - 25) + np.random.normal(0, 5, num_records)
    humidity = np.clip(humidity, 40, 85)
    
    df = pd.DataFrame({
        "timestamp": timestamps,
        "soil_moisture": soil_moisture,
        "soil_ph": soil_ph,
        "temperature": temperature,
        "humidity": humidity,
        "source": "DEMO",
        "validation_status": "valid"
    })
    
    return df

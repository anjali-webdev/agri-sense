"""
Sensor data processing and aggregation
"""
from typing import Optional, Dict
import pandas as pd
from datetime import datetime
from src.data_validation import SensorValidator, get_demo_data
from src.thingspeak_service import ThingSpeakService
from src.config import DEMO_MODE_ENABLED, DATA_FRESHNESS_MINUTES


class SensorDataManager:
    """Manages sensor data from ThingSpeak or demo mode"""
    
    def __init__(self):
        self.thingspeak = ThingSpeakService()
        self.validator = SensorValidator()
        self.demo_mode = DEMO_MODE_ENABLED or not self.thingspeak.is_configured()
        self._last_data = None
        self._last_fetch_time = None
    
    def is_demo_mode(self) -> bool:
        """Check if running in demo mode"""
        return self.demo_mode
    
    def get_data_source(self) -> str:
        """Get current data source"""
        return "DEMO MODE" if self.demo_mode else "LIVE IOT"
    
    def fetch_latest_data(self, force_refresh: bool = False) -> Dict[str, any]:
        """
        Fetch latest sensor data from appropriate source.
        
        Args:
            force_refresh: Force fetch from source, ignore cache
            
        Returns:
            Dictionary with sensor data and metadata
        """
        if self.demo_mode:
            return self._fetch_demo_data()
        else:
            return self._fetch_thingspeak_data(force_refresh)
    
    def _fetch_demo_data(self) -> Dict[str, any]:
        """Fetch data from demo mode"""
        df = get_demo_data(num_records=100)
        latest = df.iloc[-1]
        
        sensor_data = {
            "soil_moisture": latest["soil_moisture"],
            "soil_ph": latest["soil_ph"],
            "temperature": latest["temperature"],
            "humidity": latest["humidity"]
        }
        
        # Validate
        validation = self.validator.validate_sensor_data(sensor_data)
        
        return {
            "success": True,
            "source": "DEMO",
            "timestamp": latest["timestamp"],
            "data": sensor_data,
            "validation": validation,
            "is_fresh": True,
            "message": "Demo data (synthetic sensor readings for testing)"
        }
    
    def _fetch_thingspeak_data(self, force_refresh: bool = False) -> Dict[str, any]:
        """Fetch data from ThingSpeak"""
        if not force_refresh and self._last_data and self._last_fetch_time:
            # Return cached data if recent
            age = (datetime.now() - self._last_fetch_time).total_seconds() / 60
            if age < 1:  # Cache for 1 minute
                return self._last_data
        
        reading = self.thingspeak.get_latest_reading()
        
        if reading is None:
            return {
                "success": False,
                "source": "ThingSpeak",
                "timestamp": None,
                "data": None,
                "validation": None,
                "is_fresh": False,
                "message": "No data available from ThingSpeak. Check channel configuration."
            }
        
        sensor_data = {
            "soil_moisture": reading["soil_moisture"],
            "soil_ph": reading["soil_ph"],
            "temperature": reading["temperature"],
            "humidity": reading["humidity"]
        }
        
        # Validate
        validation = self.validator.validate_sensor_data(sensor_data)
        
        # Check freshness
        is_fresh, freshness_msg = self.validator.check_data_freshness(
            reading["timestamp"],
            DATA_FRESHNESS_MINUTES
        )
        
        result = {
            "success": validation["is_valid"],
            "source": "ThingSpeak",
            "timestamp": reading["timestamp"],
            "data": sensor_data,
            "validation": validation,
            "is_fresh": is_fresh,
            "message": freshness_msg if not is_fresh else "Data received successfully"
        }
        
        # Cache successful results
        if result["success"]:
            self._last_data = result
            self._last_fetch_time = datetime.now()
        
        return result
    
    def get_historical_data(
        self,
        days: int = 7,
        force_refresh: bool = False
    ) -> Optional[pd.DataFrame]:
        """
        Get historical sensor data.
        
        Args:
            days: Number of days of history
            force_refresh: Force refresh from source
            
        Returns:
            DataFrame with historical data or None
        """
        if self.demo_mode:
            # Generate more demo data for historical view
            num_records = min(days * 24 * 12, 1000)  # Up to 1000 records
            df = get_demo_data(num_records=num_records)
            
            # Validate each row
            for idx, row in df.iterrows():
                sensor_data = {
                    "soil_moisture": row["soil_moisture"],
                    "soil_ph": row["soil_ph"],
                    "temperature": row["temperature"],
                    "humidity": row["humidity"]
                }
                validation = self.validator.validate_sensor_data(sensor_data)
                df.at[idx, "validation_status"] = "valid" if validation["is_valid"] else "invalid"
            
            return df
        else:
            df = self.thingspeak.get_historical_data(days=days, use_cache=not force_refresh)
            
            if df is None or df.empty:
                return None
            
            # Validate each row
            for idx, row in df.iterrows():
                sensor_data = {
                    "soil_moisture": row["soil_moisture"],
                    "soil_ph": row["soil_ph"],
                    "temperature": row["temperature"],
                    "humidity": row["humidity"]
                }
                validation = self.validator.validate_sensor_data(sensor_data)
                df.at[idx, "validation_status"] = "valid" if validation["is_valid"] else "invalid"
            
            # Clean the dataframe
            df, stats = self.validator.clean_dataframe(df)
            
            return df
    
    def get_summary_statistics(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """
        Calculate summary statistics for sensor data.
        
        Args:
            df: DataFrame with sensor data
            
        Returns:
            Dictionary with statistics for each sensor
        """
        if df is None or df.empty:
            return {}
        
        stats = {}
        sensor_cols = ["soil_moisture", "soil_ph", "temperature", "humidity"]
        
        for col in sensor_cols:
            if col in df.columns:
                stats[col] = {
                    "current": df[col].iloc[-1] if len(df) > 0 else None,
                    "min": df[col].min(),
                    "max": df[col].max(),
                    "mean": df[col].mean(),
                    "median": df[col].median(),
                    "std": df[col].std()
                }
        
        return stats

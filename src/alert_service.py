"""
Alert and notification service for sensor monitoring
"""
from typing import List, Dict
from datetime import datetime
from src.config import ALERT_THRESHOLDS, SENSOR_RANGES


class AlertService:
    """Service for generating alerts based on sensor readings"""
    
    def __init__(self, custom_thresholds: Dict = None):
        """
        Initialize alert service.
        
        Args:
            custom_thresholds: Optional custom thresholds to override defaults
        """
        self.thresholds = custom_thresholds if custom_thresholds else ALERT_THRESHOLDS.copy()
    
    def update_thresholds(self, sensor_type: str, min_val: float = None, max_val: float = None):
        """Update thresholds for a specific sensor"""
        if sensor_type not in self.thresholds:
            self.thresholds[sensor_type] = {}
        
        if min_val is not None:
            self.thresholds[sensor_type]["min"] = min_val
        if max_val is not None:
            self.thresholds[sensor_type]["max"] = max_val
    
    def check_sensor_alert(
        self,
        sensor_type: str,
        value: float,
        timestamp: datetime = None
    ) -> Dict[str, any]:
        """
        Check if a sensor reading triggers an alert.
        
        Args:
            sensor_type: Type of sensor
            value: Sensor reading
            timestamp: Optional timestamp
            
        Returns:
            Dictionary with alert information
        """
        if sensor_type not in self.thresholds:
            return {
                "has_alert": False,
                "severity": None,
                "message": None
            }
        
        threshold = self.thresholds[sensor_type]
        min_threshold = threshold.get("min")
        max_threshold = threshold.get("max")
        
        # Check thresholds
        if min_threshold is not None and value < min_threshold:
            return {
                "has_alert": True,
                "severity": "warning",
                "sensor": sensor_type,
                "value": value,
                "threshold": min_threshold,
                "condition": "below",
                "message": f"{sensor_type} is below threshold: {value:.2f} < {min_threshold}",
                "timestamp": timestamp or datetime.now()
            }
        
        if max_threshold is not None and value > max_threshold:
            return {
                "has_alert": True,
                "severity": "warning",
                "sensor": sensor_type,
                "value": value,
                "threshold": max_threshold,
                "condition": "above",
                "message": f"{sensor_type} is above threshold: {value:.2f} > {max_threshold}",
                "timestamp": timestamp or datetime.now()
            }
        
        return {
            "has_alert": False,
            "severity": None,
            "message": None
        }
    
    def check_all_sensors(self, sensor_data: Dict[str, float]) -> List[Dict]:
        """
        Check all sensor readings for alerts.
        
        Args:
            sensor_data: Dictionary with sensor readings
            
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        for sensor_type, value in sensor_data.items():
            if value is None:
                continue
            
            alert = self.check_sensor_alert(sensor_type, value)
            if alert["has_alert"]:
                alerts.append(alert)
        
        return alerts
    
    def check_data_freshness(
        self,
        last_update: datetime,
        max_age_minutes: int = 30
    ) -> Dict[str, any]:
        """
        Check if data is stale.
        
        Args:
            last_update: Timestamp of last update
            max_age_minutes: Maximum age in minutes
            
        Returns:
            Alert dictionary if data is stale
        """
        if last_update is None:
            return {
                "has_alert": True,
                "severity": "critical",
                "sensor": "system",
                "message": "No data received - timestamp unavailable",
                "timestamp": datetime.now()
            }
        
        age_minutes = (datetime.now() - last_update).total_seconds() / 60
        
        if age_minutes > max_age_minutes:
            return {
                "has_alert": True,
                "severity": "warning",
                "sensor": "system",
                "value": age_minutes,
                "threshold": max_age_minutes,
                "message": f"Data is stale: {age_minutes:.1f} minutes old (max: {max_age_minutes})",
                "timestamp": datetime.now()
            }
        
        return {
            "has_alert": False,
            "severity": None,
            "message": None
        }
    
    def get_alert_summary(self, alerts: List[Dict]) -> Dict[str, any]:
        """
        Generate a summary of alerts.
        
        Args:
            alerts: List of alert dictionaries
            
        Returns:
            Summary dictionary
        """
        if not alerts:
            return {
                "total_alerts": 0,
                "critical": 0,
                "warning": 0,
                "status": "healthy"
            }
        
        critical_count = sum(1 for a in alerts if a.get("severity") == "critical")
        warning_count = sum(1 for a in alerts if a.get("severity") == "warning")
        
        status = "healthy"
        if critical_count > 0:
            status = "critical"
        elif warning_count > 0:
            status = "warning"
        
        return {
            "total_alerts": len(alerts),
            "critical": critical_count,
            "warning": warning_count,
            "status": status
        }

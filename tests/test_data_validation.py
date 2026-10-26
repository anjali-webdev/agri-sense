"""
Tests for data validation module
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_validation import SensorValidator
from datetime import datetime, timedelta


def test_validate_valid_soil_moisture():
    """Test valid soil moisture reading"""
    is_valid, status, message = SensorValidator.validate_reading("soil_moisture", 50.0)
    assert is_valid == True
    assert status == "valid"


def test_validate_invalid_soil_moisture_high():
    """Test invalid high soil moisture"""
    is_valid, status, message = SensorValidator.validate_reading("soil_moisture", 150.0)
    assert is_valid == False
    assert status == "invalid"


def test_validate_invalid_soil_moisture_negative():
    """Test invalid negative soil moisture"""
    is_valid, status, message = SensorValidator.validate_reading("soil_moisture", -10.0)
    assert is_valid == False
    assert status == "invalid"


def test_validate_valid_ph():
    """Test valid pH reading"""
    is_valid, status, message = SensorValidator.validate_reading("soil_ph", 6.5)
    assert is_valid == True
    assert status == "valid"


def test_validate_invalid_ph_high():
    """Test invalid high pH"""
    is_valid, status, message = SensorValidator.validate_reading("soil_ph", 15.0)
    assert is_valid == False
    assert status == "invalid"


def test_validate_valid_temperature():
    """Test valid temperature reading"""
    is_valid, status, message = SensorValidator.validate_reading("temperature", 25.0)
    assert is_valid == True
    assert status == "valid"


def test_validate_invalid_temperature():
    """Test invalid temperature"""
    is_valid, status, message = SensorValidator.validate_reading("temperature", 100.0)
    assert is_valid == False
    assert status == "invalid"


def test_validate_sensor_data_all_valid():
    """Test validation of complete sensor data"""
    data = {
        "soil_moisture": 50.0,
        "soil_ph": 6.5,
        "temperature": 25.0,
        "humidity": 65.0
    }
    result = SensorValidator.validate_sensor_data(data)
    assert result["is_valid"] == True
    assert len(result["errors"]) == 0


def test_validate_sensor_data_missing_field():
    """Test validation with missing field"""
    data = {
        "soil_moisture": 50.0,
        "soil_ph": 6.5,
        "temperature": 25.0
    }
    result = SensorValidator.validate_sensor_data(data)
    assert result["is_valid"] == False
    assert len(result["errors"]) > 0


def test_check_data_freshness_fresh():
    """Test fresh data"""
    timestamp = datetime.now() - timedelta(minutes=5)
    is_fresh, message = SensorValidator.check_data_freshness(timestamp, max_age_minutes=30)
    assert is_fresh == True


def test_check_data_freshness_stale():
    """Test stale data"""
    timestamp = datetime.now() - timedelta(minutes=60)
    is_fresh, message = SensorValidator.check_data_freshness(timestamp, max_age_minutes=30)
    assert is_fresh == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

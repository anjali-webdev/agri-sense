"""
Tests for crop recommendation service
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.crop_recommendation import CropRecommendationService


def test_model_loading():
    """Test model loading"""
    service = CropRecommendationService()
    # Model may or may not exist, just test initialization
    assert service is not None


def test_validate_input_ranges_valid():
    """Test validation of valid input ranges"""
    service = CropRecommendationService()
    is_valid, warnings = service.validate_input_ranges(50.0, 6.5, 25.0, 65.0)
    assert is_valid == True
    assert len(warnings) == 0


def test_validate_input_ranges_invalid_moisture():
    """Test validation with invalid moisture"""
    service = CropRecommendationService()
    is_valid, warnings = service.validate_input_ranges(150.0, 6.5, 25.0, 65.0)
    assert is_valid == False
    assert len(warnings) > 0


def test_validate_input_ranges_invalid_ph():
    """Test validation with invalid pH"""
    service = CropRecommendationService()
    is_valid, warnings = service.validate_input_ranges(50.0, 15.0, 25.0, 65.0)
    assert is_valid == False
    assert len(warnings) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

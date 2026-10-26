"""
Tests for ThingSpeak service
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.thingspeak_service import ThingSpeakService


def test_thingspeak_service_initialization():
    """Test ThingSpeak service initialization"""
    service = ThingSpeakService()
    assert service is not None


def test_thingspeak_is_configured():
    """Test configuration check"""
    service = ThingSpeakService()
    # Will return False if not configured (expected in test environment)
    result = service.is_configured()
    assert isinstance(result, bool)


def test_cache_key_generation():
    """Test cache key generation"""
    service = ThingSpeakService()
    key = service._get_cache_key("/test", {"param1": "value1", "param2": "value2"})
    assert "param1=value1" in key
    assert "param2=value2" in key


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

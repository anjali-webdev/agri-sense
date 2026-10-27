"""
ThingSpeak cloud service integration
"""
import requests
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import pandas as pd
import time
from src.config import (
    THINGSPEAK_CHANNEL_ID,
    THINGSPEAK_READ_API_KEY,
    THINGSPEAK_BASE_URL,
    THINGSPEAK_TIMEOUT,
    THINGSPEAK_CACHE_DURATION
)


class ThingSpeakService:
    """Service for fetching data from ThingSpeak IoT platform"""
    
    def __init__(self):
        self.channel_id = THINGSPEAK_CHANNEL_ID
        self.read_api_key = THINGSPEAK_READ_API_KEY
        self.base_url = THINGSPEAK_BASE_URL
        self.timeout = THINGSPEAK_TIMEOUT
        self._cache = {}
        self._cache_timestamp = {}
    
    def _get_cache_key(self, endpoint: str, params: Dict) -> str:
        """Generate cache key from endpoint and parameters"""
        param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
        return f"{endpoint}?{param_str}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self._cache_timestamp:
            return False
        
        age = time.time() - self._cache_timestamp[cache_key]
        return age < THINGSPEAK_CACHE_DURATION
    
    def is_configured(self) -> bool:
        """Check if ThingSpeak is properly configured"""
        return bool(self.channel_id)
    
    def fetch_channel_feeds(
        self,
        results: int = 100,
        use_cache: bool = True
    ) -> Dict[str, any]:
        """
        Fetch channel feeds from ThingSpeak.
        
        Args:
            results: Number of results to fetch (max 8000)
            use_cache: Whether to use cached data if available
            
        Returns:
            Dictionary with status and data
        """
        if not self.is_configured():
            return {
                "success": False,
                "error": "ThingSpeak not configured. Please set THINGSPEAK_CHANNEL_ID.",
                "data": None
            }
        
        # Build request URL
        url = f"{self.base_url}/channels/{self.channel_id}/feeds.json"
        params = {"results": min(results, 8000)}
        
        # Add API key if available
        if self.read_api_key:
            params["api_key"] = self.read_api_key
        
        # Check cache
        cache_key = self._get_cache_key(url, params)
        if use_cache and self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            result = {
                "success": True,
                "error": None,
                "data": data,
                "timestamp": datetime.now()
            }
            
            # Update cache
            self._cache[cache_key] = result
            self._cache_timestamp[cache_key] = time.time()
            
            return result
            
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "ThingSpeak request timed out. Please check your internet connection.",
                "data": None
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Cannot connect to ThingSpeak. Please check your internet connection.",
                "data": None
            }
        except requests.exceptions.HTTPError as e:
            return {
                "success": False,
                "error": f"ThingSpeak HTTP error: {e.response.status_code}",
                "data": None
            }
        except ValueError:
            return {
                "success": False,
                "error": "Invalid JSON response from ThingSpeak",
                "data": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "data": None
            }
    
    def parse_feeds_to_dataframe(self, feeds_data: Dict) -> Optional[pd.DataFrame]:
        """
        Parse ThingSpeak feeds data into a pandas DataFrame.
        
        Args:
            feeds_data: Response from fetch_channel_feeds
            
        Returns:
            DataFrame with parsed sensor data or None
        """
        if not feeds_data.get("success") or not feeds_data.get("data"):
            return None
        
        data = feeds_data["data"]
        feeds = data.get("feeds", [])
        
        if not feeds:
            return None
        
        # Parse feeds into records
        records = []
        for feed in feeds:
            try:
                # Parse timestamp from ThingSpeak (UTC)
                ts = pd.to_datetime(feed.get("created_at"))
                
                # Convert UTC to local timezone (IST = UTC+5:30)
                if hasattr(ts, 'tz_localize'):
                    if ts.tzinfo is None:
                        # If naive, assume UTC
                        ts = ts.tz_localize('UTC')
                    # Convert to IST (Indian Standard Time)
                    ts = ts.tz_convert('Asia/Kolkata')
                    # Keep as timezone-aware for accurate display
                
                record = {
                    "timestamp": ts,
                    "soil_moisture": float(feed.get("field1")) if feed.get("field1") else None,
                    "soil_ph": float(feed.get("field2")) if feed.get("field2") else None,
                    "temperature": float(feed.get("field3")) if feed.get("field3") else None,
                    "humidity": float(feed.get("field4")) if feed.get("field4") else None,
                    "source": "ThingSpeak",
                    "validation_status": "pending"
                }
                records.append(record)
            except (ValueError, TypeError):
                # Skip invalid records
                continue
        
        if not records:
            return None
        
        df = pd.DataFrame(records)
        return df
    
    def get_latest_reading(self) -> Optional[Dict[str, any]]:
        """
        Get the latest sensor reading from ThingSpeak.
        
        Returns:
            Dictionary with latest sensor values or None
        """
        result = self.fetch_channel_feeds(results=1, use_cache=False)
        df = self.parse_feeds_to_dataframe(result)
        
        if df is None or df.empty:
            return None
        
        latest = df.iloc[-1]
        return {
            "timestamp": latest["timestamp"],
            "soil_moisture": latest["soil_moisture"],
            "soil_ph": latest["soil_ph"],
            "temperature": latest["temperature"],
            "humidity": latest["humidity"],
            "source": latest["source"]
        }
    
    def get_historical_data(
        self,
        days: int = 7,
        use_cache: bool = True
    ) -> Optional[pd.DataFrame]:
        """
        Get historical sensor data from ThingSpeak.
        
        Args:
            days: Number of days of history to fetch
            use_cache: Whether to use cached data
            
        Returns:
            DataFrame with historical data or None
        """
        # Calculate number of results needed (assuming 1 reading per 5 minutes)
        results = min(days * 24 * 12, 8000)
        
        result = self.fetch_channel_feeds(results=results, use_cache=use_cache)
        df = self.parse_feeds_to_dataframe(result)
        
        if df is None:
            return None
        
        # Filter to requested time range
        cutoff = datetime.now() - timedelta(days=days)
        df = df[df["timestamp"] >= cutoff].copy()
        
        return df
    
    def clear_cache(self):
        """Clear all cached data"""
        self._cache.clear()
        self._cache_timestamp.clear()

"""
Crop recommendation using machine learning
"""
import joblib
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import numpy as np
from src.config import MODEL_PATH, MODEL_METADATA_PATH


class CropRecommendationService:
    """Service for crop recommendation using trained ML model"""
    
    def __init__(self):
        self.model = None
        self.metadata = None
        self.is_loaded = False
        self._load_model()
    
    def _load_model(self):
        """Load trained model and metadata"""
        try:
            if not MODEL_PATH.exists():
                return
            
            self.model = joblib.load(MODEL_PATH)
            
            if MODEL_METADATA_PATH.exists():
                with open(MODEL_METADATA_PATH, 'r') as f:
                    self.metadata = json.load(f)
            
            self.is_loaded = True
            
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
            self.metadata = None
            self.is_loaded = False
    
    def is_model_available(self) -> bool:
        """Check if model is loaded and ready"""
        return self.is_loaded and self.model is not None
    
    def get_model_info(self) -> Optional[Dict]:
        """Get model metadata information"""
        if not self.metadata:
            return None
        
        return {
            "algorithm": self.metadata.get("algorithm", "Unknown"),
            "training_date": self.metadata.get("training_date", "Unknown"),
            "dataset_source": self.metadata.get("dataset_source", "Unknown"),
            "n_samples": self.metadata.get("n_samples", 0),
            "n_classes": self.metadata.get("n_classes", 0),
            "feature_names": self.metadata.get("feature_names", []),
            "class_names": self.metadata.get("class_names", []),
            "test_accuracy": self.metadata.get("test_accuracy", 0),
            "macro_f1": self.metadata.get("macro_f1", 0),
            "weighted_f1": self.metadata.get("weighted_f1", 0)
        }
    
    def predict_crop(
        self,
        soil_moisture: float,
        soil_ph: float,
        temperature: float,
        humidity: float
    ) -> Dict[str, any]:
        """
        Predict suitable crop based on sensor readings.
        
        Args:
            soil_moisture: Soil moisture percentage
            soil_ph: Soil pH value
            temperature: Air temperature in Celsius
            humidity: Relative humidity percentage
            
        Returns:
            Dictionary with prediction results
        """
        if not self.is_model_available():
            return {
                "success": False,
                "error": "Model not trained. Please run scripts/train_model.py first.",
                "predicted_crop": None,
                "probabilities": None
            }
        
        try:
            # Prepare input features in correct order
            expected_features = self.metadata.get("feature_names", [
                "soil_moisture", "soil_ph", "temperature", "humidity"
            ])
            
            # Create feature array
            features = np.array([[soil_moisture, soil_ph, temperature, humidity]])
            
            # Make prediction
            prediction = self.model.predict(features)[0]
            
            # Get probabilities if available
            probabilities = None
            if hasattr(self.model, 'predict_proba'):
                proba = self.model.predict_proba(features)[0]
                class_names = self.metadata.get("class_names", [])
                
                if class_names:
                    # Create probability dictionary
                    prob_dict = {
                        class_names[i]: float(proba[i])
                        for i in range(len(class_names))
                    }
                    # Sort by probability
                    probabilities = dict(
                        sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)
                    )
            
            return {
                "success": True,
                "error": None,
                "predicted_crop": prediction,
                "probabilities": probabilities,
                "input_features": {
                    "soil_moisture": soil_moisture,
                    "soil_ph": soil_ph,
                    "temperature": temperature,
                    "humidity": humidity
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Prediction error: {str(e)}",
                "predicted_crop": None,
                "probabilities": None
            }
    
    def get_top_n_crops(
        self,
        soil_moisture: float,
        soil_ph: float,
        temperature: float,
        humidity: float,
        n: int = 3
    ) -> List[Tuple[str, float]]:
        """
        Get top N crop recommendations with scores.
        
        Args:
            soil_moisture: Soil moisture percentage
            soil_ph: Soil pH value
            temperature: Air temperature in Celsius
            humidity: Relative humidity percentage
            n: Number of top recommendations
            
        Returns:
            List of tuples (crop_name, probability)
        """
        result = self.predict_crop(soil_moisture, soil_ph, temperature, humidity)
        
        if not result["success"] or not result["probabilities"]:
            return []
        
        # Get top N from probabilities
        probs = result["probabilities"]
        top_n = list(probs.items())[:n]
        
        return top_n
    
    def validate_input_ranges(
        self,
        soil_moisture: float,
        soil_ph: float,
        temperature: float,
        humidity: float
    ) -> Tuple[bool, List[str]]:
        """
        Validate if input values are within reasonable ranges.
        
        Args:
            soil_moisture: Soil moisture percentage
            soil_ph: Soil pH value
            temperature: Air temperature in Celsius
            humidity: Relative humidity percentage
            
        Returns:
            Tuple of (is_valid, list of warnings)
        """
        warnings = []
        
        # Check basic physical ranges
        if not (0 <= soil_moisture <= 100):
            warnings.append(f"Soil moisture {soil_moisture}% is outside valid range [0, 100]")
        
        if not (0 <= soil_ph <= 14):
            warnings.append(f"Soil pH {soil_ph} is outside valid range [0, 14]")
        
        if not (-40 <= temperature <= 85):
            warnings.append(f"Temperature {temperature}°C is outside valid range [-40, 85]")
        
        if not (0 <= humidity <= 100):
            warnings.append(f"Humidity {humidity}% is outside valid range [0, 100]")
        
        is_valid = len(warnings) == 0
        
        return is_valid, warnings

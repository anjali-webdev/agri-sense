"""
Download Real Agricultural Dataset for Crop Recommendation
"""
import pandas as pd
import requests
from pathlib import Path

print("=" * 60)
print("  Download Real Crop Recommendation Dataset")
print("=" * 60)
print()

# Kaggle Crop Recommendation Dataset (modified for our features)
# This is a popular agricultural dataset with NPK, temperature, humidity, pH, rainfall

print("Downloading dataset from online source...")
print()

# URL for a real agricultural dataset
url = "https://raw.githubusercontent.com/atharvapatil1210/his-repo/master/Crop_recommendation.csv"

try:
    print(f"Fetching from: {url}")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    
    # Save original dataset
    original_path = Path("data/original_crop_data.csv")
    with open(original_path, 'wb') as f:
        f.write(response.content)
    
    print(f"✓ Downloaded to: {original_path}")
    print()
    
    # Load and inspect
    df = pd.read_csv(original_path)
    print("Dataset Info:")
    print(f"  Rows: {len(df)}")
    print(f"  Columns: {list(df.columns)}")
    print()
    
    # Check what we have
    print("Available columns:")
    for col in df.columns:
        print(f"  - {col}")
    print()
    
    # Transform for our model (soil_moisture, soil_ph, temperature, humidity)
    # We'll derive soil_moisture from available data
    
    if 'rainfall' in df.columns and 'humidity' in df.columns:
        # Create soil moisture estimate from rainfall and humidity
        # This is a simplified approach - real soil moisture depends on many factors
        df_transformed = pd.DataFrame()
        
        # Normalize rainfall to 0-100 scale as moisture proxy
        rain_min = df['rainfall'].min()
        rain_max = df['rainfall'].max()
        df_transformed['soil_moisture'] = ((df['rainfall'] - rain_min) / (rain_max - rain_min) * 50 + 
                                           df['humidity'] * 0.3).clip(20, 80)
        
        df_transformed['soil_ph'] = df['ph'] if 'ph' in df.columns else 6.5
        df_transformed['temperature'] = df['temperature'] if 'temperature' in df.columns else 25.0
        df_transformed['humidity'] = df['humidity'] if 'humidity' in df.columns else 65.0
        df_transformed['crop'] = df['label'] if 'label' in df.columns else df['crop']
        
        # Save transformed dataset
        output_path = Path("data/crop_dataset_real.csv")
        df_transformed.to_csv(output_path, index=False)
        
        print("=" * 60)
        print("✓ Dataset transformed and saved!")
        print("=" * 60)
        print()
        print(f"Output file: {output_path}")
        print(f"Total samples: {len(df_transformed)}")
        print(f"Crops: {df_transformed['crop'].nunique()}")
        print()
        print("Crop distribution:")
        print(df_transformed['crop'].value_counts().head(10))
        print()
        print("To use this dataset:")
        print("1. Backup current: copy data\\crop_dataset.csv data\\crop_dataset_backup.csv")
        print("2. Replace: copy data\\crop_dataset_real.csv data\\crop_dataset.csv")
        print("3. Train: python scripts\\train_model.py")
        print()
    else:
        print("⚠️  Dataset structure different than expected")
        print("Original dataset saved for manual inspection")
        print()
        print("You can:")
        print("1. Inspect: data/original_crop_data.csv")
        print("2. Manually create dataset with required columns:")
        print("   soil_moisture, soil_ph, temperature, humidity, crop")
        
except requests.exceptions.RequestException as e:
    print(f"❌ Error downloading dataset: {e}")
    print()
    print("Alternative: Manual dataset creation")
    print("See instructions below...")
    print()

print("=" * 60)
print("Manual Dataset Creation (If download failed)")
print("=" * 60)
print()
print("Create CSV file: data/crop_dataset.csv")
print()
print("Required columns:")
print("soil_moisture,soil_ph,temperature,humidity,crop")
print()
print("Example rows:")
print("45.2,6.5,25.3,65.5,Rice")
print("32.1,7.2,28.5,55.2,Wheat")
print("68.5,5.8,22.1,75.8,Cotton")
print()
print("Data sources:")
print("- Agricultural research papers")
print("- Government agricultural databases")
print("- Kaggle datasets")
print("- University agricultural extensions")
print("- Your own field measurements")
print()

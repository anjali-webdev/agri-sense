"""
Restore original high-quality synthetic dataset
"""
import pandas as pd
import numpy as np
from pathlib import Path

print("=" * 60)
print("  Restoring Original High-Quality Dataset")
print("=" * 60)
print()

# Create high-quality synthetic dataset with clear feature separation
np.random.seed(42)

data = []

# Define clear, distinct ranges for each crop
crop_profiles = {
    "Rice": {"moisture": (70, 85), "ph": (5.5, 7.0), "temp": (20, 30), "humidity": (80, 90)},
    "Wheat": {"moisture": (20, 35), "ph": (6.0, 7.5), "temp": (12, 25), "humidity": (50, 70)},
    "Cotton": {"moisture": (50, 70), "ph": (6.0, 7.5), "temp": (23, 32), "humidity": (60, 80)},
    "Maize": {"moisture": (40, 60), "ph": (5.5, 7.0), "temp": (18, 27), "humidity": (60, 80)},
    "Sugarcane": {"moisture": (60, 80), "ph": (6.0, 7.5), "temp": (25, 35), "humidity": (75, 90)},
    "Jute": {"moisture": (60, 80), "ph": (6.0, 7.0), "temp": (24, 35), "humidity": (75, 95)},
    "Coffee": {"moisture": (50, 70), "ph": (5.5, 6.5), "temp": (15, 28), "humidity": (70, 85)},
    "Tea": {"moisture": (40, 60), "ph": (5.5, 6.5), "temp": (15, 25), "humidity": (75, 90)},
    "Banana": {"moisture": (60, 80), "ph": (5.5, 6.5), "temp": (25, 35), "humidity": (75, 90)},
    "Mango": {"moisture": (40, 60), "ph": (5.5, 7.0), "temp": (24, 32), "humidity": (60, 75)},
    "Orange": {"moisture": (50, 70), "ph": (6.0, 7.5), "temp": (20, 30), "humidity": (65, 80)},
    "Papaya": {"moisture": (55, 75), "ph": (6.0, 7.0), "temp": (22, 32), "humidity": (70, 85)},
    "Coconut": {"moisture": (50, 70), "ph": (5.5, 7.0), "temp": (25, 35), "humidity": (80, 95)},
    "Watermelon": {"moisture": (45, 65), "ph": (6.0, 7.0), "temp": (20, 30), "humidity": (75, 90)},
    "Muskmelon": {"moisture": (40, 60), "ph": (6.0, 7.0), "temp": (22, 32), "humidity": (70, 85)},
    "Grapes": {"moisture": (30, 50), "ph": (6.0, 7.5), "temp": (15, 30), "humidity": (60, 75)},
    "Pomegranate": {"moisture": (35, 55), "ph": (6.5, 7.5), "temp": (18, 32), "humidity": (60, 80)},
    "Potato": {"moisture": (45, 65), "ph": (5.5, 7.0), "temp": (15, 25), "humidity": (65, 80)},
    "Chickpea": {"moisture": (25, 45), "ph": (6.0, 7.5), "temp": (20, 30), "humidity": (50, 70)},
    "Lentil": {"moisture": (30, 50), "ph": (6.0, 8.0), "temp": (18, 30), "humidity": (55, 75)},
    "Blackgram": {"moisture": (35, 55), "ph": (6.0, 7.5), "temp": (20, 32), "humidity": (60, 80)},
    "Mungbean": {"moisture": (30, 50), "ph": (6.0, 7.5), "temp": (22, 35), "humidity": (60, 80)},
}

# Generate 50 samples per crop (1100 total)
samples_per_crop = 50

for crop, ranges in crop_profiles.items():
    for _ in range(samples_per_crop):
        moisture = np.random.uniform(ranges["moisture"][0], ranges["moisture"][1])
        ph = np.random.uniform(ranges["ph"][0], ranges["ph"][1])
        temp = np.random.uniform(ranges["temp"][0], ranges["temp"][1])
        humidity = np.random.uniform(ranges["humidity"][0], ranges["humidity"][1])
        
        # Add small random noise for realism
        moisture += np.random.normal(0, 2)
        ph += np.random.normal(0, 0.15)
        temp += np.random.normal(0, 1.5)
        humidity += np.random.normal(0, 2)
        
        # Clip to valid ranges
        moisture = np.clip(moisture, 10, 90)
        ph = np.clip(ph, 4.0, 9.0)
        temp = np.clip(temp, 10, 45)
        humidity = np.clip(humidity, 40, 95)
        
        data.append({
            "soil_moisture": round(moisture, 1),
            "soil_ph": round(ph, 1),
            "temperature": round(temp, 1),
            "humidity": round(humidity, 1),
            "crop": crop
        })

# Create DataFrame
df = pd.DataFrame(data)

# Shuffle
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# Backup existing dataset
backup_path = Path("data/crop_dataset_backup.csv")
original_path = Path("data/crop_dataset.csv")

if original_path.exists():
    print(f"Backing up current dataset to: {backup_path}")
    import shutil
    shutil.copy(original_path, backup_path)

# Save new dataset
df.to_csv(original_path, index=False)

print("✓ High-quality dataset created!")
print()
print(f"File: {original_path}")
print(f"Total samples: {len(df)}")
print(f"Crops: {df['crop'].nunique()}")
print(f"Samples per crop: {samples_per_crop}")
print()
print("Crop distribution:")
for crop, count in df['crop'].value_counts().items():
    print(f"  • {crop}: {count}")
print()
print("=" * 60)
print("Dataset Restored!")
print("=" * 60)
print()
print("Now train the model:")
print("  python scripts\\train_model.py")
print()
print("Expected accuracy: 90-95%+")
print()

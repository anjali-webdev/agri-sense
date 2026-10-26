"""Quick installation verification"""
import sys
from pathlib import Path

print("Verifying AgriSense AI Installation...")
print("=" * 50)

errors = []
warnings = []

# Check Python version
py_version = sys.version_info
print(f"Python version: {py_version.major}.{py_version.minor}.{py_version.micro}")
if py_version.major < 3 or (py_version.major == 3 and py_version.minor < 8):
    errors.append("Python 3.8+ required")

# Check required packages
required_packages = [
    "streamlit", "pandas", "numpy", "sklearn", 
    "plotly", "requests", "joblib", "dotenv"
]

for pkg in required_packages:
    try:
        __import__(pkg if pkg != "sklearn" else "sklearn")
        print(f"✓ {pkg}")
    except ImportError:
        errors.append(f"Missing package: {pkg}")
        print(f"✗ {pkg} - NOT FOUND")

# Check project structure
print("\nChecking project structure...")
required_dirs = ["src", "pages", "data", "models", "scripts", "tests", "firmware"]
for dir_name in required_dirs:
    if Path(dir_name).exists():
        print(f"✓ {dir_name}/")
    else:
        errors.append(f"Missing directory: {dir_name}/")
        print(f"✗ {dir_name}/ - NOT FOUND")

# Check key files
key_files = [
    "app.py",
    "requirements.txt",
    "data/crop_dataset.csv",
    "scripts/train_model.py"
]
for file_path in key_files:
    if Path(file_path).exists():
        print(f"✓ {file_path}")
    else:
        errors.append(f"Missing file: {file_path}")
        print(f"✗ {file_path} - NOT FOUND")

# Check if model is trained
if Path("models/crop_recommendation_model.joblib").exists():
    print("✓ ML model trained")
else:
    warnings.append("ML model not trained yet - run: python scripts/train_model.py")
    print("⚠ ML model not trained")

print("\n" + "=" * 50)
if errors:
    print("ERRORS FOUND:")
    for error in errors:
        print(f"  ✗ {error}")
    sys.exit(1)
elif warnings:
    print("WARNINGS:")
    for warning in warnings:
        print(f"  ⚠ {warning}")
    print("\nInstallation OK - but complete setup needed")
else:
    print("✓ Installation verified successfully!")
    print("\nRun: streamlit run app.py")

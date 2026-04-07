#!/usr/bin/env python3
"""
Setup dataset directories and download instructions for Traffic Violation Detection
"""

import os
from pathlib import Path
import json

def create_dataset_structure():
    """Create complete dataset directory structure"""
    
    # Main dataset directory
    dataset_dir = Path("dataset")
    dataset_dir.mkdir(exist_ok=True)
    
    # Subdirectories
    subdirs = [
        "helmet/with_helmet",
        "helmet/without_helmet", 
        "anpr/images",
        "anpr/annotations",
        "traffic_violations/images",
        "traffic_violations/videos",
        "traffic_violations/annotations",
        "models"
    ]
    
    for subdir in subdirs:
        (dataset_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    print("Dataset directory structure created:")
    for subdir in subdirs:
        print(f"  dataset/{subdir}")
    
    return dataset_dir

def create_download_instructions(dataset_dir):
    """Create download instructions file"""
    
    instructions = """
TRAFFIC VIOLATION DETECTION SYSTEM - DATASET DOWNLOAD GUIDE
==========================================================

1. HELMET DETECTION DATASET
---------------------------
Option 1: Kaggle Dataset
- URL: https://www.kaggle.com/datasets/andrewmvd/helmet-detection
- Command: kaggle datasets download -d andrewmvd/helmet-detection
- Extract to: dataset/helmet/

Option 2: Open Source Dataset
- URL: https://github.com/opencv/opencv/wiki/TensorFlow-Object-Detection-API
- Download helmet detection datasets
- Organize into: dataset/helmet/with_helmet/ and dataset/helmet/without_helmet/

2. ANPR (NUMBER PLATE) DATASET
-------------------------------
Option 1: Indian License Plates
- URL: https://github.com/sergiomsilva/alpr-unconstrained
- Download and extract to: dataset/anpr/

Option 2: Kaggle Dataset
- URL: https://www.kaggle.com/datasets/andrewmvd/license-plate-recognition
- Command: kaggle datasets download -d andrewmvd/license-plate-recognition
- Extract to: dataset/anpr/

3. TRAFFIC VIOLATION DATASET
----------------------------
Option 1: CCTV Traffic Dataset
- URL: https://github.com/amir-hz/CCTV_Traffic_Detection
- Download traffic videos and extract frames

Option 2: UA-DETRAC Dataset
- URL: https://github.com/ua-detrac/ua-detrac
- Download vehicle detection dataset

4. QUICK START WITH SAMPLE DATA
------------------------------
Run: python download_sample_data.py
This will create synthetic sample data for testing.

5. INSTALL KAGGLE API (Optional)
-------------------------------
pip install kaggle
# Download kaggle.json from Kaggle account settings
# Place in: C:/Users/[username]/.kaggle/kaggle.json

6. DATASET FORMATS
------------------
Images: .jpg, .png, .jpeg
Videos: .mp4, .avi, .mov
Annotations: .xml, .json, .txt

7. INDIAN NUMBER PLATE FORMATS
------------------------------
- MH-12-AB-1234 (Maharashtra)
- DL-05-CD-5678 (Delhi)
- KA-03-EF-9012 (Karnataka)
- TN-07-GH-3456 (Tamil Nadu)

After downloading datasets, run:
python demo_with_dataset.py
"""
    
    with open(dataset_dir / "DOWNLOAD_GUIDE.txt", "w") as f:
        f.write(instructions)
    
    print(f"Download guide created: {dataset_dir / 'DOWNLOAD_GUIDE.txt'}")

def create_dataset_configs():
    """Create dataset configuration files"""
    
    # Helmet dataset config
    helmet_config = {
        "name": "Helmet Detection Dataset",
        "path": "dataset/helmet",
        "classes": ["with_helmet", "without_helmet"],
        "nc": 2,
        "download_urls": [
            "https://www.kaggle.com/datasets/andrewmvd/helmet-detection"
        ]
    }
    
    with open("helmet_dataset.json", "w") as f:
        json.dump(helmet_config, f, indent=2)
    
    # ANPR dataset config
    anpr_config = {
        "name": "ANPR Dataset",
        "path": "dataset/anpr", 
        "classes": ["license_plate"],
        "nc": 1,
        "download_urls": [
            "https://www.kaggle.com/datasets/andrewmvd/license-plate-recognition",
            "https://github.com/sergiomsilva/alpr-unconstrained"
        ],
        "indian_patterns": [
            "MH-XX-YY-ZZZZ",
            "DL-XX-YY-ZZZZ", 
            "KA-XX-YY-ZZZZ",
            "TN-XX-YY-ZZZZ"
        ]
    }
    
    with open("anpr_dataset.json", "w") as f:
        json.dump(anpr_config, f, indent=2)
    
    # Traffic violations config
    traffic_config = {
        "name": "Traffic Violations Dataset",
        "path": "dataset/traffic_violations",
        "violation_types": {
            "no_helmet": {"fine": 500, "description": "Riding without helmet"},
            "triple_riding": {"fine": 1000, "description": "More than 2 riders"},
            "signal_jump": {"fine": 500, "description": "Crossing red signal"},
            "overspeeding": {"fine": 2000, "description": "Exceeding speed limit"}
        },
        "download_urls": [
            "https://github.com/amir-hz/CCTV_Traffic_Detection",
            "https://github.com/ua-detrac/ua-detrac"
        ]
    }
    
    with open("traffic_violations_dataset.json", "w") as f:
        json.dump(traffic_config, f, indent=2)
    
    print("Configuration files created:")
    print("  helmet_dataset.json")
    print("  anpr_dataset.json") 
    print("  traffic_violations_dataset.json")

def create_quick_download_script():
    """Create a quick download script for common datasets"""
    
    script_content = '''
# Quick Download Script for Common Datasets
# Run these commands in your terminal

# 1. Install Kaggle API
pip install kaggle

# 2. Download Helmet Detection Dataset
kaggle datasets download -d andrewmvd/helmet-detection
unzip helmet-detection.zip -d dataset/helmet/

# 3. Download License Plate Dataset  
kaggle datasets download -d andrewmvd/license-plate-recognition
unzip license-plate-recognition.zip -d dataset/anpr/

# 4. Alternative: Use wget/curl for direct downloads
# wget https://example.com/dataset.zip

# 5. After downloading, run the demo
python demo_with_dataset.py
'''
    
    with open("quick_download.sh", "w") as f:
        f.write(script_content)
    
    # Windows batch file version
    batch_content = '''
@echo off
REM Quick Download Script for Windows

REM 1. Install Kaggle API
pip install kaggle

REM 2. Download Helmet Detection Dataset
kaggle datasets download -d andrewmvd/helmet-detection
powershell -Command "Expand-Archive -Path 'helmet-detection.zip' -DestinationPath 'dataset/helmet/' -Force"

REM 3. Download License Plate Dataset
kaggle datasets download -d andrewmvd/license-plate-recognition  
powershell -Command "Expand-Archive -Path 'license-plate-recognition.zip' -DestinationPath 'dataset/anpr/' -Force"

REM 4. Run demo
python demo_with_dataset.py

pause
'''
    
    with open("quick_download.bat", "w") as f:
        f.write(batch_content)
    
    print("Quick download scripts created:")
    print("  quick_download.sh (Linux/Mac)")
    print("  quick_download.bat (Windows)")

def main():
    """Main setup function"""
    print("TRAFFIC VIOLATION DETECTION - DATASET SETUP")
    print("="*50)
    
    # Create directory structure
    dataset_dir = create_dataset_structure()
    
    # Create download instructions
    create_download_instructions(dataset_dir)
    
    # Create configuration files
    create_dataset_configs()
    
    # Create quick download scripts
    create_quick_download_script()
    
    print("\n" + "="*50)
    print("DATASET SETUP COMPLETED!")
    print("="*50)
    
    print("\nNext Steps:")
    print("1. Read: dataset/DOWNLOAD_GUIDE.txt")
    print("2. Install Kaggle API: pip install kaggle")
    print("3. Download datasets using the provided scripts")
    print("4. Run demo: python demo_with_dataset.py")
    print("5. Or use sample data: python download_sample_data.py")
    
    print("\nQuick Start Options:")
    print("- Windows: Run quick_download.bat")
    print("- Linux/Mac: bash quick_download.sh")
    print("- Sample data: python download_sample_data.py")

if __name__ == "__main__":
    main()

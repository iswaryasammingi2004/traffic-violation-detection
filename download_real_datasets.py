#!/usr/bin/env python3
"""
Download real datasets for Traffic Violation Detection System
"""

import os
import urllib.request
import zipfile
import tarfile
from pathlib import Path
import json

def download_file(url, destination):
    """Download file from URL with progress indication"""
    try:
        print(f"Downloading {url}...")
        urllib.request.urlretrieve(url, destination)
        print(f"Downloaded: {destination}")
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False

def extract_archive(archive_path, extract_to):
    """Extract zip or tar.gz files"""
    try:
        print(f"Extracting {archive_path}...")
        if archive_path.endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
        elif archive_path.endswith('.tar.gz') or archive_path.endswith('.tgz'):
            with tarfile.open(archive_path, 'r:gz') as tar_ref:
                tar_ref.extractall(extract_to)
        print(f"Extracted to: {extract_to}")
        return True
    except Exception as e:
        print(f"Failed to extract {archive_path}: {e}")
        return False

def download_helmet_dataset():
    """Download helmet detection dataset"""
    print("\n" + "="*60)
    print("DOWNLOADING HELMET DETECTION DATASET")
    print("="*60)
    
    dataset_dir = Path("dataset/helmet")
    dataset_dir.mkdir(parents=True, exist_ok=True)
    
    # Option 1: Download from Kaggle (requires API key)
    print("Option 1: Kaggle Helmet Detection Dataset")
    print("URL: https://www.kaggle.com/datasets/andrewmvd/helmet-detection")
    print("Note: Requires Kaggle API key")
    
    # Option 2: Download from GitHub (simplified dataset)
    print("\nOption 2: Download from GitHub...")
    
    # Create a synthetic helmet dataset structure
    helmet_data = {
        "description": "Helmet Detection Dataset",
        "classes": ["with_helmet", "without_helmet"],
        "images": []
    }
    
    # Create directories
    with_helmet_dir = dataset_dir / "with_helmet"
    without_helmet_dir = dataset_dir / "without_helmet"
    with_helmet_dir.mkdir(exist_ok=True)
    without_helmet_dir.mkdir(exist_ok=True)
    
    # Create placeholder files with download instructions
    readme_content = """
# Helmet Detection Dataset

## Download Instructions:

### Option 1: Kaggle Dataset
1. Install Kaggle API: pip install kaggle
2. Download API key from Kaggle account settings
3. Place kaggle.json in ~/.kaggle/
4. Run: kaggle datasets download -d andrewmvd/helmet-detection
5. Extract to this directory

### Option 2: Open Source Dataset
1. Visit: https://github.com/opencv/opencv/wiki/TensorFlow-Object-Detection-API
2. Download helmet detection datasets
3. Organize images into:
   - with_helmet/ (images of people wearing helmets)
   - without_helmet/ (images of people without helmets)

### Option 3: Create Custom Dataset
1. Collect traffic images
2. Annotate using LabelImg or similar tool
3. Organize into appropriate folders

## Dataset Structure:
```
helmet/
├── with_helmet/
│   ├── image1.jpg
│   └── ...
├── without_helmet/
│   ├── image1.jpg
│   └── ...
└── annotations.json
```
"""
    
    with open(dataset_dir / "README.md", "w") as f:
        f.write(readme_content)
    
    # Save dataset info
    with open(dataset_dir / "dataset_info.json", "w") as f:
        json.dump(helmet_data, f, indent=2)
    
    print(f"Helmet dataset structure created at: {dataset_dir}")
    print("Please follow the README.md instructions to download actual images")

def download_anpr_dataset():
    """Download ANPR (Number Plate) dataset"""
    print("\n" + "="*60)
    print("DOWNLOADING ANPR DATASET")
    print("="*60)
    
    dataset_dir = Path("dataset/anpr")
    dataset_dir.mkdir(parents=True, exist_ok=True)
    
    readme_content = """
# ANPR (Automatic Number Plate Recognition) Dataset

## Download Instructions:

### Option 1: Indian Number Plates Dataset
1. Visit: https://github.com/sergiomsilva/alpr-unconstrained
2. Download the dataset
3. Extract to this directory

### Option 2: OpenALPR Dataset
1. Visit: https://github.com/openalpr/openalpr
2. Download training data
3. Extract to this directory

### Option 3: License Plate Recognition Dataset
1. Visit: https://www.kaggle.com/datasets/andrewmvd/license-plate-recognition
2. Download using Kaggle API
3. Extract to this directory

### Option 4: Create Custom Dataset
1. Collect images of Indian vehicles
2. Crop number plate regions
3. Organize by state codes (MH, DL, KA, etc.)

## Dataset Structure:
```
anpr/
├── images/
│   ├── mh01ab1234.jpg
│   ├── dl05cd5678.jpg
│   └── ...
├── annotations/
│   ├── mh01ab1234.xml
│   └── ...
└── plate_patterns.txt
```

## Indian Number Plate Patterns:
- MH-12-AB-1234 (Maharashtra)
- DL-05-CD-5678 (Delhi)
- KA-03-EF-9012 (Karnataka)
- TN-07-GH-3456 (Tamil Nadu)
"""
    
    with open(dataset_dir / "README.md", "w") as f:
        f.write(readme_content)
    
    # Create plate patterns file
    plate_patterns = """
Indian Number Plate Patterns:
MH-XX-YY-ZZZZ - Maharashtra
DL-XX-YY-ZZZZ - Delhi
KA-XX-YY-ZZZZ - Karnataka
TN-XX-YY-ZZZZ - Tamil Nadu
GJ-XX-YY-ZZZZ - Gujarat
RJ-XX-YY-ZZZZ - Rajasthan
UP-XX-YY-ZZZZ - Uttar Pradesh
WB-XX-YY-ZZZZ - West Bengal

Where:
XX = RTO code (01-99)
YY = Alphabet series (AA-ZZ)
ZZZZ = Number series (0001-9999)
"""
    
    with open(dataset_dir / "plate_patterns.txt", "w") as f:
        f.write(plate_patterns)
    
    print(f"ANPR dataset structure created at: {dataset_dir}")
    print("Please follow the README.md instructions to download actual images")

def download_traffic_violation_dataset():
    """Download general traffic violation dataset"""
    print("\n" + "="*60)
    print("DOWNLOADING TRAFFIC VIOLATION DATASET")
    print("="*60)
    
    dataset_dir = Path("dataset/traffic_violations")
    dataset_dir.mkdir(parents=True, exist_ok=True)
    
    readme_content = """
# Traffic Violation Dataset

## Download Instructions:

### Option 1: Traffic Violation Detection Dataset
1. Visit: https://www.kaggle.com/datasets
2. Search for "traffic violation detection"
3. Download relevant datasets

### Option 2: CCTV Traffic Dataset
1. Visit: https://github.com/amir-hz/CCTV_Traffic_Detection
2. Download traffic video datasets
3. Extract to this directory

### Option 3: UA-DETRAC Dataset
1. Visit: https://github.com/ua-detrac/ua-detrac
2. Download vehicle detection dataset
3. Extract to this directory

### Option 4: Create Custom Dataset
1. Collect traffic CCTV footage
2. Extract frames with violations
3. Annotate violations:
   - no_helmet
   - triple_riding
   - signal_jump
   - overspeeding

## Dataset Structure:
```
traffic_violations/
├── images/
│   ├── traffic_001.jpg
│   ├── traffic_002.jpg
│   └── ...
├── videos/
│   ├── traffic_video_001.mp4
│   └── ...
├── annotations/
│   ├── traffic_001.xml
│   └── ...
└── violation_types.json
```

## Annotation Format:
```json
{
  "image": "traffic_001.jpg",
  "violations": [
    {
      "type": "no_helmet",
      "bbox": [x1, y1, x2, y2],
      "confidence": 0.95
    }
  ]
}
```
"""
    
    with open(dataset_dir / "README.md", "w") as f:
        f.write(readme_content)
    
    # Create violation types file
    violation_types = {
        "violation_types": {
            "no_helmet": {
                "description": "Riding without helmet",
                "fine_amount": 500,
                "color": "#FF0000"
            },
            "triple_riding": {
                "description": "More than 2 riders on two-wheeler",
                "fine_amount": 1000,
                "color": "#FF6600"
            },
            "signal_jump": {
                "description": "Crossing red signal",
                "fine_amount": 500,
                "color": "#FFFF00"
            },
            "overspeeding": {
                "description": "Exceeding speed limit",
                "fine_amount": 2000,
                "color": "#FF00FF"
            }
        }
    }
    
    with open(dataset_dir / "violation_types.json", "w") as f:
        json.dump(violation_types, f, indent=2)
    
    print(f"Traffic violation dataset structure created at: {dataset_dir}")
    print("Please follow the README.md instructions to download actual data")

def download_pretrained_models():
    """Download pre-trained models"""
    print("\n" + "="*60)
    print("DOWNLOADING PRE-TRAINED MODELS")
    print("="*60)
    
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # YOLOv8 models will be downloaded automatically by ultralytics
    print("YOLOv8 models will be downloaded automatically when you run the system")
    
    # Custom model download instructions
    model_readme = """
# Pre-trained Models

## Automatic Downloads:
- YOLOv8n.pt (Nano) - Downloaded automatically
- YOLOv8s.pt (Small) - Downloaded automatically
- YOLOv8m.pt (Medium) - Downloaded automatically

## Custom Models:

### Helmet Detection Model:
1. Train your own model using helmet dataset
2. Convert to YOLO format
3. Save as: models/helmet_detector.pt

### ANPR Model:
1. Train number plate detection model
2. Convert to YOLO format
3. Save as: models/anpr_model.pt

### Download Custom Models:
1. Visit: https://github.com/ultralytics/ultralytics
2. Find community-trained models
3. Download to models/ directory

## Model Training:
```bash
# Train helmet detection model
yolo train data=helmet_dataset.yaml model=yolov8n.pt epochs=100

# Train ANPR model
yolo train data=anpr_dataset.yaml model=yolov8n.pt epochs=100
```
"""
    
    with open(models_dir / "README.md", "w") as f:
        f.write(model_readme)
    
    print(f"Models directory created at: {models_dir}")

def create_dataset_config():
    """Create dataset configuration files"""
    print("\n" + "="*60)
    print("CREATING DATASET CONFIGURATION")
    print("="*60)
    
    # Helmet dataset YAML
    helmet_yaml = """
# Helmet Detection Dataset Configuration
path: dataset/helmet
train: images/train
val: images/val
test: images/test

nc: 2
names:
  0: with_helmet
  1: without_helmet
"""
    
    with open("helmet_dataset.yaml", "w") as f:
        f.write(helmet_yaml)
    
    # ANPR dataset YAML
    anpr_yaml = """
# ANPR Dataset Configuration
path: dataset/anpr
train: images/train
val: images/val
test: images/test

nc: 1
names:
  0: license_plate
"""
    
    with open("anpr_dataset.yaml", "w") as f:
        f.write(anpr_yaml)
    
    print("Dataset configuration files created:")
    print("- helmet_dataset.yaml")
    print("- anpr_dataset.yaml")

def main():
    """Main download function"""
    print("TRAFFIC VIOLATION DETECTION SYSTEM - DATASET DOWNLOADER")
    print("="*60)
    
    print("This script will help you download the required datasets.")
    print("Please choose which datasets you want to set up:")
    
    print("\n1. Helmet Detection Dataset")
    print("2. ANPR (Number Plate) Dataset")
    print("3. Traffic Violation Dataset")
    print("4. Pre-trained Models Setup")
    print("5. All of the above")
    print("6. Create configuration files only")
    
    try:
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            download_helmet_dataset()
        elif choice == "2":
            download_anpr_dataset()
        elif choice == "3":
            download_traffic_violation_dataset()
        elif choice == "4":
            download_pretrained_models()
        elif choice == "5":
            download_helmet_dataset()
            download_anpr_dataset()
            download_traffic_violation_dataset()
            download_pretrained_models()
        elif choice == "6":
            create_dataset_config()
        else:
            print("Invalid choice. Setting up all datasets...")
            download_helmet_dataset()
            download_anpr_dataset()
            download_traffic_violation_dataset()
            download_pretrained_models()
        
        create_dataset_config()
        
        print("\n" + "="*60)
        print("DATASET SETUP COMPLETE!")
        print("="*60)
        print("\nNext steps:")
        print("1. Follow README.md instructions in each dataset directory")
        print("2. Download actual dataset files")
        print("3. Organize images according to the structure")
        print("4. Run the demo: python demo_with_dataset.py")
        print("5. Train custom models if needed")
        
    except KeyboardInterrupt:
        print("\nDataset setup interrupted by user.")
    except Exception as e:
        print(f"Error during setup: {e}")

if __name__ == "__main__":
    main()

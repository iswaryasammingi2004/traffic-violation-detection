#!/usr/bin/env python3
"""
Setup Kaggle API and download datasets
"""

import os
import json
from pathlib import Path

def setup_kaggle_api():
    """Setup Kaggle API configuration"""
    print("KAGGLE API SETUP")
    print("="*40)
    
    # Create .kaggle directory
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_dir.mkdir(exist_ok=True)
    
    kaggle_json = kaggle_dir / "kaggle.json"
    
    if kaggle_json.exists():
        print("✓ Kaggle API key already found!")
        return True
    
    print("Kaggle API key not found!")
    print("\nTo get your Kaggle API key:")
    print("1. Go to https://www.kaggle.com/account")
    print("2. Click 'Create New API Token'")
    print("3. Download the kaggle.json file")
    print("4. Place it in:", kaggle_dir)
    print("\nOr enter your credentials manually:")
    
    try:
        username = input("Kaggle username: ").strip()
        key = input("Kaggle API key: ").strip()
        
        if username and key:
            api_config = {"username": username, "key": key}
            with open(kaggle_json, "w") as f:
                json.dump(api_config, f)
            
            # Set file permissions (Windows doesn't have chmod 600)
            print(f"✓ Kaggle API configured successfully!")
            print(f"  Config file: {kaggle_json}")
            return True
        else:
            print("✗ Invalid credentials")
            return False
            
    except KeyboardInterrupt:
        print("\nSetup cancelled.")
        return False
    except Exception as e:
        print(f"✗ Error setting up Kaggle API: {e}")
        return False

def download_datasets():
    """Download the required datasets"""
    print("\nDOWNLOADING DATASETS")
    print("="*40)
    
    datasets = [
        {
            "name": "Helmet Detection",
            "command": "kaggle datasets download -d andrewmvd/helmet-detection",
            "extract_to": "dataset/helmet/",
            "filename": "helmet-detection.zip"
        },
        {
            "name": "License Plate Recognition", 
            "command": "kaggle datasets download -d andrewmvd/license-plate-recognition",
            "extract_to": "dataset/anpr/",
            "filename": "license-plate-recognition.zip"
        }
    ]
    
    for dataset in datasets:
        print(f"\nDownloading {dataset['name']}...")
        
        # Download
        result = os.system(dataset['command'])
        
        if result == 0:
            print(f"✓ Downloaded {dataset['filename']}")
            
            # Extract
            extract_cmd = f'unzip {dataset["filename"]} -d {dataset["extract_to"]}'
            print(f"Extracting to {dataset['extract_to']}...")
            
            # For Windows, use PowerShell
            if os.name == 'nt':
                extract_cmd = f'powershell -Command "Expand-Archive -Path \'{dataset["filename"]}\' -DestinationPath \'{dataset["extract_to"]}\' -Force"'
            
            extract_result = os.system(extract_cmd)
            
            if extract_result == 0:
                print(f"✓ Extracted {dataset['name']}")
            else:
                print(f"✗ Failed to extract {dataset['name']}")
        else:
            print(f"✗ Failed to download {dataset['name']}")

def alternative_download_methods():
    """Provide alternative download methods"""
    print("\nALTERNATIVE DOWNLOAD METHODS")
    print("="*40)
    
    print("\nIf Kaggle API doesn't work, you can:")
    
    print("\n1. MANUAL DOWNLOAD:")
    print("   Helmet Dataset: https://www.kaggle.com/datasets/andrewmvd/helmet-detection")
    print("   License Plate: https://www.kaggle.com/datasets/andrewmvd/license-plate-recognition")
    print("   Download and extract to dataset/ folders")
    
    print("\n2. USE SAMPLE DATA:")
    print("   python download_sample_data.py")
    print("   python demo_with_dataset.py")
    
    print("\n3. GITHUB DATASETS:")
    print("   Helmet: https://github.com/opencv/opencv/wiki/TensorFlow-Object-Detection-API")
    print("   ANPR: https://github.com/sergiomsilva/alpr-unconstrained")

def main():
    """Main function"""
    print("TRAFFIC VIOLATION DETECTION - DATASET DOWNLOADER")
    print("="*50)
    
    # Setup Kaggle API
    if setup_kaggle_api():
        # Download datasets
        download_datasets()
    else:
        print("Kaggle API setup failed. Using alternative methods...")
        alternative_download_methods()
    
    print("\n" + "="*50)
    print("SETUP COMPLETE!")
    print("="*50)
    
    print("\nNext steps:")
    print("1. Check dataset/ folder for downloaded data")
    print("2. Run: python demo_with_dataset.py")
    print("3. Or use sample data: python download_sample_data.py")

if __name__ == "__main__":
    main()

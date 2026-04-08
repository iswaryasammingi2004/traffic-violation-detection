#!/usr/bin/env python3
"""
Load and integrate dataset archive files into the Traffic Violation Detection System
"""

import os
import zipfile
import shutil
from pathlib import Path
import json

def extract_dataset_archive(archive_path, extract_to="dataset"):
    """
    Extract dataset archive and organize it for the system
    
    Args:
        archive_path: Path to the dataset archive.zip file
        extract_to: Directory to extract to (default: dataset)
    """
    archive_path = Path(archive_path)
    extract_dir = Path(extract_to)
    
    if not archive_path.exists():
        print(f"❌ Archive not found: {archive_path}")
        return False
    
    print(f"📦 Extracting dataset archive: {archive_path}")
    print(f"📂 Extracting to: {extract_dir}")
    
    try:
        # Extract the archive
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        print(f"✅ Successfully extracted {archive_path}")
        
        # Organize the extracted data
        organize_extracted_data(extract_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ Error extracting archive: {e}")
        return False

def organize_extracted_data(extract_dir):
    """Organize extracted data into the expected structure"""
    extract_dir = Path(extract_dir)
    
    print("🔧 Organizing dataset structure...")
    
    # Create standard directories
    standard_dirs = [
        "helmet/with_helmet",
        "helmet/without_helmet",
        "anpr/images", 
        "anpr/annotations",
        "traffic_violations/images",
        "traffic_violations/videos",
        "traffic_violations/annotations"
    ]
    
    for dir_path in standard_dirs:
        (extract_dir / dir_path).mkdir(parents=True, exist_ok=True)
    
    # Auto-detect and organize files
    organize_helmet_data(extract_dir)
    organize_anpr_data(extract_dir)
    organize_traffic_data(extract_dir)
    
    print("✅ Dataset organization complete!")

def organize_helmet_data(extract_dir):
    """Organize helmet detection data"""
    extract_dir = Path(extract_dir)
    
    # Look for common helmet dataset patterns
    helmet_patterns = [
        "helmet",
        "with_helmet", 
        "without_helmet",
        "helmet_detection",
        "safety_helmet"
    ]
    
    for item in extract_dir.iterdir():
        if item.is_dir():
            # Check if this directory contains helmet data
            dir_name_lower = item.name.lower()
            
            if any(pattern in dir_name_lower for pattern in helmet_patterns):
                print(f"🪖 Found helmet data: {item.name}")
                
                # Move images to appropriate folders
                for sub_item in item.iterdir():
                    if sub_item.is_file() and sub_item.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                        # Determine if it's with or without helmet based on folder name
                        if "without" in dir_name_lower or "no" in dir_name_lower:
                            dest = extract_dir / "helmet" / "without_helmet" / sub_item.name
                        else:
                            dest = extract_dir / "helmet" / "with_helmet" / sub_item.name
                        
                        shutil.move(str(sub_item), str(dest))
                        print(f"  📁 Moved: {sub_item.name} → {dest.parent.name}")

def organize_anpr_data(extract_dir):
    """Organize ANPR/number plate data"""
    extract_dir = Path(extract_dir)
    
    # Look for ANPR/number plate patterns
    anpr_patterns = [
        "anpr",
        "license_plate", 
        "number_plate",
        "lp",
        "plate"
    ]
    
    for item in extract_dir.iterdir():
        if item.is_dir():
            dir_name_lower = item.name.lower()
            
            if any(pattern in dir_name_lower for pattern in anpr_patterns):
                print(f"🚗 Found ANPR data: {item.name}")
                
                # Move images to ANPR folder
                for sub_item in item.iterdir():
                    if sub_item.is_file() and sub_item.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                        dest = extract_dir / "anpr" / "images" / sub_item.name
                        shutil.move(str(sub_item), str(dest))
                        print(f"  📁 Moved: {sub_item.name} → ANPR images")

def organize_traffic_data(extract_dir):
    """Organize traffic violation data"""
    extract_dir = Path(extract_dir)
    
    # Look for traffic patterns
    traffic_patterns = [
        "traffic",
        "violation",
        "cctv",
        "road",
        "vehicle"
    ]
    
    for item in extract_dir.iterdir():
        if item.is_dir():
            dir_name_lower = item.name.lower()
            
            if any(pattern in dir_name_lower for pattern in traffic_patterns):
                print(f"🚦 Found traffic data: {item.name}")
                
                # Organize by file type
                for sub_item in item.iterdir():
                    if sub_item.is_file():
                        if sub_item.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                            dest = extract_dir / "traffic_violations" / "images" / sub_item.name
                            shutil.move(str(sub_item), str(dest))
                        elif sub_item.suffix.lower() in ['.mp4', '.avi', '.mov']:
                            dest = extract_dir / "traffic_violations" / "videos" / sub_item.name
                            shutil.move(str(sub_item), str(dest))

def create_dataset_info(extract_dir):
    """Create dataset information file"""
    extract_dir = Path(extract_dir)
    
    dataset_info = {
        "name": "Custom Dataset",
        "extracted_from": "archive.zip",
        "structure": {},
        "file_counts": {}
    }
    
    # Count files in each directory
    for root, dirs, files in os.walk(extract_dir):
        rel_path = os.path.relpath(root, extract_dir)
        if rel_path != '.':
            dataset_info["structure"][rel_path] = len(files)
    
    # Save dataset info
    with open(extract_dir / "dataset_info.json", "w") as f:
        json.dump(dataset_info, f, indent=2)
    
    print(f"📊 Dataset info saved: {extract_dir / 'dataset_info.json'}")

def update_config_for_dataset(extract_dir="dataset"):
    """Update configuration to use the new dataset"""
    extract_dir = Path(extract_dir)
    
    config_updates = {
        "dataset_path": str(extract_dir),
        "helmet_dataset_path": str(extract_dir / "helmet"),
        "anpr_dataset_path": str(extract_dir / "anpr"),
        "traffic_dataset_path": str(extract_dir / "traffic_violations")
    }
    
    # Save to config file
    config_file = Path("dataset_config.json")
    with open(config_file, "w") as f:
        json.dump(config_updates, f, indent=2)
    
    print(f"⚙️ Configuration updated: {config_file}")

def main():
    """Main function to load dataset archive"""
    print("📦 DATASET ARCHIVE LOADER")
    print("="*50)
    
    # Get archive path from user
    archive_path = input("Enter path to your dataset archive.zip: ").strip()
    
    if not archive_path:
        # Try common locations
        common_paths = [
            "dataset.zip",
            "archive.zip", 
            "data.zip",
            "dataset/archive.zip"
        ]
        
        for path in common_paths:
            if Path(path).exists():
                archive_path = path
                print(f"🔍 Found archive at: {archive_path}")
                break
        else:
            print("❌ No archive found. Please provide the correct path.")
            return
    
    # Extract and organize
    if extract_dataset_archive(archive_path):
        create_dataset_info("dataset")
        update_config_for_dataset()
        
        print("\n" + "="*50)
        print("✅ DATASET LOADING COMPLETE!")
        print("="*50)
        
        print("\n📁 Dataset Structure:")
        print("dataset/")
        print("├── helmet/")
        print("│   ├── with_helmet/")
        print("│   └── without_helmet/")
        print("├── anpr/")
        print("│   ├── images/")
        print("│   └── annotations/")
        print("└── traffic_violations/")
        print("    ├── images/")
        print("    ├── videos/")
        print("    └── annotations/")
        
        print("\n🚀 Next Steps:")
        print("1. Run demo with new dataset:")
        print("   python demo_with_dataset.py")
        print("2. Or process specific files:")
        print("   python main.py --input dataset/traffic_violations/images/your_image.jpg")
        
    else:
        print("❌ Failed to load dataset archive")

if __name__ == "__main__":
    main()

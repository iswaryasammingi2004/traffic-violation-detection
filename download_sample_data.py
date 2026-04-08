#!/usr/bin/env python3
"""
Download sample traffic violation datasets for demonstration
"""

import os
import urllib.request
import zipfile
from pathlib import Path

def create_sample_dataset():
    """Create a sample dataset structure and download sample data"""
    
    # Create dataset directories
    dataset_dir = Path("dataset")
    images_dir = dataset_dir / "images"
    videos_dir = dataset_dir / "videos"
    annotations_dir = dataset_dir / "annotations"
    
    for dir_path in [dataset_dir, images_dir, videos_dir, annotations_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print("Created dataset structure:")
    print(f"  {dataset_dir}")
    print(f"  {images_dir}")
    print(f"  {videos_dir}")
    print(f"  {annotations_dir}")
    
    # Create sample annotation file
    sample_annotations = {
        "images": [
            {
                "filename": "sample1.jpg",
                "vehicles": [
                    {
                        "bbox": [100, 200, 200, 350],
                        "type": "motorcycle",
                        "violations": ["no_helmet"],
                        "plate": "MH12AB1234"
                    },
                    {
                        "bbox": [300, 180, 400, 340],
                        "type": "motorcycle", 
                        "violations": ["triple_riding"],
                        "plate": "DL05CD5678"
                    }
                ]
            }
        ],
        "violation_types": {
            "no_helmet": {"fine": 500, "description": "Riding without helmet"},
            "triple_riding": {"fine": 1000, "description": "More than 2 riders"}
        }
    }
    
    import json
    with open(annotations_dir / "sample_annotations.json", "w") as f:
        json.dump(sample_annotations, f, indent=2)
    
    print(f"Created sample annotations: {annotations_dir / 'sample_annotations.json'}")
    
    # Create a simple script to generate synthetic traffic images
    create_synthetic_data_script(images_dir)
    
    print("\nDataset setup complete!")
    print("You can now run the demo with real data using:")
    print("python demo_with_dataset.py")

def create_synthetic_data_script(images_dir):
    """Create script to generate synthetic traffic images"""
    
    script_content = '''
import cv2
import numpy as np
import random
from datetime import datetime

def generate_traffic_image(index):
    """Generate a synthetic traffic violation image"""
    height, width = 480, 640
    image = np.ones((height, width, 3), dtype=np.uint8) * 200
    
    # Draw road
    cv2.rectangle(image, (0, height//2), (width, height), (100, 100, 100), -1)
    
    # Generate random vehicles
    num_vehicles = random.randint(1, 3)
    
    for i in range(num_vehicles):
        x = random.randint(50, width - 200)
        y = random.randint(150, height//2 - 50)
        
        # Vehicle bounding box
        x1, y1 = x, y
        x2, y2 = x + 100, y + 150
        
        # Draw vehicle
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 100, 200), -1)
        
        # Random violations
        has_helmet = random.choice([True, False])
        rider_count = random.randint(1, 3)
        
        # Draw riders
        if rider_count >= 1:
            cv2.circle(image, (x1 + 30, y1 + 30), 15, (255, 200, 150), -1)
            if has_helmet:
                cv2.circle(image, (x1 + 30, y1 + 30), 18, (50, 50, 50), 2)
        
        if rider_count >= 2:
            cv2.circle(image, (x1 + 70, y1 + 30), 15, (255, 200, 150), -1)
            if has_helmet:
                cv2.circle(image, (x1 + 70, y1 + 30), 18, (50, 50, 50), 2)
        
        if rider_count >= 3:
            cv2.circle(image, (x1 + 50, y1 + 60), 12, (255, 200, 150), -1)
            cv2.circle(image, (x1 + 50, y1 + 60), 15, (50, 50, 50), 2)
        
        # License plate
        plate_y = y2 - 20
        cv2.rectangle(image, (x1 + 10, plate_y), (x1 + 80, plate_y + 15), (255, 255, 255), -1)
        
        # Generate random plate number
        state = random.choice(['MH', 'DL', 'KA', 'TN', 'GJ'])
        rto = f"{random.randint(1, 99):02d}"
        letters = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2))
        numbers = f"{random.randint(1000, 9999):04d}"
        plate = f"{state}{rto}{letters}{numbers}"
        
        cv2.putText(image, plate, (x1 + 12, plate_y + 12), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        
        # Draw violation indicators
        violations = []
        if not has_helmet:
            violations.append("NO HELMET")
        if rider_count > 2:
            violations.append("TRIPLE RIDING")
        
        if violations:
            violation_text = " | ".join(violations)
            cv2.putText(image, violation_text, (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    # Add timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(image, f"Traffic Image {index} - {timestamp}", (10, height - 20), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    
    return image

# Generate sample images
for i in range(5):
    image = generate_traffic_image(i + 1)
    filename = f"sample_{i+1:02d}.jpg"
    cv2.imwrite(filename, image)
    print(f"Generated {filename}")

print("Generated 5 sample traffic images!")
'''
    
    with open(images_dir / "generate_samples.py", "w") as f:
        f.write(script_content)
    
    print(f"Created synthetic data generator: {images_dir / 'generate_samples.py'}")

if __name__ == "__main__":
    create_sample_dataset()

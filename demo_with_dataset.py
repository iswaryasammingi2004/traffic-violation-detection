#!/usr/bin/env python3
"""
Demo script using the created dataset
"""

import os
import cv2
import json
from pathlib import Path
from main import TrafficViolationSystem
from datetime import datetime

def demo_with_dataset():
    """Run demo using the created dataset"""
    print("="*60)
    print("TRAFFIC VIOLATION DETECTION - DATASET DEMO")
    print("="*60)
    
    # Check dataset directory
    dataset_dir = Path("dataset")
    images_dir = dataset_dir / "images"
    
    if not images_dir.exists():
        print("Dataset not found! Run download_sample_data.py first.")
        return
    
    # Get all sample images
    image_files = list(images_dir.glob("sample_*.jpg"))
    
    if not image_files:
        print("No sample images found!")
        return
    
    print(f"\nFound {len(image_files)} sample images")
    
    # Initialize the system
    print("\nInitializing Traffic Violation Detection System...")
    try:
        system = TrafficViolationSystem()
        print("System initialized successfully!")
    except Exception as e:
        print(f"Error initializing system: {e}")
        return
    
    # Process each image
    total_violations = []
    
    for i, image_path in enumerate(image_files, 1):
        print(f"\n{'='*40}")
        print(f"Processing Image {i}: {image_path.name}")
        print(f"{'='*40}")
        
        try:
            # Process the image
            output_path = f"outputs/processed_{image_path.name}"
            os.makedirs("outputs", exist_ok=True)
            
            results = system.process_image(str(image_path), output_path)
            
            print(f"Vehicles detected: {len(results['vehicles'])}")
            print(f"Violations detected: {len(results['violations'])}")
            
            # Display violation details
            if results['violations']:
                for j, violation in enumerate(results['violations'], 1):
                    print(f"\n  Violation {j}:")
                    print(f"    Type: {violation['violation_type']}")
                    print(f"    Plate: {violation['plate_number']}")
                    print(f"    Fine: ₹{violation['fine_amount']}")
                    print(f"    Time: {violation['timestamp']}")
                    print(f"    Location: {violation['location']}")
                    
                    total_violations.append(violation)
            else:
                print("  No violations detected in this image")
                
        except Exception as e:
            print(f"Error processing {image_path.name}: {e}")
    
    # Generate summary report
    print(f"\n{'='*60}")
    print("DEMO SUMMARY REPORT")
    print(f"{'='*60}")
    
    print(f"Total images processed: {len(image_files)}")
    print(f"Total violations detected: {len(total_violations)}")
    
    if total_violations:
        # Group violations by type
        violation_types = {}
        total_fines = 0
        
        for violation in total_violations:
            v_type = violation['violation_type']
            violation_types[v_type] = violation_types.get(v_type, 0) + 1
            total_fines += violation['fine_amount']
        
        print(f"\nViolation Breakdown:")
        for v_type, count in violation_types.items():
            print(f"  {v_type.replace('_', ' ').title()}: {count}")
        
        print(f"\nTotal fines generated: ₹{total_fines}")
        
        # Get system statistics
        stats = system.get_statistics()
        print(f"\nSystem Statistics:")
        print(f"  Total vehicles processed: {stats['total_vehicles']}")
        print(f"  Violation rate: {stats['violation_rate']:.2%}")
    
    # Display sample output image
    output_files = list(Path("outputs").glob("processed_*.jpg"))
    if output_files:
        print(f"\nSample output images saved in 'outputs' directory:")
        for output_file in output_files[:3]:  # Show first 3
            print(f"  - {output_file.name}")
        
        try:
            # Display first output image
            sample_output = cv2.imread(str(output_files[0]))
            if sample_output is not None:
                cv2.imshow('Sample Output - Press any key to continue', sample_output)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
        except Exception as e:
            print(f"Could not display image: {e}")
    
    print(f"\n{'='*60}")
    print("DATASET DEMO COMPLETED")
    print(f"{'='*60}")
    print("\nNext steps:")
    print("1. Check 'outputs' directory for processed images")
    print("2. Check 'data/tickets' directory for generated tickets")
    print("3. Check 'data/violations.db' for violation records")
    print("4. Add your own traffic images to 'dataset/images' directory")

def create_sample_video():
    """Create a sample video from the dataset images"""
    print("\nCreating sample video from dataset images...")
    
    images_dir = Path("dataset/images")
    image_files = sorted(list(images_dir.glob("sample_*.jpg")))
    
    if not image_files:
        print("No images found for video creation!")
        return
    
    # Read first image to get dimensions
    first_image = cv2.imread(str(image_files[0]))
    height, width = first_image.shape[:2]
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_path = "dataset/videos/sample_traffic_video.mp4"
    os.makedirs("dataset/videos", exist_ok=True)
    
    out = cv2.VideoWriter(video_path, fourcc, 2.0, (width, height))
    
    # Add each image to video (repeat each frame for 1 second)
    for image_path in image_files:
        frame = cv2.imread(str(image_path))
        
        # Add frame number text
        cv2.putText(frame, f"Frame: {image_path.stem}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Add each frame multiple times for longer duration
        for _ in range(10):  # 10 frames per image at 2fps = 5 seconds per image
            out.write(frame)
    
    out.release()
    print(f"Sample video created: {video_path}")
    
    # Process the video
    print("\nProcessing sample video...")
    try:
        system = TrafficViolationSystem()
        violations = system.process_video(video_path, "outputs/processed_sample_video.mp4")
        print(f"Video processing complete! Found {len(violations)} violations")
    except Exception as e:
        print(f"Error processing video: {e}")

if __name__ == "__main__":
    print("Traffic Violation Detection System - Dataset Demo")
    print("Choose an option:")
    print("1. Process dataset images")
    print("2. Create and process sample video")
    print("3. Run both")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            demo_with_dataset()
        elif choice == "2":
            create_sample_video()
        elif choice == "3":
            demo_with_dataset()
            create_sample_video()
        else:
            print("Invalid choice. Running image demo...")
            demo_with_dataset()
    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")
    except Exception as e:
        print(f"Demo error: {e}")
        demo_with_dataset()

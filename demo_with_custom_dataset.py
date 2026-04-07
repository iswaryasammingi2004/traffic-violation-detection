#!/usr/bin/env python3
"""
Demo script that works with custom dataset archives
"""

import os
import json
from pathlib import Path
from main import TrafficViolationSystem

def find_dataset_images():
    """Find images in the dataset directory"""
    dataset_dir = Path("dataset")
    image_extensions = ['.jpg', '.jpeg', '.png']
    
    image_paths = []
    
    # Search in all subdirectories
    for ext in image_extensions:
        image_paths.extend(dataset_dir.rglob(f"*{ext}"))
    
    return sorted(image_paths)

def demo_with_custom_dataset():
    """Run demo using custom dataset"""
    print("🚀 TRAFFIC VIOLATION DETECTION - CUSTOM DATASET DEMO")
    print("="*60)
    
    # Check if dataset exists
    if not Path("dataset").exists():
        print("❌ Dataset directory not found!")
        print("Please run: python load_dataset_archive.py")
        print("Or place your dataset in the 'dataset/' folder")
        return
    
    # Find all images
    image_paths = find_dataset_images()
    
    if not image_paths:
        print("❌ No images found in dataset!")
        print("Please add images to dataset/ folders")
        return
    
    print(f"📸 Found {len(image_paths)} images in dataset")
    
    # Show dataset structure
    print("\n📁 Dataset Structure:")
    for root, dirs, files in os.walk("dataset"):
        level = root.replace("dataset", "").count(os.sep)
        indent = " " * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 2 * (level + 1)
        for file in files[:3]:  # Show first 3 files
            if file.endswith(('.jpg', '.jpeg', '.png')):
                print(f"{subindent}{file}")
        if len([f for f in files if f.endswith(('.jpg', '.jpeg', '.png'))]) > 3:
            print(f"{subindent}... and {len([f for f in files if f.endswith(('.jpg', '.jpeg', '.png'))]) - 3} more")
    
    # Initialize system
    print("\n🤖 Initializing Traffic Violation Detection System...")
    try:
        system = TrafficViolationSystem()
        print("✅ System initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing system: {e}")
        return
    
    # Process images
    total_violations = []
    processed_count = 0
    max_images = 10  # Process max 10 images for demo
    
    print(f"\n🔄 Processing up to {max_images} images...")
    
    for i, image_path in enumerate(image_paths[:max_images]):
        print(f"\n{'='*50}")
        print(f"📸 Processing Image {i+1}: {image_path.name}")
        print(f"📍 Path: {image_path}")
        print(f"{'='*50}")
        
        try:
            # Create output filename
            output_name = f"outputs/custom_{image_path.name}"
            os.makedirs("outputs", exist_ok=True)
            
            # Process the image
            results = system.process_image(str(image_path), output_name)
            
            print(f"🚗 Vehicles detected: {len(results['vehicles'])}")
            print(f"⚠️ Violations detected: {len(results['violations'])}")
            
            # Show violation details
            if results['violations']:
                for j, violation in enumerate(results['violations'], 1):
                    print(f"\n  🎫 Violation {j}:")
                    print(f"     Type: {violation['violation_type']}")
                    print(f"     Plate: {violation['plate_number']}")
                    print(f"     Fine: ₹{violation['fine_amount']}")
                    print(f"     Time: {violation['timestamp']}")
                    
                    total_violations.append(violation)
            else:
                print("  ✅ No violations detected")
            
            processed_count += 1
            
        except Exception as e:
            print(f"❌ Error processing {image_path.name}: {e}")
    
    # Generate summary
    print(f"\n" + "="*60)
    print("📊 CUSTOM DATASET DEMO SUMMARY")
    print("="*60)
    
    print(f"📸 Images processed: {processed_count}")
    print(f"⚠️ Total violations: {len(total_violations)}")
    
    if total_violations:
        # Group violations by type
        violation_types = {}
        total_fines = 0
        
        for violation in total_violations:
            v_type = violation['violation_type']
            violation_types[v_type] = violation_types.get(v_type, 0) + 1
            total_fines += violation['fine_amount']
        
        print(f"\n📈 Violation Breakdown:")
        for v_type, count in violation_types.items():
            print(f"  🎯 {v_type.replace('_', ' ').title()}: {count}")
        
        print(f"\n💰 Total fines: ₹{total_fines}")
    
    # System statistics
    try:
        stats = system.get_statistics()
        print(f"\n📊 System Statistics:")
        print(f"  🚗 Total vehicles: {stats['total_vehicles']}")
        print(f"  📈 Violation rate: {stats['violation_rate']:.2%}")
    except:
        pass
    
    # Show output files
    output_files = list(Path("outputs").glob("custom_*.jpg"))
    if output_files:
        print(f"\n📁 Output files created:")
        for output_file in output_files[:5]:
            print(f"  📸 {output_file.name}")
        if len(output_files) > 5:
            print(f"  ... and {len(output_files) - 5} more")
    
    print(f"\n" + "="*60)
    print("✅ CUSTOM DATASET DEMO COMPLETED!")
    print("="*60)
    
    print("\n🎯 Next Steps:")
    print("1. Check 'outputs/' folder for processed images")
    print("2. Check 'data/tickets/' for generated e-challans")
    print("3. Check 'data/violations.db' for violation records")
    print("4. Add more images to dataset/ folders")

def quick_test_with_sample():
    """Quick test with sample data if no custom dataset"""
    print("🔧 Running quick test with sample data...")
    
    # Create sample dataset if it doesn't exist
    if not Path("dataset/images").exists():
        print("📦 Creating sample dataset...")
        os.system("python download_sample_data.py")
    
    # Run dataset demo
    os.system("python demo_with_dataset.py")

if __name__ == "__main__":
    print("🚀 TRAFFIC VIOLATION DETECTION SYSTEM")
    print("Choose an option:")
    print("1. Load and use custom dataset archive")
    print("2. Run with existing dataset")
    print("3. Quick test with sample data")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            os.system("python load_dataset_archive.py")
            demo_with_custom_dataset()
        elif choice == "2":
            demo_with_custom_dataset()
        elif choice == "3":
            quick_test_with_sample()
        else:
            print("Invalid choice. Running with existing dataset...")
            demo_with_custom_dataset()
            
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user.")
    except Exception as e:
        print(f"❌ Demo error: {e}")
        demo_with_custom_dataset()

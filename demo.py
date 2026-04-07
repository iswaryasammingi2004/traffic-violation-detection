#!/usr/bin/env python3
"""
Demo script for Traffic Violation Detection System
Demonstrates the system with sample data and visualizations
"""

import cv2
import numpy as np
import os
import time
from datetime import datetime
from main import TrafficViolationSystem
import matplotlib.pyplot as plt
import seaborn as sns

def create_demo_image():
    """Create a demo image with simulated two-wheelers and violations"""
    # Create a blank image (traffic scene)
    height, width = 480, 640
    image = np.ones((height, width, 3), dtype=np.uint8) * 200  # Light gray background
    
    # Draw road
    cv2.rectangle(image, (0, height//2), (width, height), (100, 100, 100), -1)
    
    # Draw lane markings
    for x in range(0, width, 40):
        cv2.rectangle(image, (x, height//2 - 2), (x+20, height//2 + 2), (255, 255, 255), -1)
    
    # Simulate two-wheelers with bounding boxes
    demo_vehicles = [
        {
            'bbox': [100, 200, 200, 350],  # Motorcycle with helmet
            'has_helmet': True,
            'rider_count': 2,
            'plate': 'MH12AB1234'
        },
        {
            'bbox': [300, 180, 400, 340],  # Motorcycle without helmet
            'has_helmet': False,
            'rider_count': 2,
            'plate': 'DL05CD5678'
        },
        {
            'bbox': [450, 160, 550, 320],  # Triple riding
            'has_helmet': True,
            'rider_count': 3,
            'plate': 'KA03EF9012'
        }
    ]
    
    # Draw vehicles and labels
    for i, vehicle in enumerate(demo_vehicles):
        x1, y1, x2, y2 = vehicle['bbox']
        
        # Draw vehicle
        color = (0, 100, 200)  # Blue for vehicle
        cv2.rectangle(image, (x1, y1), (x2, y2), color, -1)
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 0), 2)
        
        # Draw riders (simplified)
        if vehicle['rider_count'] >= 1:
            cv2.circle(image, (x1 + 30, y1 + 30), 15, (255, 200, 150), -1)  # Driver
            if vehicle['has_helmet']:
                cv2.circle(image, (x1 + 30, y1 + 30), 18, (50, 50, 50), 2)  # Helmet
        
        if vehicle['rider_count'] >= 2:
            cv2.circle(image, (x1 + 70, y1 + 30), 15, (255, 200, 150), -1)  # Pillion
            if vehicle['has_helmet']:
                cv2.circle(image, (x1 + 70, y1 + 30), 18, (50, 50, 50), 2)  # Helmet
        
        if vehicle['rider_count'] >= 3:
            cv2.circle(image, (x1 + 50, y1 + 60), 12, (255, 200, 150), -1)  # Third rider
            cv2.circle(image, (x1 + 50, y1 + 60), 15, (50, 50, 50), 2)  # Helmet
        
        # Draw license plate
        plate_y = y2 - 20
        cv2.rectangle(image, (x1 + 10, plate_y), (x1 + 80, plate_y + 15), (255, 255, 255), -1)
        cv2.putText(image, vehicle['plate'], (x1 + 12, plate_y + 12), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        
        # Draw violation indicators
        violations = []
        if not vehicle['has_helmet']:
            violations.append("NO HELMET")
        if vehicle['rider_count'] > 2:
            violations.append("TRIPLE RIDING")
        
        if violations:
            violation_text = " | ".join(violations)
            cv2.putText(image, violation_text, (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    # Add title
    cv2.putText(image, "Traffic Violation Detection Demo", (10, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    return image, demo_vehicles

def run_demo():
    """Run the complete demo"""
    print("="*60)
    print("TRAFFIC VIOLATION DETECTION SYSTEM DEMO")
    print("="*60)
    
    # Create demo image
    print("\n1. Creating demo traffic scene...")
    demo_image, ground_truth = create_demo_image()
    
    # Save demo image
    demo_path = "demo_scene.jpg"
    cv2.imwrite(demo_path, demo_image)
    print(f"   Demo scene saved as: {demo_path}")
    
    # Initialize the system
    print("\n2. Initializing Traffic Violation Detection System...")
    try:
        system = TrafficViolationSystem()
        print("   System initialized successfully!")
    except Exception as e:
        print(f"   Error initializing system: {e}")
        print("   This is normal if models are not downloaded yet.")
        return
    
    # Process the demo image
    print("\n3. Processing demo image for violations...")
    try:
        results = system.process_image(demo_path, "demo_output.jpg")
        
        print(f"   Vehicles detected: {len(results['vehicles'])}")
        print(f"   Violations detected: {len(results['violations'])}")
        
        # Display results
        for i, violation in enumerate(results['violations'], 1):
            print(f"\n   Violation {i}:")
            print(f"     Type: {violation['violation_type']}")
            print(f"     Plate: {violation['plate_number']}")
            print(f"     Fine: ₹{violation['fine_amount']}")
            print(f"     Time: {violation['timestamp']}")
            
    except Exception as e:
        print(f"   Error processing image: {e}")
    
    # Generate statistics
    print("\n4. Generating system statistics...")
    try:
        stats = system.get_statistics()
        print(f"   Total vehicles processed: {stats['total_vehicles']}")
        print(f"   Total violations detected: {stats['total_violations']}")
        print(f"   Violation rate: {stats['violation_rate']:.2%}")
    except Exception as e:
        print(f"   Error generating statistics: {e}")
    
    # Display demo image
    print("\n5. Displaying demo scene...")
    try:
        cv2.imshow('Traffic Violation Detection Demo', demo_image)
        print("   Press any key to continue...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"   Error displaying image: {e}")
    
    print("\n" + "="*60)
    print("DEMO COMPLETED")
    print("="*60)
    print("\nNext steps:")
    print("1. Install required dependencies: pip install -r requirements.txt")
    print("2. Test with real video: python main.py --input your_video.mp4")
    print("3. Configure settings: cp config.example.json config.json")
    print("4. Check generated tickets in data/tickets/")
    print("5. View database statistics using the database module")

def performance_test():
    """Run performance tests"""
    print("\n" + "="*60)
    print("PERFORMANCE TEST")
    print("="*60)
    
    # Create test image
    test_image, _ = create_demo_image()
    
    # Initialize system
    try:
        system = TrafficViolationSystem()
        
        # Run multiple iterations
        iterations = 10
        times = []
        
        print(f"\nRunning {iterations} iterations...")
        
        for i in range(iterations):
            start_time = time.time()
            results = system.process_frame(test_image)
            end_time = time.time()
            
            processing_time = end_time - start_time
            times.append(processing_time)
            
            print(f"   Iteration {i+1}: {processing_time:.3f}s")
        
        # Calculate statistics
        avg_time = np.mean(times)
        min_time = np.min(times)
        max_time = np.max(times)
        fps = 1.0 / avg_time
        
        print(f"\nPerformance Results:")
        print(f"   Average processing time: {avg_time:.3f}s")
        print(f"   Min processing time: {min_time:.3f}s")
        print(f"   Max processing time: {max_time:.3f}s")
        print(f"   Estimated FPS: {fps:.1f}")
        
        # Create performance plot
        plt.figure(figsize=(10, 6))
        plt.plot(range(1, iterations + 1), times, 'b-o', linewidth=2, markersize=8)
        plt.axhline(y=avg_time, color='r', linestyle='--', label=f'Average: {avg_time:.3f}s')
        plt.xlabel('Iteration')
        plt.ylabel('Processing Time (seconds)')
        plt.title('Traffic Violation Detection Performance')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('performance_test.png', dpi=150, bbox_inches='tight')
        print(f"\nPerformance plot saved as: performance_test.png")
        
        try:
            plt.show()
        except:
            print("Could not display plot (matplotlib backend issue)")
        
    except Exception as e:
        print(f"Performance test failed: {e}")

def create_sample_videos():
    """Create sample videos for testing"""
    print("\n" + "="*60)
    print("CREATING SAMPLE VIDEOS")
    print("="*60)
    
    try:
        # Create a series of demo images
        frames = []
        for i in range(30):  # 30 frames for 1 second video
            # Create slightly different scenes
            image, _ = create_demo_image()
            
            # Add some movement simulation
            offset = i * 5
            if offset < 200:
                image = np.roll(image, offset, axis=1)
            
            # Add frame number
            cv2.putText(image, f"Frame {i+1}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            frames.append(image)
        
        # Save as video
        height, width = frames[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter('sample_video.mp4', fourcc, 10.0, (width, height))
        
        for frame in frames:
            out.write(frame)
        
        out.release()
        print("Sample video created: sample_video.mp4")
        
        print("\nYou can now test the system with:")
        print("python main.py --input sample_video.mp4 --output processed_video.mp4")
        
    except Exception as e:
        print(f"Error creating sample video: {e}")

if __name__ == "__main__":
    print("Traffic Violation Detection System Demo")
    print("Choose an option:")
    print("1. Run basic demo")
    print("2. Performance test")
    print("3. Create sample videos")
    print("4. Run all")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            run_demo()
        elif choice == "2":
            performance_test()
        elif choice == "3":
            create_sample_videos()
        elif choice == "4":
            run_demo()
            performance_test()
            create_sample_videos()
        else:
            print("Invalid choice. Running basic demo...")
            run_demo()
    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")
    except Exception as e:
        print(f"Demo error: {e}")
        print("Running basic demo...")
        run_demo()

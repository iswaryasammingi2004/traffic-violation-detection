#!/usr/bin/env python3
"""
Two-Wheeler Vehicle Traffic Violations Detection and Automated Ticketing System
Main entry point for the traffic violation detection system
"""

import cv2
import numpy as np
import argparse
import os
from datetime import datetime
from modules.vehicle_detector import VehicleDetector
from modules.helmet_detector import HelmetDetector
from modules.triple_riding_detector import TripleRidingDetector
from modules.anpr_system import ANPRSystem
from modules.ticket_generator import TicketGenerator
from modules.database import DatabaseManager
from utils.config import Config

class TrafficViolationSystem:
    def __init__(self, config_path=None):
        """Initialize the traffic violation detection system"""
        self.config = Config(config_path)
        
        # Initialize all modules
        self.vehicle_detector = VehicleDetector(self.config)
        self.helmet_detector = HelmetDetector(self.config)
        self.triple_riding_detector = TripleRidingDetector(self.config)
        self.anpr_system = ANPRSystem(self.config)
        self.ticket_generator = TicketGenerator(self.config)
        self.db_manager = DatabaseManager(self.config)
        
        # Statistics
        self.total_vehicles = 0
        self.violations_detected = 0
        
    def process_frame(self, frame, timestamp=None):
        """
        Process a single frame for traffic violations
        
        Args:
            frame: Input frame (numpy array)
            timestamp: Frame timestamp
            
        Returns:
            dict: Detection results and violations
        """
        if timestamp is None:
            timestamp = datetime.now()
            
        results = {
            'timestamp': timestamp,
            'violations': [],
            'vehicles': []
        }
        
        # Step 1: Detect two-wheelers
        two_wheelers = self.vehicle_detector.detect_two_wheelers(frame)
        results['vehicles'] = two_wheelers
        
        self.total_vehicles += len(two_wheelers)
        
        # Step 2: Process each detected two-wheeler
        for vehicle in two_wheelers:
            vehicle_data = {
                'bbox': vehicle['bbox'],
                'confidence': vehicle['confidence'],
                'violations': []
            }
            
            # Extract vehicle ROI
            x1, y1, x2, y2 = vehicle['bbox']
            vehicle_roi = frame[y1:y2, x1:x2]
            
            # Step 3: Helmet detection
            helmet_result = self.helmet_detector.detect_helmet_violation(vehicle_roi)
            if helmet_result['violation']:
                vehicle_data['violations'].append({
                    'type': 'no_helmet',
                    'confidence': helmet_result['confidence'],
                    'riders_without_helmet': helmet_result['riders_without_helmet']
                })
            
            # Step 4: Triple riding detection
            triple_result = self.triple_riding_detector.detect_triple_riding(vehicle_roi)
            if triple_result['violation']:
                vehicle_data['violations'].append({
                    'type': 'triple_riding',
                    'confidence': triple_result['confidence'],
                    'rider_count': triple_result['rider_count']
                })
            
            # Step 5: Number plate recognition
            if vehicle_data['violations']:  # Only process ANPR for violations
                plate_result = self.anpr_system.recognize_plate(vehicle_roi)
                if plate_result['plate_number']:
                    vehicle_data['plate_number'] = plate_result['plate_number']
                    vehicle_data['plate_confidence'] = plate_result['confidence']
                    
                    # Step 6: Generate ticket for violations
                    for violation in vehicle_data['violations']:
                        ticket = self.ticket_generator.generate_ticket(
                            plate_number=plate_result['plate_number'],
                            violation_type=violation['type'],
                            timestamp=timestamp,
                            location=self.config.get('location', 'Unknown Location'),
                            confidence=violation['confidence']
                        )
                        
                        # Store in database
                        self.db_manager.store_violation(ticket)
                        
                        results['violations'].append(ticket)
            
            results['vehicles'].append(vehicle_data)
        
        self.violations_detected += len(results['violations'])
        return results
    
    def process_video(self, video_path, output_path=None):
        """
        Process video file for traffic violations
        
        Args:
            video_path: Path to input video
            output_path: Path to save output video (optional)
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Setup video writer if output path specified
        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        frame_count = 0
        total_violations = []
        
        print(f"Processing video: {video_path}")
        print(f"Resolution: {width}x{height}, FPS: {fps}")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Process every nth frame for efficiency
            if frame_count % self.config.get('frame_skip', 5) == 0:
                timestamp = datetime.now()
                results = self.process_frame(frame, timestamp)
                
                # Draw detections on frame
                annotated_frame = self.draw_detections(frame, results)
                
                if writer:
                    writer.write(annotated_frame)
                
                total_violations.extend(results['violations'])
                
                # Print progress
                if frame_count % 100 == 0:
                    print(f"Processed {frame_count} frames, Found {len(total_violations)} violations")
        
        cap.release()
        if writer:
            writer.release()
        
        print(f"Video processing complete!")
        print(f"Total frames processed: {frame_count}")
        print(f"Total vehicles detected: {self.total_vehicles}")
        print(f"Total violations detected: {len(total_violations)}")
        
        return total_violations
    
    def process_image(self, image_path, output_path=None):
        """
        Process single image for traffic violations
        
        Args:
            image_path: Path to input image
            output_path: Path to save output image (optional)
        """
        frame = cv2.imread(image_path)
        if frame is None:
            raise ValueError(f"Cannot read image: {image_path}")
        
        timestamp = datetime.now()
        results = self.process_frame(frame, timestamp)
        
        # Draw detections on image
        annotated_frame = self.draw_detections(frame, results)
        
        if output_path:
            cv2.imwrite(output_path, annotated_frame)
            print(f"Output saved to: {output_path}")
        
        print(f"Vehicles detected: {len(results['vehicles'])}")
        print(f"Violations detected: {len(results['violations'])}")
        
        return results
    
    def draw_detections(self, frame, results):
        """Draw detection results on frame"""
        annotated_frame = frame.copy()
        
        for vehicle in results['vehicles']:
            x1, y1, x2, y2 = vehicle['bbox']
            
            # Draw vehicle bounding box
            color = (0, 255, 0) if not vehicle['violations'] else (0, 0, 255)
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw violations
            for violation in vehicle['violations']:
                violation_text = f"{violation['type'].replace('_', ' ').title()}"
                if violation['type'] == 'no_helmet':
                    violation_text += f" ({violation['riders_without_helmet']} riders)"
                elif violation['type'] == 'triple_riding':
                    violation_text += f" ({violation['rider_count']} riders)"
                
                cv2.putText(annotated_frame, violation_text, 
                           (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.6, (0, 0, 255), 2)
            
            # Draw plate number if available
            if 'plate_number' in vehicle:
                cv2.putText(annotated_frame, f"Plate: {vehicle['plate_number']}", 
                           (x1, y2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.6, (255, 0, 0), 2)
        
        # Add statistics
        cv2.putText(annotated_frame, f"Vehicles: {len(results['vehicles'])}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(annotated_frame, f"Violations: {len(results['violations'])}", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        return annotated_frame
    
    def get_statistics(self):
        """Get system statistics"""
        return {
            'total_vehicles': self.total_vehicles,
            'total_violations': self.violations_detected,
            'violation_rate': self.violations_detected / max(self.total_vehicles, 1)
        }

def main():
    parser = argparse.ArgumentParser(description='Traffic Violation Detection System')
    parser.add_argument('--input', '-i', required=True, help='Input video/image path')
    parser.add_argument('--output', '-o', help='Output video/image path')
    parser.add_argument('--config', '-c', help='Configuration file path')
    parser.add_argument('--mode', '-m', choices=['video', 'image'], 
                       help='Input mode (auto-detected if not specified)')
    
    args = parser.parse_args()
    
    # Initialize system
    system = TrafficViolationSystem(args.config)
    
    # Determine input mode
    if args.mode:
        mode = args.mode
    else:
        # Auto-detect from file extension
        ext = os.path.splitext(args.input)[1].lower()
        mode = 'video' if ext in ['.mp4', '.avi', '.mov', '.mkv'] else 'image'
    
    # Process input
    if mode == 'video':
        violations = system.process_video(args.input, args.output)
    else:
        results = system.process_image(args.input, args.output)
        violations = results['violations']
    
    # Print final statistics
    stats = system.get_statistics()
    print("\n" + "="*50)
    print("FINAL STATISTICS")
    print("="*50)
    print(f"Total Vehicles Detected: {stats['total_vehicles']}")
    print(f"Total Violations Detected: {stats['total_violations']}")
    print(f"Violation Rate: {stats['violation_rate']:.2%}")
    print("="*50)

if __name__ == "__main__":
    main()

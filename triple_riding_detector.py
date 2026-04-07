"""
Triple Riding Detection Module
Detects when more than two people are riding a two-wheeler
"""

import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Dict, Tuple
import logging

class TripleRidingDetector:
    """Triple riding detection for two-wheelers"""
    
    def __init__(self, config):
        """Initialize triple riding detector
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.model = None
        self.confidence_threshold = config.get('triple_riding_threshold', 0.7)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self._load_model()
    
    def _load_model(self):
        """Load YOLO model for person detection"""
        try:
            self.logger.info("Loading person detection model for triple riding analysis")
            
            # Use YOLOv8 for person detection
            self.model = YOLO('yolov8n.pt')
            
            # Test model with dummy input
            test_input = np.zeros((640, 640, 3), dtype=np.uint8)
            _ = self.model(test_input, verbose=False)
            
            self.logger.info("Triple riding detection model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading triple riding detection model: {e}")
            raise
    
    def detect_triple_riding(self, vehicle_roi: np.ndarray) -> Dict:
        """
        Detect triple riding violation in vehicle ROI
        
        Args:
            vehicle_roi: Region of interest containing the two-wheeler
            
        Returns:
            Dictionary with violation status and rider count
        """
        if self.model is None:
            return {
                'violation': False,
                'confidence': 0.0,
                'rider_count': 0,
                'detections': []
            }
        
        try:
            # Detect persons in the vehicle ROI
            person_detections = self._detect_persons(vehicle_roi)
            
            # Analyze rider count
            rider_analysis = self._analyze_rider_count(person_detections)
            
            return rider_analysis
            
        except Exception as e:
            self.logger.error(f"Error in triple riding detection: {e}")
            return {
                'violation': False,
                'confidence': 0.0,
                'rider_count': 0,
                'error': str(e)
            }
    
    def _detect_persons(self, image: np.ndarray) -> List[Dict]:
        """
        Detect persons in the image
        
        Args:
            image: Input image
            
        Returns:
            List of person detections
        """
        # Resize for faster processing
        resize_width = self.config.get('resize_width', 640)
        original_size = image.shape[:2]
        
        if image.shape[1] > resize_width:
            scale_factor = resize_width / image.shape[1]
            new_height = int(image.shape[0] * scale_factor)
            image_resized = cv2.resize(image, (resize_width, new_height))
        else:
            image_resized = image
            scale_factor = 1.0
        
        # Run inference
        results = self.model(image_resized, verbose=False)
        person_detections = []
        
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
            
            for box in boxes:
                class_id = int(box.cls)
                confidence = float(box.conf)
                
                # Filter for person class (class_id = 0 in COCO)
                if class_id == 0 and confidence >= self.confidence_threshold:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    
                    # Scale back to original image size
                    if scale_factor != 1.0:
                        x1 = int(x1 / scale_factor)
                        y1 = int(y1 / scale_factor)
                        x2 = int(x2 / scale_factor)
                        y2 = int(y2 / scale_factor)
                    else:
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    
                    # Ensure coordinates are within image bounds
                    x1 = max(0, min(x1, original_size[1]))
                    y1 = max(0, min(y1, original_size[0]))
                    x2 = max(0, min(x2, original_size[1]))
                    y2 = max(0, min(y2, original_size[0]))
                    
                    person_detections.append({
                        'bbox': [x1, y1, x2, y2],
                        'confidence': confidence,
                        'center': self._get_bbox_center([x1, y1, x2, y2]),
                        'area': (x2 - x1) * (y2 - y1),
                        'width': x2 - x1,
                        'height': y2 - y1
                    })
        
        return person_detections
    
    def _analyze_rider_count(self, person_detections: List[Dict]) -> Dict:
        """
        Analyze person detections to determine rider count and violations
        
        Args:
            person_detections: List of person detections
            
        Returns:
            Analysis results
        """
        if not person_detections:
            return {
                'violation': False,
                'confidence': 0.0,
                'rider_count': 0,
                'detections': []
            }
        
        # Filter detections based on size and position
        valid_riders = self._filter_valid_riders(person_detections)
        
        # Group overlapping detections (might be same person detected multiple times)
        grouped_riders = self._group_overlapping_detections(valid_riders)
        
        rider_count = len(grouped_riders)
        
        # Triple riding violation if more than 2 riders
        violation = rider_count > 2
        
        # Calculate overall confidence
        if grouped_riders:
            confidences = []
            for group in grouped_riders:
                group_confidences = [d['confidence'] for d in group]
                confidences.append(np.mean(group_confidences))
            overall_confidence = np.mean(confidences)
        else:
            overall_confidence = 0.0
        
        # Flatten detections for output
        flattened_detections = []
        for group in grouped_riders:
            flattened_detections.extend(group)
        
        return {
            'violation': violation,
            'confidence': float(overall_confidence),
            'rider_count': rider_count,
            'detections': flattened_detections,
            'grouped_riders': grouped_riders
        }
    
    def _filter_valid_riders(self, person_detections: List[Dict]) -> List[Dict]:
        """
        Filter person detections to keep only valid riders
        
        Args:
            person_detections: List of person detections
            
        Returns:
            Filtered list of valid rider detections
        """
        valid_riders = []
        
        for detection in person_detections:
            # Filter by minimum size (riders should be reasonably sized)
            min_area = self.config.get('min_rider_area', 500)
            if detection['area'] < min_area:
                continue
            
            # Filter by aspect ratio (people typically have certain proportions)
            aspect_ratio = detection['height'] / detection['width']
            if not (1.5 <= aspect_ratio <= 4.0):  # Typical human aspect ratio
                continue
            
            # Filter by position (riders should be on the vehicle)
            # This is a simplified check - in practice, you'd use vehicle position
            image_height = detection['bbox'][3]  # y2 coordinate
            
            # Riders should typically be in the upper portion of the vehicle ROI
            if detection['bbox'][1] > image_height * 0.7:  # y1 coordinate
                continue
            
            valid_riders.append(detection)
        
        return valid_riders
    
    def _group_overlapping_detections(self, detections: List[Dict], 
                                    iou_threshold: float = 0.3) -> List[List[Dict]]:
        """
        Group overlapping detections that likely represent the same person
        
        Args:
            detections: List of detections
            iou_threshold: IoU threshold for grouping
            
        Returns:
            List of grouped detections
        """
        if not detections:
            return []
        
        # Sort by confidence (highest first)
        detections.sort(key=lambda x: x['confidence'], reverse=True)
        
        groups = []
        used_indices = set()
        
        for i, detection in enumerate(detections):
            if i in used_indices:
                continue
            
            # Start a new group
            current_group = [detection]
            used_indices.add(i)
            
            # Find overlapping detections
            for j, other_detection in enumerate(detections):
                if j in used_indices:
                    continue
                
                iou = self._calculate_iou(detection['bbox'], other_detection['bbox'])
                if iou >= iou_threshold:
                    current_group.append(other_detection)
                    used_indices.add(j)
            
            groups.append(current_group)
        
        return groups
    
    def _get_bbox_center(self, bbox: List[int]) -> Tuple[int, int]:
        """Get center point of bounding box"""
        x1, y1, x2, y2 = bbox
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        return (center_x, center_y)
    
    def _calculate_iou(self, box1: List[int], box2: List[int]) -> float:
        """Calculate Intersection over Union between two bounding boxes"""
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        
        if x2 <= x1 or y2 <= y1:
            return 0.0
        
        intersection = (x2 - x1) * (y2 - y1)
        
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def estimate_rider_positions(self, vehicle_bbox: List[int], 
                               rider_detections: List[Dict]) -> List[Dict]:
        """
        Estimate rider positions relative to the vehicle
        
        Args:
            vehicle_bbox: Bounding box of the vehicle
            rider_detections: List of rider detections
            
        Returns:
            List of rider detections with position information
        """
        if not rider_detections:
            return []
        
        vehicle_x1, vehicle_y1, vehicle_x2, vehicle_y2 = vehicle_bbox
        vehicle_width = vehicle_x2 - vehicle_x1
        vehicle_height = vehicle_y2 - vehicle_y1
        
        riders_with_positions = []
        
        for rider in rider_detections:
            rider_x1, rider_y1, rider_x2, rider_y2 = rider['bbox']
            rider_center_x = (rider_x1 + rider_x2) // 2
            rider_center_y = (rider_y1 + rider_y2) // 2
            
            # Calculate relative position
            rel_x = (rider_center_x - vehicle_x1) / vehicle_width
            rel_y = (rider_center_y - vehicle_y1) / vehicle_height
            
            # Determine position (front, middle, back)
            if rel_x < 0.4:
                position = "front"
            elif rel_x < 0.7:
                position = "middle"
            else:
                position = "back"
            
            rider_with_pos = rider.copy()
            rider_with_pos.update({
                'relative_position': (rel_x, rel_y),
                'position_label': position
            })
            
            riders_with_positions.append(rider_with_pos)
        
        return riders_with_positions
    
    def visualize_detections(self, image: np.ndarray, 
                           detections: List[Dict], grouped_riders: List[List[Dict]] = None) -> np.ndarray:
        """
        Visualize triple riding detections on image
        
        Args:
            image: Input image
            detections: List of detections
            grouped_riders: Grouped detections (optional)
            
        Returns:
            Annotated image
        """
        annotated = image.copy()
        
        if grouped_riders:
            # Use grouped detections for better visualization
            colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
            
            for i, group in enumerate(grouped_riders):
                color = colors[i % len(colors)]
                
                # Draw each detection in the group
                for detection in group:
                    x1, y1, x2, y2 = detection['bbox']
                    confidence = detection['confidence']
                    
                    # Draw bounding box
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
                    
                    # Draw label
                    label = f"Rider {i+1} {confidence:.2f}"
                    cv2.putText(annotated, label, (x1, y1 - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        else:
            # Use individual detections
            for i, detection in enumerate(detections):
                x1, y1, x2, y2 = detection['bbox']
                confidence = detection['confidence']
                
                # Draw bounding box
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Draw label
                label = f"Rider {i+1} {confidence:.2f}"
                cv2.putText(annotated, label, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Add rider count
        rider_count = len(grouped_riders) if grouped_riders else len(detections)
        violation_text = f"Riders: {rider_count} {'(VIOLATION)' if rider_count > 2 else ''}"
        cv2.putText(annotated, violation_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255) if rider_count > 2 else (0, 255, 0), 2)
        
        return annotated

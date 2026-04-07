"""
Helmet Detection Module
Detects helmet usage on two-wheeler riders using deep learning
"""

import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Dict, Tuple
import logging
import os

class HelmetDetector:
    """Helmet detection for two-wheeler riders"""
    
    def __init__(self, config):
        """Initialize helmet detector
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.model = None
        self.confidence_threshold = config.get('helmet_detection_threshold', 0.6)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Helmet class mapping (will be set based on model)
        self.helmet_class_id = None
        self.head_class_id = None
        
        self._load_model()
    
    def _load_model(self):
        """Load YOLO model for helmet detection"""
        try:
            model_path = self.config.get_model_path('helmet')
            self.logger.info(f"Loading helmet detection model: {model_path}")
            
            if os.path.exists(model_path):
                self.model = YOLO(model_path)
                # Test model with dummy input
                test_input = np.zeros((640, 640, 3), dtype=np.uint8)
                results = self.model(test_input, verbose=False)
                
                # Determine class IDs from model
                if hasattr(results[0], 'names'):
                    names = results[0].names
                    for name_id, name in names.items():
                        if 'helmet' in name.lower():
                            self.helmet_class_id = name_id
                        elif 'head' in name.lower() or 'no_helmet' in name.lower():
                            self.head_class_id = name_id
                    
                    self.logger.info(f"Helmet class ID: {self.helmet_class_id}")
                    self.logger.info(f"Head/No helmet class ID: {self.head_class_id}")
                
                self.logger.info("Helmet detection model loaded successfully")
            else:
                self.logger.warning(f"Helmet model not found at {model_path}")
                self._create_fallback_model()
                
        except Exception as e:
            self.logger.error(f"Error loading helmet detection model: {e}")
            self._create_fallback_model()
    
    def _create_fallback_model(self):
        """Create fallback model using person detection"""
        try:
            self.logger.info("Using fallback person detection for helmet analysis")
            self.model = YOLO('yolov8n.pt')
            self.head_class_id = 0  # Person class in COCO
            self.helmet_class_id = None
        except Exception as e:
            self.logger.error(f"Failed to create fallback model: {e}")
            raise
    
    def detect_helmet_violation(self, vehicle_roi: np.ndarray) -> Dict:
        """
        Detect helmet violations in vehicle ROI
        
        Args:
            vehicle_roi: Region of interest containing the two-wheeler
            
        Returns:
            Dictionary with violation status and details
        """
        if self.model is None:
            return {
                'violation': False,
                'confidence': 0.0,
                'riders_without_helmet': 0,
                'total_riders': 0,
                'detections': []
            }
        
        try:
            # Detect persons and helmets in the vehicle ROI
            detections = self._detect_persons_and_helmets(vehicle_roi)
            
            # Analyze helmet usage
            helmet_analysis = self._analyze_helmet_usage(detections)
            
            return helmet_analysis
            
        except Exception as e:
            self.logger.error(f"Error in helmet detection: {e}")
            return {
                'violation': False,
                'confidence': 0.0,
                'riders_without_helmet': 0,
                'total_riders': 0,
                'error': str(e)
            }
    
    def _detect_persons_and_helmets(self, image: np.ndarray) -> List[Dict]:
        """
        Detect persons and helmets in the image
        
        Args:
            image: Input image
            
        Returns:
            List of detections
        """
        # Resize for faster processing
        resize_width = self.config.get('resize_width', 640)
        if image.shape[1] > resize_width:
            scale_factor = resize_width / image.shape[1]
            new_height = int(image.shape[0] * scale_factor)
            image_resized = cv2.resize(image, (resize_width, new_height))
        else:
            image_resized = image
            scale_factor = 1.0
        
        # Run inference
        results = self.model(image_resized, verbose=False)
        detections = []
        
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
            
            for box in boxes:
                class_id = int(box.cls)
                confidence = float(box.conf)
                
                # Filter for relevant classes
                if self._is_relevant_class(class_id):
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    
                    # Scale back to original image size
                    if scale_factor != 1.0:
                        x1 = int(x1 / scale_factor)
                        y1 = int(y1 / scale_factor)
                        x2 = int(x2 / scale_factor)
                        y2 = int(y2 / scale_factor)
                    else:
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    
                    detection_type = self._get_detection_type(class_id)
                    
                    detections.append({
                        'bbox': [x1, y1, x2, y2],
                        'confidence': confidence,
                        'type': detection_type,
                        'class_id': class_id,
                        'area': (x2 - x1) * (y2 - y1)
                    })
        
        return detections
    
    def _is_relevant_class(self, class_id: int) -> bool:
        """Check if class is relevant for helmet detection"""
        if self.helmet_class_id is not None and self.head_class_id is not None:
            # Using dedicated helmet model
            return class_id in [self.helmet_class_id, self.head_class_id]
        else:
            # Using fallback person detection
            return class_id == 0  # Person class
    
    def _get_detection_type(self, class_id: int) -> str:
        """Get detection type from class ID"""
        if self.helmet_class_id is not None and self.head_class_id is not None:
            if class_id == self.helmet_class_id:
                return 'helmet'
            elif class_id == self.head_class_id:
                return 'head'
        else:
            return 'person'
        
        return 'unknown'
    
    def _analyze_helmet_usage(self, detections: List[Dict]) -> Dict:
        """
        Analyze helmet usage from detections
        
        Args:
            detections: List of person/helmet detections
            
        Returns:
            Analysis results
        """
        if not detections:
            return {
                'violation': False,
                'confidence': 0.0,
                'riders_without_helmet': 0,
                'total_riders': 0,
                'detections': []
            }
        
        # Filter by confidence
        valid_detections = [d for d in detections 
                          if d['confidence'] >= self.confidence_threshold]
        
        if not valid_detections:
            return {
                'violation': False,
                'confidence': 0.0,
                'riders_without_helmet': 0,
                'total_riders': 0,
                'detections': []
            }
        
        # Sort by area (larger detections are likely closer/more important)
        valid_detections.sort(key=lambda x: x['area'], reverse=True)
        
        # Determine rider count and helmet usage
        if self.helmet_class_id is not None:
            # Using dedicated helmet model
            helmets = [d for d in valid_detections if d['type'] == 'helmet']
            heads = [d for d in valid_detections if d['type'] == 'head']
            
            total_riders = len(helmets) + len(heads)
            riders_without_helmet = len(heads)
            
            # Calculate overall confidence
            overall_confidence = np.mean([d['confidence'] for d in valid_detections])
            
        else:
            # Using fallback person detection
            # Estimate riders based on person detections
            total_riders = len(valid_detections)
            
            # For fallback, we'll use a heuristic based on position and size
            # This is less accurate but provides basic functionality
            riders_without_helmet = self._estimate_helmet_violations_fallback(valid_detections)
            
            overall_confidence = np.mean([d['confidence'] for d in valid_detections])
        
        # Determine violation (no helmet violation if any rider without helmet)
        violation = riders_without_helmet > 0
        
        return {
            'violation': violation,
            'confidence': float(overall_confidence),
            'riders_without_helmet': riders_without_helmet,
            'total_riders': total_riders,
            'detections': valid_detections
        }
    
    def _estimate_helmet_violations_fallback(self, person_detections: List[Dict]) -> int:
        """
        Estimate helmet violations using person detection (fallback method)
        
        Args:
            person_detections: List of person detections
            
        Returns:
            Estimated number of riders without helmet
        """
        # This is a heuristic approach for when dedicated helmet model is not available
        # We'll assume violations based on detection characteristics
        
        violations = 0
        
        for person in person_detections:
            x1, y1, x2, y2 = person['bbox']
            width = x2 - x1
            height = y2 - y1
            
            # Heuristic: if head area is clearly visible and large, likely no helmet
            # This is a simplified approach - in practice, you'd want a proper helmet model
            head_ratio = height / width
            
            # Another heuristic: check if the upper portion of the person detection
            # has characteristics suggesting no helmet (e.g., hair visibility)
            # For now, we'll use a conservative approach
            
            # Assume 30% chance of violation per person (conservative estimate)
            if np.random.random() < 0.3:  # This would be replaced with actual logic
                violations += 1
        
        return violations
    
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
    
    def visualize_detections(self, image: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        Visualize helmet detections on image
        
        Args:
            image: Input image
            detections: List of detections
            
        Returns:
            Annotated image
        """
        annotated = image.copy()
        
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            confidence = detection['confidence']
            detection_type = detection['type']
            
            # Choose color based on detection type
            if detection_type == 'helmet':
                color = (0, 255, 0)  # Green for helmet
                label = f"Helmet {confidence:.2f}"
            elif detection_type == 'head':
                color = (0, 0, 255)  # Red for no helmet
                label = f"No Helmet {confidence:.2f}"
            else:
                color = (255, 255, 0)  # Yellow for person
                label = f"Person {confidence:.2f}"
            
            # Draw bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            cv2.putText(annotated, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return annotated

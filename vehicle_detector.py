"""
Vehicle Detection Module
Detects two-wheelers (motorcycles, scooters) using YOLO
"""

import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Dict, Tuple
import logging

class VehicleDetector:
    """Two-wheeler detection using YOLO model"""
    
    # COCO class IDs for two-wheelers
    TWO_WHEELER_CLASSES = {
        'motorcycle': 3,
        'bicycle': 1
    }
    
    def __init__(self, config):
        """Initialize vehicle detector
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.model = None
        self.confidence_threshold = config.get('vehicle_detection_threshold', 0.5)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self._load_model()
    
    def _load_model(self):
        """Load YOLO model for vehicle detection"""
        try:
            model_path = self.config.get_model_path('vehicle')
            self.logger.info(f"Loading vehicle detection model: {model_path}")
            
            # Load YOLOv8 model
            self.model = YOLO(model_path)
            
            # Test model with dummy input
            test_input = np.zeros((640, 640, 3), dtype=np.uint8)
            _ = self.model(test_input, verbose=False)
            
            self.logger.info("Vehicle detection model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading vehicle detection model: {e}")
            # Fallback to a basic model
            try:
                self.model = YOLO('yolov8n.pt')  # Use default model
                self.logger.info("Using default YOLOv8n model")
            except Exception as fallback_error:
                self.logger.error(f"Failed to load fallback model: {fallback_error}")
                raise
    
    def detect_two_wheelers(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect two-wheelers in the given frame
        
        Args:
            frame: Input image frame
            
        Returns:
            List of detected two-wheelers with bounding boxes and confidence
        """
        if self.model is None:
            self.logger.error("Model not loaded")
            return []
        
        try:
            # Resize frame for faster processing if specified
            original_size = frame.shape[:2]
            resize_width = self.config.get('resize_width', 640)
            
            if resize_width and frame.shape[1] > resize_width:
                scale_factor = resize_width / frame.shape[1]
                new_height = int(frame.shape[0] * scale_factor)
                frame_resized = cv2.resize(frame, (resize_width, new_height))
            else:
                frame_resized = frame
                scale_factor = 1.0
            
            # Run inference
            results = self.model(frame_resized, verbose=False)
            
            two_wheelers = []
            
            for result in results:
                boxes = result.boxes
                if boxes is None:
                    continue
                
                for box in boxes:
                    # Get class and confidence
                    class_id = int(box.cls)
                    confidence = float(box.conf)
                    
                    # Check if it's a two-wheeler
                    if class_id in self.TWO_WHEELER_CLASSES.values():
                        if confidence >= self.confidence_threshold:
                            # Get bounding box coordinates
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            
                            # Scale back to original frame size
                            if scale_factor != 1.0:
                                x1 = int(x1 / scale_factor)
                                y1 = int(y1 / scale_factor)
                                x2 = int(x2 / scale_factor)
                                y2 = int(y2 / scale_factor)
                            else:
                                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                            
                            # Ensure coordinates are within frame bounds
                            x1 = max(0, min(x1, original_size[1]))
                            y1 = max(0, min(y1, original_size[0]))
                            x2 = max(0, min(x2, original_size[1]))
                            y2 = max(0, min(y2, original_size[0]))
                            
                            # Get class name
                            class_name = self._get_class_name(class_id)
                            
                            two_wheelers.append({
                                'bbox': [x1, y1, x2, y2],
                                'confidence': confidence,
                                'class_name': class_name,
                                'class_id': class_id,
                                'area': (x2 - x1) * (y2 - y1)
                            })
            
            # Sort by confidence (highest first)
            two_wheelers.sort(key=lambda x: x['confidence'], reverse=True)
            
            return two_wheelers
            
        except Exception as e:
            self.logger.error(f"Error in vehicle detection: {e}")
            return []
    
    def _get_class_name(self, class_id: int) -> str:
        """Get class name from class ID
        
        Args:
            class_id: COCO class ID
            
        Returns:
            Class name string
        """
        class_names = {
            0: 'person',
            1: 'bicycle',
            2: 'car',
            3: 'motorcycle',
            5: 'bus',
            7: 'truck'
        }
        return class_names.get(class_id, f'unknown_{class_id}')
    
    def filter_overlapping_detections(self, detections: List[Dict], 
                                    iou_threshold: float = 0.5) -> List[Dict]:
        """
        Filter overlapping detections using Non-Maximum Suppression
        
        Args:
            detections: List of vehicle detections
            iou_threshold: IoU threshold for NMS
            
        Returns:
            Filtered list of detections
        """
        if not detections:
            return []
        
        # Sort by confidence
        detections.sort(key=lambda x: x['confidence'], reverse=True)
        
        keep = []
        while detections:
            # Keep the highest confidence detection
            current = detections.pop(0)
            keep.append(current)
            
            # Remove overlapping detections
            remaining = []
            for detection in detections:
                iou = self._calculate_iou(current['bbox'], detection['bbox'])
                if iou < iou_threshold:
                    remaining.append(detection)
            
            detections = remaining
        
        return keep
    
    def _calculate_iou(self, box1: List[int], box2: List[int]) -> float:
        """
        Calculate Intersection over Union (IoU) between two bounding boxes
        
        Args:
            box1: First bounding box [x1, y1, x2, y2]
            box2: Second bounding box [x1, y1, x2, y2]
            
        Returns:
            IoU value
        """
        # Calculate intersection
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        
        if x2 <= x1 or y2 <= y1:
            return 0.0
        
        intersection = (x2 - x1) * (y2 - y1)
        
        # Calculate union
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = area1 + area2 - intersection
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def get_vehicle_roi(self, frame: np.ndarray, bbox: List[int]) -> np.ndarray:
        """
        Extract Region of Interest for detected vehicle
        
        Args:
            frame: Input frame
            bbox: Bounding box coordinates [x1, y1, x2, y2]
            
        Returns:
            Vehicle ROI
        """
        x1, y1, x2, y2 = bbox
        
        # Ensure coordinates are within frame bounds
        height, width = frame.shape[:2]
        x1 = max(0, min(x1, width))
        y1 = max(0, min(y1, height))
        x2 = max(0, min(x2, width))
        y2 = max(0, min(y2, height))
        
        return frame[y1:y2, x1:x2]
    
    def validate_detection(self, detection: Dict) -> bool:
        """
        Validate if detection meets criteria
        
        Args:
            detection: Detection dictionary
            
        Returns:
            True if valid detection
        """
        # Check minimum size
        min_area = self.config.get('min_vehicle_area', 1000)
        if detection['area'] < min_area:
            return False
        
        # Check aspect ratio (two-wheelers typically have specific ratios)
        x1, y1, x2, y2 = detection['bbox']
        width = x2 - x1
        height = y2 - y1
        
        if width <= 0 or height <= 0:
            return False
        
        aspect_ratio = width / height
        
        # Two-wheelers typically have aspect ratio between 0.5 and 2.0
        if not (0.5 <= aspect_ratio <= 2.0):
            return False
        
        return True

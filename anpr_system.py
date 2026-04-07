"""
Automatic Number Plate Recognition (ANPR) System
Detects and recognizes vehicle number plates using deep learning and OCR
"""

import cv2
import numpy as np
import pytesseract
import re
from ultralytics import YOLO
from typing import List, Dict, Tuple, Optional
import logging
import os

class ANPRSystem:
    """Automatic Number Plate Recognition System"""
    
    def __init__(self, config):
        """Initialize ANPR system
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.plate_detector = None
        self.confidence_threshold = config.get('plate_detection_threshold', 0.5)
        self.ocr_confidence_threshold = config.get('ocr_confidence_threshold', 0.6)
        
        # Indian number plate patterns
        self.plate_patterns = [
            # Standard Indian format: XX-XX-XX-XXXX (e.g., MH-12-AB-1234)
            r'^[A-Z]{2}[ -][0-9]{2}[ -][A-Z]{1,2}[ -][0-9]{4}$',
            # Alternative format: XXXX-XXXX-XXXX
            r'^[A-Z]{2,3}[0-9]{1,4}[A-Z]{0,3}[0-9]{1,4}$',
            # Simple format: XX-XXXX-XXXX
            r'^[A-Z]{2}[ -][0-9]{1,2}[ -][A-Z]{0,2}[ -][0-9]{4}$',
            # Old format: XX-XX-XXXX
            r'^[A-Z]{2}[ -][0-9]{2}[ -][A-Z]{0,2}[ -][0-9]{4}$'
        ]
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Configure Tesseract
        self._configure_tesseract()
        
        self._load_plate_detector()
    
    def _configure_tesseract(self):
        """Configure Tesseract OCR"""
        try:
            # Set Tesseract configuration for Indian number plates
            self.tesseract_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789- '
            
            # Test Tesseract
            test_image = np.zeros((50, 200, 3), dtype=np.uint8)
            cv2.putText(test_image, "TEST1234", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            result = pytesseract.image_to_string(test_image, config=self.tesseract_config)
            self.logger.info("Tesseract OCR configured successfully")
            
        except Exception as e:
            self.logger.error(f"Error configuring Tesseract: {e}")
            self.logger.warning("ANPR functionality may be limited")
    
    def _load_plate_detector(self):
        """Load YOLO model for number plate detection"""
        try:
            model_path = self.config.get_model_path('anpr')
            self.logger.info(f"Loading ANPR model: {model_path}")
            
            if os.path.exists(model_path):
                self.plate_detector = YOLO(model_path)
                # Test model
                test_input = np.zeros((640, 640, 3), dtype=np.uint8)
                _ = self.plate_detector(test_input, verbose=False)
                self.logger.info("ANPR model loaded successfully")
            else:
                self.logger.warning(f"ANPR model not found at {model_path}")
                self._create_fallback_detector()
                
        except Exception as e:
            self.logger.error(f"Error loading ANPR model: {e}")
            self._create_fallback_detector()
    
    def _create_fallback_detector(self):
        """Create fallback plate detection using traditional methods"""
        self.logger.info("Using fallback plate detection method")
        self.plate_detector = None
    
    def recognize_plate(self, vehicle_roi: np.ndarray) -> Dict:
        """
        Recognize number plate from vehicle ROI
        
        Args:
            vehicle_roi: Region of interest containing the vehicle
            
        Returns:
            Dictionary with plate recognition results
        """
        try:
            # Step 1: Detect number plates in the vehicle ROI
            plate_detections = self._detect_plates(vehicle_roi)
            
            if not plate_detections:
                return {
                    'plate_number': '',
                    'confidence': 0.0,
                    'plate_bbox': None,
                    'detections': []
                }
            
            # Step 2: Process each detected plate
            best_result = {
                'plate_number': '',
                'confidence': 0.0,
                'plate_bbox': None,
                'detections': plate_detections
            }
            
            for detection in plate_detections:
                # Extract plate ROI
                plate_roi = self._extract_plate_roi(vehicle_roi, detection['bbox'])
                
                if plate_roi is None:
                    continue
                
                # Step 3: Preprocess plate image for OCR
                processed_plate = self._preprocess_plate_image(plate_roi)
                
                # Step 4: Perform OCR
                ocr_result = self._perform_ocr(processed_plate)
                
                # Step 5: Validate and format the plate number
                validated_plate = self._validate_plate_number(ocr_result['text'])
                
                if validated_plate and ocr_result['confidence'] > best_result['confidence']:
                    best_result.update({
                        'plate_number': validated_plate,
                        'confidence': ocr_result['confidence'],
                        'plate_bbox': detection['bbox'],
                        'raw_text': ocr_result['text'],
                        'processed_image': processed_plate
                    })
            
            return best_result
            
        except Exception as e:
            self.logger.error(f"Error in plate recognition: {e}")
            return {
                'plate_number': '',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _detect_plates(self, image: np.ndarray) -> List[Dict]:
        """
        Detect number plates in the image
        
        Args:
            image: Input image
            
        Returns:
            List of plate detections
        """
        if self.plate_detector is not None:
            return self._detect_plates_yolo(image)
        else:
            return self._detect_plates_traditional(image)
    
    def _detect_plates_yolo(self, image: np.ndarray) -> List[Dict]:
        """Detect plates using YOLO model"""
        detections = []
        
        try:
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
            results = self.plate_detector(image_resized, verbose=False)
            
            for result in results:
                boxes = result.boxes
                if boxes is None:
                    continue
                
                for box in boxes:
                    confidence = float(box.conf)
                    
                    if confidence >= self.confidence_threshold:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        
                        # Scale back to original image size
                        if scale_factor != 1.0:
                            x1 = int(x1 / scale_factor)
                            y1 = int(y1 / scale_factor)
                            x2 = int(x2 / scale_factor)
                            y2 = int(y2 / scale_factor)
                        else:
                            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                        
                        # Validate plate dimensions
                        if self._validate_plate_dimensions(x1, y1, x2, y2, original_size):
                            detections.append({
                                'bbox': [x1, y1, x2, y2],
                                'confidence': confidence,
                                'area': (x2 - x1) * (y2 - y1)
                            })
            
            # Sort by confidence
            detections.sort(key=lambda x: x['confidence'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error in YOLO plate detection: {e}")
        
        return detections
    
    def _detect_plates_traditional(self, image: np.ndarray) -> List[Dict]:
        """Detect plates using traditional computer vision methods"""
        detections = []
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply bilateral filter to reduce noise while preserving edges
            filtered = cv2.bilateralFilter(gray, 11, 17, 17)
            
            # Edge detection
            edges = cv2.Canny(filtered, 30, 200)
            
            # Find contours
            contours, _ = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            # Sort contours by area
            contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
            
            image_height, image_width = image.shape[:2]
            
            for contour in contours:
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Validate plate dimensions
                if self._validate_plate_dimensions(x, y, x + w, y + h, (image_height, image_width)):
                    # Calculate aspect ratio
                    aspect_ratio = w / h
                    
                    # Number plates typically have aspect ratio between 2 and 6
                    if 2 <= aspect_ratio <= 6:
                        detections.append({
                            'bbox': [x, y, x + w, y + h],
                            'confidence': 0.5,  # Default confidence for traditional method
                            'area': w * h
                        })
            
            # Sort by area (largest first)
            detections.sort(key=lambda x: x['area'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error in traditional plate detection: {e}")
        
        return detections[:3]  # Return top 3 candidates
    
    def _validate_plate_dimensions(self, x1: int, y1: int, x2: int, y2: int, 
                                 image_size: Tuple[int, int]) -> bool:
        """Validate if detected region has valid plate dimensions"""
        width = x2 - x1
        height = y2 - y1
        image_height, image_width = image_size
        
        # Minimum dimensions
        min_width = self.config.get('min_plate_width', 80)
        min_height = self.config.get('min_plate_height', 20)
        
        if width < min_width or height < min_height:
            return False
        
        # Maximum dimensions (plate shouldn't be too large)
        if width > image_width * 0.8 or height > image_height * 0.8:
            return False
        
        # Aspect ratio check
        aspect_ratio = width / height
        if not (2.0 <= aspect_ratio <= 6.0):
            return False
        
        return True
    
    def _extract_plate_roi(self, image: np.ndarray, bbox: List[int]) -> Optional[np.ndarray]:
        """Extract plate region of interest"""
        try:
            x1, y1, x2, y2 = bbox
            height, width = image.shape[:2]
            
            # Ensure coordinates are within bounds
            x1 = max(0, min(x1, width))
            y1 = max(0, min(y1, height))
            x2 = max(0, min(x2, width))
            y2 = max(0, min(y2, height))
            
            if x2 <= x1 or y2 <= y1:
                return None
            
            return image[y1:y2, x1:x2]
            
        except Exception as e:
            self.logger.error(f"Error extracting plate ROI: {e}")
            return None
    
    def _preprocess_plate_image(self, plate_image: np.ndarray) -> np.ndarray:
        """
        Preprocess plate image for better OCR accuracy
        
        Args:
            plate_image: Raw plate image
            
        Returns:
            Processed plate image
        """
        try:
            # Convert to grayscale
            if len(plate_image.shape) == 3:
                gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
            else:
                gray = plate_image.copy()
            
            # Resize to a standard height for better OCR
            target_height = 50
            aspect_ratio = gray.shape[1] / gray.shape[0]
            target_width = int(target_height * aspect_ratio)
            resized = cv2.resize(gray, (target_width, target_height))
            
            # Apply adaptive thresholding
            binary = cv2.adaptiveThreshold(resized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY, 11, 2)
            
            # Remove noise
            kernel = np.ones((1, 1), np.uint8)
            processed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            processed = cv2.morphologyEx(processed, cv2.MORPH_OPEN, kernel)
            
            return processed
            
        except Exception as e:
            self.logger.error(f"Error preprocessing plate image: {e}")
            return plate_image
    
    def _perform_ocr(self, processed_image: np.ndarray) -> Dict:
        """
        Perform OCR on processed plate image
        
        Args:
            processed_image: Preprocessed plate image
            
        Returns:
            OCR results
        """
        try:
            # Perform OCR using Tesseract
            text = pytesseract.image_to_string(processed_image, config=self.tesseract_config)
            
            # Clean the text
            text = text.strip().upper()
            text = re.sub(r'[^A-Z0-9-]', '', text)  # Keep only alphanumeric and hyphens
            
            # Get confidence data
            data = pytesseract.image_to_data(processed_image, config=self.tesseract_config, 
                                            output_type=pytesseract.Output.DICT)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = np.mean(confidences) / 100.0 if confidences else 0.0
            
            return {
                'text': text,
                'confidence': avg_confidence,
                'raw_data': data
            }
            
        except Exception as e:
            self.logger.error(f"Error performing OCR: {e}")
            return {
                'text': '',
                'confidence': 0.0
            }
    
    def _validate_plate_number(self, text: str) -> Optional[str]:
        """
        Validate and format the detected plate number
        
        Args:
            text: Raw OCR text
            
        Returns:
            Validated plate number or None if invalid
        """
        if not text or len(text) < 4:
            return None
        
        # Try to match against Indian plate patterns
        for pattern in self.plate_patterns:
            if re.match(pattern, text):
                return self._format_plate_number(text)
        
        # Try common variations and corrections
        corrected_text = self._correct_common_errors(text)
        
        for pattern in self.plate_patterns:
            if re.match(pattern, corrected_text):
                return self._format_plate_number(corrected_text)
        
        # If no pattern matches, return text if it meets minimum criteria
        if len(text) >= 6 and any(c.isdigit() for c in text) and any(c.isalpha() for c in text):
            return self._format_plate_number(text)
        
        return None
    
    def _correct_common_errors(self, text: str) -> str:
        """Correct common OCR errors in number plates"""
        # Common character substitutions
        corrections = {
            '0': 'O',  # Zero to O (in certain positions)
            '1': 'I',  # One to I (in certain positions)
            '5': 'S',  # Five to S
            '8': 'B',  # Eight to B
        }
        
        # Apply corrections based on position (simplified)
        corrected = text
        if len(corrected) >= 2:
            # First two characters are usually state code (letters)
            if corrected[0].isdigit():
                corrected = corrections.get(corrected[0], corrected[0]) + corrected[1:]
            if corrected[1].isdigit():
                corrected = corrected[0] + corrections.get(corrected[1], corrected[1]) + corrected[2:]
        
        return corrected
    
    def _format_plate_number(self, text: str) -> str:
        """Format plate number according to Indian standards"""
        # Remove extra spaces and hyphens
        text = re.sub(r'[ -]+', ' ', text).strip()
        
        # Try to format as standard Indian plate: XX-XX-XX-XXXX
        if len(text) >= 10:
            # Example: MH12AB1234 -> MH-12-AB-1234
            if text[2].isdigit() and text[4].isdigit():
                formatted = f"{text[:2]}-{text[2:4]}-{text[4:6]}-{text[6:]}"
                return formatted
        
        return text
    
    def visualize_detections(self, image: np.ndarray, detections: List[Dict], 
                           plate_number: str = '') -> np.ndarray:
        """
        Visualize plate detections on image
        
        Args:
            image: Input image
            detections: List of plate detections
            plate_number: Recognized plate number
            
        Returns:
            Annotated image
        """
        annotated = image.copy()
        
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            confidence = detection['confidence']
            
            # Draw bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw confidence
            label = f"Plate {confidence:.2f}"
            cv2.putText(annotated, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Draw recognized plate number
        if plate_number:
            cv2.putText(annotated, f"Number: {plate_number}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        
        return annotated

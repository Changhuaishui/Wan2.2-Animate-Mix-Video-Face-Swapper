"""
Image validation module for Wan2.2 Video Processor
Validates images according to API requirements
"""
import os
from typing import Tuple, Optional, List
from pathlib import Path
from PIL import Image

# OpenCV is optional - face detection will be disabled if not available
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

from ..config.settings import Config
from ..utils.logger import setup_logger
from ..utils.file_handler import FileHandler

logger = setup_logger("image_validator")


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class ImageValidator:
    """
    Validator for input images

    Validates:
    - File format (JPG, JPEG, PNG, BMP, WEBP)
    - Image dimensions (200-4096 pixels)
    - Aspect ratio (1:3 to 3:1)
    - File size (<5MB)
    - Face detection (optional, must have exactly 1 face)
    """

    def __init__(self):
        """Initialize the image validator"""
        self.allowed_formats = Config.IMAGE_FORMATS
        self.min_size = Config.IMAGE_MIN_SIZE
        self.max_size = Config.IMAGE_MAX_SIZE
        self.max_file_size = Config.IMAGE_MAX_FILE_SIZE
        self.min_aspect_ratio = Config.IMAGE_MIN_ASPECT_RATIO
        self.max_aspect_ratio = Config.IMAGE_MAX_ASPECT_RATIO
        self.enable_face_detection = Config.ENABLE_FACE_DETECTION
        self.required_face_count = Config.REQUIRED_FACE_COUNT

        # Load face detector if needed
        self.face_cascade = None
        if self.enable_face_detection:
            self._load_face_detector()

    def _load_face_detector(self):
        """Load OpenCV face detector"""
        if not CV2_AVAILABLE:
            logger.warning("OpenCV not available. Face detection will be disabled.")
            self.enable_face_detection = False
            return

        try:
            # Load Haar Cascade for face detection
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            logger.debug("Face detector loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load face detector: {e}. Face detection will be disabled.")
            self.enable_face_detection = False

    def validate(self, image_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate an image file

        Args:
            image_path: Path to the image file

        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if validation passes, False otherwise
            - error_message: None if valid, error description if invalid
        """
        try:
            # Check 1: File exists
            if not os.path.exists(image_path):
                return False, f"File not found: {image_path}"

            # Check 2: File format
            extension = FileHandler.get_file_extension(image_path)
            if extension not in self.allowed_formats:
                return False, (
                    f"Invalid image format: {extension}. "
                    f"Allowed formats: {', '.join(self.allowed_formats)}"
                )

            # Check 3: File size
            file_size = FileHandler.get_file_size(image_path)
            if file_size > self.max_file_size:
                return False, (
                    f"Image file too large: {FileHandler.format_file_size(file_size)}. "
                    f"Maximum allowed: {FileHandler.format_file_size(self.max_file_size)}"
                )

            # Load image for further checks
            try:
                img = Image.open(image_path)
                width, height = img.size
            except Exception as e:
                return False, f"Failed to load image: {str(e)}"

            # Check 4: Image dimensions
            if width < self.min_size or height < self.min_size:
                return False, (
                    f"Image too small: {width}x{height}. "
                    f"Minimum size: {self.min_size}x{self.min_size}"
                )

            if width > self.max_size or height > self.max_size:
                return False, (
                    f"Image too large: {width}x{height}. "
                    f"Maximum size: {self.max_size}x{self.max_size}"
                )

            # Check 5: Aspect ratio
            aspect_ratio = width / height
            if aspect_ratio < self.min_aspect_ratio or aspect_ratio > self.max_aspect_ratio:
                return False, (
                    f"Invalid aspect ratio: {aspect_ratio:.2f}. "
                    f"Must be between {self.min_aspect_ratio:.2f} and {self.max_aspect_ratio:.2f}"
                )

            # Check 6: Face detection (if enabled)
            if self.enable_face_detection:
                face_check_result = self._check_faces(image_path)
                if not face_check_result[0]:
                    return face_check_result

            logger.info(f"Image validation passed: {image_path}")
            return True, None

        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def _check_faces(self, image_path: str) -> Tuple[bool, Optional[str]]:
        """
        Check if image contains exactly one face

        Args:
            image_path: Path to the image

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.face_cascade:
            return True, None  # Skip if detector not loaded

        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                return False, "Failed to read image for face detection"

            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )

            face_count = len(faces)

            if face_count == 0:
                return False, "No face detected in image. Please ensure the image contains a clear, visible face."

            if face_count > self.required_face_count:
                return False, (
                    f"Multiple faces detected ({face_count}). "
                    f"Image must contain exactly {self.required_face_count} face."
                )

            logger.debug(f"Face detection passed: found {face_count} face(s)")
            return True, None

        except Exception as e:
            logger.warning(f"Face detection error: {e}. Skipping face validation.")
            return True, None  # Don't fail validation if face detection errors occur

    def get_image_info(self, image_path: str) -> dict:
        """
        Get detailed information about an image

        Args:
            image_path: Path to the image

        Returns:
            Dictionary with image information
        """
        info = {
            "path": image_path,
            "exists": os.path.exists(image_path),
            "valid": False,
            "error": None
        }

        if not info["exists"]:
            info["error"] = "File not found"
            return info

        try:
            # Basic file info
            info["extension"] = FileHandler.get_file_extension(image_path)
            info["file_size"] = FileHandler.get_file_size(image_path)
            info["file_size_formatted"] = FileHandler.format_file_size(info["file_size"])

            # Image info
            img = Image.open(image_path)
            width, height = img.size
            info["width"] = width
            info["height"] = height
            info["aspect_ratio"] = width / height
            info["mode"] = img.mode
            info["format"] = img.format

            # Validation
            is_valid, error = self.validate(image_path)
            info["valid"] = is_valid
            info["error"] = error

        except Exception as e:
            info["error"] = str(e)

        return info

    def validate_and_raise(self, image_path: str):
        """
        Validate image and raise exception if invalid

        Args:
            image_path: Path to the image

        Raises:
            ValidationError: If validation fails
        """
        is_valid, error_message = self.validate(image_path)
        if not is_valid:
            raise ValidationError(f"Image validation failed: {error_message}")


if __name__ == "__main__":
    # Test validator
    validator = ImageValidator()

    # Test with a sample image path
    test_image = "test_image.jpg"
    if os.path.exists(test_image):
        is_valid, error = validator.validate(test_image)
        if is_valid:
            print(f"Image is valid: {test_image}")
            info = validator.get_image_info(test_image)
            print(f"Image info: {info}")
        else:
            print(f"Image validation failed: {error}")
    else:
        print(f"Test image not found: {test_image}")

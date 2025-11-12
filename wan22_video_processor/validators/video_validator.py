"""
Video validation module for Wan2.2 Video Processor
Validates videos according to API requirements
"""
import os
from typing import Tuple, Optional
from pathlib import Path

# OpenCV is optional - face detection will be disabled if not available
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

from ..config.settings import Config
from ..utils.logger import setup_logger
from ..utils.file_handler import FileHandler

logger = setup_logger("video_validator")


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class VideoValidator:
    """
    Validator for input videos

    Validates:
    - File format (MP4, AVI, MOV)
    - Video resolution (200-2048 pixels)
    - Aspect ratio (1:3 to 3:1)
    - Duration (2-30 seconds)
    - File size (<200MB)
    - First frame face detection (optional)
    """

    def __init__(self):
        """Initialize the video validator"""
        self.allowed_formats = Config.VIDEO_FORMATS
        self.min_size = Config.VIDEO_MIN_SIZE
        self.max_size = Config.VIDEO_MAX_SIZE
        self.min_duration = Config.VIDEO_MIN_DURATION
        self.max_duration = Config.VIDEO_MAX_DURATION
        self.max_file_size = Config.VIDEO_MAX_FILE_SIZE
        self.min_aspect_ratio = Config.VIDEO_MIN_ASPECT_RATIO
        self.max_aspect_ratio = Config.VIDEO_MAX_ASPECT_RATIO
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
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            logger.debug("Face detector loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load face detector: {e}. Face detection will be disabled.")
            self.enable_face_detection = False

    def validate(self, video_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a video file

        Args:
            video_path: Path to the video file

        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if validation passes, False otherwise
            - error_message: None if valid, error description if invalid
        """
        try:
            # Check 1: File exists
            if not os.path.exists(video_path):
                return False, f"File not found: {video_path}"

            # Check 2: File format
            extension = FileHandler.get_file_extension(video_path)
            if extension not in self.allowed_formats:
                return False, (
                    f"Invalid video format: {extension}. "
                    f"Allowed formats: {', '.join(self.allowed_formats)}"
                )

            # Check 3: File size
            file_size = FileHandler.get_file_size(video_path)
            if file_size > self.max_file_size:
                return False, (
                    f"Video file too large: {FileHandler.format_file_size(file_size)}. "
                    f"Maximum allowed: {FileHandler.format_file_size(self.max_file_size)}"
                )

            # Load video for further checks
            if not CV2_AVAILABLE:
                logger.warning("OpenCV not available. Skipping detailed video validation.")
                logger.info("Only basic file checks performed (format, size)")
                return True, None

            try:
                cap = cv2.VideoCapture(video_path)
                if not cap.isOpened():
                    return False, "Failed to open video file"

                # Get video properties
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

                # Calculate duration
                if fps > 0:
                    duration = frame_count / fps
                else:
                    cap.release()
                    return False, "Could not determine video FPS"

            except Exception as e:
                return False, f"Failed to load video: {str(e)}"

            # Check 4: Video dimensions
            if width < self.min_size or height < self.min_size:
                cap.release()
                return False, (
                    f"Video resolution too small: {width}x{height}. "
                    f"Minimum: {self.min_size}x{self.min_size}"
                )

            if width > self.max_size or height > self.max_size:
                cap.release()
                return False, (
                    f"Video resolution too large: {width}x{height}. "
                    f"Maximum: {self.max_size}x{self.max_size}"
                )

            # Check 5: Aspect ratio
            aspect_ratio = width / height
            if aspect_ratio < self.min_aspect_ratio or aspect_ratio > self.max_aspect_ratio:
                cap.release()
                return False, (
                    f"Invalid aspect ratio: {aspect_ratio:.2f}. "
                    f"Must be between {self.min_aspect_ratio:.2f} and {self.max_aspect_ratio:.2f}"
                )

            # Check 6: Duration
            if duration < self.min_duration:
                cap.release()
                return False, (
                    f"Video too short: {duration:.2f}s. "
                    f"Minimum duration: {self.min_duration}s"
                )

            if duration > self.max_duration:
                cap.release()
                return False, (
                    f"Video too long: {duration:.2f}s. "
                    f"Maximum duration: {self.max_duration}s"
                )

            # Check 7: First frame face detection (if enabled)
            if self.enable_face_detection:
                face_check_result = self._check_first_frame_face(cap)
                cap.release()
                if not face_check_result[0]:
                    return face_check_result
            else:
                cap.release()

            logger.info(f"Video validation passed: {video_path} ({duration:.2f}s, {width}x{height})")
            return True, None

        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def _check_first_frame_face(self, cap: cv2.VideoCapture) -> Tuple[bool, Optional[str]]:
        """
        Check if first frame of video contains exactly one face

        Args:
            cap: OpenCV VideoCapture object

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.face_cascade:
            return True, None  # Skip if detector not loaded

        try:
            # Reset to first frame
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

            # Read first frame
            ret, frame = cap.read()
            if not ret or frame is None:
                return False, "Failed to read first frame for face detection"

            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )

            face_count = len(faces)

            if face_count == 0:
                return False, "No face detected in first frame of video. Please ensure the video shows a clear face."

            if face_count > self.required_face_count:
                return False, (
                    f"Multiple faces detected in first frame ({face_count}). "
                    f"Video must show exactly {self.required_face_count} face."
                )

            logger.debug(f"First frame face detection passed: found {face_count} face(s)")
            return True, None

        except Exception as e:
            logger.warning(f"Face detection error: {e}. Skipping face validation.")
            return True, None  # Don't fail validation if face detection errors occur

    def get_video_info(self, video_path: str) -> dict:
        """
        Get detailed information about a video

        Args:
            video_path: Path to the video

        Returns:
            Dictionary with video information
        """
        info = {
            "path": video_path,
            "exists": os.path.exists(video_path),
            "valid": False,
            "error": None
        }

        if not info["exists"]:
            info["error"] = "File not found"
            return info

        try:
            # Basic file info
            info["extension"] = FileHandler.get_file_extension(video_path)
            info["file_size"] = FileHandler.get_file_size(video_path)
            info["file_size_formatted"] = FileHandler.format_file_size(info["file_size"])

            # Video info
            if not CV2_AVAILABLE:
                logger.warning("OpenCV not available. Video properties not available.")
            else:
                cap = cv2.VideoCapture(video_path)
                if cap.isOpened():
                    info["width"] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    info["height"] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    info["fps"] = cap.get(cv2.CAP_PROP_FPS)
                    info["frame_count"] = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

                    if info["fps"] > 0:
                        info["duration"] = info["frame_count"] / info["fps"]
                        info["aspect_ratio"] = info["width"] / info["height"]

                    cap.release()

            # Validation
            is_valid, error = self.validate(video_path)
            info["valid"] = is_valid
            info["error"] = error

        except Exception as e:
            info["error"] = str(e)

        return info

    def validate_and_raise(self, video_path: str):
        """
        Validate video and raise exception if invalid

        Args:
            video_path: Path to the video

        Raises:
            ValidationError: If validation fails
        """
        is_valid, error_message = self.validate(video_path)
        if not is_valid:
            raise ValidationError(f"Video validation failed: {error_message}")

    def estimate_processing_cost(self, video_path: str, mode: str = None) -> Optional[float]:
        """
        Estimate the cost to process this video

        Args:
            video_path: Path to the video
            mode: Processing mode ('wan-std' or 'wan-pro')

        Returns:
            Estimated cost in RMB, or None if video info unavailable
        """
        info = self.get_video_info(video_path)
        if "duration" in info:
            return Config.estimate_cost(info["duration"], mode)
        return None


if __name__ == "__main__":
    # Test validator
    validator = VideoValidator()

    # Test with a sample video path
    test_video = "test_video.mp4"
    if os.path.exists(test_video):
        is_valid, error = validator.validate(test_video)
        if is_valid:
            print(f"Video is valid: {test_video}")
            info = validator.get_video_info(test_video)
            print(f"Video info: {info}")

            # Estimate cost
            cost = validator.estimate_processing_cost(test_video, "wan-std")
            if cost:
                print(f"Estimated cost (standard mode): {cost:.2f} RMB")
        else:
            print(f"Video validation failed: {error}")
    else:
        print(f"Test video not found: {test_video}")

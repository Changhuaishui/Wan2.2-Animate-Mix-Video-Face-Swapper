"""
Configuration settings for Wan2.2-Animate-Mix Video Processor
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for the application"""

    # ========== API Configuration ==========
    API_KEY = os.getenv("DASHSCOPE_API_KEY")
    API_BASE_URL = "https://dashscope.aliyuncs.com/api/v1"
    API_REGION = "cn-beijing"

    # Task endpoints
    CREATE_TASK_ENDPOINT = f"{API_BASE_URL}/services/aigc/image2video/video-synthesis"
    QUERY_TASK_ENDPOINT = f"{API_BASE_URL}/tasks"

    # Model name
    MODEL_NAME = "wan2.2-animate-mix"

    # ========== OSS Configuration (Optional) ==========
    OSS_ACCESS_KEY_ID = os.getenv("OSS_ACCESS_KEY_ID")
    OSS_ACCESS_KEY_SECRET = os.getenv("OSS_ACCESS_KEY_SECRET")
    OSS_BUCKET = os.getenv("OSS_BUCKET", "wan22-videos")
    OSS_ENDPOINT = os.getenv("OSS_ENDPOINT", "oss-cn-beijing.aliyuncs.com")

    # ========== Image Validation Constraints ==========
    IMAGE_FORMATS = ['jpg', 'jpeg', 'png', 'bmp', 'webp']
    IMAGE_MIN_SIZE = 200  # pixels
    IMAGE_MAX_SIZE = 4096  # pixels
    IMAGE_MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    IMAGE_MIN_ASPECT_RATIO = 1 / 3  # 1:3
    IMAGE_MAX_ASPECT_RATIO = 3 / 1  # 3:1

    # ========== Video Validation Constraints ==========
    VIDEO_FORMATS = ['mp4', 'avi', 'mov']
    VIDEO_MIN_SIZE = 200  # pixels
    VIDEO_MAX_SIZE = 2048  # pixels
    VIDEO_MIN_DURATION = 2  # seconds
    VIDEO_MAX_DURATION = 30  # seconds
    VIDEO_MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB
    VIDEO_MIN_ASPECT_RATIO = 1 / 3  # 1:3
    VIDEO_MAX_ASPECT_RATIO = 3 / 1  # 3:1

    # ========== Processing Parameters ==========
    DEFAULT_MODE = os.getenv("DEFAULT_MODE", "wan-std")  # wan-std or wan-pro
    POLLING_INTERVAL = int(os.getenv("POLLING_INTERVAL", "15"))  # seconds
    MAX_WAIT_TIME = int(os.getenv("MAX_WAIT_TIME", "600"))  # seconds (10 minutes)

    # ========== Retry Configuration ==========
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_BACKOFF_FACTOR = float(os.getenv("RETRY_BACKOFF_FACTOR", "2.0"))
    RETRY_ON_FAILURE = os.getenv("RETRY_ON_FAILURE", "true").lower() == "true"

    # ========== File Upload Configuration ==========
    USE_OSS = os.getenv("USE_OSS", "false").lower() == "true"
    TEMP_UPLOAD_SERVICE = os.getenv("TEMP_UPLOAD_SERVICE", "dashscope")  # dashscope or custom

    # ========== Directory Configuration ==========
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    OUTPUT_DIR = PROJECT_ROOT / "output"
    TEMP_DIR = PROJECT_ROOT / "temp"
    LOG_DIR = PROJECT_ROOT / "logs"

    # Create directories if they don't exist
    OUTPUT_DIR.mkdir(exist_ok=True)
    TEMP_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)

    # ========== Logging Configuration ==========
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = LOG_DIR / "wan22_processor.log"

    # ========== Face Detection Configuration ==========
    ENABLE_FACE_DETECTION = os.getenv("ENABLE_FACE_DETECTION", "true").lower() == "true"
    REQUIRED_FACE_COUNT = 1  # Must have exactly 1 face
    FACE_DETECTION_CONFIDENCE = float(os.getenv("FACE_DETECTION_CONFIDENCE", "0.5"))

    # ========== Rate Limiting ==========
    MAX_RPS = 5  # Maximum requests per second (API limit)
    MAX_CONCURRENT_TASKS = 1  # Maximum concurrent tasks (API limit)

    # ========== Cost Optimization ==========
    PRICING = {
        "wan-std": 0.6,  # RMB per second (Beijing region)
        "wan-pro": 0.9   # RMB per second (Beijing region)
    }
    FREE_QUOTA_SECONDS = 50  # Initial free quota

    @classmethod
    def validate_config(cls):
        """Validate that required configuration is set"""
        errors = []

        if not cls.API_KEY:
            errors.append("DASHSCOPE_API_KEY is not set in environment variables")

        if cls.USE_OSS:
            if not cls.OSS_ACCESS_KEY_ID:
                errors.append("OSS_ACCESS_KEY_ID is required when USE_OSS is true")
            if not cls.OSS_ACCESS_KEY_SECRET:
                errors.append("OSS_ACCESS_KEY_SECRET is required when USE_OSS is true")

        if cls.DEFAULT_MODE not in ["wan-std", "wan-pro"]:
            errors.append(f"Invalid DEFAULT_MODE: {cls.DEFAULT_MODE}. Must be 'wan-std' or 'wan-pro'")

        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {err}" for err in errors))

        return True

    @classmethod
    def get_mode_price(cls, mode: str) -> float:
        """Get the price per second for a given mode"""
        return cls.PRICING.get(mode, cls.PRICING["wan-std"])

    @classmethod
    def estimate_cost(cls, video_duration: float, mode: str = None) -> float:
        """Estimate the cost for processing a video"""
        if mode is None:
            mode = cls.DEFAULT_MODE
        price_per_second = cls.get_mode_price(mode)
        return video_duration * price_per_second

    @classmethod
    def print_config(cls):
        """Print current configuration (excluding sensitive data)"""
        print("=" * 60)
        print("Wan2.2 Video Processor Configuration")
        print("=" * 60)
        print(f"API Region: {cls.API_REGION}")
        print(f"Model: {cls.MODEL_NAME}")
        print(f"Default Mode: {cls.DEFAULT_MODE}")
        print(f"Max Wait Time: {cls.MAX_WAIT_TIME}s")
        print(f"Polling Interval: {cls.POLLING_INTERVAL}s")
        print(f"Max Retries: {cls.MAX_RETRIES}")
        print(f"Use OSS: {cls.USE_OSS}")
        print(f"Enable Face Detection: {cls.ENABLE_FACE_DETECTION}")
        print(f"Output Directory: {cls.OUTPUT_DIR}")
        print(f"Log Level: {cls.LOG_LEVEL}")
        print("=" * 60)


if __name__ == "__main__":
    # Test configuration
    try:
        Config.validate_config()
        Config.print_config()
        print("\nConfiguration is valid!")
    except ValueError as e:
        print(f"Configuration error: {e}")

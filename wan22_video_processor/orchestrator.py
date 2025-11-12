"""
Main orchestrator for Wan2.2 Video Face Swapper
Coordinates all components for end-to-end processing
"""
import os
import time
from pathlib import Path
from typing import Optional, Dict, List

from .config.settings import Config
from .validators.image_validator import ImageValidator, ValidationError as ImageValidationError
from .validators.video_validator import VideoValidator, ValidationError as VideoValidationError
from .uploaders.oss_uploader import OSSUploader, UploadError
from .processors.wan_processor import Wan22Processor, APIError
from .utils.logger import setup_logger
from .utils.file_handler import FileHandler

logger = setup_logger("orchestrator")


class ProcessingError(Exception):
    """Custom exception for processing errors"""
    pass


class VideoFaceSwapper:
    """
    Main orchestrator for video face swapping

    Coordinates:
    - Input validation
    - File upload
    - API processing
    - Result download
    - Error handling
    """

    def __init__(self, mode: str = None, api_key: Optional[str] = None):
        """
        Initialize the video face swapper

        Args:
            mode: Processing mode ('wan-std' or 'wan-pro')
            api_key: DashScope API Key (uses Config if not provided)
        """
        self.mode = mode or Config.DEFAULT_MODE

        # Initialize components
        logger.info("Initializing VideoFaceSwapper components...")

        try:
            self.image_validator = ImageValidator()
            self.video_validator = VideoValidator()
            self.uploader = OSSUploader()
            self.processor = Wan22Processor(api_key=api_key, mode=self.mode)

            logger.info(f"VideoFaceSwapper initialized (mode: {self.mode})")

        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise ProcessingError(f"Failed to initialize: {e}")

    def process(
        self,
        image_path: str,
        video_path: str,
        output_dir: Optional[str] = None,
        output_filename: Optional[str] = None,
        skip_validation: bool = False,
        progress_callback: Optional[callable] = None
    ) -> Dict:
        """
        Process a video face-swapping task

        Args:
            image_path: Path to person image
            video_path: Path to reference video
            output_dir: Directory to save result (uses Config if not provided)
            output_filename: Custom output filename (auto-generated if not provided)
            skip_validation: Skip input validation (not recommended)
            progress_callback: Optional callback(message) for progress updates

        Returns:
            Dictionary with processing results

        Raises:
            ProcessingError: If processing fails
        """
        start_time = time.time()

        result = {
            "success": False,
            "image_path": image_path,
            "video_path": video_path,
            "output_path": None,
            "task_id": None,
            "processing_time": None,
            "cost": None,
            "error": None
        }

        def log_progress(message: str):
            """Log and callback progress"""
            logger.info(message)
            if progress_callback:
                try:
                    progress_callback(message)
                except Exception as e:
                    logger.warning(f"Progress callback error: {e}")

        try:
            # === Step 1: Validate inputs ===
            if not skip_validation:
                log_progress("Step 1/5: Validating inputs...")

                # Validate image
                log_progress("  - Validating image...")
                is_valid, error = self.image_validator.validate(image_path)
                if not is_valid:
                    raise ProcessingError(f"Image validation failed: {error}")

                log_progress("  - Image validation passed")

                # Validate video
                log_progress("  - Validating video...")
                is_valid, error = self.video_validator.validate(video_path)
                if not is_valid:
                    raise ProcessingError(f"Video validation failed: {error}")

                log_progress("  - Video validation passed")

                # Get video info for cost estimation
                video_info = self.video_validator.get_video_info(video_path)
                if "duration" in video_info:
                    estimated_cost = Config.estimate_cost(video_info["duration"], self.mode)
                    log_progress(f"  - Estimated cost: {estimated_cost:.2f} RMB")
            else:
                log_progress("Step 1/5: Skipping validation (not recommended)")

            # === Step 2: Upload files ===
            log_progress("Step 2/5: Uploading files to cloud storage...")

            try:
                log_progress("  - Uploading image...")
                image_url = self.uploader.upload_file(image_path)
                log_progress(f"  - Image uploaded: {image_url[:50]}...")

                log_progress("  - Uploading video...")
                video_url = self.uploader.upload_file(video_path)
                log_progress(f"  - Video uploaded: {video_url[:50]}...")

            except UploadError as e:
                raise ProcessingError(f"Upload failed: {e}")

            # === Step 3: Create task ===
            log_progress("Step 3/5: Creating processing task...")

            try:
                task_id = self.processor.create_task(image_url, video_url)
                result["task_id"] = task_id
                log_progress(f"  - Task created: {task_id}")

            except APIError as e:
                raise ProcessingError(f"Task creation failed: {e}")

            # === Step 4: Wait for completion ===
            log_progress("Step 4/5: Processing video (this may take a few minutes)...")

            def task_progress_callback(task_info):
                """Callback for task progress"""
                status = task_info.get("task_status", "UNKNOWN")
                log_progress(f"  - Task status: {status}")

            try:
                task_info = self.processor.wait_for_task(
                    task_id,
                    progress_callback=task_progress_callback
                )

                # Extract result URL
                if "results" not in task_info or "video_url" not in task_info["results"]:
                    raise ProcessingError("Result video URL not found")

                result_url = task_info["results"]["video_url"]
                log_progress(f"  - Processing complete!")

                # Get usage info
                if "usage" in task_info:
                    usage = task_info["usage"]
                    video_duration = usage.get("video_duration", 0)
                    result["video_duration"] = video_duration
                    result["cost"] = Config.estimate_cost(video_duration, self.mode)
                    log_progress(f"  - Actual cost: {result['cost']:.2f} RMB")

            except APIError as e:
                raise ProcessingError(f"Task processing failed: {e}")

            # === Step 5: Download result ===
            log_progress("Step 5/5: Downloading result...")

            # Determine output path
            if output_dir is None:
                output_dir = Config.OUTPUT_DIR

            FileHandler.ensure_directory(output_dir)

            if output_filename is None:
                # Generate filename
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                output_filename = f"result_{timestamp}.mp4"

            output_path = os.path.join(output_dir, output_filename)

            try:
                success, message = self.processor.download_result(result_url, output_path)
                if not success:
                    raise ProcessingError(f"Download failed: {message}")

                result["output_path"] = output_path
                log_progress(f"  - Result saved to: {output_path}")

            except Exception as e:
                raise ProcessingError(f"Download failed: {e}")

            # === Complete ===
            elapsed = time.time() - start_time
            result["processing_time"] = elapsed
            result["success"] = True

            log_progress(f"\nProcessing complete in {elapsed:.1f}s!")
            log_progress(f"Output: {output_path}")

            return result

        except ProcessingError:
            raise
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            result["error"] = error_msg
            raise ProcessingError(error_msg)

    def process_batch(
        self,
        tasks: List[Dict],
        output_dir: Optional[str] = None,
        continue_on_error: bool = True,
        progress_callback: Optional[callable] = None
    ) -> Dict:
        """
        Process multiple tasks in batch

        Args:
            tasks: List of task dictionaries with 'image_path' and 'video_path'
            output_dir: Directory to save results
            continue_on_error: Continue processing if a task fails
            progress_callback: Optional progress callback

        Returns:
            Dictionary with batch results
        """
        results = {
            "total": len(tasks),
            "successful": 0,
            "failed": 0,
            "tasks": []
        }

        logger.info(f"Starting batch processing: {len(tasks)} tasks")

        for i, task in enumerate(tasks, 1):
            logger.info(f"\n{'=' * 60}")
            logger.info(f"Processing task {i}/{len(tasks)}")
            logger.info(f"{'=' * 60}")

            image_path = task.get("image_path")
            video_path = task.get("video_path")

            if not image_path or not video_path:
                logger.error(f"Task {i}: Missing image_path or video_path")
                results["failed"] += 1
                results["tasks"].append({
                    "task_number": i,
                    "success": False,
                    "error": "Missing image_path or video_path"
                })
                continue

            try:
                result = self.process(
                    image_path=image_path,
                    video_path=video_path,
                    output_dir=output_dir,
                    progress_callback=progress_callback
                )

                results["successful"] += 1
                results["tasks"].append({
                    "task_number": i,
                    **result
                })

            except Exception as e:
                logger.error(f"Task {i} failed: {e}")
                results["failed"] += 1
                results["tasks"].append({
                    "task_number": i,
                    "image_path": image_path,
                    "video_path": video_path,
                    "success": False,
                    "error": str(e)
                })

                if not continue_on_error:
                    logger.error("Stopping batch processing due to error")
                    break

        # Summary
        logger.info(f"\n{'=' * 60}")
        logger.info("Batch Processing Summary")
        logger.info(f"{'=' * 60}")
        logger.info(f"Total tasks: {results['total']}")
        logger.info(f"Successful: {results['successful']}")
        logger.info(f"Failed: {results['failed']}")

        return results

    def get_info(self) -> Dict:
        """
        Get information about the face swapper configuration

        Returns:
            Dictionary with configuration info
        """
        return {
            "mode": self.mode,
            "api_region": Config.API_REGION,
            "model": Config.MODEL_NAME,
            "price_per_second": Config.get_mode_price(self.mode),
            "max_wait_time": Config.MAX_WAIT_TIME,
            "polling_interval": Config.POLLING_INTERVAL,
            "use_oss": Config.USE_OSS,
            "face_detection_enabled": Config.ENABLE_FACE_DETECTION,
            "output_directory": str(Config.OUTPUT_DIR)
        }


if __name__ == "__main__":
    # Test orchestrator
    try:
        swapper = VideoFaceSwapper(mode="wan-std")
        info = swapper.get_info()
        print("VideoFaceSwapper Configuration:")
        for key, value in info.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"Error: {e}")

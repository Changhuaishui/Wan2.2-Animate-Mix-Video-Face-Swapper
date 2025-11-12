"""
Wan2.2-Animate-Mix API processor
Handles API communication with DashScope
"""
import time
import requests
from typing import Optional, Dict, Tuple
from pathlib import Path

from ..config.settings import Config
from ..utils.logger import setup_logger
from ..utils.file_handler import FileHandler

logger = setup_logger("wan_processor")


class APIError(Exception):
    """Custom exception for API errors"""
    pass


class TaskStatus:
    """Task status constants"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"
    UNKNOWN = "UNKNOWN"


class Wan22Processor:
    """
    Wan2.2-Animate-Mix API client

    Handles:
    - Task creation
    - Status polling
    - Result download
    - Error handling with retry logic
    """

    def __init__(self, api_key: Optional[str] = None, mode: str = None):
        """
        Initialize the processor

        Args:
            api_key: DashScope API Key (uses Config if not provided)
            mode: Processing mode ('wan-std' or 'wan-pro')
        """
        self.api_key = api_key or Config.API_KEY
        if not self.api_key:
            raise ValueError("API Key is required. Set DASHSCOPE_API_KEY environment variable.")

        self.mode = mode or Config.DEFAULT_MODE
        if self.mode not in ["wan-std", "wan-pro"]:
            raise ValueError(f"Invalid mode: {self.mode}. Must be 'wan-std' or 'wan-pro'")

        self.base_url = Config.API_BASE_URL
        self.create_endpoint = Config.CREATE_TASK_ENDPOINT
        self.query_endpoint = Config.QUERY_TASK_ENDPOINT

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-DashScope-Async": "enable",
            "X-DashScope-OssResourceResolve": "enable"  # Required for oss:// URLs
        }

        self.max_retries = Config.MAX_RETRIES
        self.retry_backoff = Config.RETRY_BACKOFF_FACTOR
        self.polling_interval = Config.POLLING_INTERVAL
        self.max_wait_time = Config.MAX_WAIT_TIME

        logger.info(f"Wan22Processor initialized (mode: {self.mode})")

    def create_task(
        self,
        image_url: str,
        video_url: str,
        check_image: bool = True
    ) -> str:
        """
        Create a video face-swapping task

        Args:
            image_url: Public URL of the person image
            video_url: Public URL of the reference video
            check_image: Whether to perform image detection

        Returns:
            Task ID

        Raises:
            APIError: If task creation fails
        """
        payload = {
            "model": Config.MODEL_NAME,
            "input": {
                "image_url": image_url,
                "video_url": video_url
            },
            "parameters": {
                "mode": self.mode,
                "check_image": check_image
            }
        }

        logger.info(f"Creating task with mode: {self.mode}")
        logger.debug(f"Request payload: {payload}")

        try:
            response = requests.post(
                self.create_endpoint,
                headers=self.headers,
                json=payload,
                timeout=60
            )

            response.raise_for_status()
            result = response.json()

            logger.debug(f"API response: {result}")

            # Check for errors
            if "code" in result:
                error_code = result.get("code")
                error_msg = result.get("message", "Unknown error")
                raise APIError(f"API Error [{error_code}]: {error_msg}")

            # Extract task ID
            if "output" in result and "task_id" in result["output"]:
                task_id = result["output"]["task_id"]
                task_status = result["output"].get("task_status", "UNKNOWN")
                logger.info(f"Task created successfully: {task_id} (status: {task_status})")
                return task_id
            else:
                raise APIError(f"Unexpected response format: {result}")

        except requests.exceptions.RequestException as e:
            error_msg = f"Task creation failed: {str(e)}"
            logger.error(error_msg)
            raise APIError(error_msg)
        except APIError:
            raise
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            raise APIError(error_msg)

    def query_task(self, task_id: str) -> Dict:
        """
        Query task status

        Args:
            task_id: Task ID to query

        Returns:
            Task information dictionary

        Raises:
            APIError: If query fails
        """
        query_url = f"{self.query_endpoint}/{task_id}"

        try:
            response = requests.get(
                query_url,
                headers=self.headers,
                timeout=30
            )

            response.raise_for_status()
            result = response.json()

            logger.debug(f"Query response for {task_id}: {result}")

            # Check for errors
            if "code" in result and "output" not in result:
                error_code = result.get("code")
                error_msg = result.get("message", "Unknown error")
                raise APIError(f"Query Error [{error_code}]: {error_msg}")

            if "output" not in result:
                raise APIError(f"Unexpected response format: {result}")

            return result["output"]

        except requests.exceptions.RequestException as e:
            error_msg = f"Task query failed: {str(e)}"
            logger.error(error_msg)
            raise APIError(error_msg)
        except APIError:
            raise
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            raise APIError(error_msg)

    def wait_for_task(
        self,
        task_id: str,
        timeout: Optional[int] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict:
        """
        Wait for task to complete with polling

        Args:
            task_id: Task ID to wait for
            timeout: Maximum wait time in seconds (uses Config if not provided)
            progress_callback: Optional callback function(task_info) called on each poll

        Returns:
            Final task information dictionary

        Raises:
            APIError: If task fails or times out
        """
        if timeout is None:
            timeout = self.max_wait_time

        start_time = time.time()
        poll_count = 0

        logger.info(f"Waiting for task {task_id} (timeout: {timeout}s)")

        while True:
            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise APIError(f"Task timeout after {elapsed:.1f}s")

            # Query task status
            poll_count += 1
            task_info = self.query_task(task_id)
            status = task_info.get("task_status", TaskStatus.UNKNOWN)

            logger.debug(f"Poll #{poll_count}: status={status}, elapsed={elapsed:.1f}s")

            # Call progress callback if provided
            if progress_callback:
                try:
                    progress_callback(task_info)
                except Exception as e:
                    logger.warning(f"Progress callback error: {e}")

            # Check status
            if status == TaskStatus.SUCCEEDED:
                logger.info(f"Task succeeded after {elapsed:.1f}s ({poll_count} polls)")
                return task_info

            elif status == TaskStatus.FAILED:
                error_code = task_info.get("code", "UNKNOWN")
                error_msg = task_info.get("message", "Task failed")
                raise APIError(f"Task failed [{error_code}]: {error_msg}")

            elif status == TaskStatus.CANCELED:
                raise APIError("Task was canceled")

            elif status == TaskStatus.UNKNOWN:
                raise APIError("Task not found or status unknown")

            elif status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                # Continue polling
                logger.info(f"Task {status.lower()}, waiting {self.polling_interval}s...")
                time.sleep(self.polling_interval)

            else:
                logger.warning(f"Unknown status: {status}")
                time.sleep(self.polling_interval)

    def download_result(
        self,
        video_url: str,
        save_path: str,
        show_progress: bool = True
    ) -> Tuple[bool, str]:
        """
        Download result video

        Args:
            video_url: URL of the result video
            save_path: Path to save the video
            show_progress: Whether to show download progress

        Returns:
            Tuple of (success, message)
        """
        logger.info(f"Downloading result video to: {save_path}")

        return FileHandler.download_file(
            video_url,
            save_path,
            show_progress=show_progress
        )

    def process(
        self,
        image_url: str,
        video_url: str,
        output_path: str,
        check_image: bool = True,
        progress_callback: Optional[callable] = None
    ) -> Dict:
        """
        Complete processing workflow

        Args:
            image_url: Public URL of the person image
            video_url: Public URL of the reference video
            output_path: Path to save the result video
            check_image: Whether to perform image detection
            progress_callback: Optional progress callback

        Returns:
            Dictionary with processing results

        Raises:
            APIError: If processing fails
        """
        start_time = time.time()
        result = {
            "success": False,
            "task_id": None,
            "output_path": None,
            "duration": None,
            "cost": None,
            "error": None
        }

        try:
            # Step 1: Create task
            logger.info("Step 1/3: Creating task...")
            task_id = self.create_task(image_url, video_url, check_image)
            result["task_id"] = task_id

            # Step 2: Wait for completion
            logger.info("Step 2/3: Waiting for processing...")
            task_info = self.wait_for_task(task_id, progress_callback=progress_callback)

            # Extract video URL
            if "results" not in task_info or "video_url" not in task_info["results"]:
                raise APIError("Result video URL not found in response")

            result_video_url = task_info["results"]["video_url"]
            logger.info(f"Processing complete, result URL: {result_video_url}")

            # Step 3: Download result
            logger.info("Step 3/3: Downloading result...")
            success, message = self.download_result(result_video_url, output_path)

            if not success:
                raise APIError(f"Download failed: {message}")

            # Calculate metrics
            elapsed = time.time() - start_time
            result["duration"] = elapsed
            result["output_path"] = output_path
            result["success"] = True

            # Get usage info for cost calculation
            if "usage" in task_info:
                usage = task_info["usage"]
                video_duration = usage.get("video_duration", 0)
                result["video_duration"] = video_duration
                result["cost"] = Config.estimate_cost(video_duration, self.mode)

            logger.info(f"Processing complete in {elapsed:.1f}s")

            return result

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Processing failed: {e}")
            raise

    def retry_with_backoff(
        self,
        func: callable,
        *args,
        **kwargs
    ):
        """
        Execute function with retry and exponential backoff

        Args:
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Function result

        Raises:
            Last exception if all retries fail
        """
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_backoff ** attempt
                    logger.warning(
                        f"Attempt {attempt + 1}/{self.max_retries} failed: {e}. "
                        f"Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"All {self.max_retries} attempts failed")

        raise last_exception


if __name__ == "__main__":
    # Test processor
    processor = Wan22Processor(mode="wan-std")

    # Test with sample URLs (replace with actual URLs)
    test_image_url = "https://example.com/person.jpg"
    test_video_url = "https://example.com/reference.mp4"
    test_output = "output_test.mp4"

    print("Wan22Processor test - please provide valid URLs to test")

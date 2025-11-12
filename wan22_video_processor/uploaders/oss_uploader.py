"""
Cloud storage uploader for Wan2.2 Video Processor
Supports Alibaba Cloud OSS and DashScope temporary file upload
"""
import os
import time
import requests
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime, timedelta

try:
    import oss2
    OSS_AVAILABLE = True
except ImportError:
    OSS_AVAILABLE = False

from ..config.settings import Config
from ..utils.logger import setup_logger
from ..utils.file_handler import FileHandler

logger = setup_logger("oss_uploader")


class UploadError(Exception):
    """Custom exception for upload errors"""
    pass


class OSSUploader:
    """
    Cloud storage uploader

    Supports two modes:
    1. Alibaba Cloud OSS (requires oss2 library and credentials)
    2. DashScope temporary file upload (uses API Key)
    """

    def __init__(self):
        """Initialize the uploader"""
        self.use_oss = Config.USE_OSS
        self.oss_bucket = None

        if self.use_oss:
            self._init_oss()
        else:
            logger.info("Using DashScope temporary file upload")

    def _init_oss(self):
        """Initialize OSS client"""
        if not OSS_AVAILABLE:
            logger.error("oss2 library not available. Install with: pip install oss2")
            raise ImportError("oss2 library is required for OSS upload. Install with: pip install oss2")

        if not Config.OSS_ACCESS_KEY_ID or not Config.OSS_ACCESS_KEY_SECRET:
            logger.error("OSS credentials not configured")
            raise ValueError("OSS credentials (OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET) must be set")

        try:
            auth = oss2.Auth(Config.OSS_ACCESS_KEY_ID, Config.OSS_ACCESS_KEY_SECRET)
            self.oss_bucket = oss2.Bucket(auth, Config.OSS_ENDPOINT, Config.OSS_BUCKET)
            logger.info(f"OSS client initialized: {Config.OSS_BUCKET}")
        except Exception as e:
            logger.error(f"Failed to initialize OSS: {e}")
            raise

    def upload_file(self, local_path: str, remote_name: Optional[str] = None) -> str:
        """
        Upload a file and return public URL

        Args:
            local_path: Path to local file
            remote_name: Optional remote filename (auto-generated if not provided)

        Returns:
            Public URL of the uploaded file

        Raises:
            UploadError: If upload fails
        """
        if not os.path.exists(local_path):
            raise UploadError(f"File not found: {local_path}")

        if self.use_oss:
            return self._upload_to_oss(local_path, remote_name)
        else:
            return self._upload_to_dashscope(local_path)

    def _upload_to_oss(self, local_path: str, remote_name: Optional[str] = None) -> str:
        """
        Upload file to Alibaba Cloud OSS

        Args:
            local_path: Path to local file
            remote_name: Optional remote filename

        Returns:
            Public URL of uploaded file
        """
        try:
            # Generate remote path if not provided
            if remote_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = Path(local_path).name
                remote_name = f"wan22/{timestamp}_{filename}"

            # Upload file
            logger.info(f"Uploading to OSS: {local_path} -> {remote_name}")
            self.oss_bucket.put_object_from_file(remote_name, local_path)

            # Generate public URL
            # Note: Bucket must have public read access, or use signed URL
            url = f"https://{Config.OSS_BUCKET}.{Config.OSS_ENDPOINT}/{remote_name}"

            logger.info(f"Upload successful: {url}")
            return url

        except Exception as e:
            error_msg = f"OSS upload failed: {str(e)}"
            logger.error(error_msg)
            raise UploadError(error_msg)

    def _upload_to_dashscope(self, local_path: str) -> str:
        """
        Upload file to DashScope temporary storage (3-step process)

        Args:
            local_path: Path to local file

        Returns:
            OSS URL (valid for 48 hours)
        """
        try:
            logger.info(f"Uploading to DashScope temporary storage: {local_path}")

            # Step 1: Get upload policy
            logger.debug("Step 1: Getting upload policy...")
            policy_url = "https://dashscope.aliyuncs.com/api/v1/uploads"

            headers = {
                "Authorization": f"Bearer {Config.API_KEY}",
                "Content-Type": "application/json"
            }

            params = {
                "action": "getPolicy",
                "model": Config.MODEL_NAME
            }

            response = requests.get(
                policy_url,
                headers=headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            policy_data = response.json()

            # Handle different response formats
            if 'data' in policy_data:
                data = policy_data['data']
            elif 'output' in policy_data and 'data' in policy_data['output']:
                data = policy_data['output']['data']
            else:
                raise UploadError(f"Invalid policy response: {policy_data}")

            upload_host = data['upload_host']
            upload_dir = data['upload_dir']
            oss_access_key_id = data['oss_access_key_id']
            policy = data['policy']
            signature = data['signature']

            logger.debug(f"Policy obtained, upload_host: {upload_host}")

            # Step 2: Upload file to OSS
            logger.debug("Step 2: Uploading file to OSS...")

            filename = Path(local_path).name
            file_key = f"{upload_dir}/{filename}"

            with open(local_path, 'rb') as f:
                files = {'file': (filename, f)}

                form_data = {
                    'OSSAccessKeyId': oss_access_key_id,
                    'policy': policy,
                    'Signature': signature,
                    'key': file_key,
                    'x-oss-object-acl': 'private',
                    'x-oss-forbid-overwrite': 'true',
                    'success_action_status': '200'
                }

                upload_response = requests.post(
                    upload_host,
                    data=form_data,
                    files=files,
                    timeout=300
                )

            if upload_response.status_code != 200:
                raise UploadError(f"OSS upload failed: {upload_response.status_code} - {upload_response.text}")

            # Step 3: Generate OSS URL
            oss_url = f"oss://{file_key}"
            logger.info(f"Upload successful: {oss_url}")

            return oss_url

        except requests.exceptions.RequestException as e:
            error_msg = f"DashScope upload failed: {str(e)}"
            logger.error(error_msg)
            raise UploadError(error_msg)
        except Exception as e:
            error_msg = f"Upload error: {str(e)}"
            logger.error(error_msg)
            raise UploadError(error_msg)

    def generate_signed_url(self, remote_path: str, expires_in_hours: int = 24) -> Optional[str]:
        """
        Generate a signed URL for OSS object (if using OSS)

        Args:
            remote_path: Remote object key
            expires_in_hours: URL expiration time in hours

        Returns:
            Signed URL or None if not using OSS
        """
        if not self.use_oss:
            return None

        try:
            expires_in_seconds = expires_in_hours * 3600
            url = self.oss_bucket.sign_url('GET', remote_path, expires_in_seconds)
            return url
        except Exception as e:
            logger.error(f"Failed to generate signed URL: {e}")
            return None

    def delete_file(self, remote_path: str) -> bool:
        """
        Delete a file from OSS (if using OSS)

        Args:
            remote_path: Remote object key

        Returns:
            True if deleted successfully, False otherwise
        """
        if not self.use_oss:
            logger.warning("Delete operation only supported for OSS")
            return False

        try:
            self.oss_bucket.delete_object(remote_path)
            logger.info(f"Deleted from OSS: {remote_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete from OSS: {e}")
            return False

    def cleanup_old_files(self, days: int = 7, prefix: str = "wan22/") -> int:
        """
        Clean up old files from OSS (if using OSS)

        Args:
            days: Delete files older than this many days
            prefix: Only delete files with this prefix

        Returns:
            Number of files deleted
        """
        if not self.use_oss:
            logger.warning("Cleanup operation only supported for OSS")
            return 0

        try:
            deleted_count = 0
            cutoff_time = time.time() - (days * 24 * 3600)

            logger.info(f"Cleaning up files older than {days} days with prefix '{prefix}'")

            for obj in oss2.ObjectIterator(self.oss_bucket, prefix=prefix):
                # Check if file is older than cutoff
                if obj.last_modified < cutoff_time:
                    self.oss_bucket.delete_object(obj.key)
                    deleted_count += 1
                    logger.debug(f"Deleted old file: {obj.key}")

            logger.info(f"Cleanup complete: {deleted_count} files deleted")
            return deleted_count

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return 0

    def batch_upload(self, file_paths: list) -> dict:
        """
        Upload multiple files in batch

        Args:
            file_paths: List of local file paths

        Returns:
            Dictionary mapping local paths to URLs (or error messages)
        """
        results = {}

        for file_path in file_paths:
            try:
                url = self.upload_file(file_path)
                results[file_path] = {"success": True, "url": url}
            except UploadError as e:
                results[file_path] = {"success": False, "error": str(e)}

        return results


if __name__ == "__main__":
    # Test uploader
    uploader = OSSUploader()

    # Test with a sample file
    test_file = "test_file.txt"
    if os.path.exists(test_file):
        try:
            url = uploader.upload_file(test_file)
            print(f"Upload successful: {url}")
        except UploadError as e:
            print(f"Upload failed: {e}")
    else:
        print(f"Test file not found: {test_file}")

"""
File handling utilities for Wan2.2 Video Processor
"""
import os
import hashlib
import mimetypes
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse
import requests
from .logger import setup_logger

logger = setup_logger("file_handler")


class FileHandler:
    """Utility class for file operations"""

    @staticmethod
    def get_file_size(file_path: str) -> int:
        """
        Get file size in bytes

        Args:
            file_path: Path to the file

        Returns:
            File size in bytes
        """
        return os.path.getsize(file_path)

    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """
        Get file extension without the dot

        Args:
            file_path: Path to the file

        Returns:
            File extension (e.g., 'jpg', 'mp4')
        """
        return Path(file_path).suffix.lstrip('.').lower()

    @staticmethod
    def get_mime_type(file_path: str) -> Optional[str]:
        """
        Get MIME type of a file

        Args:
            file_path: Path to the file

        Returns:
            MIME type string or None
        """
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type

    @staticmethod
    def calculate_md5(file_path: str, chunk_size: int = 8192) -> str:
        """
        Calculate MD5 hash of a file

        Args:
            file_path: Path to the file
            chunk_size: Size of chunks to read

        Returns:
            MD5 hash string
        """
        md5_hash = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()

    @staticmethod
    def ensure_directory(directory: str) -> Path:
        """
        Ensure a directory exists, create if it doesn't

        Args:
            directory: Directory path

        Returns:
            Path object
        """
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def generate_unique_filename(
        original_name: str,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None
    ) -> str:
        """
        Generate a unique filename based on original name

        Args:
            original_name: Original filename
            prefix: Optional prefix to add
            suffix: Optional suffix to add before extension

        Returns:
            Unique filename
        """
        import time
        path = Path(original_name)
        name = path.stem
        ext = path.suffix

        parts = []
        if prefix:
            parts.append(prefix)
        parts.append(name)
        if suffix:
            parts.append(suffix)
        parts.append(str(int(time.time() * 1000)))

        return "_".join(parts) + ext

    @staticmethod
    def download_file(
        url: str,
        save_path: str,
        chunk_size: int = 8192,
        timeout: int = 300,
        show_progress: bool = True
    ) -> Tuple[bool, str]:
        """
        Download a file from a URL

        Args:
            url: URL to download from
            save_path: Path to save the file
            chunk_size: Size of chunks to download
            timeout: Request timeout in seconds
            show_progress: Whether to show download progress

        Returns:
            Tuple of (success, message)
        """
        try:
            logger.info(f"Downloading file from {url}")

            # Ensure directory exists
            FileHandler.ensure_directory(Path(save_path).parent)

            # Stream download
            response = requests.get(url, stream=True, timeout=timeout)
            response.raise_for_status()

            # Get total file size if available
            total_size = int(response.headers.get('content-length', 0))

            # Download with progress
            downloaded = 0
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        if show_progress and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            logger.debug(f"Download progress: {progress:.1f}%")

            logger.info(f"File downloaded successfully to {save_path}")
            return True, f"Downloaded successfully: {save_path}"

        except requests.exceptions.RequestException as e:
            error_msg = f"Download failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error during download: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        Check if a string is a valid URL

        Args:
            url: URL string to validate

        Returns:
            True if valid URL, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Format file size in human-readable format

        Args:
            size_bytes: File size in bytes

        Returns:
            Formatted string (e.g., "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"

    @staticmethod
    def cleanup_file(file_path: str, ignore_errors: bool = True) -> bool:
        """
        Delete a file safely

        Args:
            file_path: Path to file to delete
            ignore_errors: Whether to ignore errors

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Deleted file: {file_path}")
                return True
            return False
        except Exception as e:
            if not ignore_errors:
                logger.error(f"Failed to delete file {file_path}: {e}")
                raise
            return False


if __name__ == "__main__":
    # Test file handler
    handler = FileHandler()

    # Test utility methods
    print(f"Format 1024 bytes: {handler.format_file_size(1024)}")
    print(f"Format 1048576 bytes: {handler.format_file_size(1048576)}")
    print(f"Is valid URL: {handler.is_valid_url('https://example.com')}")
    print(f"Generate unique filename: {handler.generate_unique_filename('test.jpg', prefix='wan22')}")

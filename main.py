"""
Wan2.2-Animate-Mix Video Face Swapper - CLI Interface
Main entry point for the application
"""
import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from wan22_video_processor.orchestrator import VideoFaceSwapper, ProcessingError
from wan22_video_processor.config.settings import Config
from wan22_video_processor.utils.logger import setup_logger

logger = setup_logger("main")


def print_banner():
    """Print application banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        Wan2.2-Animate-Mix Video Face Swapper v1.0           ║
    ║                                                              ║
    ║        Powered by Alibaba Cloud Tongyi Wanxiang             ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def progress_callback(message: str):
    """Progress callback for CLI"""
    print(f"  {message}")


def cmd_process(args):
    """Process single video command"""
    try:
        # Initialize swapper
        swapper = VideoFaceSwapper(mode=args.mode, api_key=args.api_key)

        print(f"\nStarting video face-swapping...")
        print(f"Image: {args.image}")
        print(f"Video: {args.video}")
        print(f"Mode: {args.mode}")
        print(f"Output: {args.output or Config.OUTPUT_DIR}\n")

        # Process
        result = swapper.process(
            image_path=args.image,
            video_path=args.video,
            output_dir=args.output,
            output_filename=args.filename,
            skip_validation=args.skip_validation,
            progress_callback=progress_callback if args.verbose else None
        )

        # Print results
        print("\n" + "=" * 60)
        print("✓ Processing Complete!")
        print("=" * 60)
        print(f"Output file: {result['output_path']}")
        print(f"Processing time: {result['processing_time']:.1f}s")

        if result.get('cost'):
            print(f"Cost: {result['cost']:.2f} RMB")

        if result.get('task_id'):
            print(f"Task ID: {result['task_id']}")

        return 0

    except ProcessingError as e:
        logger.error(f"Processing failed: {e}")
        print(f"\n✗ Error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n✗ Unexpected error: {e}")
        return 1


def cmd_validate(args):
    """Validate files command"""
    from wan22_video_processor.validators.image_validator import ImageValidator
    from wan22_video_processor.validators.video_validator import VideoValidator

    print("\nValidating files...\n")

    # Validate image
    if args.image:
        print(f"Validating image: {args.image}")
        validator = ImageValidator()
        is_valid, error = validator.validate(args.image)

        if is_valid:
            print("  ✓ Image is valid")
            if args.verbose:
                info = validator.get_image_info(args.image)
                print(f"    - Size: {info['width']}x{info['height']}")
                print(f"    - Aspect ratio: {info['aspect_ratio']:.2f}")
                print(f"    - File size: {info['file_size_formatted']}")
        else:
            print(f"  ✗ Image validation failed: {error}")
            return 1

    # Validate video
    if args.video:
        print(f"\nValidating video: {args.video}")
        validator = VideoValidator()
        is_valid, error = validator.validate(args.video)

        if is_valid:
            print("  ✓ Video is valid")
            if args.verbose:
                info = validator.get_video_info(args.video)
                print(f"    - Resolution: {info['width']}x{info['height']}")
                print(f"    - Duration: {info['duration']:.2f}s")
                print(f"    - FPS: {info['fps']:.2f}")
                print(f"    - File size: {info['file_size_formatted']}")

                # Estimate cost
                cost_std = validator.estimate_processing_cost(args.video, "wan-std")
                cost_pro = validator.estimate_processing_cost(args.video, "wan-pro")
                if cost_std and cost_pro:
                    print(f"    - Estimated cost (standard): {cost_std:.2f} RMB")
                    print(f"    - Estimated cost (professional): {cost_pro:.2f} RMB")
        else:
            print(f"  ✗ Video validation failed: {error}")
            return 1

    print("\n✓ All validations passed!")
    return 0


def cmd_config(args):
    """Show configuration command"""
    try:
        Config.validate_config()
        print("\nCurrent Configuration:")
        print("=" * 60)

        Config.print_config()

        return 0
    except ValueError as e:
        print(f"\n✗ Configuration error: {e}")
        return 1


def cmd_info(args):
    """Show info command"""
    try:
        swapper = VideoFaceSwapper(mode=args.mode)
        info = swapper.get_info()

        print("\nVideoFaceSwapper Information:")
        print("=" * 60)
        for key, value in info.items():
            print(f"{key.replace('_', ' ').title()}: {value}")

        return 0
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Wan2.2-Animate-Mix Video Face Swapper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single video
  python main.py process -i person.jpg -v video.mp4

  # Use professional mode
  python main.py process -i person.jpg -v video.mp4 --mode wan-pro

  # Validate files before processing
  python main.py validate -i person.jpg -v video.mp4

  # Show configuration
  python main.py config

For more information, visit: https://help.aliyun.com/zh/model-studio/wan-animate-mix-api
        """
    )

    # Global arguments
    parser.add_argument(
        "--api-key",
        type=str,
        help="DashScope API Key (overrides DASHSCOPE_API_KEY env var)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Process command
    process_parser = subparsers.add_parser("process", help="Process video face-swapping")
    process_parser.add_argument(
        "-i", "--image",
        required=True,
        type=str,
        help="Path to person image"
    )
    process_parser.add_argument(
        "-v", "--video",
        required=True,
        type=str,
        help="Path to reference video"
    )
    process_parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output directory (default: ./output)"
    )
    process_parser.add_argument(
        "-f", "--filename",
        type=str,
        help="Output filename (default: auto-generated)"
    )
    process_parser.add_argument(
        "--mode",
        type=str,
        choices=["wan-std", "wan-pro"],
        default="wan-std",
        help="Processing mode (default: wan-std)"
    )
    process_parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip input validation (not recommended)"
    )

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate image and video files")
    validate_parser.add_argument(
        "-i", "--image",
        type=str,
        help="Path to image file"
    )
    validate_parser.add_argument(
        "-v", "--video",
        type=str,
        help="Path to video file"
    )

    # Config command
    config_parser = subparsers.add_parser("config", help="Show configuration")

    # Info command
    info_parser = subparsers.add_parser("info", help="Show application info")
    info_parser.add_argument(
        "--mode",
        type=str,
        choices=["wan-std", "wan-pro"],
        default="wan-std",
        help="Mode to show info for"
    )

    # Parse arguments
    args = parser.parse_args()

    # Print banner
    print_banner()

    # Execute command
    if args.command == "process":
        return cmd_process(args)
    elif args.command == "validate":
        return cmd_validate(args)
    elif args.command == "config":
        return cmd_config(args)
    elif args.command == "info":
        return cmd_info(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())

"""
Example usage of Wan2.2-Animate-Mix Video Face Swapper
This script demonstrates how to use the library programmatically
"""
from wan22_video_processor.orchestrator import VideoFaceSwapper, ProcessingError
from wan22_video_processor.config.settings import Config


def example_single_processing():
    """Example: Process a single video"""
    print("=" * 60)
    print("Example 1: Single Video Processing")
    print("=" * 60)

    try:
        # Initialize the swapper with standard mode
        swapper = VideoFaceSwapper(mode="wan-std")

        # Define input files
        image_path = "test_data/person.jpg"
        video_path = "test_data/reference.mp4"

        # Progress callback
        def progress(message):
            print(f"  >> {message}")

        # Process the video
        result = swapper.process(
            image_path=image_path,
            video_path=video_path,
            output_dir="./output",
            progress_callback=progress
        )

        # Display results
        if result["success"]:
            print("\n✓ Processing successful!")
            print(f"  Output: {result['output_path']}")
            print(f"  Time: {result['processing_time']:.1f}s")
            print(f"  Cost: {result.get('cost', 0):.2f} RMB")
        else:
            print(f"\n✗ Processing failed: {result.get('error')}")

    except ProcessingError as e:
        print(f"\n✗ Error: {e}")


def example_batch_processing():
    """Example: Process multiple videos in batch"""
    print("\n" + "=" * 60)
    print("Example 2: Batch Processing")
    print("=" * 60)

    try:
        swapper = VideoFaceSwapper(mode="wan-std")

        # Define multiple tasks
        tasks = [
            {
                "image_path": "test_data/person1.jpg",
                "video_path": "test_data/video1.mp4"
            },
            {
                "image_path": "test_data/person2.jpg",
                "video_path": "test_data/video2.mp4"
            }
        ]

        # Process all tasks
        results = swapper.process_batch(
            tasks=tasks,
            output_dir="./batch_output",
            continue_on_error=True
        )

        # Display summary
        print("\n" + "=" * 60)
        print("Batch Processing Summary")
        print("=" * 60)
        print(f"Total: {results['total']}")
        print(f"Successful: {results['successful']}")
        print(f"Failed: {results['failed']}")

    except Exception as e:
        print(f"\n✗ Error: {e}")


def example_validation():
    """Example: Validate files before processing"""
    print("\n" + "=" * 60)
    print("Example 3: File Validation")
    print("=" * 60)

    from wan22_video_processor.validators.image_validator import ImageValidator
    from wan22_video_processor.validators.video_validator import VideoValidator

    # Validate image
    image_path = "test_data/person.jpg"
    image_validator = ImageValidator()
    is_valid, error = image_validator.validate(image_path)

    print(f"Image validation: {'✓ PASS' if is_valid else '✗ FAIL'}")
    if not is_valid:
        print(f"  Error: {error}")

    # Validate video
    video_path = "test_data/reference.mp4"
    video_validator = VideoValidator()
    is_valid, error = video_validator.validate(video_path)

    print(f"Video validation: {'✓ PASS' if is_valid else '✗ FAIL'}")
    if not is_valid:
        print(f"  Error: {error}")

    # Get detailed info
    if is_valid:
        info = video_validator.get_video_info(video_path)
        print(f"\nVideo info:")
        print(f"  Resolution: {info['width']}x{info['height']}")
        print(f"  Duration: {info['duration']:.2f}s")
        print(f"  FPS: {info['fps']:.2f}")

        # Estimate costs
        cost_std = video_validator.estimate_processing_cost(video_path, "wan-std")
        cost_pro = video_validator.estimate_processing_cost(video_path, "wan-pro")
        print(f"\nEstimated costs:")
        print(f"  Standard mode: {cost_std:.2f} RMB")
        print(f"  Professional mode: {cost_pro:.2f} RMB")


def example_custom_configuration():
    """Example: Using custom configuration"""
    print("\n" + "=" * 60)
    print("Example 4: Custom Configuration")
    print("=" * 60)

    # Initialize with custom API key and professional mode
    swapper = VideoFaceSwapper(
        mode="wan-pro",
        api_key="sk-your-custom-api-key"  # Optional: override env var
    )

    # Get configuration info
    info = swapper.get_info()
    print("Current configuration:")
    for key, value in info.items():
        print(f"  {key}: {value}")


def main():
    """Main function"""
    print("\n" + "=" * 70)
    print(" " * 15 + "Wan2.2-Animate-Mix Examples")
    print("=" * 70)

    # Check configuration
    try:
        Config.validate_config()
        print("\n✓ Configuration valid")
    except ValueError as e:
        print(f"\n✗ Configuration error: {e}")
        print("\nPlease set DASHSCOPE_API_KEY in your .env file")
        return

    # Run examples
    # Uncomment the examples you want to run:

    # example_single_processing()
    # example_batch_processing()
    # example_validation()
    # example_custom_configuration()

    print("\n" + "=" * 70)
    print("Examples complete!")
    print("=" * 70)
    print("\nNote: Uncomment the example functions in example.py to run them")
    print("Make sure you have valid test files in the test_data/ directory")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
Simple test script to validate and process test files
Bypasses CLI encoding issues
"""
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

from wan22_video_processor.validators.image_validator import ImageValidator
from wan22_video_processor.validators.video_validator import VideoValidator
from wan22_video_processor.orchestrator import VideoFaceSwapper

def test_validation():
    """Test file validation"""
    print("=" * 70)
    print("Testing File Validation")
    print("=" * 70)

    # File paths
    image_path = r"C:\code\ali\video\测试文件\图片\2024-08-25_Motorsport,_Formel_1,_Großer_Preis_der_Niederlande_2024_STP_3978_by_Stepro_(cropped2).jpg"
    video_path = r"C:\code\ali\video\测试文件\视频\Video Project 1.mp4"

    print(f"\nChecking image file...")
    print(f"Checking video file...")

    # Validate image
    print("\n--- Image Validation ---")
    image_validator = ImageValidator()
    is_valid, error = image_validator.validate(image_path)

    if is_valid:
        print("[OK] Image is valid")
        info = image_validator.get_image_info(image_path)
        if 'width' in info:
            print(f"  Size: {info['width']}x{info['height']}")
            print(f"  Aspect ratio: {info['aspect_ratio']:.2f}")
        print(f"  File size: {info['file_size_formatted']}")
    else:
        print(f"[FAIL] Image validation failed: {error}")
        return False

    # Validate video
    print("\n--- Video Validation ---")
    video_validator = VideoValidator()
    is_valid, error = video_validator.validate(video_path)

    if is_valid:
        print("[OK] Video is valid")
        info = video_validator.get_video_info(video_path)
        if 'width' in info:
            print(f"  Resolution: {info.get('width', 'N/A')}x{info.get('height', 'N/A')}")
            if 'duration' in info:
                print(f"  Duration: {info['duration']:.2f}s")
            if 'fps' in info:
                print(f"  FPS: {info['fps']:.2f}")
        print(f"  File size: {info['file_size_formatted']}")

        # Estimate cost
        if 'duration' in info:
            cost_std = video_validator.estimate_processing_cost(video_path, "wan-std")
            cost_pro = video_validator.estimate_processing_cost(video_path, "wan-pro")
            if cost_std and cost_pro:
                print(f"\n  Estimated cost (standard): {cost_std:.2f} RMB")
                print(f"  Estimated cost (professional): {cost_pro:.2f} RMB")
    else:
        print(f"[FAIL] Video validation failed: {error}")
        return False

    print("\n" + "=" * 70)
    print("[SUCCESS] All validations passed!")
    print("=" * 70)

    return True


def process_files():
    """Process the test files"""
    print("\n" + "=" * 70)
    print("Processing Files (WILL CONSUME QUOTA!)")
    print("=" * 70)

    # File paths
    image_path = r"C:\code\ali\video\测试文件\图片\2024-08-25_Motorsport,_Formel_1,_Großer_Preis_der_Niederlande_2024_STP_3978_by_Stepro_(cropped2).jpg"
    video_path = r"C:\code\ali\video\测试文件\视频\Video Project 1.mp4"

    # Initialize swapper
    swapper = VideoFaceSwapper(mode="wan-std")

    # Progress callback
    def progress(message):
        print(f"  >> {message}")

    # Process
    result = swapper.process(
        image_path=image_path,
        video_path=video_path,
        output_dir="./output",
        progress_callback=progress
    )

    print("\n" + "=" * 70)
    if result["success"]:
        print("[SUCCESS] Processing complete!")
        print(f"  Output: {result['output_path']}")
        print(f"  Time: {result['processing_time']:.1f}s")
        if 'cost' in result and result['cost']:
            print(f"  Cost: {result['cost']:.2f} RMB")
    else:
        print(f"[FAIL] Processing failed: {result.get('error')}")
    print("=" * 70)

    return result["success"]


if __name__ == "__main__":
    # Step 1: Validation (free, no quota consumed)
    print("\nStep 1: Validating files (no quota consumed)...\n")
    validation_ok = test_validation()

    if not validation_ok:
        print("\n[ERROR] Validation failed. Cannot proceed.")
        sys.exit(1)

    # Step 2: Ask user if they want to process
    print("\n" + "=" * 70)
    print("Validation complete. Ready to process.")
    print("=" * 70)
    print("\nWARNING: The next step will consume your quota!")
    print("Type 'yes' to proceed with processing: ")

    # For automation, let's just show the option
    print("\n[INFO] To process files, run:")
    print("  python test_files.py --process")

    if "--process" in sys.argv:
        print("\nProceeding with processing...")
        process_files()
    else:
        print("\n[INFO] Validation completed. No processing performed.")
        print("[INFO] Your quota has NOT been consumed.")

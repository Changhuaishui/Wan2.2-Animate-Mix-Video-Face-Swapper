# Wan2.2-Animate-Mix Video Face Swapper

A Python application for video face-swapping using Alibaba Cloud's Tongyi Wanxiang Wan2.2-Animate-Mix API. Replace faces in videos while preserving the original scene, lighting, and movements.

## Features

- **Intelligent Validation**: Automatic validation of image and video inputs
- **Flexible Upload**: Support for both OSS and temporary file hosting
- **Two Processing Modes**: Standard (wan-std) and Professional (wan-pro)
- **Robust Error Handling**: Automatic retry and comprehensive error messages
- **Cost Estimation**: Calculate processing costs before running
- **Progress Tracking**: Real-time status updates during processing
- **CLI Interface**: Easy-to-use command-line interface

## Requirements

- Python 3.8 or higher
- Alibaba Cloud account with DashScope API access
- API Key from [DashScope Console](https://dashscope.console.aliyun.com/apiKey)

## Installation

### 1. Clone or Download

```bash
git clone <repository-url>
cd video
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy the example configuration
copy .env.example .env

# Edit .env and add your API key
# DASHSCOPE_API_KEY=sk-your-actual-api-key-here
```

**Note**: Configure your API key in `.env` file. Keep it secure and never commit to version control!

### 5. Test API Connection (Recommended)

Before processing videos, test the API connection without consuming quota:

```bash
python test_api_connection.py
```

This test script will:
- ✅ Verify API key validity
- ✅ Test API authentication
- ✅ Check query interface
- ✅ **Not consume any processing quota**

Expected output:
```
✓ 通过  API Key 有效性
✓ 通过  API 认证
✓ 通过  查询接口

🎉 所有测试通过！API 连接正常，可以开始使用
```

## Quick Start

### Basic Usage

```bash
# Process a video with default settings (standard mode)
python main.py process -i person.jpg -v video.mp4

# Use professional mode for better quality
python main.py process -i person.jpg -v video.mp4 --mode wan-pro

# Specify custom output
python main.py process -i person.jpg -v video.mp4 -o ./results -f my_result.mp4
```

### Validate Files Before Processing

```bash
# Validate image and video
python main.py validate -i person.jpg -v video.mp4

# Validate with detailed info
python main.py validate -i person.jpg -v video.mp4 --verbose
```

### Check Configuration

```bash
# Show current configuration
python main.py config

# Show application info
python main.py info
```

## Input Requirements

### Image Requirements

- **Formats**: JPG, JPEG, PNG, BMP, WEBP
- **Resolution**: 200-4096 pixels (both width and height)
- **Aspect Ratio**: Between 1:3 and 3:1
- **File Size**: Maximum 5MB
- **Content**: Must contain exactly one clear, unobstructed face

### Video Requirements

- **Formats**: MP4, AVI, MOV
- **Resolution**: 200-2048 pixels (both width and height)
- **Aspect Ratio**: Between 1:3 and 3:1
- **Duration**: 2-30 seconds
- **File Size**: Maximum 200MB
- **Content**: First frame should show a clear face

## Processing Modes

| Mode | Cost (Beijing) | Speed | Quality | Best For |
|------|---------------|-------|---------|----------|
| wan-std | 0.6 RMB/sec | Faster | Good | Quick previews, basic animations |
| wan-pro | 0.9 RMB/sec | Slower | Excellent | Professional use, high quality output |

## Project Structure

```
video/
├── wan22_video_processor/       # Main package
│   ├── config/                  # Configuration management
│   │   └── settings.py
│   ├── validators/              # Input validation
│   │   ├── image_validator.py
│   │   └── video_validator.py
│   ├── uploaders/               # File upload
│   │   └── oss_uploader.py
│   ├── processors/              # API integration
│   │   └── wan_processor.py
│   ├── utils/                   # Utilities
│   │   ├── logger.py
│   │   └── file_handler.py
│   └── orchestrator.py          # Main orchestrator
├── main.py                      # CLI entry point
├── requirements.txt             # Dependencies
├── .env.example                 # Configuration template
├── output/                      # Output directory
├── logs/                        # Log files
└── README.md                    # This file
```

## Programmatic Usage

You can also use the library in your Python code:

```python
from wan22_video_processor.orchestrator import VideoFaceSwapper

# Initialize
swapper = VideoFaceSwapper(mode="wan-std")

# Process single video
result = swapper.process(
    image_path="person.jpg",
    video_path="video.mp4",
    output_dir="./output"
)

print(f"Success: {result['success']}")
print(f"Output: {result['output_path']}")
print(f"Cost: {result['cost']:.2f} RMB")
```

### Batch Processing

```python
from wan22_video_processor.orchestrator import VideoFaceSwapper

swapper = VideoFaceSwapper(mode="wan-std")

tasks = [
    {"image_path": "person1.jpg", "video_path": "video1.mp4"},
    {"image_path": "person2.jpg", "video_path": "video2.mp4"},
]

results = swapper.process_batch(tasks, output_dir="./batch_output")

print(f"Successful: {results['successful']}/{results['total']}")
```

## Configuration Options

All configuration can be set via environment variables in `.env`:

### Required
- `DASHSCOPE_API_KEY`: Your DashScope API key

### Optional
- `DEFAULT_MODE`: Processing mode (wan-std or wan-pro)
- `USE_OSS`: Use Alibaba Cloud OSS for storage (true/false)
- `POLLING_INTERVAL`: Status check interval in seconds (default: 15)
- `MAX_WAIT_TIME`: Maximum processing timeout (default: 600)
- `ENABLE_FACE_DETECTION`: Validate faces in inputs (default: true)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Common Issues

### API Key Not Found
```
Error: API Key is required
```
**Solution**: Set `DASHSCOPE_API_KEY` in your `.env` file

### Validation Failed
```
Error: Image validation failed: No face detected
```
**Solution**: Ensure your image contains a clear, single face

### Upload Failed
```
Error: Upload failed: Connection timeout
```
**Solution**: Check your network connection or try again

### Task Timeout
```
Error: Task timeout after 600s
```
**Solution**: Increase `MAX_WAIT_TIME` in `.env` or use standard mode for faster processing

## Pricing

Free tier includes 50 seconds of processing. After that:

- **Standard Mode**: 0.6 RMB per second of generated video
- **Professional Mode**: 0.9 RMB per second of generated video

**Note**: Failed tasks are not charged and can be retried.

### 💰 How to Save Quota

**Important Tips**:
1. ✅ **Test API connection first** - Run `python test_api_connection.py` (doesn't consume quota)
2. ✅ **Validate files before processing** - Use `python main.py validate -i image.jpg -v video.mp4`
3. ✅ **Start with short videos** - Test with 2-5 second videos first
4. ✅ **Use standard mode for testing** - wan-std is 40% cheaper than wan-pro
5. ✅ **Failed tasks are free** - Don't worry about retrying failed tasks
6. ✅ **Check cost estimate** - Use `--verbose` flag to see estimated cost before processing

**Example workflow**:
```bash
# Step 1: Test API (free)
python test_api_connection.py

# Step 2: Validate files (free)
python main.py validate -i image.jpg -v video.mp4 --verbose

# Step 3: Process with cost-efficient mode
python main.py process -i image.jpg -v video.mp4 --mode wan-std
```

## API Documentation

For detailed API documentation, visit:
- [Wan2.2-Animate-Mix API Guide](https://help.aliyun.com/zh/model-studio/wan-animate-mix-api)
- [DashScope Console](https://dashscope.console.aliyun.com/)

## Limitations

- Maximum 5 requests per second (RPS limit)
- Only 1 concurrent task at a time
- Task results expire after 24 hours
- Video URLs expire after 24 hours (download immediately)

## Advanced Features

### Custom Progress Callback

```python
def my_progress(message):
    print(f"[PROGRESS] {message}")

result = swapper.process(
    image_path="person.jpg",
    video_path="video.mp4",
    progress_callback=my_progress
)
```

### Using OSS for Permanent Storage

1. Set up Alibaba Cloud OSS bucket
2. Configure OSS credentials in `.env`:
   ```
   USE_OSS=true
   OSS_ACCESS_KEY_ID=your-access-key-id
   OSS_ACCESS_KEY_SECRET=your-access-key-secret
   OSS_BUCKET=your-bucket-name
   ```

### Cost Estimation

```python
from wan22_video_processor.validators.video_validator import VideoValidator

validator = VideoValidator()
cost_std = validator.estimate_processing_cost("video.mp4", "wan-std")
cost_pro = validator.estimate_processing_cost("video.mp4", "wan-pro")

print(f"Standard mode: {cost_std:.2f} RMB")
print(f"Professional mode: {cost_pro:.2f} RMB")
```

## Troubleshooting

Enable verbose logging for debugging:

```bash
# In .env
LOG_LEVEL=DEBUG

# Or via CLI
python main.py process -i person.jpg -v video.mp4 --verbose
```

Check logs in the `logs/` directory for detailed error information.

## Contributing

Contributions are welcome! Please ensure:

1. Code follows the existing structure
2. All validators pass
3. Error handling is comprehensive
4. Documentation is updated

## License

This project is for educational and development purposes. Please comply with Alibaba Cloud's terms of service.

## Support

For issues related to:
- **This application**: Create an issue in the repository
- **API service**: Contact [Alibaba Cloud Support](https://help.aliyun.com/)
- **API errors**: Check [Error Codes Documentation](https://help.aliyun.com/zh/model-studio/error-code)

## Acknowledgments

- Alibaba Cloud Tongyi Wanxiang for the Wan2.2-Animate-Mix API
- OpenCV and Pillow for image/video processing
- Python community for excellent libraries

---

**Note**: Remember to keep your API keys secure and never commit them to version control!

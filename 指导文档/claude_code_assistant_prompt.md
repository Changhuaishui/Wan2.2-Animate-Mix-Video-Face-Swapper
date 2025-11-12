# Claude 4.5 Code Assistant Prompt for Wan2.2-Animate-Mix API Integration

## Project Context and Objective

You are tasked with implementing a Python-based local application that integrates with Alibaba Cloud's Tongyi Wanxiang Wan2.2-Animate-Mix video face-swapping model API. This is a sophisticated video processing system that requires careful attention to detail, multi-agent coordination, and systematic problem-solving.

### Core Requirements:
1. Build a robust Python application for video face-swapping
2. Handle input validation for images and videos with strict format requirements
3. Upload media files to cloud storage (OSS or temporary hosting)
4. Call the Wan2.2-Animate-Mix API for processing
5. Download and save the processed videos locally
6. Implement comprehensive error handling and retry mechanisms

## Multi-Agent Task Delegation Strategy

You should approach this project using a multi-agent mindset, where different aspects of your capabilities focus on specific domains:

### Agent 1: Architecture Designer
- Design the overall system architecture
- Create modular, maintainable code structure
- Plan interfaces between components
- Consider scalability and extensibility

### Agent 2: Validation Specialist
- Implement strict input validation for images and videos
- Ensure compliance with API requirements
- Handle edge cases and provide clear error messages
- Optimize preprocessing workflows

### Agent 3: API Integration Expert
- Handle API authentication and request construction
- Implement async task creation and polling
- Manage rate limiting and concurrency
- Ensure proper error handling for API responses

### Agent 4: Quality Assurance Engineer
- Test each component thoroughly
- Implement logging and monitoring
- Verify error handling paths
- Ensure code reliability and robustness

## Step-by-Step Implementation Guide

### Step 1: Environment Setup and Configuration
**Think through this carefully:**
- What dependencies are needed? (requests, Pillow, opencv-python, moviepy, etc.)
- How should API keys be managed securely?
- What configuration parameters should be externalized?

**Internal reflection before coding:**
```
Am I considering all security aspects?
Have I planned for different deployment environments?
Is the configuration flexible enough for different use cases?
```

**Implementation checklist:**
- [ ] Create virtual environment
- [ ] Install required packages
- [ ] Set up environment variables
- [ ] Create configuration module
- [ ] Implement logging setup

### Step 2: Input Validation Module
**Critical requirements from documentation:**
- Images: JPG/JPEG/PNG/BMP/WEBP, size [200-4096]px, aspect ratio 1:3 to 3:1, max 5MB
- Videos: MP4/AVI/MOV, size [200-2048]px, duration 2-30 seconds, max 200MB
- Both must contain single person with clear, unobstructed face

**Think through validation logic:**
```
How can I efficiently check file formats?
What's the best way to detect faces in images?
How do I validate video duration and resolution?
Should I auto-fix correctable issues or just report them?
```

**Code structure consideration:**
```python
class MediaValidator:
    def __init__(self):
        # Initialize validation parameters from config
        
    def validate_image(self, path):
        # Check format, size, aspect ratio, face detection
        # Return (is_valid, error_message, suggestions)
        
    def validate_video(self, path):
        # Check format, duration, resolution, first frame
        # Return (is_valid, error_message, suggestions)
        
    def preprocess_if_needed(self, path):
        # Optionally fix correctable issues
        # Return processed_path or original_path
```

### Step 3: Cloud Storage Integration
**Consider these aspects:**
- Should you use Alibaba Cloud OSS or temporary file hosting?
- How to handle URL generation and expiration?
- What's the cleanup strategy for uploaded files?

**Internal dialogue:**
```
Is OSS integration necessary or can I use simpler alternatives?
How do I ensure URLs are publicly accessible?
What happens if upload fails midway?
```

**Implementation approach:**
```python
class CloudStorageManager:
    def upload_to_oss(self, local_path):
        # Handle OSS upload with retry logic
        
    def upload_to_temp_host(self, local_path):
        # Alternative: use temporary file hosting services
        
    def generate_public_url(self, file_key):
        # Ensure URL is accessible from API
        
    def cleanup_expired_files(self):
        # Remove old files to save storage costs
```

### Step 4: API Integration Core
**Based on documentation, the API flow is:**
1. Create task (POST request with image_url and video_url)
2. Poll task status (GET request with task_id)
3. Download result when SUCCEEDED

**Critical thinking points:**
```
How often should I poll? (Documentation suggests 15 seconds)
What's the timeout strategy? (Task valid for 24 hours)
How to handle different failure scenarios?
Should I implement exponential backoff?
```

**Robust implementation pattern:**
```python
class Wan22APIClient:
    def __init__(self, api_key, mode="wan-std"):
        self.api_key = api_key
        self.mode = mode  # wan-std (0.6元/秒) or wan-pro (0.9元/秒)
        
    async def create_task(self, image_url, video_url):
        # Implement with proper error handling
        # Log request/response for debugging
        # Return task_id or raise specific exception
        
    async def poll_task_status(self, task_id, max_wait=600):
        # Implement intelligent polling
        # Handle PENDING, RUNNING, SUCCEEDED, FAILED states
        # Include progress callbacks if needed
        
    def download_result(self, video_url, output_path):
        # Stream download with progress bar
        # Verify file integrity
        # Handle network interruptions
```

### Step 5: Error Handling and Recovery
**Think about failure scenarios:**
- Network timeouts
- Invalid input files
- API rate limiting (5 RPS limit)
- Task failures (don't cost money, can retry)
- Storage issues

**Implement comprehensive error handling:**
```python
class ErrorHandler:
    def __init__(self):
        self.retry_config = {
            'max_retries': 3,
            'backoff_factor': 2,
            'retry_on_failure': True  # API doesn't charge for failures
        }
        
    def handle_validation_error(self, error):
        # Provide actionable feedback to user
        
    def handle_api_error(self, error):
        # Parse API error codes and messages
        # Suggest fixes based on error type
        
    def implement_retry_logic(self, func, *args, **kwargs):
        # Smart retry with exponential backoff
```

### Step 6: Main Orchestration
**Bring everything together:**
```python
class VideoFaceSwapperOrchestrator:
    def __init__(self, config):
        self.validator = MediaValidator()
        self.storage = CloudStorageManager()
        self.api_client = Wan22APIClient(config.api_key, config.mode)
        self.error_handler = ErrorHandler()
        
    def process_single_task(self, image_path, video_path):
        """
        Complete workflow with proper error handling
        1. Validate inputs
        2. Upload to cloud
        3. Create API task
        4. Poll for results
        5. Download output
        6. Cleanup
        """
        
    def process_batch(self, task_list):
        """
        Handle multiple tasks efficiently
        Note: API allows only 1 concurrent task
        """
```

## Quality Assurance Checklist

### Before Each Implementation Step:
1. **Review the documentation**: Check the technical research document for specific requirements
2. **Think about edge cases**: What could go wrong? How to handle it gracefully?
3. **Consider performance**: Is this the most efficient approach?
4. **Plan for monitoring**: How will you know if something fails in production?

### After Each Component:
1. **Unit testing**: Test each function independently
2. **Integration testing**: Verify components work together
3. **Error path testing**: Deliberately trigger failures
4. **Performance testing**: Measure processing times and resource usage

## Common Pitfalls to Avoid

1. **URL Expiration**: Video URLs expire after 24 hours - always download immediately
2. **Region Mismatch**: Must use Beijing region API key (cn-beijing)
3. **Rate Limiting**: Maximum 5 requests per second, 1 concurrent task
4. **File Size Limits**: Strict limits on image (5MB) and video (200MB) sizes
5. **Face Detection**: Both image and video first frame must contain single clear face
6. **Aspect Ratio**: Image aspect ratio must be between 1:3 and 3:1
7. **Missing Headers**: Must include `X-DashScope-Async: enable` header

## Debugging Strategy

When encountering issues, follow this systematic approach:

1. **Check logs first**: Implement comprehensive logging at each step
2. **Verify inputs**: Use validation module to check files before API calls
3. **Test with curl**: Verify API connectivity independently
4. **Use standard mode first**: Test with wan-std before wan-pro (cheaper)
5. **Monitor task status**: Log all state transitions
6. **Save intermediate results**: Keep uploaded URLs and task IDs for debugging

## Code Quality Standards

### Documentation:
- Add docstrings to all classes and methods
- Include parameter types and return values
- Document error conditions and exceptions

### Error Messages:
- Provide clear, actionable error messages
- Include suggestion for fixing the issue
- Log full error details for debugging

### Performance:
- Use async/await for I/O operations
- Implement connection pooling for requests
- Stream large file downloads
- Cache reusable data

## Example Testing Scenarios

```python
# Test Case 1: Valid single person image and video
test_result = orchestrator.process_single_task(
    "test_data/single_person.jpg",
    "test_data/reference_video.mp4"
)
assert test_result.success == True

# Test Case 2: Multiple faces in image (should fail)
with pytest.raises(ValidationError) as exc:
    orchestrator.process_single_task(
        "test_data/multiple_people.jpg",
        "test_data/reference_video.mp4"
    )
assert "multiple faces detected" in str(exc.value)

# Test Case 3: Video too long (>30 seconds)
with pytest.raises(ValidationError) as exc:
    orchestrator.process_single_task(
        "test_data/single_person.jpg",
        "test_data/long_video.mp4"
    )
assert "duration exceeds 30 seconds" in str(exc.value)

# Test Case 4: Network failure recovery
# Simulate network failure and verify retry logic works
```

## Final Implementation Notes

Remember to:
1. **Start simple**: Get basic functionality working first, then add complexity
2. **Test frequently**: Test each component as you build it
3. **Use the free tier**: You have 50 seconds free quota for testing
4. **Document everything**: Future you will thank present you
5. **Consider cost**: Standard mode is 40% cheaper than professional mode
6. **Handle failures gracefully**: Failed tasks don't cost money, so retry liberally
7. **Think about UX**: Provide progress updates for long-running tasks

## Success Metrics

Your implementation should achieve:
- ✅ 95%+ success rate for valid inputs
- ✅ Clear error messages for invalid inputs
- ✅ Automatic retry on transient failures
- ✅ Complete processing in under 5 minutes per video
- ✅ Zero data loss (always save results before URL expiration)
- ✅ Cost optimization (use standard mode when appropriate)
- ✅ Comprehensive logging for troubleshooting

## Remember: Think Step by Step

Before writing any code:
1. Understand the requirement completely
2. Design the solution
3. Consider edge cases
4. Implement with error handling
5. Test thoroughly
6. Document clearly

You have all the information needed in the technical research document. Refer to it frequently and ensure your implementation aligns with the API specifications exactly.

Good luck with the implementation! Take your time, think through each step carefully, and create a robust, production-ready solution.

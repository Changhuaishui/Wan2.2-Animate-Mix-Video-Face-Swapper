# Wan2.2-Animate-Mix Python API 调用系统设计规划

## 项目概述
基于阿里云通义万相Wan2.2-Animate-Mix视频换人模型，构建一个本地Python应用程序，实现自动化的视频换人处理流程。

## 系统架构

### 1. 核心模块设计

```
wan22_video_processor/
├── __init__.py
├── config/
│   ├── __init__.py
│   └── settings.py         # 配置管理
├── validators/
│   ├── __init__.py
│   ├── image_validator.py  # 图片验证器
│   └── video_validator.py  # 视频验证器
├── uploaders/
│   ├── __init__.py
│   └── oss_uploader.py     # OSS上传管理
├── processors/
│   ├── __init__.py
│   └── wan_processor.py    # Wan2.2 API调用处理
├── utils/
│   ├── __init__.py
│   ├── file_handler.py     # 文件处理工具
│   └── logger.py          # 日志管理
└── main.py                 # 主程序入口
```

### 2. 功能模块详细设计

#### 2.1 配置管理模块 (config/settings.py)
```python
class Config:
    # API配置
    API_KEY = os.getenv("DASHSCOPE_API_KEY")
    API_BASE_URL = "https://dashscope.aliyuncs.com/api/v1"
    API_REGION = "cn-beijing"
    
    # OSS配置（可选）
    OSS_ACCESS_KEY_ID = os.getenv("OSS_ACCESS_KEY_ID")
    OSS_ACCESS_KEY_SECRET = os.getenv("OSS_ACCESS_KEY_SECRET")
    OSS_BUCKET = "wan22-videos"
    OSS_ENDPOINT = "oss-cn-beijing.aliyuncs.com"
    
    # 文件限制
    IMAGE_FORMATS = ['jpg', 'jpeg', 'png', 'bmp', 'webp']
    VIDEO_FORMATS = ['mp4', 'avi', 'mov']
    IMAGE_MIN_SIZE = 200
    IMAGE_MAX_SIZE = 4096
    IMAGE_MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    VIDEO_MIN_SIZE = 200
    VIDEO_MAX_SIZE = 2048
    VIDEO_MIN_DURATION = 2  # 秒
    VIDEO_MAX_DURATION = 30  # 秒
    VIDEO_MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB
    
    # 处理参数
    DEFAULT_MODE = "wan-std"  # wan-std 或 wan-pro
    POLLING_INTERVAL = 15  # 轮询间隔（秒）
    MAX_WAIT_TIME = 600  # 最大等待时间（秒）
```

#### 2.2 图片验证器 (validators/image_validator.py)
```python
class ImageValidator:
    def __init__(self):
        self.allowed_formats = Config.IMAGE_FORMATS
        self.size_range = (Config.IMAGE_MIN_SIZE, Config.IMAGE_MAX_SIZE)
        self.max_file_size = Config.IMAGE_MAX_FILE_SIZE
        
    def validate(self, image_path):
        """
        验证图片是否符合要求
        返回: (is_valid, error_message)
        """
        # 1. 检查文件存在性
        # 2. 检查文件格式
        # 3. 检查文件大小
        # 4. 检查图片尺寸
        # 5. 检查宽高比（1:3 到 3:1）
        # 6. 检测人脸数量（确保只有一个人）
        pass
```

#### 2.3 视频验证器 (validators/video_validator.py)
```python
class VideoValidator:
    def __init__(self):
        self.allowed_formats = Config.VIDEO_FORMATS
        self.size_range = (Config.VIDEO_MIN_SIZE, Config.VIDEO_MAX_SIZE)
        self.duration_range = (Config.VIDEO_MIN_DURATION, Config.VIDEO_MAX_DURATION)
        self.max_file_size = Config.VIDEO_MAX_FILE_SIZE
        
    def validate(self, video_path):
        """
        验证视频是否符合要求
        返回: (is_valid, error_message)
        """
        # 1. 检查文件存在性
        # 2. 检查文件格式
        # 3. 检查文件大小
        # 4. 检查视频时长
        # 5. 检查视频分辨率
        # 6. 检查首帧人脸
        pass
```

#### 2.4 OSS上传管理器 (uploaders/oss_uploader.py)
```python
class OSSUploader:
    def __init__(self):
        self.bucket = None  # 初始化OSS客户端
        
    def upload_file(self, local_path, remote_path=None):
        """
        上传文件到OSS并返回公网URL
        """
        # 1. 生成唯一的远程路径
        # 2. 上传文件
        # 3. 生成公网访问URL
        # 4. 返回URL
        pass
        
    def cleanup_old_files(self, days=7):
        """
        清理超过指定天数的文件
        """
        pass
```

#### 2.5 Wan2.2处理器 (processors/wan_processor.py)
```python
class Wan22Processor:
    def __init__(self, api_key=None, mode="wan-std"):
        self.api_key = api_key or Config.API_KEY
        self.mode = mode
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-DashScope-Async": "enable"
        }
        
    def create_task(self, image_url, video_url):
        """
        创建视频换人任务
        返回: task_id 或 None
        """
        # 1. 构建请求体
        # 2. 发送POST请求
        # 3. 解析响应
        # 4. 返回task_id
        pass
        
    def query_task(self, task_id, timeout=600):
        """
        轮询查询任务状态
        返回: video_url 或 None
        """
        # 1. 循环查询任务状态
        # 2. 处理不同状态
        # 3. 超时处理
        # 4. 返回结果URL
        pass
        
    def download_video(self, video_url, save_path):
        """
        下载生成的视频
        """
        # 1. 请求视频URL
        # 2. 分块下载
        # 3. 保存到本地
        pass
        
    def process(self, image_path, video_path, output_path):
        """
        完整处理流程
        """
        # 1. 验证输入文件
        # 2. 上传到OSS获取URL
        # 3. 创建任务
        # 4. 轮询等待结果
        # 5. 下载结果视频
        # 6. 清理临时文件
        pass
```

### 3. 主程序设计 (main.py)

```python
class VideoFaceSwapper:
    def __init__(self, mode="wan-std"):
        self.mode = mode
        self.image_validator = ImageValidator()
        self.video_validator = VideoValidator()
        self.uploader = OSSUploader()
        self.processor = Wan22Processor(mode=mode)
        self.logger = setup_logger()
        
    def run(self, image_path, video_path, output_dir="./output"):
        """
        执行完整的视频换人流程
        """
        try:
            # 步骤1: 验证输入文件
            self.logger.info("开始验证输入文件...")
            
            # 验证图片
            is_valid, error = self.image_validator.validate(image_path)
            if not is_valid:
                raise ValueError(f"图片验证失败: {error}")
                
            # 验证视频
            is_valid, error = self.video_validator.validate(video_path)
            if not is_valid:
                raise ValueError(f"视频验证失败: {error}")
            
            # 步骤2: 上传文件到OSS
            self.logger.info("上传文件到云存储...")
            image_url = self.uploader.upload_file(image_path)
            video_url = self.uploader.upload_file(video_path)
            
            # 步骤3: 创建处理任务
            self.logger.info("创建视频换人任务...")
            task_id = self.processor.create_task(image_url, video_url)
            
            # 步骤4: 等待处理完成
            self.logger.info(f"任务ID: {task_id}, 等待处理...")
            result_url = self.processor.query_task(task_id)
            
            # 步骤5: 下载结果
            output_path = os.path.join(output_dir, f"result_{task_id}.mp4")
            self.logger.info(f"下载结果视频到: {output_path}")
            self.processor.download_video(result_url, output_path)
            
            # 步骤6: 清理临时文件
            self.uploader.cleanup_old_files()
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"处理失败: {str(e)}")
            raise
```

## 技术实现要点

### 1. 图片预处理
- 使用 `Pillow` 库进行图片格式转换和尺寸调整
- 使用 `face_recognition` 或 `opencv` 进行人脸检测
- 自动裁剪和调整宽高比

### 2. 视频预处理
- 使用 `moviepy` 或 `ffmpeg-python` 进行视频处理
- 提取首帧进行人脸检测
- 自动调整分辨率和时长

### 3. 并发处理优化
- 使用 `asyncio` 实现异步上传和下载
- 批量处理时使用任务队列
- 实现断点续传功能

### 4. 错误处理策略
- 自动重试机制（失败不计费）
- 详细的错误日志记录
- 友好的错误提示信息

### 5. 成本优化
- 先使用标准模式测试
- 批量处理时复用OSS链接
- 自动清理过期文件

## 使用示例

```python
# 简单使用
from wan22_video_processor import VideoFaceSwapper

# 初始化处理器
swapper = VideoFaceSwapper(mode="wan-std")

# 处理单个视频
result = swapper.run(
    image_path="person.jpg",
    video_path="reference.mp4",
    output_dir="./results"
)

print(f"处理完成: {result}")

# 批量处理
for image, video in task_list:
    try:
        result = swapper.run(image, video)
        successful_tasks.append(result)
    except Exception as e:
        failed_tasks.append((image, video, str(e)))
```

## 部署建议

### 1. 环境配置
```bash
# 安装依赖
pip install requests pillow opencv-python moviepy oss2 python-dotenv

# 配置环境变量
export DASHSCOPE_API_KEY="sk-xxxx"
export OSS_ACCESS_KEY_ID="xxxx"
export OSS_ACCESS_KEY_SECRET="xxxx"
```

### 2. Docker部署
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### 3. 监控与日志
- 使用 `logging` 模块记录详细日志
- 集成 Prometheus 监控指标
- 设置任务处理时间告警

## 性能指标

- 单任务处理时间: 2-5分钟
- 并发任务数: 1个（API限制）
- 日处理能力: ~200个视频
- 成功率目标: >95%
- 成本控制: 标准模式0.6元/秒，专业模式0.9元/秒

## 后续优化方向

1. **智能模式选择**: 根据素材质量自动选择标准或专业模式
2. **批处理优化**: 实现任务队列和优先级管理
3. **质量评估**: 自动评估生成视频质量
4. **缓存机制**: 相似素材复用处理结果
5. **Web界面**: 开发可视化操作界面

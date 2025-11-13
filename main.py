"""
阿里云通义万相 - 视频换脸工具
简洁交互式版本
"""
import os
import sys
import time
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    from wan22_video_processor.orchestrator import VideoFaceSwapper, ProcessingError
    from wan22_video_processor.config.settings import Config
except ImportError as e:
    print(f"错误: 无法导入项目模块: {e}")
    print("请确保wan22_video_processor文件夹存在")
    sys.exit(1)


def print_banner():
    """打印程序标题"""
    print("\n" + "=" * 70)
    print("           阿里云通义万相 - 视频换脸工具")
    print("=" * 70)


def print_requirements():
    """打印输入要求"""
    print("\n📋 输入文件要求:")
    print("  图片: JPG/PNG/BMP/WEBP | 200-4096px | <5MB | 宽高比1:3到3:1")
    print("  视频: MP4/AVI/MOV | 200-2048px | 2-30秒 | <200MB | 宽高比1:3到3:1")
    print()


def log(message, level="INFO"):
    """格式化日志输出"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    prefix = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "ERROR": "❌",
        "WARNING": "⚠️",
        "WAITING": "⏳"
    }.get(level, "  ")
    print(f"[{timestamp}] {prefix} {message}")


def get_file_path(prompt, file_type="file"):
    """获取并验证文件路径"""
    while True:
        path = input(f"{prompt}: ").strip().strip('"')

        if not path:
            log("路径不能为空", "ERROR")
            continue

        if not os.path.exists(path):
            log(f"文件不存在: {path}", "ERROR")
            retry = input("  重新输入? (y/n): ").lower()
            if retry != 'y':
                return None
            continue

        return path


def progress_callback(message):
    """进度回调函数"""
    log(message, "WAITING")


def main():
    """主程序"""
    print_banner()

    # 检查配置
    log("检查API配置...")
    try:
        Config.validate_config()
        log(f"API Key: {Config.API_KEY[:20]}...", "SUCCESS")
        log(f"区域: 北京 (cn-beijing)", "INFO")
    except ValueError as e:
        log(f"配置错误: {e}", "ERROR")
        log("请在.env文件中配置DASHSCOPE_API_KEY", "ERROR")
        return 1

    print_requirements()

    # 获取输入文件
    log("请输入文件路径（支持拖拽文件到此窗口）")
    print()

    image_path = get_file_path("  图片路径", "image")
    if not image_path:
        log("已取消", "WARNING")
        return 0

    video_path = get_file_path("  视频路径", "video")
    if not video_path:
        log("已取消", "WARNING")
        return 0

    # 选择处理模式
    print()
    print("处理模式:")
    print("  1. 标准模式 (wan-std) - 0.6元/秒 - 速度快")
    print("  2. 专业模式 (wan-pro) - 0.9元/秒 - 质量高")
    mode_choice = input("请选择 (1/2, 默认1): ").strip() or "1"
    mode = "wan-std" if mode_choice == "1" else "wan-pro"

    print()
    log(f"图片: {os.path.basename(image_path)}", "INFO")
    log(f"视频: {os.path.basename(video_path)}", "INFO")
    log(f"模式: {mode}", "INFO")
    log(f"输出: {Config.OUTPUT_DIR}", "INFO")

    # 确认开始
    print()
    confirm = input("开始处理? (y/n): ").lower()
    if confirm != 'y':
        log("已取消", "WARNING")
        return 0

    print("\n" + "=" * 70)
    log("开始处理视频换脸...", "INFO")
    print("=" * 70)

    start_time = time.time()

    try:
        # 初始化处理器
        log(f"初始化处理器（模式: {mode}）...", "INFO")
        swapper = VideoFaceSwapper(mode=mode)

        # 处理视频
        log("开始处理流程...", "INFO")
        result = swapper.process(
            image_path=image_path,
            video_path=video_path,
            output_dir=Config.OUTPUT_DIR,
            skip_validation=True,  # 跳过复杂验证，用户自己选择合适的文件
            progress_callback=progress_callback
        )

        # 成功
        elapsed = time.time() - start_time
        print("\n" + "=" * 70)
        log("处理完成!", "SUCCESS")
        print("=" * 70)
        log(f"输出文件: {result['output_path']}", "INFO")
        log(f"处理时长: {result['processing_time']:.1f}秒", "INFO")
        log(f"总耗时: {elapsed:.1f}秒", "INFO")

        if result.get('cost'):
            log(f"费用: {result['cost']:.2f}元", "INFO")

        if result.get('task_id'):
            log(f"任务ID: {result['task_id']}", "INFO")

        print("=" * 70)
        return 0

    except ProcessingError as e:
        elapsed = time.time() - start_time
        print("\n" + "=" * 70)
        log("处理失败", "ERROR")
        print("=" * 70)
        log(f"错误: {str(e)}", "ERROR")
        log(f"耗时: {elapsed:.1f}秒", "INFO")

        # 常见错误的解决建议
        error_str = str(e).lower()
        if "duration" in error_str:
            log("解决方法: 视频时长必须在2-30秒之间", "WARNING")
            log("请使用视频编辑工具裁剪视频", "WARNING")
        elif "size" in error_str or "resolution" in error_str:
            log("解决方法: 检查图片/视频尺寸是否符合要求", "WARNING")
        elif "api key" in error_str or "auth" in error_str:
            log("解决方法: 检查.env文件中的API Key是否正确", "WARNING")
        elif "network" in error_str or "timeout" in error_str:
            log("解决方法: 检查网络连接，稍后重试", "WARNING")
        elif "face" in error_str:
            log("解决方法: 确保图片/视频中有清晰的人脸", "WARNING")

        log("注意: 失败的任务不计费，可以重试", "INFO")
        print("=" * 70)
        return 1

    except KeyboardInterrupt:
        log("用户中断", "WARNING")
        return 130

    except Exception as e:
        elapsed = time.time() - start_time
        print("\n" + "=" * 70)
        log("发生未预期的错误", "ERROR")
        print("=" * 70)
        log(f"错误: {str(e)}", "ERROR")
        log(f"耗时: {elapsed:.1f}秒", "INFO")
        print("=" * 70)

        import traceback
        log("详细错误信息:", "ERROR")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()

        # 等待用户确认后退出
        print()
        input("按回车键退出...")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n程序已中断")
        sys.exit(130)

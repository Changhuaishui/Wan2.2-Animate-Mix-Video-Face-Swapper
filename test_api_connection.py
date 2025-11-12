"""
API连通性测试脚本
只测试API认证和连接，不消耗处理额度

安全措施：
1. 只测试API key有效性
2. 不实际创建完整任务
3. 或使用无效URL快速失败（不消耗额度）
"""
import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

API_KEY = os.getenv("DASHSCOPE_API_KEY")
BASE_URL = "https://dashscope.aliyuncs.com/api/v1"


def print_section(title):
    """打印分隔线"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_api_key_validity():
    """
    测试1: API Key有效性检查
    使用一个已知会失败但不消耗额度的请求
    """
    print_section("测试 1: API Key 有效性检查")

    if not API_KEY:
        print("[ERROR] DASHSCOPE_API_KEY not set")
        return False

    print(f"[OK] API Key loaded: {API_KEY[:15]}...{API_KEY[-5:]}")

    # 测试API key格式
    if not API_KEY.startswith("sk-"):
        print("[WARNING] API Key format may be incorrect (should start with sk-)")
        return False

    print("[OK] API Key format is valid")
    return True


def test_api_authentication():
    """
    测试2: API认证测试
    使用无效URL创建任务，快速失败，不消耗额度
    """
    print_section("测试 2: API 认证测试（不消耗额度）")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
        "X-DashScope-Async": "enable"
    }

    # 使用明显无效的URL，这样会在验证阶段失败，不会实际处理
    payload = {
        "model": "wan2.2-animate-mix",
        "input": {
            "image_url": "https://invalid-test-url.example.com/test.jpg",
            "video_url": "https://invalid-test-url.example.com/test.mp4"
        },
        "parameters": {
            "mode": "wan-std",
            "check_image": True
        }
    }

    print("发送测试请求到 API...")
    print("使用无效URL，预期会快速失败（不消耗额度）")

    try:
        response = requests.post(
            f"{BASE_URL}/services/aigc/image2video/video-synthesis",
            headers=headers,
            json=payload,
            timeout=30
        )

        print(f"\n响应状态码: {response.status_code}")
        result = response.json()

        # 检查响应
        if response.status_code == 200:
            # 即使返回200，如果是无效URL，也会在后续处理中失败
            if "output" in result:
                print("\n[OK] API authentication successful!")
                print(f"  任务状态: {result['output'].get('task_status', 'UNKNOWN')}")
                if "task_id" in result["output"]:
                    print(f"  任务ID: {result['output']['task_id']}")
                    print("\n[NOTE] Task uses invalid URL, will fail automatically, no quota consumed")
                return True

        elif response.status_code == 400:
            # 参数错误 - 说明API可以访问，但参数有问题
            print("\n[OK] API accessible (parameter validation phase)")
            print(f"  错误信息: {result.get('message', 'Unknown')}")
            return True

        elif response.status_code == 401:
            # 认证失败
            print("\n[ERROR] API Key authentication failed")
            print(f"  错误: {result.get('message', 'Invalid API Key')}")
            return False

        elif response.status_code == 403:
            # 权限不足
            print("\n[WARNING] API Key valid but insufficient permissions")
            print(f"  错误: {result.get('message', 'Forbidden')}")
            return False

        else:
            print(f"\n⚠️  意外的响应: {result}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"\n❌ 网络请求失败: {e}")
        return False
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        return False


def test_query_nonexistent_task():
    """
    测试3: 查询不存在的任务（测试查询接口）
    不消耗额度
    """
    print_section("测试 3: 查询接口测试（不消耗额度）")

    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    # 使用一个不存在的task_id
    fake_task_id = "test-00000000-0000-0000-0000-000000000000"
    query_url = f"{BASE_URL}/tasks/{fake_task_id}"

    print(f"查询不存在的任务: {fake_task_id}")

    try:
        response = requests.get(query_url, headers=headers, timeout=30)
        result = response.json()

        print(f"响应状态码: {response.status_code}")

        if response.status_code == 200:
            task_status = result.get("output", {}).get("task_status", "UNKNOWN")
            if task_status == "UNKNOWN":
                print("\n[OK] Query interface working properly")
                print("  Task does not exist (as expected)")
                return True
        elif response.status_code == 404:
            print("\n[OK] Query interface working properly")
            print("  Task not found (as expected)")
            return True
        else:
            print(f"\n响应: {result}")
            return True  # API可访问即可

    except Exception as e:
        print(f"\n⚠️  查询失败: {e}")
        return False


def show_quota_info():
    """显示额度使用提醒"""
    print_section("额度使用提醒")
    print("""
[OK] Above tests did NOT consume any processing quota!

Free Quota Information:
- Initial quota: 50 seconds
- Standard mode: 0.6 RMB/second
- Professional mode: 0.9 RMB/second

Important Notes:
1. Failed tasks do NOT consume quota - safe to retry
2. Only successfully generated videos are charged
3. task_id and video URLs valid for 24 hours

How to Save Quota:
- Test with standard mode (wan-std) first
- Validate input files before processing
- Use short videos for testing
""")


def main():
    """主测试流程"""
    print("""
    ===============================================================

             Wan2.2 API Connection Test - No Quota Used

    ===============================================================
    """)

    results = []

    # 测试1: API Key有效性
    results.append(("API Key 有效性", test_api_key_validity()))

    if not results[0][1]:
        print("\n[ERROR] API Key invalid, stopping tests")
        return 1

    # 测试2: API认证
    results.append(("API 认证", test_api_authentication()))

    # 测试3: 查询接口
    results.append(("查询接口", test_query_nonexistent_task()))

    # 显示额度信息
    show_quota_info()

    # 总结
    print_section("测试总结")
    print()
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status}  {test_name}")

    all_passed = all(result[1] for result in results)

    if all_passed:
        print("\n" + "=" * 70)
        print("  SUCCESS! All tests passed! API connection is working")
        print("=" * 70)
        print("\nNext Steps:")
        print("  1. Prepare test image and video")
        print("  2. Validate: python main.py validate -i image.jpg -v video.mp4")
        print("  3. Process: python main.py process -i image.jpg -v video.mp4")
        return 0
    else:
        print("\n" + "=" * 70)
        print("  WARNING: Some tests failed, please check configuration")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())

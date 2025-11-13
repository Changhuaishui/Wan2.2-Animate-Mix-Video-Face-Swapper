# 阿里云通义万相 - 视频换脸工具

基于阿里云Wan2.2-Animate-Mix API的简洁视频换脸工具。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API Key

编辑 `.env` 文件，添加您的API Key：

```
DASHSCOPE_API_KEY=sk-your-api-key-here
```

> 获取API Key: https://dashscope.console.aliyun.com/apiKey

### 3. 运行程序

```bash
python main.py
```

程序会提示您输入：
- 图片路径（支持拖拽文件）
- 视频路径（支持拖拽文件）
- 选择处理模式（标准/专业）

### 4. 查看结果

处理完成后，视频会保存在 `output/` 文件夹。

## 输入要求

### 图片
- 格式: JPG, PNG, BMP, WEBP
- 尺寸: 200-4096px
- 大小: <5MB
- 宽高比: 1:3 到 3:1

### 视频
- 格式: MP4, AVI, MOV
- 尺寸: 200-2048px
- 时长: **2-30秒**（重要）
- 大小: <200MB
- 宽高比: 1:3 到 3:1

## 费用

- 免费额度: 50秒
- 标准模式: 0.6元/秒
- 专业模式: 0.9元/秒

**注意**: 失败的任务不计费，可以重试！

## 常见问题

### 视频时长问题
❌ 错误: "Invalid video duration"

✅ 解决: 视频必须在2-30秒之间。使用视频编辑工具（如剪映）裁剪视频。

### API Key错误
❌ 错误: "Invalid API Key"

✅ 解决: 检查 `.env` 文件中的 `DASHSCOPE_API_KEY` 是否正确。

### 连接超时
❌ 错误: "Connection timeout"

✅ 解决: 检查网络连接，稍后重试。

## 项目结构

```
video/
├── main.py                    # 主程序（唯一入口）
├── wan22_video_processor/     # 核心处理模块
│   ├── config/               # 配置管理
│   ├── uploaders/            # 文件上传
│   ├── processors/           # API调用
│   └── orchestrator.py       # 流程编排
├── output/                    # 输出文件夹
├── .env                       # API配置
└── requirements.txt           # 依赖列表
```

## API文档

- API文档: https://help.aliyun.com/zh/model-studio/wan-animate-mix-api
- 控制台: https://dashscope.console.aliyun.com/
- 错误码: https://help.aliyun.com/zh/model-studio/error-code

## 注意事项

1. **API Key安全**: 不要将 `.env` 文件提交到版本控制
2. **视频时长**: 务必确保视频在2-30秒之间
3. **网络连接**: 需要稳定的网络连接
4. **结果保存**: 视频URL 24小时后失效，及时下载

## 使用技巧

1. **测试建议**: 先用短视频（2-5秒）测试
2. **模式选择**: 测试时优先用标准模式（更便宜）
3. **文件准备**: 提前准备好符合要求的文件
4. **错误重试**: 失败不计费，可以多次重试

---

**版本**: 1.0
**更新日期**: 2025-11-12

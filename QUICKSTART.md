# Quick Start Guide

Get started with Wan2.2-Animate-Mix Video Face Swapper in 5 minutes!

## 🚀 Installation (2 minutes)

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Configure API Key

1. Get your API key from [DashScope Console](https://dashscope.console.aliyun.com/apiKey)

2. Copy the example configuration:
   ```bash
   copy .env.example .env
   ```

3. Edit `.env` and add your API key:
   ```
   DASHSCOPE_API_KEY=sk-your-actual-api-key-here
   ```

## ✅ Verify Installation

```bash
python main.py config
```

You should see your configuration displayed without errors.

## 🎯 Your First Video Face Swap (3 minutes)

### Prepare Your Files

You need:
- ✅ One image with a person's face (JPG, PNG, etc.)
- ✅ One reference video (MP4, AVI, MOV)

### Run the Processing

```bash
python main.py process -i path/to/person.jpg -v path/to/video.mp4
```

**Example:**
```bash
python main.py process -i test_data/person.jpg -v test_data/video.mp4
```

### Check the Result

The processed video will be saved in the `output/` folder!

## 📋 Common Commands

### Validate Files First
```bash
python main.py validate -i person.jpg -v video.mp4 --verbose
```

### Use Professional Mode (Higher Quality)
```bash
python main.py process -i person.jpg -v video.mp4 --mode wan-pro
```

### Custom Output Location
```bash
python main.py process -i person.jpg -v video.mp4 -o ./my_results -f my_video.mp4
```

## 💡 Input Requirements Checklist

### ✅ Image Requirements
- [ ] Format: JPG, PNG, BMP, WEBP
- [ ] Size: 200-4096 pixels
- [ ] File size: Under 5MB
- [ ] Contains exactly 1 clear face

### ✅ Video Requirements
- [ ] Format: MP4, AVI, MOV
- [ ] Duration: 2-30 seconds
- [ ] Resolution: 200-2048 pixels
- [ ] File size: Under 200MB
- [ ] First frame shows a face

## 💰 Pricing

- **Free Tier**: 50 seconds
- **Standard Mode**: 0.6 RMB/second
- **Professional Mode**: 0.9 RMB/second

**Note**: Failed tasks don't cost anything!

## 🔍 Troubleshooting

### Error: "API Key is required"
➡️ Make sure you set `DASHSCOPE_API_KEY` in your `.env` file

### Error: "No face detected"
➡️ Ensure your image has a clear, single face

### Error: "Invalid file format"
➡️ Check that your files meet the requirements above

### Need More Help?
- Check the full [README.md](README.md)
- View [examples.py](example.py) for code examples
- Review the [API Documentation](https://help.aliyun.com/zh/model-studio/wan-animate-mix-api)

## 🎓 Next Steps

1. ✅ Try processing your first video
2. ⭐ Experiment with different modes (wan-std vs wan-pro)
3. 📚 Read the full [README.md](README.md) for advanced features
4. 💻 Check [example.py](example.py) for programmatic usage

## 🎉 Success!

Once you see:
```
✓ Processing Complete!
Output file: ./output/result_20250112_143022.mp4
```

You're done! Open the output file and see the result.

---

**Happy face-swapping! 🎭**

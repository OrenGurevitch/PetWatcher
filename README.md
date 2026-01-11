# Pet Camera

Turn your laptop's webcam into a smart pet monitoring system with custom recognition.

## Why This Exists

Commercial pet cameras cost **$50-300** and require subscriptions ($5-20/month). This project uses your existing laptop camera and runs completely free. Train it to recognize your specific pets by name, get notifications when they're active, and monitor them while you're away.

## Features

- **Custom pet recognition** - Train on your own pets, recognizes each by name
- **Person detection** - Know when people are in the room
- **Smart notifications** - Get alerts on your phone (Telegram/Discord) with photos
- **Real-time monitoring** - See live detections with bounding boxes
- **Free forever** - No subscriptions, runs on your hardware
- **Privacy first** - Everything stays on your device

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the camera
python3 camera.py
```

Press `Q` to quit.

## Training On Your Pets

This system works with **any pets** - cats, dogs, rabbits, birds, etc.

### 1. Collect Images

Create folders in `data/` for each pet and background:

```
data/
├── background/      # Images without pets (at least 50)
├── fluffy/         # Your first pet (at least 30)
└── spot/           # Your second pet (at least 30)
```

**Image requirements:**
- Format: `.jpg` or `.jpeg`
- Minimum: 30 images per pet, 50 background images
- Recommended: 50-100 images per category
- Tips: Various angles, lighting conditions, typical locations

### 2. Auto-Annotate Images

```bash
python3 scripts/annotate.py
```

This automatically detects and labels pets in your images.

### 3. Train Model

```bash
export COMET_API_KEY='your-key'  # Optional: for training visualization
python3 scripts/train.py
```

Training takes 20-30 minutes on a modern laptop.

### 4. Run Detection

```bash
python3 camera.py
```

Your trained model is automatically loaded from `models/cat_detector.pt`.

## Notifications

Get instant alerts when pets are detected.

**Setup (5 minutes):**

1. Install notification support:
```bash
pip install aiohttp
```

2. Create a Telegram bot:
   - Open Telegram, search for `@BotFather`
   - Send `/newbot` and follow instructions
   - Save your bot token

3. Get your chat ID:
   - Message your bot
   - Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
   - Copy the `chat.id` value

4. Create `config.json`:
```json
{
  "notifications": {
    "enabled": true,
    "cooldown_seconds": 300,
    "platforms": {
      "telegram": {
        "enabled": true,
        "bot_token": "your_bot_token_here",
        "chat_id": "your_chat_id_here"
      }
    }
  }
}
```

**Result:** Get phone notifications like "Fluffy detected!" with photos.

See `SETUP.md` for complete notification setup.

## Running 24/7

To monitor pets while away, your laptop needs to stay on.

### Power Settings

**macOS:**
```bash
# Keep laptop awake with lid open
System Settings → Lock Screen → Turn display off: Never
System Settings → Battery → Prevent sleeping when display is off: On
```

**Windows:**
```
Settings → System → Power → Screen and sleep → Never
```

**Linux:**
```bash
# Disable sleep
sudo systemctl mask sleep.target suspend.target
```

### Tips for Extended Use

- **Power**: Keep laptop plugged in
- **Cooling**: Ensure good ventilation, consider laptop cooling pad
- **Position**: Place camera with clear view of monitored area
- **Network**: Use ethernet for reliability (optional)
- **Storage**: System uses ~10MB for snapshots (auto-managed)

### Remote Access

Access camera feed remotely:

**Option 1: VPN** (Recommended)
- Use Tailscale (free) or WireGuard
- Access your laptop securely from anywhere

**Option 2: Port Forwarding** (Less secure)
- Forward port on router
- Use dynamic DNS service

**Option 3: Cloud Server**
- Run on cheap cloud instance ($5/month)
- VPS stays on 24/7

See `SETUP.md` for remote access instructions.

## How It Works

1. **Detection Model**: Uses YOLO (You Only Look Once) object detection
2. **Dual Models**:
   - Generic model for people (pre-trained)
   - Custom model for your specific pets (you train it)
3. **Smart Notifications**: Only alerts on state changes, not continuously
4. **Storage Management**: Auto-deletes old snapshots, never fills disk

## Performance

**Laptop Requirements:**
- **Minimum**: Any laptop with webcam (2015+)
- **Recommended**: M-series Mac or modern laptop with GPU
- **Performance**:
  - M-series Mac: 25-30 FPS
  - Modern laptop with GPU: 20-30 FPS
  - CPU only: 10-15 FPS (still usable)

**Storage:**
- Model: 5 MB
- Snapshots: ~10 MB (auto-managed)
- Training data: Depends on your images

## Project Structure

```
pet-camera/
├── camera.py              # Main application
├── notifications.py       # Notification system
├── models/
│   └── cat_detector.pt    # Your trained model
├── scripts/
│   ├── annotate.py        # Auto-annotate images
│   └── train.py           # Train custom model
├── data/                  # Your training images
│   ├── background/
│   ├── pet1/
│   └── pet2/
├── cat_dataset/           # Generated training dataset
├── snapshots/             # Detection snapshots (auto-managed)
├── config.json           # Configuration (create from example)
├── config.example.json   # Configuration template
├── requirements.txt      # Python dependencies
├── SETUP.md             # Complete setup guide
└── README.md            # This file
```

## Configuration Options

Edit `config.json` or use command-line arguments:

```bash
# Different camera
python3 camera.py --camera 1

# Adjust sensitivity
python3 camera.py --confidence 0.3

# Performance mode (skip frames)
python3 camera.py --skip-frames 2

# Force CPU (no GPU)
python3 camera.py --device cpu
```

## Requirements

- Python 3.8 or newer
- Webcam
- 2GB free disk space
- 4GB RAM minimum

**Operating Systems:**
- macOS (works great, MPS acceleration on M-series)
- Windows (works great, CUDA on NVIDIA GPUs)
- Linux (works great)

## Cost Comparison

| Solution | Hardware | Subscription | Total Year 1 | Total Year 3 |
|----------|----------|--------------|--------------|--------------|
| **This Project** | $0 (use laptop) | $0 | **$0** | **$0** |
| Basic Pet Cam | $50 | $0 | $50 | $50 |
| Smart Pet Cam | $150 | $10/mo | $270 | $510 |
| Premium Pet Cam | $300 | $20/mo | $540 | $1,020 |

**Savings: $500-1,000+ over 3 years**

## Limitations

- Laptop must stay on and camera positioned correctly
- Not waterproof or ruggedized like commercial cameras
- No pan/tilt/zoom (but can use external USB cameras with these features)
- Requires some technical setup (but this guide makes it easy)

## Troubleshooting

**Camera not opening:**
```bash
# Try different camera index
python3 camera.py --camera 1
```

**Low FPS:**
```bash
# Enable frame skipping
python3 camera.py --skip-frames 2
```

**Model not found:**
```bash
# Check if model exists
ls models/cat_detector.pt

# If missing, train model first
python3 scripts/train.py
```

**Not detecting pets:**
- Check if pets are in camera view
- Lower confidence: `--confidence 0.3`
- Retrain with more varied images

More troubleshooting in `SETUP.md`.

## Privacy

All processing happens locally on your device. No data is sent to external servers except:
- Telegram notifications (if enabled, images sent to Telegram servers)
- Training visualization (if using Comet ML, metrics sent to Comet)

You can run completely offline by disabling notifications.

## License

MIT License - Feel free to use, modify, and distribute.

## Contributing

Contributions welcome! Please open an issue or pull request.

## Acknowledgments

Built with:
- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) - Object detection
- [PyTorch](https://pytorch.org/) - Deep learning framework
- [OpenCV](https://opencv.org/) - Computer vision

---

**Questions?** See `SETUP.md` for detailed instructions or open an issue.

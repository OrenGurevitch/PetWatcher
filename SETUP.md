# Complete Setup Guide

Everything you need to set up, train, and run your pet camera.

## Table of Contents

- [Installation](#installation)
- [Training Your Model](#training-your-model)
- [Notifications](#notifications)
- [Running 24/7](#running-247)
- [Remote Access](#remote-access)
- [Troubleshooting](#troubleshooting)

---

## Installation

### 1. Install Python

**macOS:**
```bash
# Check if Python is installed
python3 --version

# If not, install with Homebrew
brew install python3
```

**Windows:**
- Download from [python.org](https://www.python.org/downloads/)
- Check "Add Python to PATH" during installation

**Linux:**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### 2. Clone Repository

```bash
git clone https://github.com/yourusername/pet-camera.git
cd pet-camera
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- PyTorch (deep learning)
- Ultralytics YOLO (object detection)
- OpenCV (computer vision)
- Other utilities

Installation takes 5-10 minutes depending on your connection.

---

## Training Your Model

### Step 1: Collect Images

Create training data structure:

```bash
mkdir -p data/background data/pet1 data/pet2
```

Replace `pet1` and `pet2` with your pets' names (e.g., `fluffy`, `spot`).

**Image Requirements:**
- **Format**: `.jpg` or `.jpeg` files
- **Minimum**: 30 images per pet, 50 background images
- **Recommended**: 50-100 images per category
- **Quality**: Clear, well-lit photos

**Background Images:**
Put images of your home **without pets** in `data/background/`:
- Empty rooms
- Furniture
- Different lighting conditions
- Various angles

**Pet Images:**
Put images of each pet in their folder (`data/fluffy/`, `data/spot/`):
- Different poses (sitting, standing, lying down)
- Different locations (couch, floor, bed)
- Various angles (front, side, back)
- Different lighting (day, night, shadows)

**Tips:**
- Use your phone to take photos
- Don't worry about cropping - system detects pets automatically
- More variety = better accuracy
- Include typical locations where pets hang out

### Step 2: Auto-Annotate

```bash
python3 scripts/annotate.py
```

This script:
1. Scans your `data/` folders
2. Uses pre-trained model to detect pets
3. Creates labeled dataset in `cat_dataset/`
4. Takes 2-5 minutes

**Expected output:**
```
🚀 Annotating images...
📂 background: 50 images
📂 fluffy: 45 images
📂 spot: 38 images
✅ Dataset created: cat_dataset/
```

### Step 3: Train Model

**Optional: Set up training visualization**

Get a free Comet ML account at [comet.com](https://www.comet.com/):
```bash
export COMET_API_KEY='your-api-key-here'
```

This is optional but lets you watch training progress in your browser.

**Start training:**
```bash
python3 scripts/train.py
```

**Training time:**
- M-series Mac: 20-25 minutes
- Modern laptop with GPU: 25-35 minutes
- CPU only: 45-60 minutes

**What happens:**
1. Loads pre-trained YOLO model
2. Fine-tunes on your pet images
3. Saves best model to `models/cat_detector.pt`
4. Shows progress and metrics

**Expected output:**
```
🐱 MODEL TRAINING
======================================================================
   Epochs: 200
   Batch: 8
   Device: MPS

Training...
Epoch 1/200: loss=2.45
Epoch 2/200: loss=1.98
...
Epoch 78/200: loss=0.43 (best)
✅ Training complete!
   Model: models/cat_detector.pt
   Accuracy: 96.5%
```

### Step 4: Test Detection

```bash
python3 camera.py
```

Point camera at your pets and verify detection works.

**What you should see:**
- Pets detected with bounding boxes
- Names displayed correctly
- Confidence scores (e.g., "Fluffy 95%")

If detection doesn't work well, see [Troubleshooting](#troubleshooting).

---

## Notifications

Get alerts on your phone when pets are detected.

### Telegram Setup (5 minutes)

**1. Create Telegram Bot**

Open Telegram and search for `@BotFather`.

Send these commands:
```
/newbot
```

Follow prompts:
- **Bot name**: `My Pet Camera` (whatever you want)
- **Username**: `mypetcamerabot` (must end with 'bot')

Save the **bot token** BotFather gives you:
```
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567
```

**2. Get Your Chat ID**

- Find your bot in Telegram
- Send it any message (e.g., "hello")
- Open this URL in browser (replace `<TOKEN>` with your bot token):
```
https://api.telegram.org/bot<TOKEN>/getUpdates
```

Example:
```
https://api.telegram.org/bot1234567890:ABCdef.../getUpdates
```

Look for `"chat":{"id":123456789}` in the response. That number is your chat ID.

**3. Install Notification Support**

```bash
pip install aiohttp
```

**4. Create Configuration**

Copy example config:
```bash
cp config.example.json config.json
```

Edit `config.json`:
```json
{
  "notifications": {
    "enabled": true,
    "cooldown_seconds": 300,
    "persistence_frames": 5,
    "save_images": true,
    "max_images": 100,
    "platforms": {
      "telegram": {
        "enabled": true,
        "bot_token": "YOUR_BOT_TOKEN_HERE",
        "chat_id": "YOUR_CHAT_ID_HERE"
      }
    }
  }
}
```

Replace `YOUR_BOT_TOKEN_HERE` and `YOUR_CHAT_ID_HERE` with your actual values.

**5. Test Notifications**

```bash
python3 camera.py
```

When a pet is detected for 5 consecutive frames, you'll get a Telegram message with a photo.

### Notification Settings

Adjust these in `config.json`:

**Cooldown Period** (`cooldown_seconds`):
- `300` (5 min) - Default, good for daily monitoring
- `180` (3 min) - More frequent updates
- `600` (10 min) - Less frequent, good when away

**Persistence** (`persistence_frames`):
- `5` - Default, balanced
- `3` - Faster notifications (more false positives)
- `10` - Very confident (slower to notify)

**Storage** (`max_images`):
- `100` - Default, ~10MB
- `50` - Less storage (~5MB)
- `200` - More history (~20MB)

---

## Running 24/7

To monitor pets while you're away, your laptop needs to stay on.

### Power Configuration

**macOS:**

```bash
# Via GUI
System Settings → Lock Screen → Turn display off: Never
System Settings → Battery → Prevent sleeping: On

# Via command line
sudo pmset -a displaysleep 0
sudo pmset -a sleep 0
sudo pmset -a disksleep 0
```

**Windows:**

```
Settings → System → Power & Battery
  Screen and sleep → Never
  When plugged in → Never
```

Or use command line (as Administrator):
```cmd
powercfg /change monitor-timeout-ac 0
powercfg /change standby-timeout-ac 0
```

**Linux:**

```bash
# SystemD
sudo systemctl mask sleep.target suspend.target hibernate.target

# GNOME
gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-type 'nothing'

# KDE
kwriteconfig5 --file powermanagementprofilesrc --group AC --group SuspendSession --key idleTime 0
```

### Camera Setup

**Position:**
- Place laptop where camera has clear view
- Aim at common pet areas (couch, bed, food area)
- Ensure good lighting (pets near windows may be backlit)
- Test detection before leaving

**Keep Lid Open:**
- Most laptops disable webcam when lid closes
- Use laptop stand or books to elevate for better angle
- Consider external webcam if lid position is awkward

**Cooling:**
- Ensure good airflow around laptop
- Don't place on soft surfaces (bed, couch)
- Consider laptop cooling pad for extended use
- Clean dust from vents

### Network Reliability

**Wired Connection:**
```bash
# Connect ethernet cable if possible
# More reliable than WiFi for 24/7 operation
```

**WiFi Settings:**
- Set static IP for your laptop
- Keep router nearby for strong signal
- Disable WiFi power saving

**macOS:**
```bash
sudo pmset -a womp 1  # Wake on network access
```

**Windows:**
```
Device Manager → Network Adapters → Properties
Power Management → Uncheck "Allow computer to turn off this device"
```

### Auto-Start on Boot

**macOS (launchd):**

Create `~/Library/LaunchAgents/com.petcamera.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.petcamera</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/path/to/pet-camera/camera.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Load:
```bash
launchctl load ~/Library/LaunchAgents/com.petcamera.plist
```

**Windows (Task Scheduler):**

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: When computer starts
4. Action: Start a program
5. Program: `python.exe`
6. Arguments: `C:\path\to\camera.py`

**Linux (systemd):**

Create `/etc/systemd/system/petcamera.service`:
```ini
[Unit]
Description=Pet Camera
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/pet-camera
ExecStart=/usr/bin/python3 /path/to/pet-camera/camera.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable petcamera
sudo systemctl start petcamera
```

---

## Remote Access

Access your camera feed from anywhere.

### Option 1: VPN (Recommended)

**Tailscale (Easiest):**

1. Install Tailscale on laptop and phone: [tailscale.com](https://tailscale.com)
2. Sign in on both devices
3. They can now talk to each other
4. Access laptop at its Tailscale IP (e.g., `100.64.x.x`)

**Benefits:**
- Secure
- No port forwarding
- Works behind any firewall
- Free for personal use

### Option 2: Cloud Server

Run camera on a cheap cloud instance:

**DigitalOcean/Linode ($5/month):**
```bash
# SSH to server
ssh root@your-server-ip

# Install dependencies
apt update
apt install python3 python3-pip git
git clone https://github.com/yourusername/pet-camera
cd pet-camera
pip3 install -r requirements.txt

# Run camera (headless mode needed)
python3 camera.py --headless
```

**Benefits:**
- Always on
- No laptop needed
- Reliable
- Fast internet

**Downsides:**
- Costs $5/month
- Need to upload training images
- More complex setup

### Option 3: Port Forwarding

**Warning:** Less secure, only do this if you know what you're doing.

1. Find laptop's local IP: `ifconfig` (macOS/Linux) or `ipconfig` (Windows)
2. Log into router (usually 192.168.1.1)
3. Forward port 8080 to your laptop's IP
4. Use dynamic DNS service (e.g., No-IP, DuckDNS)
5. Access at `yourdomain.ddns.net:8080`

---

## Troubleshooting

### Camera Issues

**Camera not opening:**
```bash
# List available cameras
python3 -c "import cv2; print([i for i in range(10) if cv2.VideoCapture(i).isOpened()])"

# Try different index
python3 camera.py --camera 1
```

**Permission denied:**
- macOS: System Settings → Privacy & Security → Camera → Allow Terminal
- Windows: Settings → Privacy → Camera → Allow apps
- Linux: Add user to `video` group: `sudo usermod -a -G video $USER`

**Low FPS:**
```bash
# Skip frames for better performance
python3 camera.py --skip-frames 2

# Force CPU if GPU is slow
python3 camera.py --device cpu
```

### Detection Issues

**Pets not detected:**
- Lower confidence threshold: `--confidence 0.3`
- Retrain with more/better images
- Ensure pets are in frame and well-lit

**Too many false positives:**
- Raise confidence: `--confidence 0.7`
- Increase persistence: Edit `config.json` → `persistence_frames: 10`
- Add more background images to training data

**Wrong pet identified:**
- Collect more images of each pet (especially hard-to-distinguish angles)
- Retrain model
- Ensure images are labeled correctly

### Training Issues

**Training fails:**
```bash
# Check if images are valid
find data/ -name "*.jpg" -o -name "*.jpeg"

# Verify folder structure
ls -R data/
```

**Out of memory:**
- Reduce batch size in `scripts/train.py`: Change `batch=8` to `batch=4`
- Close other applications
- Use smaller images (resize to 640×480)

**Low accuracy:**
- Collect more images (aim for 50-100 per pet)
- More variety in training images
- Better lighting in photos
- Include challenging poses

### Notification Issues

**No notifications:**
- Check config: `cat config.json`
- Verify bot token and chat ID
- Test bot: Send message in Telegram, check `/getUpdates`
- Check console for errors

**Too many notifications:**
- Increase cooldown: `cooldown_seconds: 600`
- Increase persistence: `persistence_frames: 10`

**Notifications delayed:**
- Check internet connection
- Telegram typically instant, check if bot is blocked

### System Issues

**High CPU usage:**
- Enable frame skipping: `--skip-frames 3`
- Lower resolution
- Use GPU if available

**Laptop overheating:**
- Ensure good ventilation
- Use cooling pad
- Lower FPS: `--skip-frames 5`
- Clean dust from vents

**Disk full:**
- System auto-deletes old snapshots
- Check: `du -sh snapshots/`
- Lower `max_images` in config

---

## Getting Help

1. Check this guide
2. Check common issues above
3. Open issue on GitHub: [github.com/yourusername/pet-camera/issues](https://github.com/yourusername/pet-camera/issues)
4. Include:
   - Operating system
   - Python version
   - Error messages
   - What you tried

---

## Next Steps

- Configure notifications for your needs
- Set up auto-start for 24/7 monitoring
- Fine-tune detection sensitivity
- Set up remote access if needed

Everything working? Enjoy monitoring your pets!

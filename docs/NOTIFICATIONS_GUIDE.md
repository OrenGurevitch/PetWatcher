# Notification System Guide

Complete guide to setting up smart notifications for your pet camera.

## The Problem

If you notify on every detection:
- **30 FPS** = 30 notifications per second
- **1800 notifications per minute** = Phone explodes! 💥

## The Solution: Smart Notifications

Only notify when something **changes**, not continuously.

### Best Practices

#### 1. **State Change Detection** (Most Important!)
Only notify when a cat/person **appears** or **disappears**, not while they're still there.

```
✅ Good:
  - "Miso detected!" (when Miso first appears)
  - [silence while Miso is still there]
  - "Miso left" (optional)

❌ Bad:
  - "Miso detected!" x1000 every second
```

#### 2. **Cooldown Period**
Don't notify again for the same subject within X minutes.

```
✅ Good:
  - 11:00 AM: "Miso detected!"
  - 11:05 AM: [Miso still there, no notification]
  - 11:10 AM: [Miso left and came back - notify!]

Cooldown: 5 minutes (configurable)
```

#### 3. **Persistence Checking**
Require detection for N consecutive frames before notifying (reduces false positives).

```
✅ Good:
  - Frame 1-4: Miso detected (waiting...)
  - Frame 5: Miso detected → NOTIFY!

This prevents:
  - Motion blur being detected as a cat
  - Reflections/shadows causing false alerts
  - Random noise triggering notifications
```

#### 4. **Smart Filtering**
Only notify for specific conditions:

```python
# Only notify for cats, not people
notify_on = ['miso', 'ozzy']

# Only notify when you're away
import datetime
if datetime.datetime.now().hour < 17:  # Before 5 PM
    send_notification()

# Only notify if confidence is high
if detection['confidence'] > 0.8:
    send_notification()
```

## Notification Strategies

### Strategy 1: Minimal (Recommended for daily use)
```python
NotificationManager(
    cooldown_seconds=300,      # 5 minutes between notifications
    persistence_frames=5,       # Need 5 consecutive frames
    save_images=True,
    max_images=50              # Keep only 50 recent images
)
```

**Result**: ~1-3 notifications per hour when cats are active

### Strategy 2: Moderate
```python
NotificationManager(
    cooldown_seconds=180,      # 3 minutes
    persistence_frames=3,
    save_images=True,
    max_images=100
)
```

**Result**: ~5-10 notifications per hour

### Strategy 3: Aggressive (Testing only)
```python
NotificationManager(
    cooldown_seconds=60,       # 1 minute
    persistence_frames=2,
    save_images=True,
    max_images=200
)
```

**Result**: Many notifications (good for testing, annoying for daily use)

### Strategy 4: Away From Home
```python
# Only notify when you're not home
import datetime

def should_notify():
    hour = datetime.datetime.now().hour
    # Notify between 9 AM - 5 PM (work hours)
    return 9 <= hour <= 17

NotificationManager(
    cooldown_seconds=600,      # 10 minutes (longer since you're away)
    persistence_frames=10,     # Very confident (reduce false positives)
    save_images=True,
    max_images=20              # Fewer images when away
)
```

**Result**: Check-ins every 10+ minutes during work hours

## Storage: Video vs Images

### Option 1: Images Only (Recommended) ✅

**Pros:**
- Minimal storage (~100KB per image)
- Easy to send in notifications
- Fast to save and load
- Can keep 100+ images easily

**Cons:**
- No motion/context
- Single moment in time

**Storage math:**
- 100 images × 100KB = 10 MB total
- Can keep weeks of images

### Option 2: Short Video Clips

**Pros:**
- Shows motion and context
- More information per event

**Cons:**
- Much larger (5-10MB per 10-second clip)
- Slower to send
- Fills storage quickly
- More complex to implement

**Storage math:**
- 10 clips × 5MB = 50 MB
- Only ~20 clips before 100MB

### Option 3: Continuous Recording (Not Recommended)

**Pros:**
- Complete history

**Cons:**
- HUGE storage requirements
- 30 FPS × 640×480 × 24 hours = ~50+ GB/day
- Requires dedicated storage
- Complex to manage
- Expensive

**Verdict: Use images for notifications, only record video when specifically needed.**

## Platform Comparison

### Telegram ⭐ RECOMMENDED

**Pros:**
- ✅ Free forever
- ✅ Easy API (no approval needed)
- ✅ Fast
- ✅ Supports images
- ✅ No rate limits for personal use
- ✅ Works on all platforms
- ✅ Can create private channel/group
- ✅ Rich formatting

**Cons:**
- ❌ Requires creating a bot
- ❌ Less integrated with iOS/Android than native push

**Best for:** Personal use, international users, technical users

**Setup time:** 5 minutes

### Discord

**Pros:**
- ✅ Free
- ✅ Webhooks are simple
- ✅ Supports images
- ✅ Rich embeds
- ✅ Good mobile app

**Cons:**
- ❌ Requires Discord account
- ❌ Less suited for notifications (more for chat)
- ❌ Webhook URLs can be stolen if exposed

**Best for:** If you already use Discord

**Setup time:** 2 minutes

### Email

**Pros:**
- ✅ Universal (everyone has email)
- ✅ Built-in image support
- ✅ No special setup

**Cons:**
- ❌ Slower (can take 30+ seconds)
- ❌ Might go to spam
- ❌ Not real-time
- ❌ Large images might be blocked

**Best for:** Non-technical users, backup notifications

**Setup time:** 1 minute

### Push Notifications (APNs/FCM)

**Pros:**
- ✅ Native mobile experience
- ✅ Works even if app is closed
- ✅ System-level notifications

**Cons:**
- ❌ Complex setup
- ❌ Requires mobile app
- ❌ Apple/Google approval
- ❌ Separate implementation per platform
- ❌ Costs money for service

**Best for:** Production apps, not personal projects

**Setup time:** Days/weeks

### Webhooks (Generic)

**Pros:**
- ✅ Flexible
- ✅ Integrate with anything
- ✅ Home Assistant, IFTTT, Zapier, etc.

**Cons:**
- ❌ Requires webhook endpoint
- ❌ Need to handle receiving side

**Best for:** Home automation, custom integrations

**Setup time:** Varies

### SMS

**Pros:**
- ✅ Works everywhere
- ✅ No app needed

**Cons:**
- ❌ Costs money per message
- ❌ No images (or expensive MMS)
- ❌ Rate limits
- ❌ Requires Twilio/similar service

**Best for:** Critical alerts only, not regular use

**Setup time:** 10 minutes + costs money

## Our Recommendation: Telegram

**Why Telegram:**

1. **Free and fast** - No costs, instant delivery
2. **Easy setup** - 5 minutes to create bot
3. **Perfect for images** - Sends photos instantly
4. **No limits** - Won't throttle personal use
5. **Cross-platform** - Works on phone, desktop, web
6. **Private** - Create bot just for you
7. **Reliable** - Used by millions worldwide

**Setup:** See `TELEGRAM_SETUP.md`

## Storage Management

### Auto-Delete Strategy (Implemented)

```python
NotificationManager(
    max_images=100  # Keep only last 100 images
)
```

**How it works:**
1. Save new image
2. Check total image count
3. If > max_images, delete oldest
4. Always have recent history, never fill disk

### Manual Management

Check storage:
```bash
du -sh snapshots/
# Output: 8.5M   snapshots/
```

Delete old images:
```bash
# Delete images older than 7 days
find snapshots/ -name "*.jpg" -mtime +7 -delete
```

### Cloud Backup (Optional)

Upload to cloud for permanent storage:

```bash
# Sync to cloud (requires setup)
rclone sync snapshots/ mydrive:pet_camera/
```

Options:
- Google Drive (15GB free)
- Dropbox (2GB free)
- iCloud (5GB free)
- Backblaze B2 (10GB free)

## Example Configurations

### Configuration 1: Work From Home Monitoring
```python
# Check on pets while in meetings
NotificationManager(
    cooldown_seconds=600,      # Every 10 minutes max
    persistence_frames=10,     # Very confident
    save_images=True,
    max_images=30              # Just during work day
)
```

### Configuration 2: Security Monitoring
```python
# Alert when anyone detected
NotificationManager(
    cooldown_seconds=60,       # Quick alerts
    persistence_frames=3,      # Balance speed/accuracy
    save_images=True,
    max_images=200             # Keep more history
)

# Only notify for people, not cats
notify_on = ['person']
```

### Configuration 3: Cat Activity Log
```python
# Track when cats are active
NotificationManager(
    cooldown_seconds=1800,     # Every 30 minutes
    persistence_frames=10,
    save_images=True,
    max_images=48              # 24 hours at 30min intervals
)
```

### Configuration 4: Debugging/Testing
```python
# See all detections while testing
NotificationManager(
    cooldown_seconds=10,       # Very short
    persistence_frames=1,      # Immediate
    save_images=True,
    max_images=1000            # Keep everything
)
```

## Summary

**Best Setup for Most Users:**

- **Platform**: Telegram
- **Cooldown**: 5 minutes (300 seconds)
- **Persistence**: 5 frames
- **Storage**: Images only
- **Max images**: 50-100
- **Notify on**: State changes only

This gives you:
- ✅ Instant mobile notifications
- ✅ Minimal false positives
- ✅ Won't spam you
- ✅ Images for context
- ✅ ~5-10 MB storage total
- ✅ Free forever

**Don't:**
- ❌ Notify on every frame (30 FPS = phone explosion)
- ❌ Save videos continuously (fills disk instantly)
- ❌ Use SMS (costs money, no images)
- ❌ Set cooldown < 60 seconds (too spammy)

**Next Steps:**
1. Read `TELEGRAM_SETUP.md` to create bot (5 min)
2. Run camera with notifications enabled
3. Adjust cooldown based on preference
4. Enjoy smart pet monitoring! 🐱

#!/usr/bin/env python3
"""
Smart Notification System
Handles detection notifications with cooldown, persistence, and storage management
"""

import time
import cv2
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import json


class NotificationManager:
    """
    Manages smart notifications for pet detections

    Features:
    - State change detection (only notify when something appears/disappears)
    - Cooldown periods (don't spam)
    - Persistence checking (require N consecutive frames)
    - Storage management (auto-delete old images)
    """

    def __init__(
        self,
        cooldown_seconds=300,      # 5 minutes between notifications for same detection
        persistence_frames=5,       # Require 5 consecutive frames to confirm
        save_images=True,
        image_dir="snapshots",
        max_images=100,             # Keep only last 100 images
        platforms=None              # List of notification platforms to use
    ):
        """
        Initialize notification manager

        Args:
            cooldown_seconds: Minimum seconds between notifications for same subject
            persistence_frames: Frames needed to confirm detection (reduces false positives)
            save_images: Whether to save detection snapshots
            image_dir: Directory to save images
            max_images: Maximum images to keep (oldest deleted first)
            platforms: List of NotificationPlatform objects
        """
        self.cooldown_seconds = cooldown_seconds
        self.persistence_frames = persistence_frames
        self.save_images = save_images
        self.image_dir = Path(image_dir)
        self.max_images = max_images
        self.platforms = platforms or []

        # State tracking
        self.last_notification = defaultdict(lambda: datetime.min)  # Last notification time per subject
        self.current_state = set()                                   # Currently detected subjects
        self.detection_streak = defaultdict(int)                     # Consecutive frames per subject
        self.pending_notifications = []                              # Queue of pending notifications

        # Create image directory
        if self.save_images:
            self.image_dir.mkdir(exist_ok=True)

    def process_detections(self, frame, detections):
        """
        Process current frame detections and decide what to notify

        Args:
            frame: Current video frame
            detections: List of detection dicts with 'label', 'confidence', 'type'

        Returns:
            List of notification messages that should be sent
        """
        current_frame_subjects = set()
        notifications = []

        # Extract unique subjects from detections
        for det in detections:
            # Create subject key (e.g., "miso", "ozzy", "person")
            subject = det['label'].lower()
            current_frame_subjects.add(subject)

            # Update detection streak
            self.detection_streak[subject] += 1

            # Check if detection is persistent enough (reduces false positives)
            if self.detection_streak[subject] >= self.persistence_frames:
                # Check if this is a NEW detection (state change)
                if subject not in self.current_state:
                    # Check cooldown period
                    if self._is_cooled_down(subject):
                        # This is a new, confirmed detection - notify!
                        message = self._create_notification(subject, det)
                        image_path = None

                        if self.save_images:
                            image_path = self._save_snapshot(frame, subject, detections)

                        notifications.append({
                            'subject': subject,
                            'message': message,
                            'image_path': image_path,
                            'detection': det
                        })

                        # Update last notification time
                        self.last_notification[subject] = datetime.now()

                        # Update current state
                        self.current_state.add(subject)

        # Reset streak for subjects not detected this frame
        for subject in list(self.detection_streak.keys()):
            if subject not in current_frame_subjects:
                self.detection_streak[subject] = 0

                # If subject was present but now gone, remove from current state
                # (optional: notify when they leave)
                if subject in self.current_state:
                    self.current_state.remove(subject)

        return notifications

    def _is_cooled_down(self, subject):
        """Check if enough time has passed since last notification"""
        time_since_last = datetime.now() - self.last_notification[subject]
        return time_since_last.total_seconds() >= self.cooldown_seconds

    def _create_notification(self, subject, detection):
        """Create notification message"""
        confidence = detection['confidence']
        timestamp = datetime.now().strftime("%I:%M %p")

        # Custom messages based on subject
        if subject == 'miso':
            message = f"🐱 Miso detected! ({confidence:.0%} confident) at {timestamp}"
        elif subject == 'ozzy':
            message = f"🐱 Ozzy detected! ({confidence:.0%} confident) at {timestamp}"
        elif subject == 'person':
            message = f"👤 Person detected! ({confidence:.0%} confident) at {timestamp}"
        else:
            message = f"🔍 {subject.capitalize()} detected! ({confidence:.0%} confident) at {timestamp}"

        return message

    def _save_snapshot(self, frame, subject, detections):
        """
        Save snapshot with detection boxes drawn

        Args:
            frame: Video frame
            subject: Main subject that triggered notification
            detections: All detections to draw

        Returns:
            Path to saved image
        """
        # Create annotated frame copy
        snapshot = frame.copy()

        # Draw all detections
        from camera import PetCamera
        camera = PetCamera.__new__(PetCamera)  # Get instance for drawing method
        camera.colors = {
            'person': (0, 200, 255),
            'miso': (255, 100, 255),
            'ozzy': (255, 150, 0)
        }

        for det in detections:
            camera._draw_detection(
                snapshot,
                det['box'],
                det['label'],
                det['confidence'],
                det['color']
            )

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{subject}_{timestamp}.jpg"
        filepath = self.image_dir / filename

        # Save with compression
        cv2.imwrite(str(filepath), snapshot, [cv2.IMWRITE_JPEG_QUALITY, 85])

        # Manage storage
        self._cleanup_old_images()

        return filepath

    def _cleanup_old_images(self):
        """Delete oldest images if we exceed max_images limit"""
        if not self.save_images:
            return

        # Get all images sorted by creation time
        images = sorted(self.image_dir.glob("*.jpg"), key=lambda p: p.stat().st_ctime)

        # Delete oldest if we exceed limit
        while len(images) > self.max_images:
            oldest = images.pop(0)
            oldest.unlink()

    async def send_notification(self, notification):
        """
        Send notification to all configured platforms

        Args:
            notification: Notification dict with 'subject', 'message', 'image_path'
        """
        for platform in self.platforms:
            try:
                await platform.send(
                    message=notification['message'],
                    image_path=notification.get('image_path')
                )
            except Exception as e:
                print(f"⚠️  Failed to send notification via {platform.name}: {e}")

    def get_stats(self):
        """Get notification statistics"""
        return {
            'total_subjects_seen': len(self.last_notification),
            'currently_detected': list(self.current_state),
            'images_saved': len(list(self.image_dir.glob("*.jpg"))) if self.save_images else 0,
            'last_notifications': {
                subject: time.strftime("%I:%M %p", time.localtime(self.last_notification[subject].timestamp()))
                for subject in self.last_notification
                if self.last_notification[subject] != datetime.min
            }
        }


class NotificationPlatform:
    """Base class for notification platforms"""

    def __init__(self, name):
        self.name = name

    async def send(self, message, image_path=None):
        """Send notification (override in subclasses)"""
        raise NotImplementedError


class TelegramNotifier(NotificationPlatform):
    """Send notifications via Telegram bot"""

    def __init__(self, bot_token, chat_id):
        """
        Initialize Telegram notifier

        Args:
            bot_token: Telegram bot token from @BotFather
            chat_id: Your Telegram chat ID (get from @userinfobot)
        """
        super().__init__("Telegram")
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    async def send(self, message, image_path=None):
        """Send message and optional image to Telegram"""
        import aiohttp

        async with aiohttp.ClientSession() as session:
            if image_path:
                # Send photo with caption
                url = f"{self.base_url}/sendPhoto"
                with open(image_path, 'rb') as photo:
                    data = aiohttp.FormData()
                    data.add_field('chat_id', self.chat_id)
                    data.add_field('caption', message)
                    data.add_field('photo', photo)

                    async with session.post(url, data=data) as response:
                        if response.status != 200:
                            raise Exception(f"Telegram API error: {await response.text()}")
            else:
                # Send text message only
                url = f"{self.base_url}/sendMessage"
                data = {
                    'chat_id': self.chat_id,
                    'text': message
                }
                async with session.post(url, json=data) as response:
                    if response.status != 200:
                        raise Exception(f"Telegram API error: {await response.text()}")


class DiscordNotifier(NotificationPlatform):
    """Send notifications via Discord webhook"""

    def __init__(self, webhook_url):
        """
        Initialize Discord notifier

        Args:
            webhook_url: Discord webhook URL
        """
        super().__init__("Discord")
        self.webhook_url = webhook_url

    async def send(self, message, image_path=None):
        """Send message and optional image to Discord"""
        import aiohttp

        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field('content', message)

            if image_path:
                with open(image_path, 'rb') as image:
                    data.add_field('file', image, filename=image_path.name)

            async with session.post(self.webhook_url, data=data) as response:
                if response.status not in [200, 204]:
                    raise Exception(f"Discord webhook error: {await response.text()}")


class WebhookNotifier(NotificationPlatform):
    """Send notifications to custom webhook"""

    def __init__(self, webhook_url, headers=None):
        """
        Initialize webhook notifier

        Args:
            webhook_url: URL to POST notifications to
            headers: Optional dict of HTTP headers
        """
        super().__init__("Webhook")
        self.webhook_url = webhook_url
        self.headers = headers or {}

    async def send(self, message, image_path=None):
        """Send notification to webhook"""
        import aiohttp
        import base64

        async with aiohttp.ClientSession() as session:
            payload = {
                'message': message,
                'timestamp': datetime.now().isoformat()
            }

            if image_path:
                # Encode image as base64
                with open(image_path, 'rb') as image:
                    payload['image'] = base64.b64encode(image.read()).decode('utf-8')
                    payload['image_filename'] = image_path.name

            async with session.post(
                self.webhook_url,
                json=payload,
                headers=self.headers
            ) as response:
                if response.status not in [200, 201, 202]:
                    raise Exception(f"Webhook error: {await response.text()}")


class ConsoleNotifier(NotificationPlatform):
    """Print notifications to console (for testing)"""

    def __init__(self):
        super().__init__("Console")

    async def send(self, message, image_path=None):
        """Print notification to console"""
        print(f"\n🔔 NOTIFICATION: {message}")
        if image_path:
            print(f"   📷 Image saved: {image_path}")

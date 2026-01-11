#!/usr/bin/env python3
"""
Pet Camera - Real-time pet monitoring with custom recognition
Detects your specific pets by name plus people
"""

import cv2
import argparse
from ultralytics import YOLO
import torch
from pathlib import Path
import time


class PetCamera:
    """Real-time pet detection camera with custom cat recognition"""

    def __init__(self, camera_index=0, confidence=0.5, device=None, skip_frames=0):
        """
        Initialize the pet camera

        Args:
            camera_index: Camera device index (0 = default webcam)
            confidence: Detection confidence threshold (0.0-1.0)
            device: Force specific device ('mps', 'cuda', 'cpu') or None for auto
            skip_frames: Skip N frames between detections for better performance
        """
        self.camera_index = camera_index
        self.confidence = confidence
        self.skip_frames = skip_frames
        self.frame_counter = 0

        # Model file paths
        self.cat_model_path = "models/cat_detector.pt"
        self.people_model_path = "yolo11n.pt"

        # Auto-detect best available device
        if device is None:
            if torch.cuda.is_available():
                self.device = "cuda"
            elif torch.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"
        else:
            self.device = device

        # Detection colors (BGR format for OpenCV)
        # Generate colors for detected pet names dynamically
        self.colors = {
            'person': (0, 200, 255),      # Orange
            'background': (128, 128, 128)  # Gray (not displayed)
        }
        # Default colors for pets (will be used if not specified)
        self.default_pet_colors = [
            (255, 100, 255),  # Pink
            (255, 150, 0),    # Blue
            (100, 255, 100),  # Green
            (200, 100, 255),  # Purple
            (100, 200, 255),  # Light blue
            (255, 200, 100),  # Yellow
        ]

        # Performance tracking
        self.fps = 0
        self.last_time = time.time()
        self.inference_time = 0
        self.last_detections = []

        # Track pet names for dynamic color assignment
        self.pet_color_index = 0

        # Initialize
        self._print_startup_info()
        self._load_models()
        self._open_camera()

    def _get_color_for_label(self, label):
        """Get color for a label, assigning new colors as needed"""
        label_lower = label.lower()

        # Return existing color if already assigned
        if label_lower in self.colors:
            return self.colors[label_lower]

        # Assign new color for new pet
        color = self.default_pet_colors[self.pet_color_index % len(self.default_pet_colors)]
        self.colors[label_lower] = color
        self.pet_color_index += 1

        return color

    def _print_startup_info(self):
        """Print startup information"""
        print(f"🚀 Starting Pet Camera")
        print(f"   Device: {self.device.upper()}")
        print(f"   Confidence: {self.confidence}")
        if self.skip_frames > 0:
            print(f"   Performance mode: Process every {self.skip_frames + 1} frames")

    def _load_models(self):
        """Load detection models"""
        # Load custom cat model
        cat_model_file = Path(self.cat_model_path)
        if not cat_model_file.exists():
            raise RuntimeError(
                f"Cat model not found: {self.cat_model_path}\n"
                f"Train it first: python3 scripts/train.py"
            )

        print(f"📦 Loading cat detector...")
        self.cat_model = YOLO(self.cat_model_path)
        self.cat_model.to(self.device)

        cat_classes = list(self.cat_model.names.values())
        print(f"   Classes: {', '.join(cat_classes)}")

        # Load generic people detector
        print(f"📦 Loading people detector...")
        self.people_model = YOLO(self.people_model_path)
        self.people_model.to(self.device)

        print(f"✅ Models ready")

    def _open_camera(self):
        """Open and configure camera"""
        print(f"📷 Opening camera {self.camera_index}...")
        self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera {self.camera_index}")

        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        print(f"✅ Camera ready")
        print(f"\n🎥 Press 'Q' to quit\n")

    def _draw_detection(self, frame, box, label, confidence, color):
        """
        Draw a detection box with label

        Args:
            frame: Image frame to draw on
            box: Bounding box coordinates [x1, y1, x2, y2]
            label: Detection label text
            confidence: Detection confidence (0-1)
            color: Box color in BGR format
        """
        x1, y1, x2, y2 = map(int, box)

        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        # Prepare label text
        label_text = f"{label} {confidence:.0%}"

        # Measure text size
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2
        (text_w, text_h), baseline = cv2.getTextSize(
            label_text, font, font_scale, thickness
        )

        # Draw solid background for text
        cv2.rectangle(
            frame,
            (x1, y1 - text_h - baseline - 8),
            (x1 + text_w + 8, y1),
            color,
            -1  # Filled rectangle
        )

        # Draw text in black for better visibility
        cv2.putText(
            frame,
            label_text,
            (x1 + 4, y1 - baseline - 4),
            font,
            font_scale,
            (0, 0, 0),  # Black text on colored background
            thickness
        )

    def _detect(self, frame):
        """
        Run detection on a frame

        Args:
            frame: Input image frame

        Returns:
            List of detections, each with 'box', 'label', 'confidence', 'color', 'type'
        """
        # Skip frames for performance if configured
        self.frame_counter += 1
        if self.skip_frames > 0 and self.frame_counter % (self.skip_frames + 1) != 0:
            return self.last_detections

        start_time = time.time()
        detections = []

        # Run inference without computing gradients (saves memory)
        with torch.no_grad():
            # Detect cats with custom model
            cat_results = self.cat_model(
                frame,
                verbose=False,
                device=self.device,
                conf=self.confidence  # Filter low-confidence detections early
            )[0]

            # Process cat detections
            for box in cat_results.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = self.cat_model.names[class_id]

                # Skip background class
                if class_name != 'background':
                    detections.append({
                        'box': box.xyxy[0].cpu().numpy(),
                        'label': class_name.capitalize(),
                        'confidence': confidence,
                        'color': self._get_color_for_label(class_name),
                        'type': 'pet'
                    })

            # Detect people with generic model
            people_results = self.people_model(
                frame,
                verbose=False,
                device=self.device,
                conf=self.confidence,
                classes=[0]  # Only detect person class from COCO dataset
            )[0]

            # Process people detections
            for box in people_results.boxes:
                confidence = float(box.conf[0])
                detections.append({
                    'box': box.xyxy[0].cpu().numpy(),
                    'label': 'Person',
                    'confidence': confidence,
                    'color': self.colors['person'],
                    'type': 'person'
                })

        # Cache detections for skipped frames
        self.last_detections = detections

        # Track inference time
        self.inference_time = time.time() - start_time

        return detections

    def _draw_overlay(self, frame, detections):
        """
        Draw information overlay on frame

        Args:
            frame: Image frame to draw on
            detections: List of current detections
        """
        # Count detections by type
        pets = [d['label'] for d in detections if d['type'] == 'pet']
        people_count = sum(1 for d in detections if d['type'] == 'person')

        # Build status text
        status_parts = []
        if pets:
            status_parts.append(f"Pets: {', '.join(pets)}")
        if people_count > 0:
            status_parts.append(f"People: {people_count}")

        status = " | ".join(status_parts) if status_parts else "No detections"

        # Add performance metrics
        status += f" | {self.fps:.1f} FPS | {self.inference_time*1000:.0f}ms | {self.device.upper()}"

        # Draw status bar with background
        cv2.rectangle(frame, (0, 0), (frame.shape[1], 35), (0, 0, 0), -1)
        cv2.putText(
            frame, status, (10, 23),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
        )

        # Draw instructions at bottom
        instructions = "Press 'Q' to quit"
        cv2.putText(
            frame, instructions, (10, frame.shape[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1
        )

    def run(self):
        """Main camera loop"""
        frame_count = 0
        total_detections = 0
        fps_counter = 0
        fps_start_time = time.time()

        try:
            while True:
                # Read frame from camera
                ret, frame = self.cap.read()
                if not ret:
                    print("❌ Cannot read from camera")
                    break

                # Detect objects in frame
                detections = self._detect(frame)

                # Draw all detections
                for det in detections:
                    self._draw_detection(
                        frame,
                        det['box'],
                        det['label'],
                        det['confidence'],
                        det['color']
                    )

                # Draw information overlay
                self._draw_overlay(frame, detections)

                # Update statistics
                total_detections += len(detections)
                frame_count += 1
                fps_counter += 1

                # Calculate FPS every second
                if time.time() - fps_start_time >= 1.0:
                    self.fps = fps_counter / (time.time() - fps_start_time)
                    fps_counter = 0
                    fps_start_time = time.time()

                # Show frame
                cv2.imshow("Pet Camera", frame)

                # Check for quit key
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == ord('Q'):
                    print("\n👋 Stopping camera...")
                    break

        except KeyboardInterrupt:
            print("\n👋 Interrupted")

        finally:
            # Clean up
            self.cap.release()
            cv2.destroyAllWindows()

            # Print session summary
            print(f"\n📊 Session Summary:")
            print(f"   Frames processed: {frame_count}")
            print(f"   Total detections: {total_detections}")
            if frame_count > 0:
                print(f"   Average per frame: {total_detections / frame_count:.2f}")
            print(f"   Final FPS: {self.fps:.1f}")
            print(f"   Inference time: {self.inference_time*1000:.0f}ms")


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description="Pet Camera - Detect Miso, Ozzy, and people"
    )
    parser.add_argument(
        "--camera", type=int, default=0,
        help="Camera device index (default: 0)"
    )
    parser.add_argument(
        "--confidence", type=float, default=0.5,
        help="Detection confidence threshold 0.0-1.0 (default: 0.5)"
    )
    parser.add_argument(
        "--device", choices=["cuda", "mps", "cpu"],
        help="Force specific device (default: auto-detect)"
    )
    parser.add_argument(
        "--skip-frames", type=int, default=0,
        help="Skip N frames between detections for performance (default: 0)"
    )

    args = parser.parse_args()

    # Validate confidence
    if not 0.0 <= args.confidence <= 1.0:
        print("❌ Confidence must be between 0.0 and 1.0")
        return

    try:
        # Start camera
        camera = PetCamera(
            camera_index=args.camera,
            confidence=args.confidence,
            device=args.device,
            skip_frames=args.skip_frames
        )
        camera.run()

    except RuntimeError as e:
        print(f"❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("   - Check camera permissions")
        print("   - Try different camera: --camera 1")
        print("   - Ensure model is trained: python3 scripts/train.py")

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

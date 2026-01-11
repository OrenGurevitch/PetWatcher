#!/usr/bin/env python3
"""
Model Training Script
Trains custom cat detection model with experiment tracking
"""

import comet_ml
from ultralytics import YOLO
from pathlib import Path
import shutil
import os
import sys


def train():
    """
    Train cat recognition model with Comet ML tracking

    Trains a YOLO model to detect:
    - background (negative examples)
    - miso (gray cat)
    - ozzy (black cat)

    Requires COMET_API_KEY environment variable
    """

    print("=" * 70)
    print("🐱 MODEL TRAINING")
    print("=" * 70)

    # Check for Comet API key
    comet_api_key = os.environ.get('COMET_API_KEY')
    comet_project = os.environ.get('COMET_PROJECT_NAME', 'miso-ozzy-detector')
    comet_workspace = os.environ.get('COMET_WORKSPACE')

    if not comet_api_key:
        print("\n❌ ERROR: COMET_API_KEY environment variable not set!")
        print("\n📖 Setup Instructions:")
        print("   1. Go to: https://www.comet.com/api/my/settings/")
        print("   2. Copy your API key")
        print("   3. Run: export COMET_API_KEY='your-api-key-here'")
        print("\nOptional:")
        print("   export COMET_WORKSPACE='your-workspace'")
        print("   export COMET_PROJECT_NAME='miso-ozzy-detector'\n")
        sys.exit(1)

    print("\n✅ Comet ML Configuration:")
    print(f"   Project: {comet_project}")
    if comet_workspace:
        print(f"   Workspace: {comet_workspace}")

    print("\n⚙️  Training Configuration:")
    print("   Classes: background, miso, ozzy")
    print("   Dataset: cat_dataset/")
    print("   Epochs: 200")
    print("   Batch: 8")
    print("   Patience: 50")
    print("   Device: Auto-detect (MPS/CUDA/CPU)")

    # Initialize Comet experiment
    print("\n🔬 Initializing Comet ML experiment...")

    # Set environment variables for Ultralytics integration
    os.environ['COMET_PROJECT_NAME'] = comet_project
    if comet_workspace:
        os.environ['COMET_WORKSPACE'] = comet_workspace

    # Load pre-trained model
    print("\n📦 Loading YOLOv11-nano...")
    model = YOLO("yolo11n.pt")
    print("✅ Model loaded")

    # Training configuration
    train_config = {
        'data': 'cat_dataset/data.yaml',
        'epochs': 200,
        'imgsz': 640,
        'batch': 8,
        'patience': 50,

        # Performance
        'workers': 8,
        'cache': True,

        # Augmentation (moderate for small dataset)
        'hsv_h': 0.015,
        'hsv_s': 0.7,
        'hsv_v': 0.4,
        'degrees': 10.0,
        'translate': 0.1,
        'scale': 0.5,
        'flipud': 0.0,
        'fliplr': 0.5,

        # Settings
        'optimizer': 'auto',
        'verbose': True,
        'save': True,
        'plots': True,

        # Organization
        'project': 'runs/cat_train',
        'name': 'miso_ozzy_comet',
        'exist_ok': True
    }

    # Train with Comet ML
    print("\n🚀 Starting training with Comet ML tracking...\n")
    print("📊 View live training at: https://www.comet.com/")
    print("   Your experiment will appear in the dashboard\n")

    results = model.train(**train_config)

    print("\n" + "=" * 70)
    print("🎉 TRAINING COMPLETE!")
    print("=" * 70)

    # Find best model
    best_model = Path('runs/cat_train/miso_ozzy_comet/weights/best.pt')

    if best_model.exists():
        # Copy to models folder
        models_dir = Path('models')
        models_dir.mkdir(exist_ok=True)

        dest = models_dir / 'cat_detector.pt'
        shutil.copy2(best_model, dest)

        print(f"\n✅ Model saved to: {dest}")
        print(f"   Training results: runs/cat_train/miso_ozzy_comet/")

        # Validation results
        print(f"\n📊 Final Metrics:")
        if hasattr(results, 'results_dict'):
            metrics = results.results_dict
            if 'metrics/mAP50(B)' in metrics:
                print(f"   mAP50: {metrics['metrics/mAP50(B)']:.3f}")
            if 'metrics/mAP50-95(B)' in metrics:
                print(f"   mAP50-95: {metrics['metrics/mAP50-95(B)']:.3f}")
            if 'metrics/precision(B)' in metrics:
                print(f"   Precision: {metrics['metrics/precision(B)']:.3f}")
            if 'metrics/recall(B)' in metrics:
                print(f"   Recall: {metrics['metrics/recall(B)']:.3f}")

        print(f"\n💡 Next steps:")
        print(f"   1. View results in Comet ML dashboard")
        print(f"   2. Check local results: runs/cat_train/miso_ozzy_comet/results.png")
        print(f"   3. Run hybrid cam: python hybrid_cam.py")
        print(f"\n🔬 Comet ML Dashboard: https://www.comet.com/{comet_workspace}/{comet_project}")

        return str(dest)
    else:
        print("\n⚠️  Model not found at expected location")
        return None


if __name__ == "__main__":
    train()

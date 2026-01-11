#!/usr/bin/env python3
"""
Dataset Annotation Script
Auto-annotates cat images using pre-trained YOLO model

Creates training dataset with:
- background: Images without cats (negative examples)
- miso: Gray cat
- ozzy: Black cat
"""

import os
import cv2
from pathlib import Path
from ultralytics import YOLO
import shutil


class CatAnnotator:
    """Annotate cats with proper background class"""

    def __init__(self):
        self.data_dir = Path("data")
        self.model = YOLO("yolo11n.pt")
        self.class_mapping = {}
        self.class_names = []

        print("🚀 Cat-Only Annotator")
        print("   Will create: background, miso, ozzy")

    def setup_dataset(self):
        """Create clean dataset structure"""
        dataset_root = Path("cat_dataset")

        # Remove old if exists
        if dataset_root.exists():
            shutil.rmtree(dataset_root)

        # Create new
        for split in ['train', 'val']:
            (dataset_root / 'images' / split).mkdir(parents=True, exist_ok=True)
            (dataset_root / 'labels' / split).mkdir(parents=True, exist_ok=True)

        print(f"✅ Created dataset at: {dataset_root.absolute()}")
        return dataset_root

    def discover_classes(self):
        """Discover cat classes + background"""
        # Hardcode to ensure correct order
        folders = ['background', 'miso', 'ozzy']

        for idx, folder in enumerate(folders):
            folder_path = self.data_dir / folder
            if not folder_path.exists():
                raise ValueError(f"Missing folder: {folder_path}")

            img_count = len(list(folder_path.glob('*.jp*g')))
            self.class_mapping[folder] = idx
            self.class_names.append(folder)
            print(f"   Class {idx}: '{folder}' ({img_count} images)")

    def annotate_image(self, image_path, class_name):
        """Annotate single image"""
        img = cv2.imread(str(image_path))
        if img is None:
            return None

        height, width = img.shape[:2]

        # Background class - no boxes, just empty label file
        if class_name == 'background':
            return []  # Empty annotations = background

        # For cats, detect them
        results = self.model(img, verbose=False)[0]
        annotations = []

        for box in results.boxes:
            detected_class = int(box.cls[0])
            confidence = float(box.conf[0])

            # Only annotate cats (class 15 in COCO)
            if detected_class == 15 and confidence >= 0.3:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

                # Convert to YOLO format
                x_center = ((x1 + x2) / 2) / width
                y_center = ((y1 + y2) / 2) / height
                box_width = (x2 - x1) / width
                box_height = (y2 - y1) / height

                # Get class ID
                class_id = self.class_mapping[class_name]

                annotations.append(f"{class_id} {x_center:.6f} {y_center:.6f} {box_width:.6f} {box_height:.6f}")

        return annotations if annotations else None

    def process_all(self, train_split=0.8):
        """Process all images"""
        dataset_root = self.setup_dataset()
        self.discover_classes()

        print(f"\n🔍 Processing images (train/val: {train_split:.0%}/{(1-train_split):.0%})...\n")

        total_annotated = 0
        total_skipped = 0

        for class_name in self.class_names:
            class_dir = self.data_dir / class_name
            image_files = sorted(list(class_dir.glob('*.jp*g')))

            print(f"📂 {class_name}: {len(image_files)} images")

            split_idx = int(len(image_files) * train_split)
            annotated = 0
            skipped = 0

            for idx, image_path in enumerate(image_files):
                split = 'train' if idx < split_idx else 'val'

                # Annotate
                annotations = self.annotate_image(image_path, class_name)

                # For background, empty annotations is OK
                if class_name == 'background':
                    annotations = []  # Force empty
                elif annotations is None:
                    skipped += 1
                    continue

                # Save
                new_filename = f"{class_name}_{image_path.name}"
                dest_image = dataset_root / 'images' / split / new_filename
                shutil.copy2(image_path, dest_image)

                label_filename = Path(new_filename).stem + '.txt'
                dest_label = dataset_root / 'labels' / split / label_filename

                if annotations:
                    dest_label.write_text('\n'.join(annotations))
                else:
                    dest_label.write_text('')  # Empty file for background

                annotated += 1

            total_annotated += annotated
            total_skipped += skipped

            train_count = len(list((dataset_root / 'images' / 'train').glob(f"{class_name}_*")))
            val_count = len(list((dataset_root / 'images' / 'val').glob(f"{class_name}_*")))

            print(f"   ✅ {annotated} processed ({train_count} train, {val_count} val)")
            if skipped > 0:
                print(f"   ⚠️  {skipped} skipped")

        # Create data.yaml
        self.create_yaml(dataset_root)

        print("\n" + "=" * 60)
        print("📊 SUMMARY")
        print("=" * 60)
        print(f"✅ Total processed: {total_annotated}")
        print(f"⚠️  Total skipped: {total_skipped}")
        print(f"\n📁 Dataset: {dataset_root.absolute()}/")
        print(f"   ├── images/train/ ({len(list((dataset_root / 'images' / 'train').glob('*')))} images)")
        print(f"   ├── images/val/ ({len(list((dataset_root / 'images' / 'val').glob('*')))} images)")
        print(f"   └── data.yaml")
        print("\n🎉 Ready for training!")

    def create_yaml(self, dataset_root):
        """Create YOLO config"""
        yaml_content = f"""# Cat-only detection with background class
# Auto-generated

path: {dataset_root.absolute()}
train: images/train
val: images/val

# Classes (background is class 0)
names:
"""
        for idx, name in enumerate(self.class_names):
            yaml_content += f"  {idx}: {name}\n"

        yaml_path = dataset_root / "data.yaml"
        yaml_path.write_text(yaml_content)
        print(f"✅ Created: {yaml_path}")


if __name__ == "__main__":
    annotator = CatAnnotator()
    annotator.process_all()

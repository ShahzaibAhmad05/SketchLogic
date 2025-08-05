import os
import json
import yaml
import shutil
from pathlib import Path
import numpy as np
from PIL import Image
import torch
from ultralytics import YOLO

from sklearn.model_selection import train_test_split

class LogicGatesDatasetConverter:
    """Convert logic gates dataset from JSON format to YOLO format"""
    
    def __init__(self, images_dir, annotations_dir, output_dir):
        self.images_dir = Path(images_dir)
        self.annotations_dir = Path(annotations_dir)
        self.output_dir = Path(output_dir)
        
        # Define class mappings for gate types and rotations
        self.gate_types = ['AND', 'OR', 'NOT', 'NAND', 'NOR', 'XOR', 'XNOR']
        self.rotations = [0, 90, 180, 270]
        
        # Create combined classes (gate_type + rotation)
        self.classes = []
        self.class_to_id = {}
        
        for gate_type in self.gate_types:
            for rotation in self.rotations:
                class_name = f"{gate_type}_{rotation}"
                self.classes.append(class_name)
                self.class_to_id[class_name] = len(self.classes) - 1
        
        print(f"Total classes: {len(self.classes)}")
        print(f"Classes: {self.classes}")
    
    def convert_bbox_to_yolo(self, bbox, img_width, img_height):
        """Convert bounding box from absolute coordinates to YOLO format (normalized)"""
        x, y, width, height = bbox['x'], bbox['y'], bbox['width'], bbox['height']
        
        # Calculate center coordinates
        center_x = x + width / 2
        center_y = y + height / 2
        
        # Normalize coordinates
        center_x_norm = center_x / img_width
        center_y_norm = center_y / img_height
        width_norm = width / img_width
        height_norm = height / img_height
        
        return center_x_norm, center_y_norm, width_norm, height_norm
    
    def determine_rotation(self, bbox, gate_type):
        """
        Determine rotation based on bounding box dimensions and gate type.
        This is a heuristic approach - you might need to adjust based on your data.
        """
        width, height = bbox['width'], bbox['height']
        aspect_ratio = width / height
        
        # Simple heuristic: assume standard orientation is horizontal
        # You may need to implement more sophisticated rotation detection
        # based on your actual gate images
        if abs(aspect_ratio - 1.0) < 0.2:  # Nearly square
            return 0  # Default rotation
        elif aspect_ratio > 1.2:  # Wide
            return 0  # Horizontal
        elif aspect_ratio < 0.8:  # Tall
            return 90  # Vertical
        else:
            return 0  # Default
    
    def convert_annotation(self, json_file, img_width, img_height):
        """Convert single JSON annotation to YOLO format"""
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        yolo_annotations = []
        
        for gate in data.get('gates', []):
            gate_type = gate['type']
            bbox = gate['bounding_box']
            
            # Determine rotation (you might need to implement this based on your data)
            rotation = self.determine_rotation(bbox, gate_type)
            
            # Create class name
            class_name = f"{gate_type}_{rotation}"
            
            if class_name not in self.class_to_id:
                print(f"Warning: Unknown class {class_name}, skipping...")
                continue
            
            class_id = self.class_to_id[class_name]
            
            # Convert bbox to YOLO format
            center_x, center_y, width, height = self.convert_bbox_to_yolo(
                bbox, img_width, img_height
            )
            
            yolo_annotations.append(f"{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}")
        
        return yolo_annotations
    
    def create_dataset_structure(self):
        """Create YOLO dataset directory structure"""
        dataset_dirs = [
            self.output_dir / 'images' / 'train',
            self.output_dir / 'images' / 'val',
            self.output_dir / 'labels' / 'train',
            self.output_dir / 'labels' / 'val'
        ]
        
        for dir_path in dataset_dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def convert_dataset(self, train_split=0.8):
        """Convert entire dataset from JSON to YOLO format"""
        print("Converting dataset to YOLO format...")
        
        # Create directory structure
        self.create_dataset_structure()
        
        # Get all image files
        image_files = list(self.images_dir.glob('*.png')) + list(self.images_dir.glob('*.jpg'))
        
        if not image_files:
            raise ValueError(f"No image files found in {self.images_dir}")
        
        print(f"Found {len(image_files)} images")
        
        # Split dataset
        train_files, val_files = train_test_split(
            image_files, train_size=train_split, random_state=42
        )
        
        print(f"Train set: {len(train_files)} images")
        print(f"Validation set: {len(val_files)} images")
        
        # Process training set
        self._process_split(train_files, 'train')
        
        # Process validation set
        self._process_split(val_files, 'val')
        
        # Create data.yaml file
        self.create_data_yaml()
        
        print("Dataset conversion completed!")
    
    def _process_split(self, files, split):
        """Process a data split (train/val)"""
        for img_file in files:
            # Get corresponding annotation file
            json_file = self.annotations_dir / f"{img_file.stem}.json"
            
            if not json_file.exists():
                print(f"Warning: No annotation found for {img_file.name}, skipping...")
                continue
            
            # Get image dimensions
            with Image.open(img_file) as img:
                img_width, img_height = img.size
            
            # Convert annotation
            yolo_annotations = self.convert_annotation(json_file, img_width, img_height)
            
            if not yolo_annotations:
                print(f"Warning: No valid annotations for {img_file.name}, skipping...")
                continue
            
            # Copy image
            dst_img = self.output_dir / 'images' / split / img_file.name
            shutil.copy2(img_file, dst_img)
            
            # Save YOLO annotation
            txt_file = self.output_dir / 'labels' / split / f"{img_file.stem}.txt"
            with open(txt_file, 'w') as f:
                f.write('\n'.join(yolo_annotations))
    
    def create_data_yaml(self):
        """Create data.yaml file for YOLO training"""
        data_config = {
            'path': str(self.output_dir.absolute()),
            'train': 'images/train',
            'val': 'images/val',
            'nc': len(self.classes),
            'names': self.classes
        }
        
        yaml_file = self.output_dir / 'data.yaml'
        with open(yaml_file, 'w') as f:
            yaml.dump(data_config, f, default_flow_style=False)
        
        print(f"Created data.yaml at {yaml_file}")

class LogicGatesTrainer:
    """YOLO v10 trainer for logic gates detection"""
    
    def __init__(self, data_yaml_path, model_size='n', output_dir='runs/train'):
        self.data_yaml_path = data_yaml_path
        self.model_size = model_size
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize model
        model_name = f'yolov10{model_size}.pt'  # n, s, m, l, x
        print(f"Loading YOLO v10 model: {model_name}")
        self.model = YOLO(model_name)
    
    def train(self, epochs=100, imgsz=640, batch_size=16, lr0=0.01, patience=50):
        """Train the YOLO v10 model"""
        print("Starting training...")
        
        # Training parameters - optimized for Google Colab free tier
        train_params = {
            'data': self.data_yaml_path,
            'epochs': epochs,
            'imgsz': imgsz,
            'batch': batch_size,
            'lr0': lr0,
            'patience': patience,
            'save': True,
            'save_period': 25,  # Save every 25 epochs to avoid too many checkpoints
            'project': str(self.output_dir),
            'name': 'logic_gates_detection',
            'exist_ok': True,
            'pretrained': True,
            'optimizer': 'AdamW',  # Good optimizer for small batch sizes
            'verbose': True,
            'seed': 42,
            'deterministic': False,  # Slightly faster training
            'single_cls': False,
            'rect': True,  # More efficient for Colab
            'cos_lr': True,  # Cosine learning rate scheduler
            'close_mosaic': 15,  # Close mosaic earlier for stability
            'resume': False,
            'amp': True,  # Essential for Colab GPU memory efficiency
            'fraction': 1.0,
            'profile': False,
            'freeze': None,
            'multi_scale': False,  # Disable for memory efficiency
            'overlap_mask': True,
            'mask_ratio': 4,
            'dropout': 0.1,  # Light regularization
            'val': True,
            'plots': True,
            'device': 'auto',
            'workers': 2,  # Reduced workers for Colab
            'cache': 'ram',  # Cache in RAM for faster access
            'copy_paste': 0.0,  # Disabled to save memory
            'mixup': 0.0,  # Disabled to save memory
            'hsv_h': 0.015,  # Light color augmentation
            'hsv_s': 0.3,  # Reduced saturation augmentation
            'hsv_v': 0.2,  # Reduced value augmentation
            'degrees': 15.0,  # Rotation augmentation (important for gate orientations)
            'translate': 0.1,  # Light translation
            'scale': 0.5,  # Scale augmentation
            'shear': 2.0,  # Shear augmentation
            'perspective': 0.0,  # Disabled perspective for efficiency
            'flipud': 0.5,  # Vertical flip
            'fliplr': 0.5,  # Horizontal flip
            'mosaic': 1.0,  # Keep mosaic for data diversity
            'erasing': 0.2,  # Reduced random erasing
            'crop_fraction': 1.0
        }
        
        # Start training
        results = self.model.train(**train_params)
        
        print("Training completed!")
        return results
    
    def save_best_model(self, save_path='best_model.pt'):
        """Save the best trained model"""
        # The best model is automatically saved during training
        # We'll copy it to the specified location
        
        best_model_path = self.output_dir / 'logic_gates_detection' / 'weights' / 'best.pt'
        
        if best_model_path.exists():
            shutil.copy2(best_model_path, save_path)
            print(f"Best model saved to: {save_path}")
            
            # Also save the last model
            last_model_path = self.output_dir / 'logic_gates_detection' / 'weights' / 'last.pt'
            if last_model_path.exists():
                last_save_path = save_path.replace('.pt', '_last.pt')
                shutil.copy2(last_model_path, last_save_path)
                print(f"Last model saved to: {last_save_path}")
        else:
            print(f"Warning: Best model not found at {best_model_path}")
    
    def validate(self):
        """Validate the trained model"""
        print("Running validation...")
        results = self.model.val()
        return results

def main():
    # Check if running on Google Colab
    try:
        import google.colab # type: ignore
        print("🚀 Running on Google Colab!")
    except ImportError:
        print("🖥️  Running on local machine")
    
    # Hardcoded configuration parameters - optimized for Google Colab
    class Config:
        images_dir = 'raw_data/images'  # Directory containing training images
        annotations_dir = 'raw_data/annotations'  # Directory containing JSON annotations
        output_dir = 'dataset_yolo'  # Output directory for YOLO format dataset
        model_size = 's'  # YOLO small model for Colab efficiency
        epochs = 150  # Reduced epochs for Colab time limits
        batch_size = 8  # Smaller batch size for Colab GPU memory
        imgsz = 416  # Smaller image size for faster training on Colab
        lr0 = 0.001  # Learning rate
        patience = 25  # Patience for early stopping
        train_split = 0.85  # 85% train, 15% validation
        skip_conversion = False  # Skip dataset conversion (use existing YOLO format)
    
    args = Config()
    
    # Convert dataset if not skipping
    if not args.skip_conversion:
        print("=" * 60)
        print("STEP 1: Converting dataset to YOLO format")
        print("=" * 60)
        
        converter = LogicGatesDatasetConverter(
            args.images_dir, 
            args.annotations_dir, 
            args.output_dir
        )
        converter.convert_dataset(train_split=args.train_split)
    
    # Train model
    print("\n" + "=" * 60)
    print("STEP 2: Training YOLO v10 model")
    print("=" * 60)
    
    data_yaml_path = Path(args.output_dir) / 'data.yaml'
    
    if not data_yaml_path.exists():
        raise FileNotFoundError(f"data.yaml not found at {data_yaml_path}")
    
    trainer = LogicGatesTrainer(
        data_yaml_path=str(data_yaml_path),
        model_size=args.model_size,
        output_dir='runs/train'
    )
    
    # Start training
    results = trainer.train(
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch_size=args.batch_size,
        lr0=args.lr0,
        patience=args.patience
    )
    
    # Save best model
    trainer.save_best_model('best_model.pt')
    
    # Run validation
    print("\n" + "=" * 60)
    print("STEP 3: Final validation")
    print("=" * 60)
    
    val_results = trainer.validate()
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"Best model saved as: best_model.pt")
    print(f"Training results saved in: runs/train/logic_gates_detection/")

if __name__ == "__main__":
    main()
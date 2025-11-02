#!/usr/bin/env python3
"""
Script to analyze and extract all plant classes from the Roboflow models
"""
from inference_sdk import InferenceHTTPClient
from dotenv import load_dotenv
import os
from PIL import Image
import io
import tempfile
import json

load_dotenv()

API_KEY = os.getenv("ROBOFLOW_API_KEY")
API_URL = os.getenv("ROBOFLOW_API_URL", "https://serverless.roboflow.com")

CLIENT = InferenceHTTPClient(
    api_url=API_URL,
    api_key=API_KEY
)

MODELS = [
    "herbal-plant-detection-1baib/9",
    "herbal-plants-yolo5v/2",
    "herbal-s6spz/3"
]

def get_model_classes():
    """Try to get available classes from each model"""
    all_classes = set()
    model_classes = {}
    
    # Create a test image
    test_img = Image.new('RGB', (640, 640), color='green')
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
        test_img.save(tmp_file, format="JPEG")
        tmp_file_path = tmp_file.name
    
    try:
        for model_id in MODELS:
            try:
                result = CLIENT.infer(tmp_file_path, model_id=model_id)
                
                # Extract classes from predictions
                model_class_set = set()
                if result and "predictions" in result:
                    predictions = result.get("predictions", [])
                    for pred in predictions:
                        class_name = pred.get("class", "")
                        if class_name:
                            model_class_set.add(class_name)
                            all_classes.add(class_name)
                
                # Check if model metadata has class info
                if "classes" in result:
                    classes = result.get("classes", [])
                    for cls in classes:
                        model_class_set.add(cls)
                        all_classes.add(cls)
                
                model_classes[model_id] = sorted(list(model_class_set))
                
                print(f"\nModel: {model_id}")
                print(f"  Classes found in predictions: {len(model_class_set)}")
                if model_class_set:
                    print(f"  Classes: {', '.join(sorted(model_class_set))}")
                else:
                    print(f"  (No classes detected in test image)")
                    
            except Exception as e:
                print(f"\nModel: {model_id}")
                print(f"  Error: {str(e)}")
                model_classes[model_id] = []
    finally:
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)
    
    return all_classes, model_classes

if __name__ == "__main__":
    print("🔍 Analyzing Roboflow models for plant classes...\n")
    print("Note: This may not show all classes - models only return predictions")
    print("for detected objects. To see all possible classes, check Roboflow dashboard.\n")
    
    all_classes, model_classes = get_model_classes()
    
    print("\n" + "="*60)
    print(f"📊 SUMMARY")
    print("="*60)
    print(f"Total unique plant classes detected: {len(all_classes)}")
    
    if all_classes:
        print(f"\nAll detected plant classes:")
        for i, plant in enumerate(sorted(all_classes), 1):
            print(f"  {i}. {plant}")
    else:
        print("\n⚠️  No classes detected in test image.")
        print("Models may need actual plant images to show predictions.")
        print("\n💡 To find all classes:")
        print("  1. Check your Roboflow dashboard for each model")
        print("  2. Upload various plant images to see detected classes")
        print("  3. Each model may have different plant classes")


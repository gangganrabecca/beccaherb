#!/usr/bin/env python3
"""
Simple test script to verify the detection endpoint
Requires: pip install requests pillow
"""
import requests
from PIL import Image
import io

# Create a simple test image (green rectangle to simulate a plant)
img = Image.new('RGB', (100, 100), color='green')
img_bytes = io.BytesIO()
img.save(img_bytes, format='JPEG')
img_bytes.seek(0)

# Test the endpoint
url = "http://localhost:8000/detect"
files = {'file': ('test_plant.jpg', img_bytes, 'image/jpeg')}

print("Testing detection endpoint...")
try:
    response = requests.post(url, files=files, timeout=30)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ Success!")
        print(f"Detected Plant: {data.get('detected_plant', 'N/A')}")
        print(f"Confidence: {data.get('confidence', 'N/A')}")
        print(f"Scientific Name: {data.get('scientific_name', 'N/A')}")
    else:
        print(f"\nResponse: {response.text}")
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")


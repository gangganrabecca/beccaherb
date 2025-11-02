from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from inference_sdk import InferenceHTTPClient
from PIL import Image
import io
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import base64
import tempfile
import json
from typing import Dict, List, Optional

# Load environment variables
load_dotenv()

app = FastAPI(title="Herbal Plant Detection API")

# Get the directory of the current script
BASE_DIR = Path(__file__).parent
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Ensure static directory exists
os.makedirs(STATIC_DIR, exist_ok=True)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Templates
templates = Jinja2Templates(directory=STATIC_DIR)

# Serve index.html for root path
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

# Roboflow client
API_KEY = os.getenv("ROBOFLOW_API_KEY")
API_URL = os.getenv("ROBOFLOW_API_URL", "https://serverless.roboflow.com")

CLIENT = InferenceHTTPClient(api_url=API_URL, api_key=API_KEY)

# Plant database with information
PLANT_DATABASE = {
    "aloe_vera": {
        "common_name": "Aloe Vera",
        "scientific_name": "Aloe barbadensis miller",
        "benefits": [
            "Soothes skin irritations and burns",
            "Promotes wound healing",
            "Hydrates skin and hair",
            "Helps with digestive issues",
            "Rich in antioxidants"
        ],
        "cautions": [
            "May cause allergic reactions in some people",
            "Not recommended for pregnant women",
            "Excessive consumption may cause diarrhea"
        ]
    },
    "mint": {
        "common_name": "Mint",
        "scientific_name": "Mentha",
        "benefits": [
            "Aids digestion",
            "Relieves headaches",
            "Freshens breath",
            "Helps with nausea",
            "Rich in antioxidants"
        ],
        "cautions": [
            "May cause heartburn in some people",
            "Should be used in moderation during pregnancy"
        ]
    },
    "basil": {
        "common_name": "Basil",
        "scientific_name": "Ocimum basilicum",
        "benefits": [
            "Reduces stress",
            "Rich in antioxidants",
            "Supports liver function",
            "Helps manage blood sugar levels"
        ],
        "cautions": [
            "May slow blood clotting",
            "Should be avoided before surgery"
        ]
    },
    "rosemary": {
        "common_name": "Rosemary",
        "scientific_name": "Rosmarinus officinalis",
        "benefits": [
            "Improves memory and concentration",
            "Stimulates hair growth",
            "Rich in antioxidants",
            "Aids digestion"
        ],
        "cautions": [
            "Not recommended in large amounts during pregnancy",
            "May cause allergic reactions in some people"
        ]
    },
    "thyme": {
        "common_name": "Thyme",
        "scientific_name": "Thymus vulgaris",
        "benefits": [
            "Boosts immune system",
            "Helps with respiratory issues",
            "Antibacterial properties",
            "Aids digestion"
        ],
        "cautions": [
            "May cause digestive issues in large amounts",
            "Should be used with caution by people with hormone-sensitive conditions"
        ]
    }
}

# Models
MODELS = [
    "herbal-plant-detection-1baib/9",
    "herbal-plants-yolo5v/2",
    "herbal-s6spz/3"
]

DETECTED_PLANTS_SET = set()

@app.get("/plants")
async def get_all_plants():
    """Get all detected plants and available models"""
    return {
        "total_plants_detected": len(DETECTED_PLANTS_SET),
        "plants": sorted([plant.title() for plant in DETECTED_PLANTS_SET]),
        "available_plants": list(PLANT_DATABASE.keys()),
        "models": MODELS
    }

@app.post("/detect")
async def detect_plant(file: UploadFile = File(...)):
    """
    Detect plants in an uploaded image and return plant information.
    
    Args:
        file: Uploaded image file
        
    Returns:
        JSON response with detection results and plant information
    """
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File provided is not an image.")

    try:
        # Read image file
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # Save to temporary file for inference
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            image.save(temp_file, format='JPEG')
            temp_file_path = temp_file.name

        # Perform inference
        try:
            # Try each model until we get a detection
            for model_id in MODELS:
                try:
                    result = CLIENT.infer(temp_file_path, model_id=model_id)
                    if result and 'predictions' in result and len(result['predictions']) > 0:
                        # Get the most confident prediction
                        prediction = max(result['predictions'], key=lambda x: x['confidence'])
                        plant_name = prediction['class'].lower()
                        
                        # Add to detected plants set
                        DETECTED_PLANTS_SET.add(plant_name)
                        
                        # Get plant information from our database
                        plant_info = PLANT_DATABASE.get(plant_name, {
                            "common_name": plant_name.title(),
                            "scientific_name": "Not available",
                            "benefits": ["No specific information available"],
                            "cautions": ["No specific cautions available"]
                        })
                        
                        # Prepare response
                        response = {
                            "status": "success",
                            "detected_plant": plant_name,
                            "confidence": round(prediction['confidence'] * 100, 2),
                            "plant_info": plant_info,
                            "image": f"data:image/jpeg;base64,{base64.b64encode(contents).decode('utf-8')}"
                        }
                        
                        # Clean up
                        os.unlink(temp_file_path)
                        return response
                        
                except Exception as e:
                    print(f"Error with model {model_id}: {str(e)}")
                    continue
            
            # If we get here, no detections were made
            raise HTTPException(status_code=404, detail="No plants detected in the image.")
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error during detection: {str(e)}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
    finally:
        # Clean up temp file if it still exists
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

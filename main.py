from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from inference_sdk import InferenceHTTPClient
from PIL import Image
import io
import os
from dotenv import load_dotenv
import base64
from typing import List, Dict, Optional
import json
import tempfile

# Load environment variables
load_dotenv()

app = FastAPI(title="Herbal Plant Detection API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Roboflow client
API_KEY = os.getenv("ROBOFLOW_API_KEY")
API_URL = os.getenv("ROBOFLOW_API_URL", "https://serverless.roboflow.com")

CLIENT = InferenceHTTPClient(
    api_url=API_URL,
    api_key=API_KEY
)

# Model IDs
MODELS = [
    "herbal-plant-detection-1baib/9",
    "herbal-plants-yolo5v/2",
    "herbal-s6spz/3"
]

# Track all detected plants (in-memory cache)
DETECTED_PLANTS_SET = set()

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/plants")
async def get_all_plants():
    """Get all unique plants that have been detected"""
    return {
        "total_plants_detected": len(DETECTED_PLANTS_SET),
        "plants": sorted([plant.title() for plant in DETECTED_PLANTS_SET]),
        "models": MODELS,
        "note": "This shows plants detected during runtime. For complete list, check Roboflow dashboard."
    }

@app.post("/detect")
async def detect_plant(file: UploadFile = File(...)):
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Read image file
        contents = await file.read()
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Empty file provided")
        
        try:
            image = Image.open(io.BytesIO(contents))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")
        
        # Convert to RGB if necessary
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        # Save image to a temporary file for inference
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            image.save(tmp_file, format="JPEG")
            tmp_file_path = tmp_file.name
        
        try:
            # Run inference on all models
            all_results = []
            detected_plant = None
            best_confidence = 0
            
            for model_id in MODELS:
                try:
                    result = CLIENT.infer(tmp_file_path, model_id=model_id)
                    all_results.append({
                        "model": model_id,
                        "result": result
                    })
                    
                    # Try to extract plant name and confidence
                    if result and "predictions" in result:
                        predictions = result.get("predictions", [])
                        if predictions:
                            best_pred = max(predictions, key=lambda x: x.get("confidence", 0))
                            confidence = best_pred.get("confidence", 0)
                            if confidence > best_confidence:
                                best_confidence = confidence
                                detected_plant = best_pred.get("class", "")
                except Exception as e:
                    print(f"Error with model {model_id}: {str(e)}")
                    continue
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
        
        if not detected_plant:
            return JSONResponse(
                status_code=404,
                content={
                    "error": "No plant detected",
                    "message": "Could not identify any herbal plant in the image. Please try another image."
                }
            )
        
        # Convert image to base64 for response
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="JPEG")
        img_bytes.seek(0)
        image_base64 = base64.b64encode(img_bytes.read()).decode("utf-8")
        
        # Track detected plant
        DETECTED_PLANTS_SET.add(detected_plant.lower())
        
        # Also track all classes from all predictions
        for model_result in all_results:
            result = model_result.get("result", {})
            predictions = result.get("predictions", [])
            for pred in predictions:
                class_name = pred.get("class", "")
                if class_name:
                    DETECTED_PLANTS_SET.add(class_name.lower())
        
        response = {
            "detected_plant": detected_plant.title(),
            "confidence": round(best_confidence, 2),
            "image": f"data:image/jpeg;base64,{image_base64}",
            "scientific_name": "Not available",
            "benefits": ["Information not available in database"],
            "cautions": ["Please consult a healthcare professional for plant information"],
            "raw_results": all_results
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


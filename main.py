from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from inference_sdk import InferenceHTTPClient
from PIL import Image
import io
import os
from dotenv import load_dotenv
import base64
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

# ✅ Serve frontend as root domain
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# Roboflow client
API_KEY = os.getenv("ROBOFLOW_API_KEY")
API_URL = os.getenv("ROBOFLOW_API_URL", "https://serverless.roboflow.com")

CLIENT = InferenceHTTPClient(api_url=API_URL, api_key=API_KEY)

# Models
MODELS = [
    "herbal-plant-detection-1baib/9",
    "herbal-plants-yolo5v/2",
    "herbal-s6spz/3"
]

DETECTED_PLANTS_SET = set()

@app.get("/plants")
async def get_all_plants():
    return {
        "total_plants_detected": len(DETECTED_PLANTS_SET),
        "plants": sorted([plant.title() for plant in DETECTED_PLANTS_SET]),
        "models": MODELS
    }

@app.post("/detect")
async def detect_plant(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file")

        image = Image.open(io.BytesIO(contents))
        if image.mode != "RGB":
            image = image.convert("RGB")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            image.save(tmp_file, format="JPEG")
            tmp_path = tmp_file.name

        best_conf = 0
        detected = None
        all_results = []

        for model in MODELS:
            try:
                result = CLIENT.infer(tmp_path, model_id=model)
                all_results.append({"model": model, "result": result})

                preds = result.get("predictions", [])
                if preds:
                    best_pred = max(preds, key=lambda x: x.get("confidence", 0))
                    conf = best_pred.get("confidence", 0)
                    if conf > best_conf:
                        best_conf = conf
                        detected = best_pred.get("class", "")
            except:
                continue
        os.unlink(tmp_path)

        if not detected:
            return JSONResponse(status_code=404, content={"error": "No plant detected"})

        DETECTED_PLANTS_SET.add(detected.lower())

        img_bytes = io.BytesIO()
        image.save(img_bytes, format="JPEG")
        img_base64 = base64.b64encode(img_bytes.getvalue()).decode()

        return {
            "detected_plant": detected.title(),
            "confidence": round(best_conf, 2),
            "image": f"data:image/jpeg;base64,{img_base64}",
            "scientific_name": "Not available",
            "benefits": ["Not available"],
            "cautions": ["Consult a medical professional"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

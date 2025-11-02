# 🌿 Herbal Plant Detection System

A beautiful web application for detecting herbal plants from images using AI models from Roboflow. The system identifies plants and provides detailed information including scientific names, benefits, and cautions.

## Features

- 📸 Upload plant images via drag-and-drop or file selection
- 🔍 Multi-model AI detection using 3 Roboflow models
- 📊 Detailed plant information:
  - Scientific name
  - Health benefits
  - Safety cautions
- 🎨 Beautiful, modern UI with gradient design
- 📱 Responsive design for mobile and desktop

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the root directory with your Roboflow API credentials:

```env
ROBOFLOW_API_KEY=eb6rXUxlCKM7cgv0duMU
ROBOFLOW_API_URL=https://serverless.roboflow.com
```

**Note:** Make sure to use your actual API key. The one provided in the example is for reference.

### 3. Run the Application

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Access the Application

Open your browser and navigate to:
```
http://localhost:8000
```

## Project Structure

```
herplants/
├── main.py                 # FastAPI backend server
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
├── README.md              # This file
└── static/                # Frontend files
    ├── index.html         # Main HTML page
    ├── style.css          # Stylesheet
    └── script.js          # Frontend JavaScript
```

## API Endpoints

### `GET /`
Serves the main web interface.

### `POST /detect`
Uploads an image for plant detection.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: image file

**Response:**
```json
{
  "detected_plant": "Basil",
  "confidence": 0.95,
  "image": "data:image/jpeg;base64,...",
  "scientific_name": "Ocimum basilicum",
  "benefits": ["Antioxidant properties", ...],
  "cautions": ["May cause allergic reactions", ...]
}
```

## Roboflow Models

The application uses three pre-trained models from Roboflow:
1. `herbal-plant-detection-1baib/9`
2. `herbal-plants-yolo5v/2`
3. `herbal-s6spz/3`

The system runs inference on all three models and selects the result with the highest confidence.

## Supported Plants

The database currently includes information for:
- Basil
- Mint
- Ginger
- Turmeric
- Aloe Vera
- Rosemary
- Oregano
- Sage
- Thyme
- Chamomile
- Lavender
- Cilantro

## Technologies Used

- **Backend:** FastAPI, Python
- **AI/ML:** Roboflow Inference SDK
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Image Processing:** Pillow (PIL)

## Development

To run in development mode with auto-reload:

```bash
uvicorn main:app --reload
```

## Notes

- Make sure your `.env` file contains valid Roboflow API credentials
- The application handles image uploads up to reasonable file sizes
- Plant information is matched by the detected class name from the models
- If a plant is not found in the database, generic placeholder information is shown

## License

This project is for educational and personal use.

---

Enjoy discovering the secrets of nature's healing plants! 🌱✨


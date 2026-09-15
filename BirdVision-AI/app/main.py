"""
app/main.py
FastAPI backend for BirdVision AI.
"""

from io import BytesIO
from pathlib import Path
import sys
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image

# Add root directory to path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.pipeline import BirdVisionPipeline

app = FastAPI(
    title="BirdVision AI API",
    description="Two-stage detection and species classification pipeline for flock counting",
    version="1.0.0"
)

# Initialize pipeline once on startup
pipeline = None

@app.on_event("startup")
def load_model():
    global pipeline
    weights_path = ROOT_DIR / "models" / "best_transfer_resnet18.pth"
    pipeline = BirdVisionPipeline(model_path=str(weights_path))

@app.get("/health")
def health():
    return {"status": "healthy", "classes": pipeline.classes if pipeline else []}

@app.post("/predict")
async def predict_birds(
    file: UploadFile = File(...),
    det_conf: str = "auto",
    clf_conf: str = "auto"
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")

    try:
        contents = await file.read()
        pil_img = Image.open(BytesIO(contents)).convert("RGB")

        # Parse threshold inputs
        det_val = float(det_conf) if det_conf != "auto" else "auto"
        clf_val = float(clf_conf) if clf_conf != "auto" else "auto"

        _, summary, detections = pipeline.predict(
            image_input=pil_img,
            det_conf=det_val,
            clf_conf=clf_val
        )

        return JSONResponse(content={
            "filename": file.filename,
            "total_count": summary["total_count"],
            "species_breakdown": summary["species_breakdown"],
            "detections": detections
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
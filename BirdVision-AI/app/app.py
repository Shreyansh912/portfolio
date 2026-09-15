"""
app/app.py
Streamlit Frontend for BirdVision AI.
Consumes the FastAPI backend endpoint (/predict) via HTTP POST requests.
"""

from io import BytesIO
from PIL import Image, ImageDraw
import requests
import streamlit as st

# Backend Configuration
API_URL = "http://127.0.0.1:8001/predict"
HEALTH_URL = "http://127.0.0.1:8001/health"

st.set_page_config(
    page_title="BirdVision AI | Flock Detection & Counting",
    page_icon="🪶",
    layout="wide",
)

st.title("🪶 BirdVision AI: Client Dashboard")
st.caption("Streamlit Client connected to FastAPI Two-Stage Inference Engine")

# 1. Live Backend Connectivity Check (No Caching)
def check_backend_status():
    try:
        response = requests.get(HEALTH_URL, timeout=2)
        if response.status_code == 200:
            return True, response.json().get("classes", [])
    except requests.exceptions.RequestException:
        pass
    return False, []

backend_online, supported_classes = check_backend_status()

# 2. Sidebar Configuration
st.sidebar.header("Pipeline Settings")

if backend_online:
    st.sidebar.success("Backend API: Connected (Port 8001)")
else:
    st.sidebar.error("Backend API: Offline")
    st.sidebar.caption("Run `python run_api.py` in your backend terminal.")
    if st.sidebar.button("Retry Connection"):
        st.rerun()

auto_tune = st.sidebar.toggle("⚡ Auto-Tune Thresholds (Adaptive)", value=True)

if auto_tune:
    det_conf = "auto"
    clf_conf = "auto"
    st.sidebar.info("Using dynamic backend thresholds.")
else:
    st.sidebar.subheader("Manual Hyperparameters")
    det_conf = str(st.sidebar.slider(
        "Stage 1: YOLO Detection Confidence",
        min_value=0.05,
        max_value=0.90,
        value=0.25,
        step=0.05
    ))
    clf_conf = str(st.sidebar.slider(
        "Stage 2: ResNet-18 Species Threshold",
        min_value=0.10,
        max_value=0.95,
        value=0.50,
        step=0.05
    ))

if supported_classes:
    st.sidebar.markdown("---")
    st.sidebar.subheader("Supported Species")
    for species in supported_classes:
        st.sidebar.markdown(f"- `{species}`")

# 3. File Uploader and API Interaction
uploaded_file = st.file_uploader(
    "Upload bird or flock image",
    type=["jpg", "jpeg", "png", "webp"]
)

if uploaded_file is not None:
    input_image = Image.open(uploaded_file).convert("RGB")

    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Original Image")
        st.image(input_image, use_container_width=True)

    if not backend_online:
        st.error("Cannot process request: FastAPI server is unreachable at http://127.0.0.1:8001.")
    else:
        with st.spinner("Running two-stage inference via FastAPI backend..."):
            uploaded_file.seek(0)
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            params = {"det_conf": det_conf, "clf_conf": clf_conf}

            try:
                response = requests.post(API_URL, files=files, params=params, timeout=30)

                if response.status_code == 200:
                    data = response.json()
                    total_count = data.get("total_count", 0)
                    breakdown = data.get("species_breakdown", {})
                    detections = data.get("detections", [])

                    # Draw bounding boxes
                    annotated_image = input_image.copy()
                    draw = ImageDraw.Draw(annotated_image)

                    for det in detections:
                        x1, y1, x2, y2 = det["box"]
                        label = f"{det['species']} ({det['confidence'] * 100:.1f}%)"
                        draw.rectangle([x1, y1, x2, y2], outline="#00FF00", width=3)
                        draw.text((x1, max(5, y1 - 15)), label, fill="#00FF00")

                    with col_right:
                        st.subheader("Annotated Detections")
                        st.image(annotated_image, use_container_width=True)

                    # 4. Metrics Display
                    st.markdown("---")
                    st.subheader("Inference Summary")
                    metric_cols = st.columns(4)
                    metric_cols[0].metric(label="Total Birds Detected", value=total_count)

                    if total_count > 0:
                        st.markdown("#### Species Breakdown")
                        b_cols = st.columns(max(len(breakdown), 1))
                        for idx, (sp, cnt) in enumerate(breakdown.items()):
                            col = b_cols[idx % len(breakdown)]
                            col.metric(label=sp.replace("_", " ").title(), value=cnt)

                        with st.expander("Raw API JSON Response"):
                            st.json(data)
                    else:
                        st.info("No birds detected. Try lowering the Stage 1 threshold in the sidebar.")

                else:
                    st.error(f"API Error {response.status_code}: {response.text}")

            except requests.exceptions.RequestException as exc:
                st.error(f"Request failed: {exc}")
else:
    st.info("Upload an image to trigger the backend API.")
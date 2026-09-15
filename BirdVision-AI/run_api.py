"""run_api.py

Explicit launcher for BirdVision AI FastAPI backend on Windows with auto-open
browser.
"""

import sys
import threading
import time
import webbrowser
from app.main import app
import uvicorn


def launch_browser():
  time.sleep(1.2)  # Give uvicorn a second to bind to port 8001
  webbrowser.open("http://127.0.0.1:8001/docs")


if __name__ == "__main__":
  print("=" * 50)
  print("Starting BirdVision AI Backend Server...")
  print("API Documentation: http://127.0.0.1:8001/docs")
  print("=" * 50)

  # Start the background thread to pop open the browser
  threading.Thread(target=launch_browser, daemon=True).start()

  # Use 'asyncio' selector policy to prevent silent exit on Windows
  uvicorn.run(
      app,
      host="127.0.0.1",
      port=8001,
      log_level="info",
      loop="asyncio",
  )
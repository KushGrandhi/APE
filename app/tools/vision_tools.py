"""Vision analysis tool — mock, image directory, and camera feed implementations."""

import base64
import os
from pathlib import Path

import ollama
from ollama._types import Image

from app.tools.base import VisionSource

VISION_MODEL = os.getenv("VISION_MODEL", "gemma3:4b")

VISION_PROMPT = (
    "You are a chemical warehouse dock inspector. "
    "Describe every container, drum, bag, and box you see. "
    "For each item report: quantity, label text, hazard symbols "
    "(Flammable, Corrosive, Toxic, Oxidizer, Explosive, etc.), "
    "and a confidence score from 0.0 to 1.0 for each detection. "
    "For hazard symbols, give a separate confidence per symbol. "
    "Also flag any unmarked or suspicious items. "
    "End with an overall scene confidence score (0.0–1.0) based on image clarity."
)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# Camera burst settings
BURST_FRAMES = int(os.getenv("BURST_FRAMES", "5"))
BURST_INTERVAL_SEC = float(os.getenv("BURST_INTERVAL_SEC", "0.5"))


def _describe_image_bytes(img_bytes: bytes) -> str:
    """Send image bytes to the vision model and return its description."""
    b64 = base64.b64encode(img_bytes).decode()
    response = ollama.chat(
        model=VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": VISION_PROMPT,
                "images": [Image(value=b64)],
            }
        ],
    )
    return response.message.content


def _describe_image(image_path: str) -> str:
    """Send a single image file to the vision model and return its description."""
    return _describe_image_bytes(Path(image_path).read_bytes())


# ---------------------------------------------------------------------------
# 1. Mock implementation (no model, no camera)
# ---------------------------------------------------------------------------

class MockVisionSource(VisionSource):
    """Returns a hardcoded dock camera observation with confidence scores."""

    def observe(self, source: str) -> str:
        return (
            "Visible at dock: "
            "8x large drums labeled 'HCL' with Corrosive (confidence: 0.95) "
            "and Toxic (confidence: 0.91) hazard symbols, detection confidence: 0.93. "
            "5x white bags labeled 'NaOH' with Corrosive (confidence: 0.88) "
            "hazard symbol, detection confidence: 0.85. "
            "1x unmarked small box with no visible hazard labels, detection confidence: 0.70. "
            "Overall scene confidence: 0.87."
        )


# ---------------------------------------------------------------------------
# 2. Image directory implementation
# ---------------------------------------------------------------------------

class ImageDirVisionSource(VisionSource):
    """Processes a single image file or all images in a directory through the vision model."""

    def observe(self, source: str) -> str:
        src_path = Path(source)

        # Single file
        if src_path.is_file() and src_path.suffix.lower() in IMAGE_EXTENSIONS:
            return _describe_image(str(src_path))

        # Directory
        if not src_path.is_dir():
            return f"Error: '{source}' is not a file or directory."

        image_files = sorted(
            f for f in src_path.iterdir()
            if f.suffix.lower() in IMAGE_EXTENSIONS
        )
        if not image_files:
            return f"No images found in '{source}'."

        descriptions: list[str] = []
        for img_file in image_files:
            desc = _describe_image(str(img_file))
            descriptions.append(f"[{img_file.name}]: {desc}")

        return "\n\n".join(descriptions)


# ---------------------------------------------------------------------------
# 3. Camera feed implementation (webcam or RTSP)
# ---------------------------------------------------------------------------

class CameraVisionSource(VisionSource):
    """Captures a burst of frames from a webcam or RTSP stream, analyzes the last one.

    Captures BURST_FRAMES frames so the camera auto-exposure can settle,
    then sends only the final frame to the vision model.

    source can be:
      - "0", "1", etc.  → local webcam index
      - "rtsp://..."     → network camera URL

    Falls back to CAMERA_URL env var if source is empty.

    Configure via env vars:
      BURST_FRAMES       — number of frames to capture (default: 5)
      BURST_INTERVAL_SEC — seconds between captures (default: 0.5)
    """

    def observe(self, source: str) -> str:
        import time

        try:
            import cv2
        except ImportError:
            return "Error: opencv-python is not installed. Run: pip install opencv-python"

        camera_source = source or os.getenv("CAMERA_URL", "0")

        # int index for local webcam, string for RTSP
        try:
            camera_source = int(camera_source)
        except ValueError:
            pass

        cap = cv2.VideoCapture(camera_source)
        if not cap.isOpened():
            return f"Error: could not open camera '{camera_source}'."

        try:
            last_frame: bytes | None = None
            for i in range(BURST_FRAMES):
                ret, frame = cap.read()
                if ret:
                    _, buf = cv2.imencode(".jpg", frame)
                    last_frame = buf.tobytes()
                if i < BURST_FRAMES - 1:
                    time.sleep(BURST_INTERVAL_SEC)
        finally:
            cap.release()

        if last_frame is None:
            return "Error: failed to capture any frames from camera."

        print(f"  [Camera] Captured {BURST_FRAMES} frames, analyzing last frame...")
        desc = _describe_image_bytes(last_frame)
        print(f"  [Camera] Analysis complete.")
        return desc


# ---------------------------------------------------------------------------
# Default source selection via VISION_SOURCE env var
# ---------------------------------------------------------------------------

def _build_default() -> VisionSource:
    mode = os.getenv("VISION_SOURCE", "mock")
    if mode == "camera":
        return CameraVisionSource()
    if mode == "images":
        return ImageDirVisionSource()
    return MockVisionSource()


_default = _build_default()


def inventory_what_you_see(source: str) -> str:
    """Analyze the dock visuals to identify containers and hazard symbols."""
    return _default.observe(source)

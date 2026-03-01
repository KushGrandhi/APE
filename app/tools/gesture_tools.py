"""Gesture recognition tool — mock, image, and camera implementations."""

import base64
import os
from pathlib import Path

import ollama
from ollama._types import Image

from app.tools.base import GestureSource

GESTURE_MODEL = os.getenv("GESTURE_MODEL", "gemma3:4b")

GESTURE_PROMPT = (
    "You are observing a dock worker at a chemical warehouse. "
    "Look at the person's hand gesture or body language. "
    "Determine if they are signaling one of these: "
    "thumbs_up / nod / wave-forward = 'approve', "
    "palm-out / stop / hand-raised = 'decline', "
    "pointing / shrug / head-tilt = 'review'. "
    "Respond with: the gesture you see, your interpretation "
    "(approve, review, or decline), and a confidence score from 0.0 to 1.0."
)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def _analyze_gesture_bytes(img_bytes: bytes) -> str:
    """Send image bytes to the gesture model and return interpretation."""
    b64 = base64.b64encode(img_bytes).decode()
    response = ollama.chat(
        model=GESTURE_MODEL,
        messages=[
            {
                "role": "user",
                "content": GESTURE_PROMPT,
                "images": [Image(value=b64)],
            }
        ],
    )
    return response.message.content


def _analyze_gesture_file(image_path: str) -> str:
    """Send an image file to the gesture model."""
    return _analyze_gesture_bytes(Path(image_path).read_bytes())


# ---------------------------------------------------------------------------
# 1. Mock implementation
# ---------------------------------------------------------------------------

class MockGestureSource(GestureSource):
    """Returns a hardcoded gesture observation with confidence."""

    def read_gesture(self, source: str) -> str:
        return "Gesture detected: thumbs_up — interpreted as 'approve'. Confidence: 0.92."


# ---------------------------------------------------------------------------
# 2. Image implementation
# ---------------------------------------------------------------------------

class ImageGestureSource(GestureSource):
    """Analyzes a single image or all images in a directory for gestures."""

    def read_gesture(self, source: str) -> str:
        path = Path(source)

        if path.is_file():
            print(f"  [Gesture] Analyzing {path.name}...")
            return _analyze_gesture_file(str(path))

        if path.is_dir():
            image_files = sorted(
                f for f in path.iterdir()
                if f.suffix.lower() in IMAGE_EXTENSIONS
            )
            if not image_files:
                return f"No images found in '{source}'."

            descriptions: list[str] = []
            for img_file in image_files:
                print(f"  [Gesture] Analyzing {img_file.name}...")
                desc = _analyze_gesture_file(str(img_file))
                descriptions.append(f"[{img_file.name}]: {desc}")
            return "\n\n".join(descriptions)

        return f"Error: '{source}' is not a file or directory."


# ---------------------------------------------------------------------------
# 3. Camera implementation (burst capture like vision)
# ---------------------------------------------------------------------------

GESTURE_BURST_FRAMES = int(os.getenv("GESTURE_BURST_FRAMES", "3"))
GESTURE_BURST_INTERVAL_SEC = float(os.getenv("GESTURE_BURST_INTERVAL_SEC", "0.5"))


class CameraGestureSource(GestureSource):
    """Captures a burst of frames from camera, picks the last (best) one to analyze.

    Captures GESTURE_BURST_FRAMES frames so the camera auto-exposure can settle,
    then sends only the final frame to the vision model.

    Configure via env:
      GESTURE_BURST_FRAMES       — frames to capture (default: 3)
      GESTURE_BURST_INTERVAL_SEC — seconds between captures (default: 0.5)
    """

    def read_gesture(self, source: str) -> str:
        import time

        try:
            import cv2
        except ImportError:
            return "Error: opencv-python is not installed. Run: pip install opencv-python"

        camera_source = source or os.getenv("GESTURE_CAMERA_URL", "0")

        try:
            camera_source = int(camera_source)
        except ValueError:
            pass

        cap = cv2.VideoCapture(camera_source)
        if not cap.isOpened():
            return f"Error: could not open camera '{camera_source}'."

        try:
            last_frame: bytes | None = None
            for i in range(GESTURE_BURST_FRAMES):
                ret, frame = cap.read()
                if ret:
                    _, buf = cv2.imencode(".jpg", frame)
                    last_frame = buf.tobytes()
                if i < GESTURE_BURST_FRAMES - 1:
                    time.sleep(GESTURE_BURST_INTERVAL_SEC)
        finally:
            cap.release()

        if last_frame is None:
            return "Error: failed to capture any frames from camera."

        print(f"  [Gesture] Captured {GESTURE_BURST_FRAMES} frames, analyzing last frame...")
        desc = _analyze_gesture_bytes(last_frame)
        print(f"  [Gesture] Analysis complete.")
        return desc


# ---------------------------------------------------------------------------
# Default source selection via GESTURE_SOURCE env var
# ---------------------------------------------------------------------------

def _build_default() -> GestureSource:
    mode = os.getenv("GESTURE_SOURCE", "mock")
    if mode == "camera":
        return CameraGestureSource()
    if mode == "image":
        return ImageGestureSource()
    return MockGestureSource()


_default = _build_default()


def see_what_human_has_to_say(source: str) -> str:
    """Observe dock worker gesture and return interpretation."""
    return _default.read_gesture(source)

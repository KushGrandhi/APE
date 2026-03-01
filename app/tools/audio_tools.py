"""Audio processing tool — mock, file, and microphone implementations."""

import os
from pathlib import Path

from app.tools.base import AudioSource

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
MIC_DURATION_SEC = int(os.getenv("MIC_DURATION_SEC", "5"))


def _transcribe(audio_path: str) -> tuple[str, float]:
    """Transcribe an audio file using Whisper.

    Returns:
        Tuple of (transcription text, average confidence 0.0–1.0).
    """
    import whisper

    model = whisper.load_model(WHISPER_MODEL)
    result = model.transcribe(audio_path)
    text = result["text"].strip()

    # Average no_speech_prob across segments — lower means more confident
    segments = result.get("segments", [])
    if segments:
        avg_no_speech = sum(s.get("no_speech_prob", 0.0) for s in segments) / len(segments)
        confidence = round(1.0 - avg_no_speech, 2)
    else:
        confidence = 0.0

    return text, confidence


# ---------------------------------------------------------------------------
# 1. Mock implementation
# ---------------------------------------------------------------------------

class MockAudioSource(AudioSource):
    """Returns a hardcoded dock worker transcription with confidence."""

    def listen(self, source: str) -> str:
        return (
            "Dock worker said: 'We're expecting the HCL shipment today, "
            "should be 10 drums plus 5 bags of sodium hydroxide. "
            "All hazardous, make sure the labels are checked.' "
            "Transcription confidence: 0.94."
        )


# ---------------------------------------------------------------------------
# 2. Audio file implementation
# ---------------------------------------------------------------------------

class FileAudioSource(AudioSource):
    """Transcribes an audio file (.wav, .mp3, etc.) using Whisper."""

    def listen(self, source: str) -> str:
        path = Path(source)
        if not path.is_file():
            return f"Error: audio file '{source}' not found."

        print(f"  [Audio] Transcribing {path.name} with Whisper ({WHISPER_MODEL})...")
        text, confidence = _transcribe(source)
        print(f"  [Audio] Transcription complete (confidence: {confidence}).")
        return f"Dock worker said: '{text}' Transcription confidence: {confidence}."


# ---------------------------------------------------------------------------
# 3. Microphone implementation
# ---------------------------------------------------------------------------

class MicAudioSource(AudioSource):
    """Records from microphone for MIC_DURATION_SEC seconds, then transcribes.

    Configure via env:
      MIC_DURATION_SEC — seconds to record (default: 5)
    """

    def listen(self, source: str) -> str:
        import tempfile
        import wave

        try:
            import pyaudio
        except ImportError:
            return "Error: pyaudio is not installed. Run: pip install pyaudio"

        duration = MIC_DURATION_SEC
        sample_rate = 16000
        channels = 1
        chunk = 1024
        fmt = pyaudio.paInt16

        pa = pyaudio.PyAudio()
        print(f"  [Mic] Recording for {duration}s...")

        stream = pa.open(
            format=fmt,
            channels=channels,
            rate=sample_rate,
            input=True,
            frames_per_buffer=chunk,
        )

        frames: list[bytes] = []
        for _ in range(0, int(sample_rate / chunk * duration)):
            data = stream.read(chunk)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        pa.terminate()

        print(f"  [Mic] Recording done, transcribing with Whisper ({WHISPER_MODEL})...")

        # Write to temp wav, transcribe, clean up
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name
            wf = wave.open(tmp, "wb")
            wf.setnchannels(channels)
            wf.setsampwidth(pa.get_sample_size(fmt) if hasattr(pa, "get_sample_size") else 2)
            wf.setframerate(sample_rate)
            wf.writeframes(b"".join(frames))
            wf.close()

        try:
            text, confidence = _transcribe(tmp_path)
        finally:
            os.unlink(tmp_path)

        print(f"  [Mic] Transcription complete (confidence: {confidence}).")
        return f"Dock worker said: '{text}' Transcription confidence: {confidence}."


# ---------------------------------------------------------------------------
# Default source selection via AUDIO_SOURCE env var
# ---------------------------------------------------------------------------

def _build_default() -> AudioSource:
    mode = os.getenv("AUDIO_SOURCE", "mock")
    if mode == "file":
        return FileAudioSource()
    if mode == "mic":
        return MicAudioSource()
    return MockAudioSource()


_default = _build_default()


def listen_what_to_expect(source: str) -> str:
    """Process dock worker audio and return what they said."""
    return _default.listen(source)

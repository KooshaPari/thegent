"""WP-32001: Sensory Context Bridge (Audio/Video).

Provides audio and video processing capabilities for agent context awareness.
Supports transcription, feature extraction, and frame analysis.
"""

import io
import logging
import tempfile
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class AudioFeatures:
    """Extracted audio features."""

    transcript: str
    duration: float
    sample_rate: int
    channels: int
    language: str | None = None
    sentiment: dict[str, float] | None = None
    keywords: list[str] | None = None


@dataclass
class VideoFeatures:
    """Extracted video features."""

    frame_count: int
    fps: float
    resolution: tuple[int, int]
    duration: float
    scenes: list[dict[str, Any]] | None = None
    objects: list[dict[str, Any]] | None = None
    text_overlays: list[str] | None = None


class SensoryContextBridge:
    """Bridge for audio/video sensory context processing.

    Provides unified interface for processing audio and video data
    to extract contextual information for agent decision-making.
    """

    def __init__(self) -> None:
        """Initialize sensory context bridge."""
        self._audio_processors: dict[str, Any] = {}
        self._video_processors: dict[str, Any] = {}

    def process_audio(
        self,
        audio_data: bytes,
        format: str = "wav",
        language: str | None = None,
    ) -> dict[str, Any]:
        """Process audio data and extract features.

        Args:
            audio_data: Raw audio bytes
            format: Audio format (wav, mp3, flac, etc.)
            language: Expected language code (e.g., 'en', 'es') for transcription

        Returns:
            Dictionary containing transcript, features, and metadata
        """
        logger.info("Processing audio data (%s bytes, format: %s)", len(audio_data), format)

        transcript = ""
        if processor := self._audio_processors.get(format):
            if hasattr(processor, "process"):
                result = processor.process(audio_data, format=format, language=language)
                if isinstance(result, dict):
                    transcript = str(result.get("transcript", ""))
                elif isinstance(result, str):
                    transcript = result

        duration = 0.0
        sample_rate = 0
        channels = 0
        if format.lower() == "wav":
            import wave

            with wave.open(io.BytesIO(audio_data), "rb") as wav:
                sample_rate = wav.getframerate()
                channels = wav.getnchannels()
                frames = wav.getnframes()
                duration = frames / float(sample_rate) if sample_rate else 0.0
        else:
            msg = f"Unsupported audio format for built-in parser: {format}. Register a custom processor."
            raise ValueError(msg)

        sentiment = self._simple_sentiment(transcript) if transcript else None
        keywords = self._extract_keywords(transcript) if transcript else None

        features = AudioFeatures(
            transcript=transcript,
            duration=duration,
            sample_rate=sample_rate,
            channels=channels,
            language=language,
            sentiment=sentiment,
            keywords=keywords,
        )

        return {
            "transcript": features.transcript,
            "features": {
                "duration": features.duration,
                "sample_rate": features.sample_rate,
                "channels": features.channels,
                "language": features.language,
                "sentiment": features.sentiment,
                "keywords": features.keywords,
            },
            "metadata": {
                "format": format,
                "size_bytes": len(audio_data),
            },
        }

    def process_video(
        self,
        video_data: bytes,
        format: str = "mp4",
        extract_frames: bool = False,
        frame_interval: float = 1.0,
    ) -> dict[str, Any]:
        """Process video data and extract features.

        Args:
            video_data: Raw video bytes
            format: Video format (mp4, avi, mov, etc.)
            extract_frames: Whether to extract individual frames
            frame_interval: Interval between frames in seconds

        Returns:
            Dictionary containing frames, features, and metadata
        """
        logger.info("Processing video data (%s bytes, format: %s)", len(video_data), format)
        try:
            import cv2  # type: ignore[import-not-found]
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError("opencv-python is required for built-in video processing") from exc

        frames: list[dict[str, Any]] = []
        with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=True) as tmp:
            tmp.write(video_data)
            tmp.flush()

            capture = cv2.VideoCapture(tmp.name)
            if not capture.isOpened():
                raise ValueError(f"Unable to decode video bytes as {format}")

            frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
            fps = float(capture.get(cv2.CAP_PROP_FPS) or 0.0)
            width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
            height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
            duration = (frame_count / fps) if fps > 0 else 0.0

            if extract_frames:
                interval_frames = max(1, int(frame_interval * fps)) if fps > 0 else 1
                index = 0
                while True:
                    ok, frame = capture.read()
                    if not ok:
                        break
                    if index % interval_frames == 0:
                        frames.append(
                            {
                                "index": index,
                                "timestamp_s": (index / fps) if fps > 0 else 0.0,
                                "shape": tuple(frame.shape),
                                "mean_luma": float(frame.mean()),
                            }
                        )
                    index += 1

            capture.release()

        features = VideoFeatures(
            frame_count=frame_count,
            fps=fps,
            resolution=(width, height),
            duration=duration,
            scenes=[],
            objects=[],
            text_overlays=[],
        )

        return {
            "frames": frames,
            "features": {
                "frame_count": features.frame_count,
                "fps": features.fps,
                "resolution": features.resolution,
                "duration": features.duration,
                "scenes": features.scenes,
                "objects": features.objects,
                "text_overlays": features.text_overlays,
            },
            "metadata": {
                "format": format,
                "size_bytes": len(video_data),
                "frames_extracted": len(frames),
            },
        }

    def register_audio_processor(self, name: str, processor: Any) -> None:
        """Register a custom audio processor.

        Args:
            name: Processor identifier
            processor: Processor instance with process() method
        """
        self._audio_processors[name] = processor
        logger.info(f"Registered audio processor: {name}")

    def register_video_processor(self, name: str, processor: Any) -> None:
        """Register a custom video processor.

        Args:
            name: Processor identifier
            processor: Processor instance with process() method
        """
        self._video_processors[name] = processor
        logger.info(f"Registered video processor: {name}")

    @staticmethod
    def _extract_keywords(text: str) -> list[str]:
        words = [w.strip(".,!?;:()[]{}").lower() for w in text.split()]
        words = [w for w in words if len(w) >= 4]
        counts: dict[str, int] = {}
        for word in words:
            counts[word] = counts.get(word, 0) + 1
        ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        return [w for w, _ in ranked[:5]]

    @staticmethod
    def _simple_sentiment(text: str) -> dict[str, float]:
        positive = {"good", "great", "excellent", "happy", "love", "success"}
        negative = {"bad", "poor", "terrible", "sad", "fail", "failure", "error"}
        words = [w.strip(".,!?;:()[]{}").lower() for w in text.split()]
        if not words:
            return {"positive": 0.0, "negative": 0.0, "neutral": 1.0}
        pos = sum(1 for w in words if w in positive)
        neg = sum(1 for w in words if w in negative)
        total = len(words)
        positive_score = pos / total
        negative_score = neg / total
        neutral_score = max(0.0, 1.0 - positive_score - negative_score)
        return {
            "positive": round(positive_score, 4),
            "negative": round(negative_score, 4),
            "neutral": round(neutral_score, 4),
        }

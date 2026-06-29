from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Protocol

from yolo_openai_detector.config import Settings
from yolo_openai_detector.image_input import ValidatedImage


@dataclass(frozen=True)
class Detection:
    label: str
    confidence: float
    bbox_xyxy: tuple[int, int, int, int]


@dataclass(frozen=True)
class DetectionResult:
    objects: list[Detection]


class Detector(Protocol):
    def detect(self, image: ValidatedImage) -> DetectionResult: ...


class DetectorConfigurationError(ValueError):
    pass


class DetectorRuntimeError(RuntimeError):
    pass


class StubDetector:
    def detect(self, image: ValidatedImage) -> DetectionResult:
        return DetectionResult(objects=[])


def detection_response_content(
    *,
    model_id: str,
    detection_result: DetectionResult,
    image: ValidatedImage,
) -> dict[str, object]:
    return {
        "model": model_id,
        "objects": [
            {
                "label": detection.label,
                "confidence": detection.confidence,
                "bbox_xyxy": list(detection.bbox_xyxy),
            }
            for detection in detection_result.objects
        ],
        "image": {
            "mime_type": image.mime_type,
            "width": image.width,
            "height": image.height,
            "bytes": image.bytes,
        },
    }


def get_detector(settings: Settings) -> Detector:
    return _get_detector(
        backend=settings.detector_backend,
        model_weights=settings.model_weights,
        confidence_threshold=settings.confidence_threshold,
        iou_threshold=settings.iou_threshold,
        image_size=settings.image_size,
        device=settings.device,
    )


def clear_detector_cache() -> None:
    _get_detector.cache_clear()


@lru_cache
def _get_detector(
    *,
    backend: str,
    model_weights: str,
    confidence_threshold: float,
    iou_threshold: float,
    image_size: int,
    device: str,
) -> Detector:
    normalized_backend = backend.lower()
    normalized_device = device.lower()

    if normalized_backend == "stub":
        return StubDetector()

    if normalized_backend == "ultralytics":
        if normalized_device != "cpu":
            raise DetectorConfigurationError("YOLO_DEVICE must be 'cpu'.")
        from yolo_openai_detector.yolo_detector import UltralyticsYoloDetector

        return UltralyticsYoloDetector(
            model_weights=model_weights,
            confidence_threshold=confidence_threshold,
            iou_threshold=iou_threshold,
            image_size=image_size,
            device="cpu",
        )

    raise DetectorConfigurationError(f"Unsupported detector backend: {backend}")

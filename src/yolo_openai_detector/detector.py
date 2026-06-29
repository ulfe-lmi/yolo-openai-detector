from __future__ import annotations

from dataclasses import dataclass

from yolo_openai_detector.image_input import ValidatedImage


@dataclass(frozen=True)
class Detection:
    label: str
    confidence: float
    bbox_xyxy: tuple[int, int, int, int]


@dataclass(frozen=True)
class DetectionResult:
    objects: list[Detection]


class StubDetector:
    def detect(self, image: ValidatedImage) -> DetectionResult:
        return DetectionResult(objects=[])

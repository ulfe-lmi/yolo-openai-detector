from __future__ import annotations

from io import BytesIO
from typing import Any

from PIL import Image

from yolo_openai_detector.detector import Detection, DetectionResult, DetectorRuntimeError
from yolo_openai_detector.image_input import ValidatedImage


class UltralyticsYoloDetector:
    def __init__(
        self,
        model_weights: str,
        confidence_threshold: float,
        iou_threshold: float,
        image_size: int,
        device: str = "cpu",
    ) -> None:
        if device.lower() != "cpu":
            raise ValueError("UltralyticsYoloDetector only supports CPU execution.")

        self.model_weights = model_weights
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.image_size = image_size
        self.device = "cpu"
        self._model: Any | None = None

    def detect(self, image: ValidatedImage) -> DetectionResult:
        model = self._load_model()

        try:
            with Image.open(BytesIO(image.image_bytes)) as pil_image:
                pil_image.load()
                input_image = pil_image.convert("RGB")

            results = model.predict(
                input_image,
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
                imgsz=self.image_size,
                device="cpu",
                verbose=False,
            )
        except Exception as exc:
            raise DetectorRuntimeError("YOLO inference failed.") from exc

        if not results:
            return DetectionResult(objects=[])

        result = results[0]
        boxes = getattr(result, "boxes", None)
        if boxes is None:
            return DetectionResult(objects=[])

        names = getattr(result, "names", getattr(model, "names", {}))
        xyxy_values = _as_list(getattr(boxes, "xyxy", []))
        confidence_values = _as_list(getattr(boxes, "conf", []))
        class_values = _as_list(getattr(boxes, "cls", []))

        detections: list[Detection] = []
        for xyxy, confidence, class_index in zip(
            xyxy_values,
            confidence_values,
            class_values,
            strict=False,
        ):
            confidence_float = float(confidence)
            if confidence_float < self.confidence_threshold:
                continue

            bbox = tuple(int(round(float(value))) for value in xyxy)
            if len(bbox) != 4:
                continue

            detections.append(
                Detection(
                    label=_label_for_class(names, int(class_index)),
                    confidence=confidence_float,
                    bbox_xyxy=bbox,
                )
            )

        detections.sort(
            key=lambda detection: (
                -detection.confidence,
                detection.label,
                detection.bbox_xyxy,
            )
        )
        return DetectionResult(objects=detections)

    def _load_model(self) -> Any:
        if self._model is None:
            try:
                from ultralytics import YOLO

                self._model = YOLO(self.model_weights)
            except Exception as exc:
                raise DetectorRuntimeError("Failed to load YOLO model.") from exc

        return self._model


def _as_list(value: Any) -> list[Any]:
    if hasattr(value, "detach"):
        value = value.detach()
    if hasattr(value, "cpu"):
        value = value.cpu()
    if hasattr(value, "tolist"):
        return value.tolist()
    return list(value)


def _label_for_class(names: Any, class_index: int) -> str:
    if isinstance(names, dict):
        return str(names.get(class_index, class_index))
    if isinstance(names, list) and 0 <= class_index < len(names):
        return str(names[class_index])
    return str(class_index)

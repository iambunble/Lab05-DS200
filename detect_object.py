from pathlib import Path

import cv2 as cv
import mediapipe as mp
import numpy as np


MODEL_PATH = (
    Path(__file__).resolve().parent
    / "model"
    / "efficientdet_lite0.tflite"
)

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Không tìm thấy model tại: {MODEL_PATH}"
    )

base_options = mp.tasks.BaseOptions(
    model_asset_path=str(MODEL_PATH)
)

options = mp.tasks.vision.ObjectDetectorOptions(
    base_options=base_options,
    running_mode=mp.tasks.vision.RunningMode.IMAGE,
    max_results=100,
    score_threshold=0.3,
)

detector = (
    mp.tasks.vision.ObjectDetector
    .create_from_options(options)
)


def detect_person(frame: np.ndarray):
    """
    Nhận một ảnh OpenCV và trả về danh sách bounding box
    của những đối tượng có nhãn person.
    """
    if frame is None:
        raise ValueError("Khung hình đầu vào không hợp lệ.")

    frame_rgb = cv.cvtColor(
        frame,
        cv.COLOR_BGR2RGB,
    )

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=frame_rgb,
    )

    result = detector.detect(mp_image)
    output = []

    for detection in result.detections:
        if not detection.categories:
            continue

        category = detection.categories[0]

        if category.category_name != "person":
            continue

        bbox = detection.bounding_box

        output.append(
            {
                "x": int(bbox.origin_x),
                "y": int(bbox.origin_y),
                "width": int(bbox.width),
                "height": int(bbox.height),
                "score": round(
                    float(category.score),
                    4,
                ),
            }
        )

    return output

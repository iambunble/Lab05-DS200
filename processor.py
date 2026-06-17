import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

import base64
import json
import socket

import cv2 as cv
import numpy as np
from pyspark import StorageLevel
from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext

from detect_object import detect_person


class Config:
    CAMERA_HOST = "127.0.0.1"
    CAMERA_PORT = 6100

    STORAGE_HOST = "127.0.0.1"
    STORAGE_PORT = 6200

    BATCH_INTERVAL = 1


def decode_image(encoded_image):
    """Giải mã Base64 thành ảnh OpenCV."""
    image_bytes = base64.b64decode(
        encoded_image
    )

    image_array = np.frombuffer(
        image_bytes,
        dtype=np.uint8,
    )

    image = cv.imdecode(
        image_array,
        cv.IMREAD_COLOR,
    )

    if image is None:
        raise ValueError(
            "Không giải mã được khung hình."
        )

    return image


def send_to_storage(payload):
    """Gửi một kết quả sang Storage Server."""
    message = json.dumps(
        payload,
        ensure_ascii=False,
    ).encode("utf-8")

    with socket.create_connection(
        (
            Config.STORAGE_HOST,
            Config.STORAGE_PORT,
        ),
        timeout=10,
    ) as storage_socket:
        storage_socket.sendall(message)


def process_image(item):
    """Nhận diện một frame và gửi kết quả lưu trữ."""
    image = decode_image(
        item["image"]
    )
    timestamp = item["timestamp"]

    bboxes = detect_person(image)

    result = {
        "timestamp": timestamp,
        "person_count": len(bboxes),
        "bboxes": bboxes,
    }

    send_to_storage(result)

    print(
        f"[PROCESSING SERVER] Frame {timestamp} - "
        f"Số người: {len(bboxes)}"
    )


def parse_json(payload):
    return json.loads(payload)


def process_batch(batch_time, rdd):
    try:
        records = rdd.collect()

        if not records:
            return

        print(
            f"[PROCESSING SERVER] Batch {batch_time}: "
            f"{len(records)} frame"
        )

        for item in records:
            try:
                process_image(item)
            except Exception as error:
                print(
                    "[PROCESSING SERVER] "
                    f"Lỗi xử lý một frame: {error}"
                )

    except Exception as error:
        # Không để một batch lỗi làm dừng toàn bộ StreamingContext.
        print(
            "[PROCESSING SERVER] "
            f"Lỗi xử lý batch: {error}"
        )


def main():
    spark = (
        SparkSession.builder
        .master("local[2]")
        .appName(
            "LAB 5 - Person Counting Video Streaming"
        )
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel(
        "WARN"
    )

    streaming_context = StreamingContext(
        spark.sparkContext,
        Config.BATCH_INTERVAL,
    )

    stream = streaming_context.socketTextStream(
        Config.CAMERA_HOST,
        Config.CAMERA_PORT,
        storageLevel=StorageLevel.MEMORY_AND_DISK,
    )

    json_stream = stream.map(
        parse_json
    )

    json_stream.foreachRDD(
        process_batch
    )

    print(
        "[PROCESSING SERVER] Spark Streaming đã khởi động."
    )
    print(
        f"[PROCESSING SERVER] Đang nhận frame tại "
        f"{Config.CAMERA_HOST}:{Config.CAMERA_PORT}"
    )
    print(
        f"[PROCESSING SERVER] Kết quả được gửi đến "
        f"{Config.STORAGE_HOST}:{Config.STORAGE_PORT}"
    )
    print(
        "[PROCESSING SERVER] Nhấn Ctrl+C để dừng."
    )

    streaming_context.start()

    try:
        streaming_context.awaitTermination()

    except KeyboardInterrupt:
        print(
            "\n[PROCESSING SERVER] Đang dừng Spark..."
        )

        streaming_context.stop(
            stopSparkContext=True,
            stopGraceFully=True,
        )


if __name__ == "__main__":
    main()

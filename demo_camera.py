import cv2 as cv

from detect_object import detect_person


class Config:
    CAMERA_INDEX = 0
    FRAME_WIDTH = 800
    FRAME_HEIGHT = 480
    WINDOW_NAME = "LAB 5 - Camera Detection"


def open_camera():
    camera = cv.VideoCapture(
        Config.CAMERA_INDEX,
        cv.CAP_DSHOW,
    )

    if not camera.isOpened():
        camera = cv.VideoCapture(
            Config.CAMERA_INDEX
        )

    if not camera.isOpened():
        raise RuntimeError(
            "Không mở được camera. "
            "Hãy kiểm tra quyền camera hoặc đổi CAMERA_INDEX."
        )

    return camera


def draw_result(frame, bboxes):
    for index, bbox in enumerate(bboxes, start=1):
        x = int(bbox["x"])
        y = int(bbox["y"])
        width = int(bbox["width"])
        height = int(bbox["height"])
        score = float(bbox.get("score", 0))

        cv.rectangle(
            frame,
            (x, y),
            (x + width, y + height),
            (0, 255, 0),
            2,
        )

        label = f"Person {index} - {score:.2f}"

        cv.putText(
            frame,
            label,
            (x, max(25, y - 10)),
            cv.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2,
        )

    cv.putText(
        frame,
        f"Person count: {len(bboxes)}",
        (20, 35),
        cv.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 255, 0),
        2,
    )


def main():
    camera = open_camera()

    print("[DEMO CAMERA] Camera đã mở.")

    try:
        while True:
            ret, frame = camera.read()

            if not ret:
                print(
                    "[DEMO CAMERA] Không đọc được khung hình."
                )
                continue

            frame = cv.flip(frame, 1)

            frame = cv.resize(
                frame,
                (
                    Config.FRAME_WIDTH,
                    Config.FRAME_HEIGHT,
                ),
            )

            bboxes = detect_person(frame)

            draw_result(
                frame,
                bboxes,
            )

            cv.imshow(
                Config.WINDOW_NAME,
                frame,
            )

            if cv.waitKey(1) & 0xFF == ord("q"):
                print(
                    "[DEMO CAMERA] Đã dừng bằng phím q."
                )
                break

    except KeyboardInterrupt:
        print(
            "\n[DEMO CAMERA] Đã dừng bằng Ctrl+C."
        )

    finally:
        camera.release()
        cv.destroyAllWindows()


if __name__ == "__main__":
    main()
import base64
import json
import socket
import time

import cv2 as cv


class Config:
    HOST = "127.0.0.1"
    PORT = 6100
    CAMERA_INDEX = 0
    FRAME_WIDTH = 800
    FRAME_HEIGHT = 480

    SEND_INTERVAL = 1.0


def create_camera_server():
    """Tạo TCP server để Processing Server kết nối vào."""
    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )
    server_socket.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1,
    )
    server_socket.bind(
        (Config.HOST, Config.PORT)
    )
    server_socket.listen(1)

    print(
        f"[CAMERA SERVER] Đang chờ Processing Server "
        f"kết nối tại {Config.HOST}:{Config.PORT}..."
    )

    connection, address = server_socket.accept()

    print(
        f"[CAMERA SERVER] Đã kết nối với {address}"
    )

    return server_socket, connection


def open_camera():
    """Mở webcam trên Windows."""
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
            "Hãy kiểm tra quyền camera hoặc CAMERA_INDEX."
        )

    return camera


def encode_frame(frame):
    """Nén khung hình thành JPEG rồi mã hóa Base64."""
    encode_options = [
        int(cv.IMWRITE_JPEG_QUALITY),
        75,
    ]

    encoded_ok, buffer = cv.imencode(
        ".jpg",
        frame,
        encode_options,
    )

    if not encoded_ok:
        raise RuntimeError(
            "Không mã hóa được khung hình."
        )

    return base64.b64encode(
        buffer.tobytes()
    ).decode("utf-8")


def main():
    camera = open_camera()
    server_socket = None
    tcp_connection = None

    try:
        server_socket, tcp_connection = (
            create_camera_server()
        )

        print(
            "[CAMERA SERVER] Đang gửi liên tục. "
            "Nhấn Ctrl+C tại terminal này để dừng."
        )

        while True:
            ret, frame = camera.read()

            if not ret:
                print(
                    "[CAMERA SERVER] Không đọc được khung hình."
                )
                time.sleep(0.5)
                continue

            frame = cv.flip(frame, 1)
            frame = cv.resize(
                frame,
                (
                    Config.FRAME_WIDTH,
                    Config.FRAME_HEIGHT,
                ),
            )

            payload = {
                "image": encode_frame(frame),
                "timestamp": time.time(),
            }

            # socketTextStream tách từng bản ghi theo ký tự xuống dòng.
            message = (
                json.dumps(payload) + "\n"
            ).encode("utf-8")

            tcp_connection.sendall(message)

            print(
                f"[CAMERA SERVER] Đã gửi frame "
                f"{payload['timestamp']}"
            )

            cv.imshow(
                "LAB 5 - Camera",
                frame,
            )

            if cv.waitKey(1) & 0xFF == ord("q"):
                print(
                    "[CAMERA SERVER] Đã nhận phím q."
                )
                break

            time.sleep(
                Config.SEND_INTERVAL
            )

    except KeyboardInterrupt:
        print(
            "\n[CAMERA SERVER] Đã dừng bằng Ctrl+C."
        )

    except (
        BrokenPipeError,
        ConnectionResetError,
    ):
        print(
            "[CAMERA SERVER] Processing Server "
            "đã ngắt kết nối."
        )

    except Exception as error:
        print(
            f"[CAMERA SERVER] Lỗi: {error}"
        )

    finally:
        camera.release()
        cv.destroyAllWindows()

        if tcp_connection is not None:
            tcp_connection.close()

        if server_socket is not None:
            server_socket.close()


if __name__ == "__main__":
    main()

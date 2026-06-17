import json
import socket
from pathlib import Path


class Config:
    HOST = "127.0.0.1"
    PORT = 6200
    OUTPUT_DIR = (
        Path(__file__).resolve().parent
        / "json_output"
    )


def receive_all(connection):
    data = b""

    while True:
        chunk = connection.recv(4096)

        if not chunk:
            break

        data += chunk

    return data


def save_result(payload):
    """Lưu ngay một kết quả thành file JSON."""
    Config.OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = payload["timestamp"]

    output_path = (
        Config.OUTPUT_DIR
        / f"{timestamp}.json"
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as output_file:
        json.dump(
            payload,
            output_file,
            ensure_ascii=False,
            indent=4,
        )

        output_file.flush()

    return output_path


def main():
    Config.OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

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
        (
            Config.HOST,
            Config.PORT,
        )
    )
    server_socket.listen(10)

    print(
        f"[STORAGE SERVER] Đang lắng nghe tại "
        f"{Config.HOST}:{Config.PORT}..."
    )
    print(
        f"[STORAGE SERVER] Thư mục output: "
        f"{Config.OUTPUT_DIR.resolve()}"
    )
    print(
        "[STORAGE SERVER] Nhấn Ctrl+C để dừng."
    )

    saved_count = 0

    try:
        while True:
            connection, address = (
                server_socket.accept()
            )

            with connection:
                data = receive_all(
                    connection
                )

            if not data:
                continue

            try:
                payload = json.loads(
                    data.decode("utf-8")
                )

                output_path = save_result(
                    payload
                )

                saved_count += 1

                print(
                    f"[STORAGE SERVER] Đã lưu "
                    f"{output_path.resolve()} - "
                    f"Số người: "
                    f"{payload['person_count']} - "
                    f"Tổng file: {saved_count}"
                )

            except Exception as error:
                # Không để một bản ghi lỗi làm dừng server.
                print(
                    "[STORAGE SERVER] "
                    f"Lỗi lưu dữ liệu: {error}"
                )

    except KeyboardInterrupt:
        print(
            "\n[STORAGE SERVER] Đã dừng bằng Ctrl+C."
        )

    finally:
        server_socket.close()


if __name__ == "__main__":
    main()

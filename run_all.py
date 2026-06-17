import subprocess
import sys
import time
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
PYTHON_EXE = Path(sys.executable).resolve()


def open_new_terminal(script_name: str):
    script_path = PROJECT_DIR / script_name

    if not script_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {script_path}")

    subprocess.Popen(
        [str(PYTHON_EXE), str(script_path)],
        cwd=str(PROJECT_DIR),
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )


def main():
    print(f"Python đang dùng: {PYTHON_EXE}")
    print("Đang mở 3 server của LAB 5...")

    open_new_terminal("storage_server.py")
    time.sleep(1)

    open_new_terminal("sender.py")
    time.sleep(2)

    open_new_terminal("processor.py")

    print("Đã mở 3 cửa sổ chạy song song.")
    print("Thứ tự: Storage Server -> Camera Server -> Processing Server.")


if __name__ == "__main__":
    main()

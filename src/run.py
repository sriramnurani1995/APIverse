import subprocess
import time

if __name__ == "__main__":
    fastapi_process = subprocess.Popen(["python", "-m", "uvicorn", "services.fastapi_service:app", "--host", "0.0.0.0", "--port", "8000"])
    time.sleep(4)
    flask_process = subprocess.Popen(["python", "app.py"])

    try:
        flask_process.wait()
        fastapi_process.wait()
    except KeyboardInterrupt:
        fastapi_process.terminate()
        flask_process.terminate()

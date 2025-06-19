import subprocess
import time
import sys

# Start FastAPI server on all interfaces
server_proc = subprocess.Popen([
    sys.executable,
    "-m",
    "uvicorn",
    "main:app",
    "--host", "0.0.0.0",
    "--port", "8000",
    "--reload"
])

# time for server to start
time.sleep(2)

# Start the Tkinter interface
gui_proc = subprocess.Popen(["python", "interface/gui.py"])

# Wait for GUI to close to avoid conflicts
gui_proc.wait()

# Clean up server process
server_proc.terminate()

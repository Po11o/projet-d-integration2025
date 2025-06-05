import subprocess
import time
import sys

subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app", "--reload"])


# Give server time to boot up (optional but safer)
time.sleep(2)

# Start the Tkinter interface
gui_proc = subprocess.Popen(["python", "interface.py"])

gui_proc.wait()

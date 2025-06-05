import tkinter as tk
from tkinter import scrolledtext
import datetime
import requests

ROBOT_ID = 1  # You can change this or make it selectable

API_URL = "http://localhost:8000/movement"

class RobotControlConsole:
    def __init__(self, root):
        self.root = root
        self.root.title("REF Robot Control Console")
        self.root.geometry("500x400")

        # Buttons
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        self.start_btn = tk.Button(button_frame, text="Start", command=lambda: self.send_command("Start"))
        self.stop_btn = tk.Button(button_frame, text="Stop", command=lambda: self.send_command("Stop"))
        self.left_btn = tk.Button(button_frame, text="Turn Left", command=lambda: self.send_command("Turn Left"))
        self.right_btn = tk.Button(button_frame, text="Turn Right", command=lambda: self.send_command("Turn Right"))
        self.obstacle_btn = tk.Button(root, text="Simulate Obstacle Stop", command=lambda: self.send_command("Obstacle Stop"))

        self.start_btn.grid(row=0, column=0, padx=5)
        self.stop_btn.grid(row=0, column=1, padx=5)
        self.left_btn.grid(row=0, column=2, padx=5)
        self.right_btn.grid(row=0, column=3, padx=5)
        self.obstacle_btn.pack(pady=10)

        # Log
        self.log_box = scrolledtext.ScrolledText(root, width=60, height=15, state='disabled')
        self.log_box.pack(padx=10, pady=10)

    def log(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_box.config(state='normal')
        self.log_box.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_box.yview(tk.END)
        self.log_box.config(state='disabled')

    def send_command(self, action):
        try:
            response = requests.post(API_URL, json={
                "robot_id": ROBOT_ID,
                "action": action
            })
            if response.status_code == 200:
                self.log(f"Sent command: {action}")
            else:
                self.log(f"Error sending command: {response.status_code}")
        except Exception as e:
            self.log(f"Error: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RobotControlConsole(root)
    root.mainloop()

import tkinter as tk
from tkinter import scrolledtext
import datetime
import requests
import random

ROBOT_ID = 1
API_URL = "http://localhost:8000/movement"

class RobotControlConsole:
    def __init__(self, root):
        self.root = root
        self.root.title("REF Robot Control Console")
        self.root.geometry("550x500")

        # Inventories
        self.depot1_inventory = 0
        self.depot2_inventory = 0

        # --- Control buttons ---
        button_frame = tk.LabelFrame(root, text="Robot Controls", padx=10, pady=10)
        button_frame.pack(pady=10)

        self.start_btn = tk.Button(button_frame, text="Start", width=15, command=lambda: self.send_command("Start"))
        self.stop_btn = tk.Button(button_frame, text="Stop", width=15, command=lambda: self.send_command("Stop"))

        self.start_btn.grid(row=0, column=0, padx=5, pady=5)
        self.stop_btn.grid(row=0, column=1, padx=5, pady=5)

        # --- Zone buttons ---
        zone_frame = tk.LabelFrame(root, text="Zones", padx=10, pady=10)
        zone_frame.pack(pady=10)

        self.zone1_btn = tk.Button(zone_frame, text="Zone 1", width=15, command=lambda: self.handle_zone(1))
        self.zone2_btn = tk.Button(zone_frame, text="Zone 2", width=15, command=lambda: self.handle_zone(2))
        self.zone3_btn = tk.Button(zone_frame, text="Zone 3", width=15, command=lambda: self.handle_zone(3))
        self.zone4_btn = tk.Button(zone_frame, text="Zone 4", width=15, command=lambda: self.handle_zone(4))
        self.zone5_btn = tk.Button(zone_frame, text="Zone 5", width=15, command=lambda: self.handle_zone(5))

        self.zone1_btn.grid(row=0, column=0, padx=5, pady=5)
        self.zone2_btn.grid(row=0, column=1, padx=5, pady=5)
        self.zone3_btn.grid(row=0, column=2, padx=5, pady=5)
        self.zone4_btn.grid(row=1, column=0, padx=5, pady=5)
        self.zone5_btn.grid(row=1, column=1, padx=5, pady=5)

        # --- Log box ---
        log_frame = tk.LabelFrame(root, text="Event Log", padx=10, pady=10)
        log_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.log_box = scrolledtext.ScrolledText(log_frame, width=70, height=20, state='disabled')
        self.log_box.pack(fill="both", expand=True)

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
                result = response.json()
                data = result.get("data")
                if data:
                    robot_id = data.get("robot_id", "Unknown")
                    action = data.get("action", "Unknown")
                    self.log(f"Server confirmed: Robot {robot_id} performed '{action}'")
                else:
                    self.log("No movement data received.")
            else:
                self.log(f"Error sending command: {response.status_code}")
        except Exception as e:
            self.log(f"Error sending command: {e}")

    def handle_zone(self, zone_number):
        self.log("Moving forward...")
        self.log(f"Arriving at Zone {zone_number}")

        # Determine turn direction
        if zone_number == 3:
            turn_dir = "Turning left"
        else:
            turn_dir = "Turning right"

        self.log(turn_dir)
        self.log("Picking up cube")

        # Decide where to deposit cube
        if zone_number == 1:
            if self.depot1_inventory == self.depot2_inventory:
                chosen_depot = random.choice([1,2])
                self.log("Depots are equal, choosing random depot...")
            elif self.depot1_inventory < self.depot2_inventory:
                chosen_depot = 1
                self.log("Depot 1 has fewer cubes, choosing Depot 1")
            else:
                chosen_depot = 2
                self.log("Depot 2 has fewer cubes, choosing Depot 2")

        elif zone_number in [2,3]:
            chosen_depot = 1
            self.log("Going to Depot 1")

        elif zone_number in [4,5]:
            chosen_depot = 2
            self.log("Going to Depot 2")

        # Simulate depositing cube
        self.log("Turning left")
        self.log("Moving forward...")
        self.log(f"Depositing cube at Depot {chosen_depot}")

        # Update inventory
        if chosen_depot == 1:
            self.depot1_inventory += 1
        else:
            self.depot2_inventory += 1

        # Send deposit action to server
        self.send_command(f"Deposited cube at Depot {chosen_depot} from Zone {zone_number}")
        

if __name__ == "__main__":
    root = tk.Tk()
    app = RobotControlConsole(root)
    root.mainloop()

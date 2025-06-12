import tkinter as tk
from tkinter import ttk, scrolledtext
import datetime
import requests

# Robot Control Console
# This is a simple GUI application to control robots and send instructions.
class RobotControlConsole:
    def __init__(self, root):
        self.root = root
        self.root.title("Robot Control Console")
        self.root.geometry("550x600")
        self.BASE_URL = "http://localhost:8000"  # Add this line at the start of __init__

        # Add Robot
        add_f = tk.LabelFrame(root, text="Add New Robot", padx=10, pady=10)
        add_f.pack(pady=10)
        self.mac = tk.Entry(add_f, width=30)
        self.mac.grid(row=0, column=0, padx=5)
        self.mac.insert(0, "00:11:22:33:44:55")
        tk.Button(add_f, text="Add Robot", command=self.add_robot)\
          .grid(row=0, column=1, padx=5)

        # Event Log (must exist before any calls to log())
        log_f = tk.LabelFrame(root, text="Event Log", padx=10, pady=10)
        log_f.pack(fill="both", expand=True, padx=10, pady=10)
        self.log_box = scrolledtext.ScrolledText(log_f, state='disabled', width=70, height=10)
        self.log_box.pack(fill="both", expand=True)

        # Select Robot
        sel_f = tk.LabelFrame(root, text="Select Robot", padx=10, pady=10)
        sel_f.pack(pady=10)
        self.robot_var = tk.StringVar()
        self.robot_dd = ttk.Combobox(sel_f, textvariable=self.robot_var, state="readonly")
        self.robot_dd.pack()

        # Fetch robots now that log_box exists
        self.refresh_robots()

        # Select Cubes
        cube_f = tk.LabelFrame(root, text="Select Cubes", padx=10, pady=10)
        cube_f.pack(pady=10)
        self.cube_vars = {}
        for i, c in enumerate([2,3,6,7,10]):
            var = tk.BooleanVar()
            self.cube_vars[c] = var
            tk.Checkbutton(cube_f, text=f"Cube {c}", variable=var)\
              .grid(row=0, column=i, padx=5)
        tk.Button(cube_f, text="Send Instructions", command=self.send_instructions)\
          .grid(row=1, column=0, columnspan=5, pady=10)

    # Refresh the list of robots from the server.
    def refresh_robots(self):
        try:
            r = requests.get(f"{self.BASE_URL}/robots/list")
            r.raise_for_status()
            data = r.json()
            ids = [x["id"] for x in data]
            self.robot_dd["values"] = ids
            if ids:
                self.robot_dd.current(0)
        except Exception as e:
            self.log(f"Error fetching robots: {e}")

    # Add a new robot with the MAC address entered in the Entry widget.
    # This sends a POST request to the /robots endpoint.
    def add_robot(self):
        mac = self.mac.get().strip()
        if not mac:
            self.log("Please enter a MAC address")
            return
        try:
            print(f"Adding robot with MAC: {mac}")
            r = requests.post(
                url=f"{self.BASE_URL}/robots",
                json={"robot_id": mac}
            )

            print(f"Response: {r.status_code} {r.text}")
            if r.status_code == 200:
                self.log(f"Added robot: {mac}")
                self.refresh_robots()
            else:
                self.log("Error adding robot: " + r.json().get("detail", r.text))
        except Exception as e:
            self.log(f"Error adding robot: {e}")

    # Send instructions to the selected robot with the selected cubes.
    # This sends a POST request to the /instructions endpoint.
    def send_instructions(self):
        robot = self.robot_var.get()
        if not robot:
            self.log("Please select a robot")
            return
        selected = [c for c,v in self.cube_vars.items() if v.get()]
        if not selected:
            self.log("Please select at least one cube")
            return
        try:
            r = requests.post(
                f"{self.BASE_URL}/instructions",
                json={"robot_id": robot, "blocks": selected}
            )
            if r.status_code == 200:
                self.log(f"Instructions sent: {selected}")
            else:
                self.log("Error sending: " + r.json().get("detail", r.text))
        except Exception as e:
            self.log(f"Error sending instructions: {e}")
    
    # Log messages to the event log box with a timestamp.
    def log(self, msg):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_box.config(state='normal')
        self.log_box.insert(tk.END, f"[{ts}] {msg}\n")
        self.log_box.yview(tk.END)
        self.log_box.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    RobotControlConsole(root)
    root.mainloop()

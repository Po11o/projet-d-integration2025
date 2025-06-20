import tkinter as tk
from tkinter import ttk, scrolledtext
import requests
import datetime

class RobotControlMinimal:
    def __init__(self, root):
        self.root = root
        self.root.title("Command Console")
        self.API_URL = "http://localhost:8000"
        self.root.configure(bg="#1c1f2b")

        self.blocks = {
            2: {"name": "🟡 Yellow", "color": "#f7c948"},
            3: {"name": "🔴 Red", "color": "#e94e3f"},
            6: {"name": "💗 Pink", "color": "#f471b5"},
            7: {"name": "🟣 Purple", "color": "#9b59b6"},
            10: {"name": "🟢 Green", "color": "#2ecc71"}
        }

        # Create main frame
        frame = tk.Frame(self.root, padx=12, pady=12, bg="#1c1f2b")
        frame.pack()

        # Robot dropdown
        self.robot_var = tk.StringVar()
        self.robot_dd = ttk.Combobox(
            frame, 
            textvariable=self.robot_var,
            state="readonly",
            width=42
        )
        self.robot_dd.grid(row=0, column=0, columnspan=5, pady=6)

        # Block checkboxes
        self.cube_vars = {}
        for i, (block_id, block_info) in enumerate(self.blocks.items()):
            var = tk.BooleanVar()
            self.cube_vars[block_id] = var
            cb = tk.Checkbutton(
                frame,
                text=block_info["name"],
                variable=var,
                bg="#1c1f2b",
                fg=block_info["color"],
                selectcolor="#2a2d3e",
                activebackground="#1c1f2b",
                activeforeground=block_info["color"],
                font=("Segoe UI", 10)
            )
            cb.grid(row=1, column=i, padx=4)

        # Buttons
        btn_frame = tk.Frame(frame, bg="#1c1f2b")
        btn_frame.grid(row=2, column=0, columnspan=5, pady=12)

        tk.Button(
            btn_frame,
            text="🚀 Deploy",
            command=self.send_instructions,
            bg="#ff6b00",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=20
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="🔄 Reset",
            command=self.reset_instructions,
            bg="#e74c3c",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=20
        ).pack(side=tk.LEFT, padx=5)

        # Log area
        self.log_box = scrolledtext.ScrolledText(
            self.root,
            height=10,
            bg="#12141e",
            fg="#00ff90",
            font=("Consolas", 10),
            insertbackground="#00ff90"
        )
        self.log_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Initial robot load
        self.refresh_robots()

    def refresh_robots(self):
        try:
            response = requests.get(f"{self.API_URL}/robots/list")
            response.raise_for_status()
            robots = response.json()
            
            self.robot_options = {
                f"{robot.get('name', '')} ({robot['id']})": robot['id']
                for robot in robots
            }
            self.robot_dd["values"] = list(self.robot_options.keys())
            if self.robot_options:
                self.robot_dd.current(0)
                
        except Exception as e:
            self.log(f"❌ Error loading robots: {e}")

    def send_instructions(self):
        selected = self.robot_var.get()
        if not selected:
            self.log("⚠️ Please select a robot")
            return

        robot_id = self.robot_options[selected]
        blocks = [b for b, v in self.cube_vars.items() if v.get()]
        
        if not blocks:
            self.log("⚠️ Please select at least one block")
            return

        try:
            response = requests.post(
                f"{self.API_URL}/instructions/create",
                json={"robot_id": robot_id, "blocks": blocks}
            )
            response.raise_for_status()
            block_names = [self.blocks[b]["name"] for b in blocks]
            self.log(f"✅ Instructions sent to {selected}: {', '.join(block_names)}")
            
        except Exception as e:
            self.log(f"❌ Error sending instructions: {e}")

    def reset_instructions(self):
        selected = self.robot_var.get()
        if not selected:
            self.log("⚠️ Please select a robot")
            return

        robot_id = self.robot_options[selected]
        try:
            response = requests.post(
                f"{self.API_URL}/reset",
                params={"robot_id": robot_id}
            )
            response.raise_for_status()
            self.log(f"🔄 Reset instructions for {selected}")
            
        except Exception as e:
            self.log(f"❌ Error resetting instructions: {e}")

    def log(self, msg):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{timestamp}] {msg}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = RobotControlMinimal(root)
    root.mainloop()
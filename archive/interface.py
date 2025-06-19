import tkinter as tk
from tkinter import ttk, scrolledtext
import requests
import datetime

class RobotControlMinimal:
    def __init__(self, root):
        self.root = root
        self.root.title("Command Console")
        self.BASE_URL = "http://localhost:8000"
        self.root.configure(bg="#1c1f2b")

        # Block definitions with Martian-style colors
        self.blocks = {
            2: {"name": "Yellow Block", "color": "#f7c948"},
            3: {"name": "Red Block", "color": "#e94e3f"},
            6: {"name": "Pink Block", "color": "#f471b5"},
            7: {"name": "Purple Block", "color": "#9b59b6"},
            10: {"name": "Green Block", "color": "#2ecc71"}
        }

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCombobox", fieldbackground="#2b2e3b", background="#2b2e3b", foreground="#ffffff")

        frame = tk.Frame(root, padx=12, pady=12, bg="#1c1f2b")
        frame.pack()

        # Robot dropdown
        self.robot_var = tk.StringVar()
        self.robot_dd = ttk.Combobox(frame, textvariable=self.robot_var, state="readonly", width=42)
        self.robot_dd.grid(row=0, column=0, columnspan=5, pady=6)

        # Colored block checkboxes
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
                activeforeground="#ffffff",
                activebackground="#1c1f2b",
                selectcolor="#1c1f2b",
                font=("Consolas", 10, "bold")
            )
            cb.grid(row=1, column=i, padx=4, pady=4)

        tk.Button(
            frame,
            text="🚀 Deploy Instructions",
            command=self.send_instructions,
            bg="#ff6b00",
            fg="white",
            activebackground="#e55b00",
            relief=tk.FLAT,
            font=("Consolas", 10, "bold"),
            padx=8, pady=4
        ).grid(row=2, column=0, columnspan=5, pady=12)

        # Log area
        self.log_box = scrolledtext.ScrolledText(
            root, state='disabled', height=10, bg="#12141e", fg="#00ff90",
            insertbackground="white", font=("Courier New", 10), borderwidth=0
        )
        self.log_box.pack(fill="both", expand=True, padx=10, pady=10)

        self.refresh_robots()

    def refresh_robots(self):
        try:
            r = requests.get(f"{self.BASE_URL}/robots/list")
            r.raise_for_status()
            robots = r.json()
            self.robot_options = {
                f"{r.get('name', 'Unknown')} - {r['id']}": r['id']
                for r in robots
            }
            self.robot_dd["values"] = list(self.robot_options.keys())
            if self.robot_options:
                self.robot_dd.current(0)
        except Exception as e:
            self.log(f"⚠️ Error fetching robots: {e}")

    def send_instructions(self):
        selected = self.robot_var.get()
        if not selected:
            self.log("⚠️ Please select a robot")
            return

        robot_id = self.robot_options[selected]
        blocks = [b for b, v in self.cube_vars.items() if v.get()]
        if not blocks:
            self.log("⚠️ No blocks selected")
            return

        block_names = [self.blocks[b]["name"] for b in blocks]

        try:
            r = requests.post(
                f"{self.BASE_URL}/instructions/create",
                json={"robot_id": robot_id, "blocks": blocks}
            )
            if r.status_code in (200, 201, 303):
                self.log(f"✅ Sent to {selected}: {', '.join(block_names)}")
            else:
                detail = r.json().get("detail", r.text)
                self.log(f"❌ Error: {detail}")
        except Exception as e:
            self.log(f"❌ Request failed: {e}")

    def log(self, msg):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_box.config(state='normal')
        self.log_box.insert(tk.END, f"[{ts}] {msg}\n")
        self.log_box.yview(tk.END)
        self.log_box.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    RobotControlMinimal(root)
    root.mainloop()

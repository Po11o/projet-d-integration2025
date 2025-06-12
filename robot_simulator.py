import requests
import random
import time
from datetime import datetime
from statistics import mean

class RobotSimulator:
    def __init__(self, robot_id, base_url="http://localhost:8000"):
        self.robot_id = robot_id
        self.base_url = base_url.rstrip("/")
        self.current_line = 1
        self.speeds = []
        self.blocks = []

    def wait_for_instruction(self, poll_interval=5):
        """Poll /instructions until we receive a non-empty blocks list."""
        print(f"[{datetime.now().isoformat()}] Waiting for instructions for {self.robot_id}...")
        while True:
            try:
                resp = requests.get(
                    f"{self.base_url}/instructions",
                    params={"robot_id": self.robot_id},
                    timeout=3
                )
                resp.raise_for_status()
                data = resp.json()
                blocks = data.get("blocks", [])
                if blocks:
                    self.blocks = blocks
                    print(f"[{datetime.now().isoformat()}] Received instruction blocks: {blocks}")
                    return
                else:
                    # no pending instruction yet
                    time.sleep(poll_interval)
            except requests.RequestException as e:
                print(f"[ERROR] polling instructions: {e}")
                time.sleep(poll_interval)

    def send_telemetry(self):
        """Send one telemetry datapoint to /telemetry."""
        speed = random.uniform(0, 1.0)
        self.speeds.append(speed)

        payload = {
            "robot_id": self.robot_id,
            "speed": speed,
            "ultrasonic_distance": random.uniform(0, 100),
            "current_line": self.current_line,
            "gripper_state": random.choice(["open", "closed"])
        }

        try:
            resp = requests.post(f"{self.base_url}/telemetry", json=payload, timeout=3)
            resp.raise_for_status()
            print(f"[{datetime.now().isoformat()}] Telemetry sent: line={self.current_line}, speed={speed:.3f}")
        except requests.RequestException as e:
            print(f"[ERROR] sending telemetry: {e}")

    def send_summary(self):
        """Compute average speed and POST it to /summary."""
        if not self.speeds:
            print("[WARN] No speeds recorded, skipping summary.")
            return
        avg_speed = mean(self.speeds)
        payload = {
            "robot_id": self.robot_id,
            "average_speed": avg_speed
        }
        try:
            resp = requests.post(f"{self.base_url}/summary", json=payload, timeout=3)
            resp.raise_for_status()
            print(f"[{datetime.now().isoformat()}] Summary sent: average_speed={avg_speed:.3f}")
        except requests.RequestException as e:
            print(f"[ERROR] sending summary: {e}")

    def run(self):
        print(f"=== Starting simulator for robot {self.robot_id} ===")
        # 1) wait for instructions
        self.wait_for_instruction()

        # 2) execute mission (13 lines)
        while self.current_line <= 13:
            self.send_telemetry()
            time.sleep(5)
            self.current_line += 1

        # 3) send summary
        print("=== Mission complete, sending summary ===")
        self.send_summary()
        print(f"=== {self.robot_id} done ===")

if __name__ == "__main__":
    simulator = RobotSimulator("REF-01", base_url="http://localhost:8000")
    simulator.run()

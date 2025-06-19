from machine import Pin, time_pulse_us
from time import sleep

class Ultrason:
    def __init__(self, trigger_pin, echo_pin, timeout_us=30000):
        self.trigger = Pin(trigger_pin, mode=Pin.OUT)
        self.echo = Pin(echo_pin, mode=Pin.IN)
        self.timeout_us = timeout_us

    def distance_cm(self):
        # Send trigger pulse
        self.trigger.off()
        sleep(0.002)  # let sensor settle
        self.trigger.on()
        sleep(0.00001)  # 10us pulse
        self.trigger.off()

        # Measure echo pulse width
        duration = time_pulse_us(self.echo, 1, self.timeout_us)

        if duration < 0:
            return -1  # timeout or error

        # Distance in cm: speed of sound = 343 m/s = 0.0343 cm/us
        distance = (duration * 0.0343) / 2
        return round(distance, 2)

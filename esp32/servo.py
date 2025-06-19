from machine import Pin, PWM
from time import sleep

class Servo:
    def __init__(self, pin, freq=50, min_us=500, max_us=2500, max_angle=180):
        self.pwm = PWM(Pin(pin), freq=freq)
        self.min_us = min_us
        self.max_us = max_us
        self.max_angle = max_angle
        self.freq = freq

    def set_angle(self, angle):
        if angle < 0:
            angle = 0
        elif angle > self.max_angle:
            angle = self.max_angle

        # Calculate pulse width in microseconds
        us = self.min_us + (self.max_us - self.min_us) * angle / self.max_angle

        # Convert us to duty for ESP32: duty = us / 1000000 * freq * 1023
        duty = int(us * self.freq * 1023 / 1000000)
        self.pwm.duty(duty)

    def deinit(self):
        self.pwm.deinit()

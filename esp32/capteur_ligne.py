from machine import Pin

class LineSensor:
    def __init__(self, d0_pin):
        self.d0 = Pin(d0_pin, Pin.IN)

    def line_detected(self):
        # Returns True if line is detected (usually D0 goes LOW on black line)
        return self.d0.value() == 1
      

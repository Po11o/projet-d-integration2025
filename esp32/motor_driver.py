class DCMotor:
    def __init__(self, pin1, pin2, enable_pin, min_duty=750, max_duty=1023):
        self.pin1 = pin1
        self.pin2 = pin2
        self.enable_pin = enable_pin
        self.min_duty = min_duty
        self.max_duty = max_duty

    def magnetic_stop(self, speed):
        self.enable_pin.duty(self.duty_cycle(speed))
        self.pin1.value(1)
        self.pin2.value(1)

    def forward(self, speed):
        self.enable_pin.duty(self.duty_cycle(speed))
        self.pin1.value(1)
        self.pin2.value(0)

    def backwards(self, speed):
        self.enable_pin.duty(self.duty_cycle(speed))
        self.pin1.value(0)
        self.pin2.value(1)

    def stop(self):
        self.enable_pin.duty(0)
        self.pin1.value(0)
        self.pin2.value(0)

    def duty_cycle(self, speed):
        if speed <= 0 or speed > 100:
            return 0
        return int(self.min_duty + (self.max_duty - self.min_duty) * ((speed - 1) / (100 - 1)))

from machine import Pin, PWM
import utime


class Servo:
    def __init__(self, MIN_DUTY=300000, MAX_DUTY=2300000, pin=0, freq=50):
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(freq)
        self.MIN_DUTY = MIN_DUTY
        self.MAX_DUTY = MAX_DUTY

    def rotateDeg(self, deg):
        if deg < 0:
            deg = 0
        elif deg > 180:
            deg = 180
        duty_ns = int(self.MAX_DUTY - deg * (self.MAX_DUTY - self.MIN_DUTY) / 180)
        self.pwm.duty_ns(duty_ns)


servo = Servo(pin=28)

servo.rotateDeg(0)

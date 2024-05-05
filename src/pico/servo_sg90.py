from machine import Pin, PWM
import utime


class Servo:
    def __init__(self, MIN_DUTY=500000, MAX_DUTY=2400000, pin=0, freq=50):
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(freq)
        self.MIN_DUTY = MIN_DUTY
        self.MAX_DUTY = MAX_DUTY

    def rotateDeg(self, deg):
        # サーボモータが振動する角度範囲を避けるために、デッドバンド（不感帯）を設定します。
        # 0度付近と180度付近の角度指定を避けます。今回は、0〜5度は5度に、175〜180度は175度に丸めています。
        if deg < 5:
            deg = 5
        elif deg > 175:
            deg = 175
        duty_ns = int(self.MIN_DUTY + deg * (self.MAX_DUTY - self.MIN_DUTY) / 180)
        self.pwm.duty_ns(duty_ns)


servo = Servo(pin=28)

servo.rotateDeg(90)

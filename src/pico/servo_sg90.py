from machine import Pin, PWM
import utime

pwm = PWM(Pin(0))  # GPIO 0にPWM設定
pwm.freq(50)  # PWM周波数を50Hzに


def servo_write(degrees):
    duty = int((degrees * 9500 / 180) + 2500)
    pwm.duty_u16(duty)


while True:
    servo_write(0)  # 0度の位置に
    utime.sleep(1)
    servo_write(90)  # 90度の位置に
    utime.sleep(1)
    servo_write(180)  # 180度の位置に
    utime.sleep(1)

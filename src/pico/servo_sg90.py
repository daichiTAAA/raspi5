from machine import PWM, Pin
from time import sleep

servo = PWM(Pin(28))
servo.freq(50)

angle_0 = int(2.5 / 20 * 65536)
angle_90 = int(1.5 / 20 * 65536)
angle_180 = int(0.5 / 20 * 65536)

servo.duty_u16(angle_0)
sleep(1)
servo.duty_u16(angle_90)
sleep(1)
servo.duty_u16(angle_180)
sleep(1)

servo.duty_u16(0)

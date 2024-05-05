from machine import Pin
import utime

led = Pin("LED", Pin.OUT)
print("Start flashing...")

while True:
    led.toggle()
    utime.sleep(1)
    print("cycle end")
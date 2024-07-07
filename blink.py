from machine import Pin
import time

pin = Pin("LED", Pin.OUT)

while True:
    pin.toggle()
    time.sleep(1)
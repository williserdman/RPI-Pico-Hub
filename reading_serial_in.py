from machine import UART, Pin

uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))
uart.init(115200, bits=8, parity=None, stop=1)

print("running loop")
while True:
    if (uart.any() > 0):
        print(uart.read().decode())
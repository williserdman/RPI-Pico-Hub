from usocket import socket
from machine import Pin,SPI
import urequests
import network
import time
import random

#W5x00 chip init
def w5x00_init():
    spi=SPI(0,2_000_000, mosi=Pin(19),miso=Pin(16),sck=Pin(18))
    nic = network.WIZNET5K(spi,Pin(17),Pin(20)) #spi,cs,reset pin
    nic.active(True)
    
#None DHCP
    nic.ifconfig(('192.168.2.2','255.255.255.0','192.168.2.1','8.8.8.8'))
    
#DHCP
    #nic.ifconfig('dhcp')
    print('IP address :', nic.ifconfig())
    
    while not nic.isconnected():
        time.sleep(1)
        #print(nic.regs())
    
def get_request():
    r = urequests.get('http://httpbin.org/get')
    r.raise_for_status
    print(r.status_code)
    print(r.text)
    r.close()
    
list_of_ids = ["ifd2", "fdjk32", "f34s"]
    
def post_request():
    r = urequests.post('http://192.168.2.1:5173/api/sensors',
                       headers={"Authorization": "willis_is_cool"},
                       json={
                           "sensorID": random.choice(list_of_ids),
                           "CO2": random.uniform(15, 30),
                           "temperature": random.uniform(15, 30),
                           "humidity": random.uniform(15, 30)})
    if not r:
        print('spreadsheet: no response received')
    print(r.content.decode("utf-8"))
    r.close()

def main():
    w5x00_init()
    for i in range(2):
        post_request()
        time.sleep(1)
        print("----------")

if __name__ == "__main__":
    main()
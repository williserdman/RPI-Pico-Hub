import rp2
import network
import usocket as socket
import time
from machine import Pin, SPI
import json
import select
# import urequests as requests # possible to use this maybe but not sure it seems like it's only for requests

led = Pin(25, Pin.OUT)

#W5x00 chip init
def w5x00_init():
    spi=SPI(0,2_000_000, mosi=Pin(19),miso=Pin(16),sck=Pin(18))
    nic = network.WIZNET5K(spi,Pin(17),Pin(20)) #spi,cs,reset pin
    nic.active(True)
    # for running on aredn
    #nic.ifconfig(('10.57.247.122','255.255.255.0','10.71.62.239','8.8.8.8'))
    # for running on local bridge
    #nic.ifconfig(('192.168.2.6','255.255.255.0','192.168.1.1','8.8.8.8'))
    nic.ifconfig('dhcp')
    print('IP address :', nic.ifconfig())
    while not nic.isconnected():
        time.sleep(1)
        #print(nic.ifconfig())
    print('netif changed ', nic.ifconfig())
w5x00_init()

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(10)

print('listening on')

def send_file(cl, filename, packet_size = 1024):
    with open(filename, "r") as f:
        info = f.read(packet_size)
        #print(info)
        # sending this in packets
        while info:
            cl.send(bytes(info, "utf-8"))
            info = f.read(packet_size)
    return 1

# Listen for connections
while True:
    try:
        cl, addr = s.accept()
        print('client connected from', addr)
        request = cl.recv(1024)
        request = str(request)
        print(request)
        
        json_req = request.find("/json-historic")
        
        # hard coding these in here for now
        is_css_file = request.find("/assets/index-ByVuC4zf.css")
        is_js_file = request.find("/assets/index-CHoWolui.js")
        
        print(json_req, is_css_file, is_js_file)
        
        if json_req == 6:
            # it is this page (or close enough)
            print("json req")
            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/json\rAccess-Control-Allow-Origin: *\r\n\r\n')
            send_file(cl, "data.json")
        elif is_css_file == 6:
            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/css\rConnection: close\r\n\r\n')
            print("sending css")
            send_file(cl, "dist/assets/index-ByVuC4zf.css")
        elif is_js_file == 6:
            cl.send('HTTP/1.0 200 OK\r\nContent-type: application/javascript\rConnection: close\r\n\r\n')
            print("sending js")
            send_file(cl, "dist/assets/index-CHoWolui.js")
        else:
            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\rConnection: close\r\n\r\n')
            print("sending index.html")
            send_file(cl, "dist/index.html")
        
        print(0)
        #cl.send('Connection: close\n')
        poller = select.poll()
        poller.register(cl, select.POLLIN)
        res = poller.poll(1000)  # time in milliseconds
        
        cl.close()
        print(2)


    except OSError as e:
        cl.close()
        print('connection closed', e)

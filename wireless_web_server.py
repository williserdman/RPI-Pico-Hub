import network
import socket
import time
from machine import Pin
import json
# import urequests as requests # possible to use this maybe but not sure it seems like it's only for requests

led = Pin("LED", Pin.OUT)

ssid = 'PSU Registered'
password = 'Iz4gMDvaRT5XXqTm'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

html = """<!DOCTYPE html>
<html>
    <head> <title>Pico W</title> </head>
    <body> <h1>Pico W</h1>
        <p>%s</p>
    </body>
</html>
"""

max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

if wlan.status() != 3:
    print(wlan.status())
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(10) # Accepts up to 10 incoming connections.. (untested 07/01/24)

print('listening on', addr)

def send_file(cl, filename, packet_size = 64):
    with open(filename, "r") as f:
        info = f.read(packet_size)
        #print(info)
        # sending this in packets
        while info:
            cl.send(bytes(info, "utf-8"))
            info = f.read(packet_size)
    cl.close()
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
            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/css\r\n\r\n')
            print("sending css")
            send_file(cl, "dist/assets/index-ByVuC4zf.css")
        elif is_js_file == 6:
            cl.send('HTTP/1.0 200 OK\r\nContent-type: application/javascript\r\n\r\n')
            print("sending js")
            send_file(cl, "dist/assets/index-CHoWolui.js")
        else:
            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            print("sending index.html")
            send_file(cl, "dist/index.html")
        

    except OSError as e:
        cl.close()
        print('connection closed', e)

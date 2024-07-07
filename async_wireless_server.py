import uasyncio as asyncio
import network
import socket
from machine import Pin

led = Pin("LED", Pin.OUT)

ssid = "PSU Registered"
password = "Iz4gMDvaRT5XXqTm"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)
wlan.config(pm = 0xa11140)


async def serve_http(reader, writer):
    try:
        request = await reader.read(1024)
        request = str(request)
        print(request)

        json_req = request.find("/json-historic")
        is_css_file = request.find("/assets/index-ByVuC4zf.css")
        is_js_file = request.find("/assets/index-CHoWolui.js")

        if json_req == 6:
            writer.write('HTTP/1.0 200 OK\r\nContent-type: text/json\r\nAccess-Control-Allow-Origin: *\r\n\r\n')
            await send_file(writer, "data.json")
        elif is_css_file == 6:
            writer.write('HTTP/1.0 200 OK\r\nContent-type: text/css\r\n\r\n')
            await send_file(writer, "dist/assets/index-ByVuC4zf.css")
        elif is_js_file == 6:
            writer.write('HTTP/1.0 200 OK\r\nContent-type: application/javascript\r\n\r\n')
            await send_file(writer, "dist/assets/index-CHoWolui.js")
        else:
            writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            await send_file(writer, "dist/index.html")

    except OSError as e:
        print('connection closed', e)
    finally:
        await writer.drain()
        writer.close()

async def send_file(writer, filename, packet_size=64):
    try:
        with open(filename, "r") as f:
            info = f.read(packet_size)
            while info:
                await writer.awrite(info)
                info = f.read(packet_size)
    except OSError as e:
        print('send_file error:', e)

async def main():
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        await asyncio.sleep(1)

    if wlan.status() != 3:
        print(wlan.status())
        raise RuntimeError('network connection failed')
    else:
        print('connected')
        status = wlan.ifconfig()
        print('ip = ' + status[0])

    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(5)

    print('listening on', addr)

    while True:
        try:
            cl, addr = await s.accept()
            print('client connected from', addr)
            await serve_http(cl, cl)
        except OSError as e:
            print('accept error:', e)
        except Exception as e:
            print('Error:', e)

try:
    asyncio.run(main())
except Exception as e:
    print('Async runtime error:', e)

import hyperion, time

# Streaming Server
import socket
from random import randint
import pickle

HOST = ''
PORT = 15467

HEADER_SIZE = 4

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2)

try:
    s.bind((HOST, PORT))
    s.listen(1)

    header = None
    data = b''

    IMAGEMINSIZE = 0
    IMAGECROTATE = 1
    IMAGECOFFSET = 2
    IMAGECSHEAR = 3
    IMAGECONICALGRADIENT = 4
    IMAGERADIALGRADIENT = 5
    IMAGELINEARGRADIENT = 6
    IMAGEDRAWLINE = 7
    IMAGEDRAWPOINT = 8
    IMAGEDRAWPOLYGON = 9
    IMAGEDRAWPIE = 10
    IMAGEDRAWRECT = 11
    IMAGESOLIDFILL = 12
    IMAGESETPIXEL = 13
    IMAGEGETPIXEL = 14
    SETCOLOR = 15
    IMAGESHOW = 16

    function_mapping = {
        IMAGEMINSIZE: hyperion.imageMinSize,
        IMAGECROTATE: hyperion.imageCRotate,
        IMAGECOFFSET: hyperion.imageCOffset,
        IMAGECSHEAR: hyperion.imageCShear,
        IMAGECONICALGRADIENT: hyperion.imageConicalGradient,
        IMAGERADIALGRADIENT: hyperion.imageRadialGradient,
        IMAGELINEARGRADIENT: hyperion.imageLinearGradient,
        IMAGEDRAWLINE: hyperion.imageDrawLine,
        IMAGEDRAWPOINT: hyperion.imageDrawPoint,
        IMAGEDRAWPOLYGON: hyperion.imageDrawPolygon,
        IMAGEDRAWPIE: hyperion.imageDrawPie,
        IMAGEDRAWRECT: hyperion.imageDrawRect,
        IMAGESOLIDFILL: hyperion.imageSolidFill,
        IMAGESETPIXEL: hyperion.imageSetPixel,
        IMAGEGETPIXEL: hyperion.imageGetPixel,
        SETCOLOR: hyperion.setColor,
        IMAGESHOW: hyperion.imageShow
    }

    def get_function(id):
        return function_mapping[id]

    def conn_wait():
        hyperion.setColor(0, 0, 100)
        
    def connected():
        hyperion.setColor(255, 255, 255)
        time.sleep(0.5)
        hyperion.setColor(0, 0, 0)

    while not hyperion.abort():

        try:
            conn, addr = s.accept()
        except socket.timeout:
            conn_wait()
            continue

        connected()
        print('Client connection accepted ', addr)

        # send image resolution
        w = int.to_bytes(hyperion.imageWidth(), HEADER_SIZE, "big")
        h = int.to_bytes(hyperion.imageHeight(), HEADER_SIZE, "big")
        conn.send(w+h)

        conn.settimeout(5)
        while not hyperion.abort():
            try:
                buf = conn.recv(4096)
                if len(buf) == 0:
                    raise socket.error
                data += buf

                #header containing length of message
                if not header:
                    header = int.from_bytes(data[:HEADER_SIZE], "big")
                    data = data[HEADER_SIZE:]

                while len(data) > header:
                    data = data[header:]
                    header = int.from_bytes(data[:HEADER_SIZE], "big")
                    data = data[HEADER_SIZE:]
                if len(data) < header:
                    continue

                try:
                    msg = pickle.loads(data)
                    data = b''
                    header = None

                    try:
                        for cmd in msg:
                            func = get_function(cmd['id'])
                            func(*cmd['args'])
                    except Exception as e:
                        print("Could not execute command")
                        
                except Exception as e:
                    print(data)

            except socket.timeout:
                continue
            except socket.error as e:
                print('Client connection closed', addr)
                data = b''
                break

        conn.close()
    s.close()
except Exception as e:
    s.close()
    raise e

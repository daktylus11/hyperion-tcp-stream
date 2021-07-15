# Client to stream audio to a running hyperion effect tcp server
import socket
import pickle
import time
import pyaudio
import numpy as np


INPUT_DEVICE = 2 # input device to capture audio from
# for system audio I used VB-Cable

CHUNK = 2**11
RATE = 44100
MAX_AMP = 2**13

HEADER_SIZE = 4
SEND_PAUSE = 20 # time to wait before sending another message in ms (20 ms = 50 Hz)

# Host data
HOST = '192.168.2.122'
PORT = 15467

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

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

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True,
                frames_per_buffer=CHUNK, input_device_index=INPUT_DEVICE)

# receive image dimensions
screen_data = s.recv(2*HEADER_SIZE)
width = int.from_bytes(screen_data[:HEADER_SIZE], "big")
height = int.from_bytes(screen_data[HEADER_SIZE:], "big")

# create data to send to hyperion
def get_data():
    """"returns the data to be sent to the hyperion instance as list of commands
    each command is represented by a dict with an id for the Effect Engine API method defined above
    and a list of args for this method"""
    global p
    global width
    global height

    audio_data = np.abs(np.fromstring(stream.read(CHUNK),dtype=np.int16))
    audio_data = audio_data/MAX_AMP
    scaled_down = np.array_split(audio_data, width)
    scaled_down = [np.average(x) for x in scaled_down]
    data = []
    data.append({'id': IMAGESOLIDFILL, 'args': [0, 0, 0]})
    for i, x in enumerate(scaled_down):
        for j in range(int(x*height)):
            data.append({'id': IMAGEDRAWPOINT, 'args': [i, height - j, 1, int(255*(j/height)), int(100*((height-j)/height)), int(60*((height-j)/height))]})
    data.append({'id': IMAGESHOW, 'args': []})
    return data

prev_time = time.time()

# send data to remote hyperion instance in specified interval
while True:
    try:
        delta = time.time() - prev_time
        if delta < SEND_PAUSE:
            time.sleep((SEND_PAUSE - delta) / 1000)
        prev_time = time.time()
        
        data = pickle.dumps(get_data())
        header = int.to_bytes(len(data), HEADER_SIZE, "big")
        s.send(header + data)
    except Exception as e:
        raise e
        print(e)
        break

s.close()

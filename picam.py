import eventlet
from eventlet import wsgi
import os
import socketio
import time
import threading
import cv2
import base64
import subprocess
import uuid

class setInterval:
    def __init__(self, interval, action, parameters=None, iter=0):
        self.interval = interval
        self.action = action
        self.stopEvent = threading.Event()
        self.parameters = parameters
        self.iter = iter
        self.currIter = iter
        thread = threading.Thread(target=self.__setInterval)
        thread.start()

    def __setInterval(self):
        nextTime = time.time()+self.interval
        if self.iter > 0:
            while not self.stopEvent.wait(nextTime-time.time()):
                nextTime += self.interval
                self.action(self.parameters)
                self.currIter = self.currIter - 1
                if self.currIter == 0:
                    self.stopEvent.set()
        else:
            while not self.stopEvent.wait(nextTime-time.time()):
                nextTime += self.interval
                self.action(self.parameters)

    def cancel(self):
        print('## LOG ## Streaming thread stopped')
        self.stopEvent.set()

# Récupération du lien vers la picam
picam_proc = subprocess.Popen(["./picam.sh"], stdout=subprocess.PIPE)
picam = picam_proc.stdout.read().decode("utf-8").strip().split()
if len(picam) > 0:
    print("picam : " + " ".join(picam))

# Permet de patch les threads d'eventlet
eventlet.monkey_patch()

# Fusion des caméras en un tableau unique
fps = 10
clients = []
picam_capture = None
picam_thread = None

print('## LOG ## Live FPS: ' + str(fps))


def wsgi_handler(env, start_response):
    if env['PATH_INFO'] == "/":
        if os.path.exists("./index.html"):
            h = open("./index.html", 'rb')
            content = h.read()
            h.close()
            headers = [("Access-Control-Allow-Origin", "*"),
                       ('content-type', 'text/html')]
            start_response('200 OK', headers)
            return [content]
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return ['Hello, World!\r\n']

sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio, wsgi_handler)

# 0 : channel
# 1 : camera source
# 2 : room
# 3 : Encoding quality


def sendImage(params):
    flag, frame = params[1].read()
    if flag:
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 20]
        if not isinstance(params[3], bool) and isinstance(params[3], int) and params[3] >= 0 and params[3] <= 100:
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), params[3]]
        image = cv2.imencode('.jpg', frame, encode_param)[1].tostring()
        image = base64.b64encode(image)
        image = image.decode('utf-8')
        sio.emit(params[0], image)
        return image
    return False

def sendPicture(params):
    flag, frame = params[1].read()
    if flag:
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 20]
        if not isinstance(params[3], bool) and isinstance(params[3], int) and params[3] >= 0 and params[3] <= 100:
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), params[3]]
        image = cv2.imencode('.jpg', frame, encode_param)[1].tostring()
        image = base64.b64encode(image)
        image = image.decode('utf-8')
        return image
    return False

@sio.event
def connect(sid, env):
    print('## LOG ## Client connected, sid: ' + str(sid))

@sio.event
def disconnect(sid):
    print('## LOG ## Client disconnected, sid: ', str(sid))

@sio.event
def camera_count(sid, data):
    print("## LOG ## Camera count request")
    return len(camera_captures)

@sio.event
def picture(sid, data):
    print('## LOG ## Client requested a picture')
    params = ["picture", picam_capture, 666, data]
    return sendPicture(params)

id_cpt = 0
if len(picam) > 0:
    picam_capture = cv2.VideoCapture(picam[0])
    print("Picam opened")
    #capture_ref.set(3, 320)
    #capture_ref.set(4, 240)

    # 1: Nom de la caméra
    # 2: VideoCapture de la caméra
    # 3: Liste des clients connectés au flux
    # 4: Référence vers le thread de streaming
    params = ["image", picam_capture, "picam", False]
    picam_thread = setInterval(1/float(fps), sendImage, params)
    print("Picam thread created")

else:
    picam_capture = cv2.VideoCapture(0)
    print("Base camera opened")
    params = ["image", picam_capture, "picam", False]
    picam_thread = setInterval(1/float(fps), sendImage, params)
    print("Base camera thread created")

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 3000)), app)

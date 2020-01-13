import jetson.inference
import jetson.utils
import cv2
import sys
import numpy as np
import threading
import argparse
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template

network = "ssd-mobilenet-v2"
overlay = "box,labels"
threshold = 0.5
camera = "/dev/video0"
width, height = 640, 480

# load the object detection network
net = jetson.inference.detectNet(network, [], threshold)

# create the camera and display
camera = jetson.utils.gstCamera(width, height, camera)

outputFrame = None
lock = threading.Lock()

app = Flask(__name__)

def capture_n_infer():
    global outputFrame
    while True:
        img, width, height = camera.CaptureRGBA(zeroCopy=1)
        detections = net.Detect(img, width, height, overlay)
        cv2_img = jetson.utils.cudaToNumpy(img, width, height, 4)
        cv2_img = cv2.cvtColor (cv2_img.astype(np.uint8), cv2.COLOR_RGBA2BGR)
        outputFrame = cv2_img.copy()

@app.route("/")
def index():
    # return the rendered template
    return render_template("index.html")

def generate():
    # grab global references to the output frame and lock variables
    global outputFrame, lock

    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if outputFrame is None:
                continue

            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

            # ensure the frame was successfully encoded
            if not flag:
                continue

        # yield the output frame in the byte format
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate(),
        mimetype = "multipart/x-mixed-replace; boundary=frame")

if __name__ == '__main__':
    # construct the argument parser and parse command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("--ip", type=str, required=True,
        help="ip address of the device")
    ap.add_argument("--port", type=int, required=True,
        help="ephemeral port number of the server (1024 to 65535)")
    args = vars(ap.parse_args())

    # start a thread that will perform motion detection
    t = threading.Thread(target=capture_n_infer)
    t.daemon = True
    t.start()

    # start the flask app
    app.run(host=args["ip"], port=args["port"], debug=True,
        threaded=True, use_reloader=False)


import argparse
import threading
import numpy as np
import cv2
from flask import Response
from flask import Flask
from flask import render_template
import jetson.inference
import jetson.utils

network = "ssd-inception-v2"
overlay = "box,labels"
threshold = 0.5
camera = "/dev/video0"
width, height = 1280, 720

# load the object detection network
net = jetson.inference.detectNet(network, [], threshold)

# create the camera and display
camera = jetson.utils.gstCamera(width, height, camera)

outputFrame = None
lock = threading.Lock()

app = Flask(__name__)

encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]

def capture_n_infer():
    global outputFrame
    while True:
        img, width, height = camera.CaptureRGBA(zeroCopy=1)
        _ = net.Detect(img, width, height, overlay)
        cv2_img = jetson.utils.cudaToNumpy(img, width, height, 4)
        cv2_img = cv2.cvtColor(cv2_img.astype(np.uint8), cv2.COLOR_RGBA2BGR)
        outputFrame = cv2_img.copy()

# start a thread that will perform motion detection
t = threading.Thread(target=capture_n_infer)
t.daemon = True
t.start()

@app.route("/")
def index():
    # return the rendered template
    return render_template("index.html")


def generate():
    global outputFrame, lock
    while True:
        # lock required for multi-user viewing
        with lock:
            if outputFrame is None:
                continue
            _, encodedImage = cv2.imencode(".jpg", outputFrame, encode_param)
        yield(b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" +
              bytearray(encodedImage) + b"\r\n")


@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

def start_app():
    # construct the argument parser and parse command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("--ip", type=str, default="0.0.0.0",
                    help="ip address of the device")
    ap.add_argument("--port", type=int, default=5000,
                    help="ephemeral port number of the server (1024 to 65535)")
    args = vars(ap.parse_args())

    # start the flask app
    app.run(host=args["ip"], port=args["port"], debug=False,
            threaded=True, use_reloader=False)

if __name__ == "__main__":
    start_app()

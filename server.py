import argparse
import time
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

# load the object detection network
net = jetson.inference.detectNet(network, [], threshold)

# create the camera and display
camera = jetson.utils.gstCamera(1280, 720, "/dev/video0")
#camera_lower = jetson.utils.gstCamera(640, 480, "/dev/video1")

outputFrame = None
auxFrame = None
capture = None
width, height = None, None

app = Flask(__name__)

encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]


def print_perf(start, end):
    latency = round(end - start, 4)
    fps = round(1/(end-start), 1)
    print(latency, "/", fps)


def capture_aux_cam():
    global auxFrame
    camera_lower = cv2.VideoCapture("/dev/video1")
    time.sleep(0.01)
    while True:
        _, cv2_img = camera_lower.read()
        cv2_img = cv2.pyrDown(cv2_img)
        auxFrame = cv2.copyMakeBorder(
            cv2_img[-170:, -310:, :], 5, 5, 5, 5, cv2.BORDER_CONSTANT)
        time.sleep(0.0322)


def infer_main():
    global outputFrame
    while True:
        start = time.time()
        capture, _, _ = camera.CaptureRGBA(zeroCopy=1)
        net.Detect(capture, 1280, 720, overlay)
        cv2_img = jetson.utils.cudaToNumpy(capture, 1280, 720, 4)
        outputFrame = cv2.cvtColor( cv2_img.astype(np.uint8), cv2.COLOR_RGBA2BGR)
        print_perf(start, time.time())


# start background threads

t = threading.Thread(target=capture_aux_cam)
t.daemon = True
t.start()

time.sleep(0.1)

t = threading.Thread(target=infer_main)
t.daemon = True
t.start()

time.sleep(0.1)


@app.route("/")
def index():
    # return the rendered template
    return render_template("index.html")


def generate():
    global outputFrame, auxFrame
    while True:
        if auxFrame is not None and outputFrame is not None:
            _outputFrame = outputFrame.copy()
            _outputFrame[-180:, -320:, :] = auxFrame
            _, encodedImage = cv2.imencode(
                ".jpg", _outputFrame, encode_param)
            yield(b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" +
                    bytearray(encodedImage) + b"\r\n")
        else:
            time.sleep(0.5)


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

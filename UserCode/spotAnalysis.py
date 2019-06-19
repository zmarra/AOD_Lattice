import matplotlib.pyplot as plt
import numpy as np
import json
from scipy.signal import find_peaks
import zmq
from scipy import ndimage


def parse_args():
    """Parse the command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--window", default=(98, 100, 324, 110), type=tuple)
    parser.add_argument("-t", "--traps", default=1, type=int)
    parser.add_argument("-P", "--P", default=.00005, type=float)
    parser.add_argument("-I", "--I", default=0.00002, type=float)
    parser.add_argument("-D", "--D", default=0.000001, type=float)
    parser.add_argument("-p", "--peakProminence", default=400, type=int)
    return parser.parse_args()


def getImage(cameraSerial, socket):
    cmd = {
        'action': 'GET_IMAGE',
        'serial': cameraSerial
    }
    socket.send(json.dumps(cmd))
    resp = json.loads(socket.recv())
    print "status: " + str(resp["status"])
    print "server message: " + resp["message"]
    return np.array(resp["image"])


def addCamera(cameraSerial, socket):
    cmd = {
        'action': 'ADD_CAMERA',
        'serial': cameraSerial
    }
    socket.send(json.dumps(cmd))
    resp = json.loads(socket.recv())
    print "status: " + str(resp["status"])
    print "server message: " + resp["message"]

    cmd = {
        'action': 'START',
        'serial': cameraSerial
    }
    socket.send(json.dumps(cmd))
    resp = json.loads(socket.recv())
    print resp
    print "status: " + str(resp["status"])
    print "server message: " + resp["message"]


context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.setsockopt(zmq.RCVTIMEO, 5000)
addr = "{}://{}:{}".format("tcp", "10.140.178.187", 55555)
socket.connect(addr)
cameraSerial = 14353509
# addCamera(cameraSerial, socket)
rotation = 40
left = 370
right = 380
top = 300
bottom = 660
# left = 354
# right = 627
# top = 360
# bottom = 370
while True:
    grayimg = getImage(cameraSerial, socket)
    grayimg = ndimage.rotate(grayimg, rotation)
    grayimg = grayimg[left:right, top:bottom]
    grayimg = np.transpose(grayimg)
    summedFunction = np.sum(grayimg, axis=1)
    plt.clf()
    peaks, properties = find_peaks(summedFunction, prominence=(200, None))
    print len(peaks)
    plt.plot(summedFunction)
    plt.plot(peaks, summedFunction[peaks], "x")
    plt.ylim(0, 2000)
    plt.pause(.05)
# plt.show()

import matplotlib.pyplot as plt
import numpy as np
import json
from scipy.signal import find_peaks
import zmq
from scipy import ndimage


def getImage(cameraSerial, socket):
    cmd = {
        'action': 'GET_IMAGE',
        'serial': cameraSerial
    }
    socket.send(json.dumps(cmd))
    resp = json.loads(socket.recv())
    print "status: " + str(resp["status"])
    print "server message: " + resp["message"]
    return np.array(resp["image"]), resp["status"]


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
cameraSerial = 14353502
addCamera(cameraSerial, socket)

rotation = 43

left = 312
right = 612
top = 218
bottom = 522

cutSizeX = 10
cutSizeY = 20

# leftx = int((left+right)/2)
# rightx = leftx+cutSizeX
#
# lefty = int((left+right)/2)
# righty = leftx+cutSizeX
grid = plt.GridSpec(2, 2, wspace=0.4, hspace=0.3)
fig = plt.figure()

while True:
    grayimg, status = getImage(cameraSerial, socket)
    if status == 0:
        plt.clf()
        grayimg = ndimage.rotate(grayimg, rotation)
        grayimg = grayimg[left:right, top:bottom]
        cutx = fig.add_subplot(grid[0, 0])
        cuty = fig.add_subplot(grid[1, 0])
        image = fig.add_subplot(grid[:, 1])
        image.imshow(grayimg)
        dim = grayimg.shape
        print dim
        x0 = int(dim[0]/2)
        x1 = int(dim[0]/2)+cutSizeX
        y0 = int(dim[1]/2)
        y1 = int(dim[1]/2)+cutSizeY
        image.axvline(x0, color='r')
        image.axvline(x1, color='r')
        image.axhline(y0, color='r')
        image.axhline(y1, color='r')
        summedFunctionx = np.sum(grayimg[:][y0:y1], axis=0)
        summedFunctiony = np.sum(grayimg[x0:x1][:], axis=0)
        print len(summedFunctiony)

        peaksx, properties = find_peaks(summedFunctionx, prominence=(200, None))
        peaksy, properties = find_peaks(summedFunctiony, prominence=(200, None))

        print "number of x peaks = " + str(len(peaksx))
        print "number of y peaks = " + str(len(peaksy))
        cutx.plot(summedFunctionx)
        cutx.plot(peaksx, summedFunctionx[peaksx], "x")
        cuty.plot(summedFunctiony)
        cuty.plot(peaksy, summedFunctiony[peaksy], "x")
        cutx.set_ylim([0, 2000])
        cuty.set_ylim([0, 2000])
        plt.pause(.5)
# plt.show()

import numpy as np
from simple_pid import PID
import json
import time
from scipy.signal import find_peaks
import threading
import zmq


class TrapFeedback(object):

        def __init__(self, waveManager, channel, cameraSerial, cameraIP):
            self.waveManager = waveManager
            self.cameraIP = cameraIP
            self.channel = channel
            self.cameraSerial = cameraSerial
            self.trapNum = len(waveManager.getAmplitudes())
            self.PIDs = []
            self.waittime = 1
            self.initializePIDs()
            self.connectCameraServer()
            self.addCamera()

        def connectCameraServer(self):
            context = zmq.Context()
            self.socket = context.socket(zmq.REQ)
            self.socket.setsockopt(zmq.RCVTIMEO, 5000)
            addr = "{}://{}:{}".format("tcp", self.cameraIP, 55555)
            self.socket.connect(addr)

        def updateAmplitudes(self, measuredIntensities):
            newAmplitudes = []
            for i in range(len(self.PIDs)):
                newPower = self.PIDs[i](measuredIntensities[i])
                newAmplitudes += [10.0**(newPower/10.0)]
            self.waveManager.changeAmplitude(self.channel, newAmplitudes)

        def initializePIDs(self):
            for currentAmplitude in self.waveManager.getAmplitudes():
                self.PIDs += [PID(self.P, self.I, self.D, setpoint=1000, output_limits=(-10, 0))]
                self.PIDs.auto_mode = False
                self.PIDs.set_auto_mode(True, last_output=currentAmplitude)

        def getImage(self):
            cmd = {
                'action': 'GET_IMAGE',
                'serial': self.cameraSerial
            }
            self.socket.send(json.dumps(cmd))
            resp = json.loads(self.socket.recv())
            print "status: " + str(resp["status"])
            print "server message: " + resp["message"]
            return np.array(resp["image"])

        def addCamera(self):
            cmd = {
                'action': 'ADD_CAMERA',
                'serial': self.cameraSerial
            }
            self.socket.send(json.dumps(cmd))
            resp = json.loads(self.socket.recv())
            print "status: " + str(resp["status"])
            print "server message: " + resp["message"]

            cmd = {
                'action': 'START',
                'serial': self.cameraSerial
            }
            self.socket.send(json.dumps(cmd))
            resp = json.loads(self.socket.recv())
            print resp
            print "status: " + str(resp["status"])
            print "server message: " + resp["message"]

        def measureIntensities(self):
            image = self.getImage()
            summedFunction = np.sum(image, axis=0)
            peaks, properties = find_peaks(summedFunction, prominence=(self.peakProminence, None))
            return summedFunction[peaks]

        def iteratePID(self):
            self.updateAmplitudes(self.measureIntensities())
            time.sleep(self.waitTime)

        def startFeedback(self):
            self.feedback = threading.Thread(target=self.iteratePID)
            self.feedback.start()

        def stopFeedback(self):
            self.feedback.raise_exception()
            self.feedback.join()

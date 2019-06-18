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
            self.trapNum = len(waveManager.getAmplitudes(self.channel))
            self.PIDs = []
            self.P = .0005
            self.I = .00002
            self.D = .00001
            self.peakProminence = 200
            self.waitTime = 1
            self.initializePIDs()
            self.connectCameraServer()

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
            currentAmplitudes = self.waveManager.getAmplitudes(self.channel)
            for i in range(len(currentAmplitudes)):
                self.PIDs += [PID(self.P, self.I, self.D, setpoint=1000, output_limits=(-10, 0))]
                self.PIDs[i].auto_mode = False
                self.PIDs[i].set_auto_mode(True, last_output=currentAmplitudes[i])

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
            t = threading.currentThread()
            self.running = True
            while getattr(t, "run", True):
                self.updateAmplitudes(self.measureIntensities())
                time.sleep(self.waitTime)
                if not self.running:
                    break

        def startFeedback(self):
            self.feedback = threading.Thread(target=self.iteratePID, args=[])
            self.feedback.start()

        def stopFeedback(self):
            self.running = False
            self.feedback.join()

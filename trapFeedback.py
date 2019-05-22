from PIL import Image
import requests
from io import BytesIO
import numpy as np
from scipy.optimize import curve_fit
from simple_pid import PID
import json
import time
from scipy.signal import find_peaks
import sys

def rgb2gray(rgb):
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray


def func(x, *params):
    y = np.zeros_like(x)
    for i in range(1, len(params), 3):
        ctr = params[i]
        amp = params[i+1]
        wid = params[i+2]
        y = y + amp * np.exp(-((x - ctr)/wid)**2)
    y += params[0]
    return y


def updateAmplitudes(pids, amplitudes, threshold):
    with open('waveformArguments.json') as read_file:
        data = json.load(read_file)
    read_file.close()
    diffs = []
    for i in range(len(pids)):
        
        diffs += [abs(amplitudes[i] - 1000)]
        control = pids[i](amplitudes[i])
        data["Waves"][i]["amplitude"] = control
        print str(amplitudes[i]) + " " + str(control)
    print diffs
    if not all(i <= threshold for i in diffs):
        print "Changed"
        with open('waveformArguments.json', 'w') as outfile:
            json.dump(data, outfile)
    return "done"


guess = [200]
trapNum = int(sys.argv[1])
pids = []
with open('waveformArguments.json') as read_file:
    data = json.load(read_file)
read_file.close() 
for i in range(trapNum):
    pids += [PID(.00005, 0.00002, 0.000001, setpoint=800, output_limits=(.01, 3))]
    print data["Waves"][i]["amplitude"]
    pids[i].auto_mode = False
    pids[i].set_auto_mode(True, last_output=data["Waves"][i]["amplitude"])
x = range(350)
threshold = 10
while True:
    cameraImageURL = "http://10.141.230.220/html/cam_pic.php"
    response = requests.get(cameraImageURL)
    img = Image.open(BytesIO(response.content))
    img = img.crop((98, 100, 324, 110)) #(left, up, right, bottom)
    grayimg = rgb2gray(np.array(img))
    summedFunction = np.sum(grayimg, axis=0)
    peaks, properties = find_peaks(summedFunction, prominence=(400, None))
    amplitudes = summedFunction[peaks]
    updateAmplitudes(pids, amplitudes, threshold)
    time.sleep(.05)

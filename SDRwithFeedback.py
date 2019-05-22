import uhd
from uhd import libpyuhd as lib
import json
import time
import threading
import os
import numpy as np


waveforms = {
    "sine": lambda n, tone_offset, rate: np.exp(n * 2j * np.pi * tone_offset / rate),
}


def streamWaveform(streamer, wave, metadata):
    t = threading.currentThread()
    while getattr(t, "run", True):
        wave = getattr(t, "wave", wave)
        streamer.send(wave, metadata)


def generateOutputWaveform(allWaves, jsonData):
    phases = []
    amplitude = []
    for item in jsonData['Waves']:
        phases.append(item['phase'])
        amplitude.append(item['amplitude'])
    wave = 0
    for i in range(len(jsonData['Waves'])):
        if (i == 0):
            wave = amplitude[i]*allWaves[i]*np.exp(phases[i]*np.pi*2j)
        else:
            wave = np.add(wave, amplitude[i]*allWaves[i]*np.exp(phases[i]*np.pi*2j))
    return wave


def generateWaveforms(jsonData):
    freqs = []
    for item in jsonData['Waves']:
        freqs.append(item['freq'])
    dataSize = int(np.floor(jsonData["Rate"] / jsonData['waveFreq']))
    outputWaveform = []
    for channels in range(len(jsonData['Channels'])):
        for i in range(len(jsonData['Waves'])):
            wave = np.array(list(map(lambda n: waveforms['sine'](n, freqs[i], jsonData["Rate"]), np.arange(dataSize, dtype=np.complex64))), dtype=np.complex64)
            outputWaveform.append(wave)
    return outputWaveform


def main():
    with open('waveformArguments.json') as read_file:
        data = json.load(read_file)
    read_file.close()
    rate = data['Rate']
    gain = data['Gain']
    centerFreq = data['CenterFreq']
    channels = data['Channels']

###############################################
############# Generate Waveforms ##############
###############################################

    allWaves = generateWaveforms(data)
    wave = generateOutputWaveform(allWaves, data)
    wave = np.stack((wave, wave), axis=0)
###############################################
############## Initialize USRP ################
##############################################
    usrp = uhd.usrp.MultiUSRP('')

    for chan in channels:
        usrp.set_tx_rate(rate, chan)
        usrp.set_tx_freq(lib.types.tune_request(centerFreq), chan)
        usrp.set_tx_gain(gain, chan)
    st_args = lib.usrp.stream_args("fc32", "sc16")
    st_args.channels = channels
    streamer = usrp.get_tx_stream(st_args)

    buffer_samps = streamer.get_max_num_samps()

    metadata = lib.types.tx_metadata()

###############################################
############## Stream Waveforms ###############
###############################################
    modTimeOrig = os.stat('waveformArguments.json').st_mtime
    stream = threading.Thread(target=streamWaveform, args=(streamer, wave, metadata))
    stream.start()
    while True:
        time.sleep(.05)
        modTime = os.stat('waveformArguments.json').st_mtime
        if modTime != modTimeOrig:
            print "changed"
            try:
                with open('waveformArguments.json') as read_file:
                    data = json.load(read_file)
                read_file.close()
                newWave = generateOutputWaveform(allWaves, data)
                stream.wave = np.stack((newWave, newWave), axis=0)
                stream.isAlive()
                modTimeOrig = modTime
            except:
                time.sleep(.005)


if __name__ == "__main__":
    main()

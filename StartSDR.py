import numpy as np
import uhd
from uhd import libpyuhd as lib
import json
import time
import threading
import os

waveforms = {
    "sine": lambda n, tone_offset, rate: np.exp(n * 2j * np.pi * tone_offset / rate),
}


def streamWaveform(streamer, wave, metadata):
    t = threading.currentThread()
    while getattr(t, "run", True):
        wave = getattr(t, "wave", wave)
        streamer.send(wave, metadata)


def generateWaveform(data):
    freqs = []
    phases = []
    amplitude = []
    for item in data['Waves']:
        freqs.append(item['freq'])
        phases.append(item['phase'])
        amplitude.append(item['amplitude'])
    dataSize = int(np.floor(10 * data["Rate"] / data['waveFreq']))
    wave = np.array(list(map(lambda n: 0, np.arange(dataSize, dtype=np.complex64))), dtype=np.complex64)
    for i in range(len(data['Waves'])):
        currentWave = np.array(list(map(lambda n: amplitude[i] * waveforms['sine'](n, freqs[i], data["Rate"]), np.arange(dataSize, dtype=np.complex64))), dtype=np.complex64)
        wave = np.add(wave, np.exp(phases[i]*np.pi*2j) * currentWave)
    return wave


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

    wave = generateWaveform(data)

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
            try:
                with open('waveformArguments.json') as read_file:
                    data = json.load(read_file)
                read_file.close()
                stream.wave = generateWaveform(data)
                stream.isAlive()
                modTimeOrig = modTime
            except:
                time.sleep(.005)


if __name__ == "__main__":
    main()

import argparse
import json
import numpy as np
import random


waveforms = {
    "sine": lambda n, tone_offset, rate: np.exp(n * 2j * np.pi * tone_offset / rate)
}


def parse_args():
    """Parse the command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", default='../Resources/waveformArguments.json', type=str)
    return parser.parse_args()


def getMaxAmp(rate, waveFreq, amplitude, freq, phases):
    dataSize = int(np.floor(rate / waveFreq))
    wave = np.array(list(map(lambda n: 0, np.arange(dataSize, dtype=np.complex64))), dtype=np.complex64)
    for i in range(len(amplitude)):
        currentWave = np.array(list(map(lambda n: amplitude[i] * waveforms['sine'](n, freqs[i], rate), np.arange(dataSize, dtype=np.complex64))), dtype=np.complex64)
        wave = np.add(wave, np.exp(phases[i]*np.pi*2j) * currentWave)
    return np.max(np.real(wave), axis=0) - np.min(np.real(wave), axis=0)


args = parse_args()
data = {}
with open(args.file) as read_file:
    data = json.load(read_file)

rate = data['Rate']
gain = data['Gain']
centerFreq = data['CenterFreq']
waveFreq = data['waveFreq']

ampThreshold = len(data['Waves'])/1.5
maxAmp = ampThreshold + 1

while(maxAmp*2 > ampThreshold):
    freqs = []
    phases = []
    amplitude = []
    for item in data['Waves']:
        newPhase = random.random()
        freqs.append(item['freq'])
        item['phase'] = newPhase
        phases.append(newPhase)
        amplitude.append(.5)
    maxAmp = getMaxAmp(rate, waveFreq, amplitude, freqs, phases)
    print maxAmp

with open(args.file, 'w') as outfile:
    json.dump(data, outfile, indent=4, separators=(',', ': '))
outfile.close()

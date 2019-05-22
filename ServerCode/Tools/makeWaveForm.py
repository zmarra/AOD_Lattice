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
    parser.add_argument("-s", "--spots", default=1, type=float)
    parser.add_argument("-sp", "--spacing", default=1e6, type=float)
    parser.add_argument("-t", "--template", default='../Resources/waveformTemplate.json', type=str)
    parser.add_argument("-o", "--outputFile", default='../Resources/waveformArguments.json', type=str)
    return parser.parse_args()


def getMaxAmp(rate, waveFreq, amplitude, freqs, phases):
    dataSize = int(np.floor(rate / waveFreq))
    wave = np.array(list(map(lambda n: 0, np.arange(dataSize, dtype=np.complex64))), dtype=np.complex64)
    for i in range(len(amplitude)):
        currentWave = np.array(list(map(lambda n: amplitude[i] * waveforms['sine'](n, freqs[i], rate), np.arange(dataSize, dtype=np.complex64))), dtype=np.complex64)
        wave = np.add(wave, np.exp(phases[i]*np.pi*2j) * currentWave)
    return np.max(np.real(wave), axis=0) - np.min(np.real(wave), axis=0)


args = parse_args()
data = {}
with open(args.template) as read_file:
    data = json.load(read_file)

freqs = []
freqs = np.arange(-(args.spots-1)/2.0*args.spacing, ((args.spots-1)/2.0+1)*args.spacing, args.spacing)
print freqs

rate = data['Rate']
gain = data['Gain']
centerFreq = data['CenterFreq']
waveFreq = data['waveFreq']

ampThreshold = args.spots/1.5
maxAmp = ampThreshold + 1

while(maxAmp*2 > ampThreshold):
    data['Waves'] = []
    for chan in range(len(data['Channels'])):
        data['Waves'].append([])
    for freq in freqs:
        newPhase = random.random()
        for chan in range(len(data['Channels'])):
            data['Waves'][int(chan)].append({"freq": freq, "amplitude": .5, "phase": newPhase})

    freqs = []
    phases = []
    amplitude = []
    for item in data['Waves'][0]:
        freqs.append(item['freq'])
        phases.append(item['phase'])
        amplitude.append(item['amplitude'])
    maxAmp = getMaxAmp(rate, waveFreq, amplitude, freqs, phases)
    print maxAmp

with open(args.outputFile, 'w') as outfile:
    json.dump(data, outfile, indent=4, separators=(',', ': '))
outfile.close()

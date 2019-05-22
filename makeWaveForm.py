import sys
import json
import numpy as np
import random
import matplotlib.pyplot as plt


waveforms = {
    "sine": lambda n, tone_offset, rate: np.exp(n * 2j * np.pi * tone_offset / rate)
}

###############################################
############# Generate Waveforms ##############
###############################################

data = {}

with open('waveformTemplate.json') as read_file:
    data = json.load(read_file)
    print data

spots = int(sys.argv[1])
spacing = 900000
freqs = []
freqs = np.arange(-(spots-1)/2.0*spacing, ((spots-1)/2.0+1)*spacing, spacing) 
print freqs

rate = data['Rate']
gain = data['Gain']
centerFreq = data['CenterFreq']
waveFreq = data['waveFreq']

ampThreshold = spots/1.5
maxAmp = ampThreshold + 1
while(maxAmp*2 > ampThreshold):
    data['Waves'] = []
    for freq in freqs:
        data['Waves'].append({"freq": freq, "amplitude": .5, "phase": random.random()})
    freqs = []
    phases = []
    amplitude = []
    for item in data['Waves']:
        freqs.append(item['freq'])
        phases.append(item['phase'])
        amplitude.append(item['amplitude'])

    dataSize = int(np.floor(rate / waveFreq))
    wave = np.array(list(map(lambda n: 0, np.arange(dataSize, dtype=np.complex64))), dtype=np.complex64)
    for i in range(len(data['Waves'])):
        data2 = np.array(list(map(lambda n: amplitude[i] * waveforms['sine'](n, freqs[i], rate), np.arange(dataSize, dtype=np.complex64))), dtype=np.complex64)
        wave = np.add(wave, np.exp(phases[i]*np.pi*2j) * data2)
    maxAmp = np.max(np.real(wave), axis=0) - np.min(np.real(wave), axis=0)
    print maxAmp
with open('waveformArguments.json', 'w') as outfile:
    json.dump(data, outfile, indent=4, separators=(',', ': '))
outfile.close()

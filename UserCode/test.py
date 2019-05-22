import json
import numpy as np
import matplotlib.pyplot as plt


waveforms = {
    "sine": lambda n, tone_offset, rate: np.exp(n * 2j * np.pi * tone_offset / rate)
}

###############################################
############# Generate Waveforms ##############
###############################################

with open('waveformArguments.json') as read_file:
    data = json.load(read_file)
    print data

rate = data['Rate']
gain = data['Gain']
centerFreq = data['CenterFreq']
waveFreq = data['waveFreq']
freqs = []
phases = []
amplitude = []
for item in data['Waves']:
    freqs.append(item['freq'])
    phases.append(item['phase'])
    amplitude.append(item['amplitude'])

###############################################
############# Generate Waveforms ##############
###############################################

dataSize = int(np.floor(rate / waveFreq))
wave = np.array(list(map(lambda n: 0, np.arange(dataSize, dtype=np.complex64))), dtype=np.complex64)
for i in range(len(data['Waves'])):
    data = np.array(list(map(lambda n: amplitude[i] * waveforms['sine'](n, freqs[i], rate), np.arange(dataSize, dtype=np.complex64))), dtype=np.complex64)
    wave = np.add(wave, np.exp(phases[i]*np.pi*2j) * data)
plt.plot(wave)
plt.show()

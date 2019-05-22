import json
import numpy as np
import matplotlib.pyplot as plt


waveforms = {
    "sine": lambda n, tone_offset, rate: np.exp(n * 2j * np.pi * tone_offset / rate)
}


def generateWaveforms(jsonData):
    dataSize = int(np.floor(jsonData["Rate"] / jsonData['waveFreq']))
    outputWaveform = []
    for channel in range(len(jsonData['Channels'])):
        for wave in jsonData['Waves'][channel]:
            wave = np.array(list(map(lambda n: waveforms['sine'](n, wave['freq'], jsonData["Rate"]), np.arange(dataSize, dtype=np.complex64))), dtype=np.complex64)
            outputWaveform.append(wave)
    return outputWaveform


def generateOutputWaveforms(allWaves, jsonData):
    waves = []
    for channel in range(len(jsonData['Channels'])):
        wave = allWaves[0][0]*0
        i = 0
        for currentWave in jsonData['Waves'][channel]:
                print wave
                wave = np.add(wave, currentWave['amplitude']*allWaves[i]*np.exp(currentWave['phase']*np.pi*2j))
                i += 1
        waves.append(wave)
    return waves


with open('../ServerCode/Resources/waveformArguments.json') as read_file:
    data = json.load(read_file)

allWaves = generateWaveforms(data)
waves = generateOutputWaveforms(allWaves, data)
for wave in waves:
    plt.plot(wave)
plt.show()

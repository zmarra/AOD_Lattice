import json
import numpy as np
import random
import os

waveforms = {
    "sine": lambda n, tone_offset, rate: np.exp(n * 2j * np.pi * tone_offset / rate)
}


class WaveformManager(object):

    def __init__(self, waveformFile):
        self.waveformFile = waveformFile
        self.jsonData = self.getJsonData()
        self.initializeWaveforms()

    def changeFile(self, file):
        self.waveformFile = file
        self.jsonData = self.getJsonData()
        self.initializeWaveforms()

    def getJsonData(self):
        with open(self.waveformFile) as read_file:
            data = json.load(read_file)
        read_file.close()
        return data

    def updateJsonData(self, jsonData):
        with open(self.waveformFile, 'w') as outfile:
            json.dump(jsonData, self.waveformFile, indent=4, separators=(',', ': '))
        outfile.close()

    def getMaxAmp(self, channel):
        wave = self.getWaveform(channel)
        return np.max(np.real(wave), axis=0) - np.min(np.real(wave), axis=0)

    def changeAmplitude(self, channel, amplitudes):
        i = 0
        for wave in self.jsonData['Waves'][channel]:
            wave['amplitude'] = amplitudes[i]
            i += 1
        return True

    def changePhases(self, channel, phases):
        i = 0
        for wave in self.jsonData['Waves'][channel]:
            wave['phase'] = phases[i]
            i += 1
        return True

    def randomizePhases(self, channel):
        jsonData = self.getJsonData()
        lines = len(jsonData['Waves'][channel])
        ampThreshold = lines/1.5
        maxAmp = ampThreshold + 1
        while(maxAmp*2 > ampThreshold):
            newPhases = [random.random() for _ in range(lines)]
            self.changePhases(channel, newPhases)
            maxAmp = self.getMaxAmp(channel)
            print maxAmp

    def makeWaveform(self, freqsList, templateFile):
        data = {}
        with open(templateFile) as read_file:
            data = json.load(read_file)
        for channel in len(freqsList):
            for freq in freqsList[channel]:
                data['Waves'][channel].append({"freq": freq, "amplitude": .5, "phase": 0})
        self.updateJsonData(data)
        self.randomizePhases()

    def makeLatticeWaveform(self, lines, spacing, amplitudes, templateFile):
        freqs = np.arange(-(lines-1)/2.0*spacing, ((lines-1)/2.0+1)*spacing, spacing)
        freqsList = [freqs, freqs]
        self.makeWaveform(self, freqsList)

    def getUpdateStatus(self):
        oldModTime = self.modTimeOrig
        modTime = os.stat(self.waveformFile).st_mtime
        self.modTimeOrig = modTime
        return modTime != oldModTime

    def getWaveform(self, channel):
        jsonData = self.getJsonData()
        dataSize = int(np.floor(jsonData['Rate'] / jsonData['waveFreq']))
        wave = np.array(list(map(lambda n: 0, np.arange(dataSize, dtype=np.complex64))), dtype=np.complex64)
        for waveParameters in jsonData['Waves'][channel]:
            currentWave = np.array(list(map(lambda n: waveParameters['amplitude'] * waveforms['sine'](n, waveParameters['freq'], jsonData['Rate']), np.arange(dataSize, dtype=np.complex64))), dtype=np.complex64)
            wave = np.add(wave, np.exp(waveParameters['phase']*np.pi*2j) * currentWave)
        return wave

    def initializeWaveforms(self):
        self.allWaves = []
        for channel in self.jsonData["Channels"]:
            (self.allWaves).append(self.generateWaveforms(channel))

    def generateWaveforms(self, channel):
        dataSize = int(np.floor(self.jsonData["Rate"] / self.jsonData['waveFreq']))
        outputWaveform = []
        for currentWave in self.jsonData['Waves'][channel]:
            wave = np.array(list(map(lambda n: waveforms['sine'](n, currentWave['freq'], self.jsonData["Rate"]), np.arange(dataSize, dtype=np.complex64))), dtype=np.complex64)
            outputWaveform.append(wave)
        return outputWaveform

    def generateOutputWaveform(self, jsonData):
        waves = []
        for channel in range(len(jsonData['Channels'])):
            wave = self.allWaves[0][0]*0
            i = 0
            for currentWave in jsonData['Waves'][channel]:
                    wave = np.add(wave, currentWave['amplitude']*self.allWaves[channel][i]*np.exp(currentWave['phase']*np.pi*2j))
                    i += 1
            waves.append(wave)
        outputWave = np.stack((waves[0], waves[1]), axis=0)
        return outputWave

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
        self.modTime = os.stat(self.waveformFile).st_mtime

    def changeFile(self, file):
        self.waveformFile = file
        self.jsonData = self.getJsonData()
        self.initializeWaveforms()
        self.modTime = os.stat(self.waveformFile).st_mtime

    def getJsonData(self):
        with open(self.waveformFile) as read_file:
            data = json.load(read_file)
        read_file.close()
        return data

    def updateJsonData(self, jsonData):
        with open(self.waveformFile, 'w') as outfile:
            json.dump(jsonData, outfile, indent=4, separators=(',', ': '))
        outfile.close()
        self.jsonData = self.getJsonData()

    def initializeWaveforms(self):
        dataSize = int(np.floor(self.jsonData["Rate"] / self.jsonData['waveFreq']))
        self.allWaves = []
        for channel in self.jsonData["Channels"]:
            self.allWaves.append([])
            for currentWave in self.jsonData['Waves'][channel]:
                wave = np.array(list(map(lambda n: waveforms['sine'](n, currentWave['freq'], self.jsonData["Rate"]), np.arange(dataSize, dtype=np.complex64))), dtype=np.complex64)
                (self.allWaves[channel]).append(wave)

    def randomizePhases(self, channel):
        lines = len(self.jsonData['Waves'][channel])
        ampThreshold = lines/1.5
        maxAmp = ampThreshold + 1
        while(maxAmp*2 > ampThreshold):
            newPhases = [random.random() for _ in range(lines)]
            self.changePhases(channel, newPhases)
            maxAmp = self.getMaxAmp(channel)
            print maxAmp
        self.updateJsonData(self.jsonData)

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

    def getUpdateStatus(self):
        oldModTime = self.modTime
        self.modTime = os.stat(self.waveformFile).st_mtime
        return self.modTime != oldModTime

    def getWaveform(self, channel):
        wave = self.allWaves[0][0]*0
        i = 0
        for currentWave in self.jsonData['Waves'][channel]:
                wave = np.add(wave, currentWave['amplitude']*self.allWaves[channel][i]*np.exp(currentWave['phase']*np.pi*2j))
                i += 1
        return wave

    def generateOutputWaveform(self):
        outputWave = np.stack((self.getWaveform(0), self.getWaveform(1)), axis=0)
        return outputWave

    def makeWaveform(self, freqsList, templateFile):
        data = {}
        with open(templateFile) as read_file:
            data = json.load(read_file)
        print len(freqsList)
        for channel in range(len(freqsList)):
            for freq in freqsList[channel]:
                data['Waves'][channel].append({"freq": freq, "amplitude": .5, "phase": 0})
        self.updateJsonData(data)
        self.randomizePhases(0)
        self.randomizePhases(1)

    def makeLatticeWaveform(self, lines, spacing, templateFile):
        freqs = np.arange(-(lines-1)/2.0*spacing, ((lines-1)/2.0+1)*spacing, spacing)
        freqsList = [freqs, freqs]
        print freqsList
        self.makeWaveform(freqsList, templateFile)
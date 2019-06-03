import sys
import matplotlib.pyplot as plt
import threading
sys.path.insert(0, 'Tools/')
import WaveformManager
import SoftwareDefinedRadio


def streamWaveform(streamer, wave, metadata):
    t = threading.currentThread()
    while getattr(t, "run", True):
        streamingWave = getattr(t, "wave", wave)
        streamer.send(streamingWave, metadata)


waveMan = WaveformManager.WaveformManager("Resources/waveformArguments.json")
waveMan.makeLatticeWaveform(5, 7e5, "Resources/waveformTemplate.json")

SDR = SoftwareDefinedRadio.SoftwareDefinedRadio(waveMan)
SDR.initializeSDR()
wave = wave = waveMan.generateOutputWaveform()
stream = threading.Thread(target=streamWaveform, args=(SDR.streamer, wave, SDR.metadata))
stream.start()

SDR.startStreamingWaveform()
while(True):
    if waveMan.getUpdateStatus():
        stream.wave = waveMan.generateOutputWaveform()

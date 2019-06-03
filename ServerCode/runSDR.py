import sys
import matplotlib.pyplot as plt
sys.path.insert(0, 'Tools/')
import WaveformManager
import SoftwareDefinedRadio

waveMan = WaveformManager.WaveformManager("Resources/waveformArguments.json")
waveMan.makeLatticeWaveform(5, 7e5, "Resources/waveformTemplate.json")

SDR = SoftwareDefinedRadio.SoftwareDefinedRadio(waveMan)
SDR.initializeSDR()
SDR.streamWaveform()
while(True):
    if waveMan.getUpdateStatus():
        SDR.updateWaveform()

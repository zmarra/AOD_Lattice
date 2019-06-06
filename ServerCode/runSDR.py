from Tools.WaveformManager import WaveformManager
from Tools.SoftwareDefinedRadio import SoftwareDefinedRadio


waveMan = WaveformManager.WaveformManager("Resources/waveformArguments.json")
SDR = SoftwareDefinedRadio.SoftwareDefinedRadio(waveMan)

SDR.initializeSDR()
wave = waveMan.generateOutputWaveform()

SDR.startStreamingWaveform()
SDR.startMonitor()

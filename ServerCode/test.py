from Tools.WaveformManager import WaveformManager
from Tools.WaveformMonitor import WaveformMonitor
from Tools.TrapFeedback import TrapFeedback
import time


waveManager = WaveformManager("Resources/waveformArguments.json")
waveMonitor = WaveformMonitor("Resources/waveformArguments.json")
print waveMonitor.getTotalPower(0)
trapFeedback = TrapFeedback(waveManager, 0, 15102504, "127.0.0.1")

trapFeedback.startFeedback()
time.sleep(10)
trapFeedback.stopFeedback()

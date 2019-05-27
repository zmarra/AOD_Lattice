import sys
import numpy as np
import matplotlib.pyplot as plt
sys.path.insert(0, 'Tools/')

import WaveformManager


waveMan = WaveformManager.WaveformManager("Resources/waveformArguments.json")

plt.plot(waveMan.getWaveform(1))
plt.show()

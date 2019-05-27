import sys
import matplotlib.pyplot as plt
sys.path.insert(0, 'Tools/')
import WaveformManager




waveMan = WaveformManager.WaveformManager("Resources/waveformArguments.json")
waveMan.makeLatticeWaveform(5, 7e5, "Resources/waveformTemplate.json")
plt.plot(waveMan.getWaveform(1))
plt.show()





















def main():

    modTimeOrig = os.stat('waveformArguments.json').st_mtime

    while True:
        time.sleep(.05)
        modTime = os.stat('waveformArguments.json').st_mtime
        if modTime != modTimeOrig:
            try:
                with open('waveformArguments.json') as read_file:
                    data = json.load(read_file)
                read_file.close()
                stream.wave = generateOutputWaveform(data)
                stream.isAlive()
                modTimeOrig = modTime
            except:
                time.sleep(.005)


if __name__ == "__main__":
    main()

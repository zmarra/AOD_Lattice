import sys
import uhd
from uhd import libpyuhd as lib
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

jsonData = waveMan.getJsonData()
rate = jsonData['Rate']
gain = jsonData['Gain']
centerFreq = jsonData['CenterFreq']
channels = jsonData['Channels']
usrp = uhd.usrp.MultiUSRP('')

for chan in channels:
    usrp.set_tx_rate(rate, chan)
    usrp.set_tx_freq(lib.types.tune_request(centerFreq), chan)
    usrp.set_tx_gain(gain, chan)
st_args = lib.usrp.stream_args("fc32", "sc16")
st_args.channels = channels
streamer = usrp.get_tx_stream(st_args)
buffer_samps = streamer.get_max_num_samps()
metadata = lib.types.tx_metadata()

wave = waveMan.generateOutputWaveform()

stream = threading.Thread(target=streamWaveform, args=(streamer, wave, metadata))
stream.start()

while(True):
    if waveMan.getUpdateStatus():
        stream.wave = waveMan.generateOutputWaveform()

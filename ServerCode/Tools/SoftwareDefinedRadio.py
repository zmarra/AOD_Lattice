import uhd
from uhd import libpyuhd as lib
import threading


def streamWaveform(streamer, metadata, wave):
    t = threading.currentThread()
    while getattr(t, "run", True):
        streamingWave = getattr(t, "wave", wave)
        streamer.send(streamingWave, metadata)
    return "SDR killed"


class SoftwareDefinedRadio(object):

        def __init__(self, waveMan):
            self.waveMan = waveMan

        def initializeSDR(self):
            jsonData = self.waveMan.getJsonData()
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
            self.streamer = usrp.get_tx_stream(st_args)
            self.buffer_samps = self.streamer.get_max_num_samps()
            self.metadata = lib.types.tx_metadata()

        def startStreamingWaveform(self):
            wave = self.waveMan.generateOutputWaveform()
            self.stream = threading.Thread(target=streamWaveform, args=(self.streamer, self.metadata, wave))
            self.stream.start()

        def updateWaveform(self):
            (self.stream).wave = self.waveMan.generateOutputWaveform()
            self.stream.isAlive()

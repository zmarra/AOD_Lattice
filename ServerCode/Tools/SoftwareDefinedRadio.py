import uhd
from uhd import libpyuhd as lib
import threading


class SoftwareDefinedRadio(object):

        def __init__(self, waveMan):
            self.waveMan = waveMan

        def initializeSDR(self, jsonData):
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
            self.buffer_samps = streamer.get_max_num_samps()
            self.metadata = lib.types.tx_metadata()

        def streamWaveform(self, streamer, wave):
            t = threading.currentThread()
            while getattr(t, "run", True):
                streamingWave = getattr(t, "wave", self.wave)
                streamer.send(streamingWave, self.metadata)
            return "SDR killed"

'''
* All Rights Reserved.
* 
* NOTICE: All information contained herein is, and remains
* the property of Oticon Medical A/S,if any.
* The intellectual and technical concepts contained
* herein are proprietary to Oticon Medical A/S
* and may be covered by U.S. and other Patents (e.g. EP, CN or AU patents),
* patents in process, and are protected by trade secret or copyright law.
* Dissemination of this information or reproduction of this material
* is strictly forbidden unless prior written permission is obtained
* from Oticon Medical.
*
* Oticon Medical A/S, hereby claims all copyright interest in the program “libmixer.py”.
*
* Copyright,2020, Oticon Medical A/S.
*
'''

from threading import Thread
import numpy as np
import rtmixer
RingBuffer = rtmixer.RingBuffer

import soundfile as sf
import resampy
from math import sqrt, inf, log, ceil
from pylsl.pylsl import local_clock

class player(object):
    def __init__(self, level_Re_max, dic, stream = None, calibration = [], loop = False, message = [None, None]):
        """
        Player: Class to play sounds in a stream with advanced parameters.
            This class uses the rtmixer module based on sounddevice's bindings for PortAudio.

        Parameters
        ----------
        device : ``int`` --
            The index of the device to play through as referenced by the 
            rtmixer library.

        level_Re_max : ``int`` -- 
            The maximum level in decibels expected to play if the rms of the
            signal is 1. 

        dic : ``dict`` --
            A dictionnary of dictionnary of the parameters for each sound file 
            to play. Each key is the path to the sound file and the item the
            corresponding parameters:

                - 'channels': the channels through which the sound file will
                be played.

                - 'level': the level at which the file will be played.

        stream : ``rtmixer.Mixer``, optional --
            The stream to use, by default None

        loop : ``bool``, optional --
            Whether the stream should be looped or not, by default False.
            NOTE: Loop are not yet supported.

        calibration : ``list``, optional --
            The value of gains to apply to each channel, by default []

        Returns
        -------
        ``player`` --
            The instance of the object to play sounds and preprocess them.
        """
        self.dict = dic
        
        self.Lname = int(len(self.dict))
        # Initialise values
        self.device = rtmixer._sd.default.device[1]
        self.maxchan = get_max_output_channels()
        self.mapp = list(range(1, self.maxchan + 1))
        self.level_Re_max = level_Re_max

        self.loop = loop
        self.stream = stream
        self.calibration = calibration
        self.dataIn = []

        # Fix the sampling frequency here.
        self.fs = get_default_samplerate()
        self.min_len = inf
        self.signals = []
        self.end_signals = []
        
        self.message = message
        self.LSLnotifier = None

    def process_data(self) -> None:
        """
            Create the individual signals in numpy arrays that will be played. 
        """
        # Import data 
        for (_1, idn) in enumerate(self.dict.keys()):
            if len(idn) == 0:
                signal = np.zeros((1,))
            else:
                try:
                    signal, fs_s = sf.read(idn, dtype='float32')
                    
                    # Combine channels, we expected mono files
                    if len(signal.shape) > 1 :
                        signal = np.sum(signal, 1)
                        
                    if self.fs != fs_s:
                        # Prepare resampling
                        ratio = self.fs/fs_s
                        L = len(signal)
                        nextpow = ceil(log(L, 2))
                        pad = 2**nextpow - L
                        # Pad to a power of 2
                        data_pad = np.hstack([signal, np.zeros(pad)])

                        # Resample
                        data_re = resampy.resample(data_pad, fs_s, self.fs)
                        
                        # Remove extra zeros
                        signal = (data_re[:int(L*ratio)])

                    if self.fs != 0:
                        # First set level to 1
                        rms = np.sqrt(np.sum(np.square(signal)) / len(signal))
                        signal = np.divide(signal, rms)
                        
                except Exception as e:
                    print("Error in process data: ", e)
                    signal = np.zeros((1,))
                    fs_s = self.fs  

            # Get the shortest signal, we stop at the same time as it does
            if len(signal) < self.min_len:
                self.min_len = len(signal) 
            self.dataIn.append(signal)
        
        return

    def create_signal(self) -> None:    
        """
            Put the signals in the correct column for multichannels outputs. Signals are trimmed to the signal's minimum length.
        """
        # Now create matrices for each signal and create final signal 
        self.dataOut =  np.zeros(
            (self.min_len, self.maxchan), dtype = 'float32')

        # Set level and channel for final matrix
        for (ix, idn) in enumerate(self.dict.keys()):
            # Compute level
            level = min(1, 
                (10**((self.dict[idn]['level'] - self.level_Re_max)/20))
            )
            for idx in self.dict[idn]['channels']:
                # Extract the considered length
                short_sig = self.dataIn[ix][:self.min_len]
                self.dataOut[:,idx-1] += short_sig * level
        return

    def prepare_message_time(self):
        self.timings = [0, self.min_len/self.fs] 
    
    def apply_calibration(self) -> None:
        """
        If a calibration has been set apply the gains to the different channels.
        """

        # Check if calibration is valid
        if len(self.calibration) != self.maxchan: 
            self.calibration = []

        # Convert to linear scale
        if self.calibration:                                                
            for ch in range(self.maxchan):
                self.dataOut[: , ch] *= 10**(self.calibration[ch]/20)
                
        # Interleave the signal + convert to bytes to send to ringbuffer
        self.dataOut = self.dataOut.ravel('C')
        dataByte = self.dataOut.tobytes()
        nextpow = ceil(log(len(dataByte), 2))

        # Create a ring buffer length must be a power of 2.
        self.dataRB = RingBuffer(self.stream.samplesize * self.maxchan,
                                 size = 2**nextpow)

        self.dataRB.write(dataByte)

        # Make sure the stream gets the correct parameters
        self.stream_parameters()

    def stream_parameters(self) -> None:
        """
        stream_parameters: Get the relevant stream parameters for it to work.
        """
        # Get latency
        try:
            latency = self.stream.latency[1]
        except TypeError:
            latency = self.stream.latency

        # Compute the period size
        self.periodsize = max(
            int(round(latency * self.stream.samplerate)), 
            self.stream.blocksize
            )
    
        if self.stream.blocksize == 0:
            self.framePerBuffer = self.periodsize//(self.stream.samplesize-1)
        else:
            self.framePerBuffer = self.stream.blocksize
        return

    def prepare(self, messages = True) -> None:
        self.process_data()
        self.create_signal()
        self.prepare_message_time()

    def play(self, messages = True, smallblock = False) -> None:
        # Start playing and sending the signals
        if self.fs != 0:
            if self.stream is not None:
                self.stream.close()
                
            block = 32 if smallblock else 0
            self.stream = rtmixer.Mixer(
                channels = self.maxchan, 
                device = self.device, 
                samplerate = self.fs,
                blocksize = block, latency = 'low'
                )

            self.stream.start()
            self.apply_calibration()

            # Thread to play sounds
            self.thread_loop = Thread(target = self.thread_play)
            # Daemon thread to avoid blocking.
            self.thread_loop.daemon = True
            self.thread_loop.start()

    def start_pause(self) -> None:
        """
        Simple start/pause function.
        """''
        if self.stream.stopped:
            self.stream.start()
        else:
            self.stream.stop()

    def thread_play(self) -> None:
        """
        thread_play: function to play the sounds, to be called in a thread, takes care of both continuous and not continuous sounds.
        """
        timings = self.timings  
        signals = self.message
        stream = self.stream
        rb = RingBuffer(stream.samplesize * self.maxchan,
                                 size = 0)
        if self.loop:
            s = ''
            # NOTE: if enabled no more messages.
            while self.loop:
                # Self implementation of loops
                if not (s in stream.actions):
                    s = stream.play_ringbuffer(self.dataRB, channels=self.mapp)
                    wi = self.dataRB._lib.PaUtil_AdvanceRingBufferWriteIndex(self.dataRB._ptr, 0)
                ri = self.dataRB._lib.PaUtil_AdvanceRingBufferReadIndex(self.dataRB._ptr, 0)          
                if ri > wi -  self.framePerBuffer:
                    # Go back in time
                    self.dataRB._lib.PaUtil_AdvanceRingBufferReadIndex(self.dataRB._ptr, -wi + self.framePerBuffer)
        else:
            # Normal play
            action = stream.play_ringbuffer(self.dataRB, channels=self.mapp)
            stream.start()
            # Need to wait a bit to ensure time is written in memory
            stream.wait(stream.play_ringbuffer(rb, channels=self.mapp))
            
            # Get the real start, same clock as lsl
            realStart = action.actual_time 
            current = realStart
            # For each time stamp, wait and send
            for (timing, mess) in zip(timings, signals):
                
                # Wait, if negative: no wait
                while current - realStart < timing:
                    current = local_clock()
                
                # For lsl we know the timing, send the overwritten
                if self.LSLnotifier is not None:
                    self.LSLnotifier.send_message(
                        mess, 
                        timestamp = timing + realStart
                        )
        
    def get_stream(self) -> rtmixer.Mixer:
        """
        Helper function

        Returns
        -------
        ``rtmixer.Mixer`` --
            The mixer stream used by the object.
        """
        return self.stream
   
    def setLSL(self, notif):
        self.LSLnotifier = notif
        
    def cleanup(self):
        lock = self.thread_loop._tstate_lock
        if type(self.stream) is rtmixer.Mixer:
            self.stream.stop()
        self.loop = False
        if lock is not None and lock.locked() :
            self.thread_loop._tstate_lock.release()
        self.thread_loop._stop()
        
# API to use for OpenSesame integration
def string_to_list(strg, sep, to_num = 'int') -> list:
    # converts string to list, used in OpenSesame.
    if type(strg) is str:
        parse = strg.split(sep)
        if isinstance(to_num, str) or to_num:
            while '' in parse: 
                parse.remove('')
            for ix, el in enumerate(parse):
                if to_num == 'float':
                    parse[ix] = round(float(el), 1)
                elif to_num == 'int' or to_num:
                    parse[ix] = int(el)
    elif type(strg) is int:
        parse = [strg]
    else:
        raise TypeError(
        'Expected int or string but received %s' % type(strg)
        ) 
    return parse

def list_to_string(list, sep) -> str:
    # Converts string to list used in OpenSesame.
    if not isinstance(sep, str):
        raise Exception('Separator should be a string')
    stg = str(list[0])
    if len(list) > 1: 
        for i in list[1: -1]:
            stg += sep + str(i)
        stg += sep + list[-1]
    return stg

def get_max_output_channels() -> int: 
    return rtmixer._sd.query_devices(
        rtmixer._sd.default.device[1])['max_output_channels']

def get_default_samplerate() -> int:
    return int(rtmixer._sd.query_devices(
        rtmixer._sd.default.device[1])['default_samplerate'])
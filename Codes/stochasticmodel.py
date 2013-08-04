import numpy as np
import matplotlib.pyplot as plt
import wavplayer as wp
from scipy.io.wavfile import read
from scipy.signal import hamming, hanning, resample
from scipy.fftpack import fft, ifft
import time

def stochastic_model(x, w, N, H, stocf) :
  # x: input array sound, w: analysis window, N: FFT size, H: hop size, 
  # stocf: decimation factor of mag spectrum for stochastic analysis
  # y: output sound

  hN = N/2                                                 # size of positive spectrum
  hM = (w.size)/2                                          # half analysis window size
  pin = hM                                                 # initialize sound pointer in middle of analysis window       
  pend = x.size-hM                                         # last sample to start a frame
  fftbuffer = np.zeros(N)                                  # initialize buffer for FFT
  x = np.float32(x) / (2**15)                              # normalize input signal (so 0 dB is the max amp. value)
  yw = np.zeros(w.size)                                    # initialize output sound frame
  y = np.zeros(x.size)                                     # initialize output array
  w = w / sum(w)                                           # normalize analysis window
  ws = hanning(w.size)*2                                   # synthesis window

  while pin<pend:       
            
  #-----analysis-----             
    xw = x[pin-hM:pin+hM] * w                              # window the input sound
    X = fft(xw)                                            # compute FFT
    mX = 20 * np.log10( abs(X[:hN]) )                      # magnitude spectrum of positive frequencies
    mXenv = resample(np.maximum(-200, mX), mX.size*stocf)  # decimate the mag spectrum     

  #-----synthesis-----
    mY = resample(mXenv, hN)                               # interpolate to original size
    pY = 2*np.pi*np.random.rand(hN)                      # generate phase random values
    # pY = np.zeros(hN)
    Y = np.zeros(N, dtype = complex)
    Y[:hN] = 10**(mY/20) * np.exp(1j*pY)                   # generate positive freq.
    Y[hN+1:] = 10**(mY[:0:-1]/20) * np.exp(-1j*pY[:0:-1])  # generate negative freq.

    fftbuffer = np.real( ifft(Y) )                         # inverse FFT
    y[pin-hM:pin+hM] += H*ws*fftbuffer                     # overlap-add
    pin += H                                               # advance sound pointer
  
  return y

(fs, x) = read('speech-female.wav')
# wp.play(x, fs)
# fig = plt.figure()
w = np.hamming(512)
N = 512
H = 256
stocf = 0.5
y = stochastic_model(x, w, N, H, stocf)

y *= 2**15
y = y.astype(np.int16)
wp.play(y, fs)
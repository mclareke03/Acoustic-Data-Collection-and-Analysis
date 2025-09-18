import numpy as np
from scipy.signal import windows, hilbert
from scipy.fft import rfft, rfftfreq

def rms_normalize(x: np.ndarray) -> np.ndarray:
    if x.size == 0:
        return x
    rms = float(np.sqrt(np.mean(x**2)))
    return x / rms if rms > 0 else x

def apply_hann(x: np.ndarray) -> np.ndarray:
    return x * windows.hann(len(x))

def rfft_mag(x: np.ndarray) -> np.ndarray:
    return np.abs(rfft(x)) / len(x)

def rfftfreq_hz(N: int, sr: int) -> np.ndarray:
    return rfftfreq(N, d=1.0 / sr)

def envelope(x: np.ndarray) -> np.ndarray:
    return np.abs(hilbert(x))
import numpy as np
from .dsp import rms_normalize, apply_hann, rfft_mag, rfftfreq_hz, envelope

def avg_fft(chunks, sr):
    """
    Average FFT magnitude across 1 s chunks, RMS-normalized for comparison.
    Returns (freqs, mag).
    """
    if not chunks:
        return np.array([]), np.array([])
    N = len(chunks[0])
    acc = None
    for x in chunks:
        x = rms_normalize(x)
        X = rfft_mag(apply_hann(x))
        acc = X if acc is None else (acc + X)
    avg = acc / len(chunks)
    return rfftfreq_hz(N, sr), rms_normalize(avg)

def avg_envelope_fft(chunks, sr):
    """
    Average FFT magnitude of amplitude envelope, RMS-normalized.
    """
    if not chunks:
        return np.array([]), np.array([])
    N = len(chunks[0])
    acc = None
    for x in chunks:
        env = envelope(x)
        X = rfft_mag(env)  # windowing optional for envelope
        acc = X if acc is None else (acc + X)
    avg = acc / len(chunks)
    return rfftfreq_hz(N, sr), rms_normalize(avg)

def concat_time(chunks):
    """
    Concatenate chunks into one long time series and RMS-normalize.
    """
    if not chunks:
        return np.array([])
    y = np.concatenate(chunks)
    return rms_normalize(y)

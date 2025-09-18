from __future__ import annotations
import os
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets import CheckButtons
from typing import Optional
from .features import avg_fft, avg_envelope_fft, concat_time
from .dsp import rms_normalize          # NEW: we use rms_normalize here

def _add_checkboxes(fig, ax, lines, labels, panel_rect=(0.80, 0.20, 0.18, 0.60)):
    """
    Robust checkbox panel:
      - dict mapping (label -> line)
      - draw_idle() for refresh
      - keep a reference to avoid GC
      - avoid tight_layout after adding panel
    """
    fig.subplots_adjust(right=min(0.78, 1 - panel_rect[2] - 0.02))

    mapping = {}
    safe_labels = []
    for lab, ln in zip(labels, lines):
        lab = str(lab)
        mapping[lab] = ln
        safe_labels.append(lab)

    rax = fig.add_axes(panel_rect)
    rax.set_title("Show/Hide", fontsize=10)
    rax.set_facecolor((0.96, 0.96, 0.96))

    states = [ln.get_visible() for ln in lines]
    checks = CheckButtons(rax, safe_labels, states)

    def on_click(label):
        ln = mapping.get(label)
        if ln is None:
            return
        ln.set_visible(not ln.get_visible())
        fig.canvas.draw_idle()

    checks.on_clicked(on_click)
    fig._checkbox_panel = checks  # keep reference
    fig._checkbox_mapping = mapping
    return checks

def _save_or_show(fig, save_dir: Optional[str], filename: str, file_format: str):
    """
    If save_dir is provided, save as SVG (or given format) and close.
    Otherwise show interactively.
    """
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
        path = os.path.join(save_dir, filename)
        fig.savefig(path, dpi=150, bbox_inches="tight", format=file_format)
        print(f"Saved: {path}")
        plt.close(fig)
    else:
        plt.show()

def plot_avg_fft(
    results,
    xlim_hz: float = 3000,
    save_dir: Optional[str] = None,
    filename: str = "avg_fft.svg",
    file_format: str = "svg",
):
    instances = results["instances"]
    sr = results["samplerate"]
    if not instances or not sr:
        print("Nothing to plot (FFT).")
        return

    fig, ax = plt.subplots(figsize=(12, 6))
    lines, labels = [], []
    for lbl in instances:
        f, y = avg_fft(results["chunks"][lbl], sr)
        line, = ax.plot(f, y, label=lbl, linewidth=1.0)
        lines.append(line); labels.append(lbl)

    ax.set_xlim(0, xlim_hz)
    ax.set_title("Average FFT (RMS-normalized)")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Magnitude")
    ax.grid(True, alpha=0.25)

    if save_dir is None:  # only interactive
        _add_checkboxes(fig, ax, lines, labels)

    _save_or_show(fig, save_dir, filename, file_format)

def plot_avg_envelope_fft(
    results,
    xlim_hz: float = 1000,
    save_dir: Optional[str] = None,
    filename: str = "avg_envelope_fft.svg",
    file_format: str = "svg",
):
    instances = results["instances"]
    sr = results["samplerate"]
    if not instances or not sr:
        print("Nothing to plot (Envelope FFT).")
        return

    fig, ax = plt.subplots(figsize=(12, 6))
    lines, labels = [], []
    for lbl in instances:
        f, y = avg_envelope_fft(results["chunks"][lbl], sr)
        line, = ax.plot(f, y, label=lbl, linewidth=1.0)
        lines.append(line); labels.append(lbl)

    ax.set_xlim(0, xlim_hz)
    ax.set_title("Envelope FFT (RMS-normalized)")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Magnitude")
    ax.grid(True, alpha=0.25)

    if save_dir is None:
        _add_checkboxes(fig, ax, lines, labels)

    _save_or_show(fig, save_dir, filename, file_format)


def _concat_first_seconds(chunks, sr, max_seconds: float) -> np.ndarray:
    """
    Concatenate only up to 'max_seconds' of audio from the list of chunks.
    This avoids allocating the full recording if it's long.
    """
    if not chunks:
        return np.array([])
    if not max_seconds or max_seconds <= 0:
        # Fallback: full concat (not ideal for huge sets)
        y = np.concatenate(chunks)
        return rms_normalize(y)

    max_samples = int(sr * max_seconds)
    if max_samples <= 0:
        return np.array([])

    buf = []
    count = 0
    for x in chunks:
        remain = max_samples - count
        if remain <= 0:
            break
        take = min(len(x), remain)
        buf.append(x[:take])
        count += take

    if not buf:
        return np.array([])

    y = np.concatenate(buf)
    return rms_normalize(y)

def plot_concat_time_domain(
    results,
    max_seconds: float = 10.0,
    save_dir: Optional[str] = None,
    filename: str = "concat_time.svg",
    file_format: str = "svg",
):
    instances = results.get("instances", [])
    sr = results.get("samplerate", None)
    if not instances or not sr:
        print("Nothing to plot (Time Domain).")
        return

    fig, ax = plt.subplots(figsize=(12, 6))
    lines, labels = [], []
    for lbl in instances:
        # Concatenate only up to the target seconds to avoid big allocations
        y = _concat_first_seconds(results["chunks"][lbl], sr, max_seconds)
        if y.size == 0:
            continue

        # Decimate for plotting so UI remains responsive
        target_points = 20000
        step = max(1, y.size // target_points)
        y_plot = y[::step]
        t = (np.arange(y_plot.size, dtype=np.float64) * step) / sr

        line, = ax.plot(t, y_plot, label=lbl, linewidth=0.9)
        lines.append(line); labels.append(lbl)

    ax.set_title(f"Concatenated Time Domain (first {max_seconds}s, normalized)")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.grid(True, alpha=0.25)

    if save_dir is None:
        _add_checkboxes(fig, ax, lines, labels)

    _save_or_show(fig, save_dir, filename, file_format)

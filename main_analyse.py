import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

# --- Add src to sys.path so we can import analysis package ---
ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# --- Import from your analysis package ---
from analysis.analysis import load_session
from analysis.plotting import (
    plot_avg_fft,
    plot_avg_envelope_fft,
    plot_concat_time_domain,
)

from analysis.io import suggest_output_dir  # to decide where to save SVGs

def browse_path(entry):
    path = filedialog.askdirectory(
        title="Select a session folder, a single instance folder, or a chunks folder"
    )
    if path:
        entry.delete(0, tk.END)
        entry.insert(0, path)

def run_selected(selection_path, do_fft, do_env, do_time, do_save):
    if not os.path.isdir(selection_path):
        messagebox.showerror("Error", "Please select a valid folder.")
        return

    # Close GUI before plotting to avoid event loop clashes
    root.destroy()

    # Load selection (session / instance / chunks)
    results = load_session(selection_path)
    if not results["instances"]:
        print("No valid audio found. Ensure you selected a session/instance/chunks with 1-second WAV files.")
        return

    # If saving, decide where to save
    save_dir = suggest_output_dir(selection_path) if do_save.get() else None

    if do_fft.get():
        plot_avg_fft(
            results,
            xlim_hz=3000,
            save_dir=save_dir,
            filename="avg_fft.svg",
            file_format="svg",
        )

    if do_env.get():
        plot_avg_envelope_fft(
            results,
            xlim_hz=1000,
            save_dir=save_dir,
            filename="avg_envelope_fft.svg",
            file_format="svg",
        )

    if do_time.get():
        plot_concat_time_domain(
            results,
            max_seconds=10,
            save_dir=save_dir,
            filename="concat_time.svg",
            file_format="svg",
        )

# --- GUI ---
root = tk.Tk()
root.title("Acoustic Analysis")

frm = tk.Frame(root, padx=12, pady=12)
frm.pack(fill="both", expand=True)

# Path selector
tk.Label(frm, text="Session / Instance / Chunks:").grid(row=0, column=0, sticky="w")
path_entry = tk.Entry(frm, width=70)
path_entry.grid(row=0, column=1, padx=6)
tk.Button(frm, text="Browse", command=lambda: browse_path(path_entry)).grid(row=0, column=2)

# Feature checkboxes
tk.Label(frm, text="Select features to run:").grid(row=1, column=0, columnspan=3, sticky="w", pady=(12, 4))
do_fft = tk.BooleanVar(value=True)
do_env = tk.BooleanVar(value=True)
do_time = tk.BooleanVar(value=True)
tk.Checkbutton(frm, text="Average FFT", variable=do_fft).grid(row=2, column=0, sticky="w")
tk.Checkbutton(frm, text="Envelope FFT", variable=do_env).grid(row=2, column=1, sticky="w")
tk.Checkbutton(frm, text="Concatenated Time-Domain", variable=do_time).grid(row=2, column=2, sticky="w")

# Save toggle
tk.Label(frm, text="Output:").grid(row=3, column=0, sticky="w", pady=(12, 0))
do_save = tk.BooleanVar(value=False)
tk.Checkbutton(frm, text="Save plots as SVG (no interactive display)", variable=do_save).grid(
    row=3, column=1, sticky="w", columnspan=2
)

# Buttons
btn_frame = tk.Frame(frm, pady=12)
btn_frame.grid(row=4, column=0, columnspan=3, sticky="e")
tk.Button(
    btn_frame,
    text="Run",
    command=lambda: run_selected(path_entry.get(), do_fft, do_env, do_time, do_save),
).pack(side="right", padx=6)
tk.Button(btn_frame, text="Quit", command=root.destroy).pack(side="right")

root.mainloop()

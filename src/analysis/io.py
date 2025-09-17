import os
import numpy as np
import soundfile as sf
from typing import List, Tuple

def to_mono(x: np.ndarray) -> np.ndarray:
    return x if x.ndim == 1 else x.mean(axis=1)

def _is_session_folder(path: str) -> bool:
    try:
        entries = os.listdir(path)
    except Exception:
        return False
    return any(
        os.path.isdir(os.path.join(path, d)) and d.startswith("instance_")
        for d in entries
    )

def _is_instance_folder(path: str) -> bool:
    chunks_dir = os.path.join(path, "chunks")
    if os.path.isdir(chunks_dir):
        return True
    return os.path.basename(path).startswith("instance_")

def _is_chunks_folder(path: str) -> bool:
    if not os.path.isdir(path):
        return False
    return any(f.lower().endswith(".wav") for f in os.listdir(path))

def resolve_chunks_dir(path: str) -> str | None:
    """
    Accepts either:
      - an instance folder containing 'chunks'
      - a 'chunks' folder itself
    Returns the absolute chunks directory, or None if not found.
    """
    if os.path.isdir(os.path.join(path, "chunks")):
        return os.path.join(path, "chunks")
    if _is_chunks_folder(path):
        return path
    return None

def suggest_output_dir(selection_path: str) -> str:
    """
    If user selected session => save into that folder
    If instance folder => save there
    If chunks folder => save into its parent (the instance folder)
    """
    if _is_session_folder(selection_path):
        return selection_path
    if _is_instance_folder(selection_path):
        return selection_path
    if _is_chunks_folder(selection_path):
        return os.path.dirname(selection_path)
    return selection_path

def get_instance_paths_from_selection(selection_path: str) -> List[Tuple[str, str]]:
    """
    Returns a list of (label, instance_path) based on what the user selected.
    - If a session folder is selected: all instance_* subfolders
    - If an instance folder is selected: just that one
    - If a chunks folder is selected: parent instance
    """
    selection_path = os.path.abspath(selection_path)

    if _is_session_folder(selection_path):
        labels_paths = []
        for d in sorted(os.listdir(selection_path)):
            inst_path = os.path.join(selection_path, d)
            if os.path.isdir(inst_path) and d.startswith("instance_"):
                labels_paths.append((d, inst_path))
        return labels_paths

    if _is_instance_folder(selection_path):
        label = os.path.basename(selection_path)
        return [(label, selection_path)]

    if _is_chunks_folder(selection_path):
        inst_path = os.path.dirname(selection_path)
        label = os.path.basename(inst_path)
        return [(label, inst_path)]

    # Fallback: treat as instance path with best-effort label
    label = os.path.basename(selection_path) or "instance"
    return [(label, selection_path)]

def load_chunks(instance_or_chunks_path: str, expect_seconds: float = 1.0) -> List[Tuple[np.ndarray, int]]:
    """
    Loads 1-second WAV chunks, accepting either an instance path with a 'chunks' subfolder,
    or a chunks folder directly.
    Returns: list of (signal_1d, sr).
    """
    chunks_dir = resolve_chunks_dir(instance_or_chunks_path)
    if not chunks_dir or not os.path.isdir(chunks_dir):
        return []

    wav_files = sorted([f for f in os.listdir(chunks_dir) if f.lower().endswith(".wav")])
    results: List[Tuple[np.ndarray, int]] = []
    for f in wav_files:
        file_path = os.path.join(chunks_dir, f)
        try:
            data, sr = sf.read(file_path, dtype="float32", always_2d=False)
        except Exception:
            continue
        x = to_mono(np.asarray(data))
        if sr > 0 and len(x) > 0 and abs(len(x) / sr - expect_seconds) <= 1e-3:
            results.append((x, sr))
    return results
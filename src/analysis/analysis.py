from __future__ import annotations
from typing import Dict, Any, List
from .io import get_instance_paths_from_selection, load_chunks

def load_session(selection_path: str, expect_seconds: float = 1.0) -> Dict[str, Any]:
    """
    Load either:
      - a full session (multiple instance_* folders),
      - a single instance folder, OR
      - a 'chunks' folder.

    Keeps only instances whose SR and chunk length match the first accepted instance.

    Returns:
      {
        "samplerate": sr or None,
        "instances": [label, ...],
        "chunks": { label: [np.ndarray, ...] }
      }
    """
    results: Dict[str, Any] = {"samplerate": None, "instances": [], "chunks": {}}

    pairs: List[tuple[str, str]] = get_instance_paths_from_selection(selection_path)
    if not pairs:
        return results

    session_sr = None
    session_N = None

    for label, inst_path in pairs:
        chunk_pairs = load_chunks(inst_path, expect_seconds=expect_seconds)
        if not chunk_pairs:
            continue

        srs = {sr for _, sr in chunk_pairs}
        Ns  = {len(x) for x, _ in chunk_pairs}
        if len(srs) != 1 or len(Ns) != 1:
            # per-instance consistency required
            continue

        sr = srs.pop()
        N  = Ns.pop()

        if session_sr is None:
            session_sr, session_N = sr, N
        elif sr != session_sr or N != session_N:
            # skip instances that don't match the first accepted one
            continue

        results["instances"].append(label)
        results["chunks"][label] = [x for x, _ in chunk_pairs]

    results["samplerate"] = session_sr
    return results
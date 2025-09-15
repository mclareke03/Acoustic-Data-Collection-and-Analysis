import json
import os
import tkinter as tk
from tkinter import simpledialog

def save_manifest_and_notes(session_info, session_path, chunk_metadata):
    root = tk.Tk()
    root.withdraw()
    notes = simpledialog.askstring("Session Notes", "Enter any observations or notes for this session:")
    root.destroy()

    manifest = {
        "Session": {
            "Name": session_info["session_name"],
            "Timestamp": session_path.split("_")[-1],
            "Machine": {
                "Type": session_info["machine_type"],
                "RotorConfiguration": session_info["rotor_configuration"],
                "RotationSpeed": session_info["rotation_speed"]
            },
            "Fault": {
                "Status": session_info["fault_status"]
            },
            "MicPosition": session_info["mic_position"],
            "Notes": notes.strip() if notes else ""
        },
        "Chunks": chunk_metadata
    }

    manifest_path = os.path.join(session_path, "session_manifest.json")
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=4)

    print(f"📁 Manifest saved to: {manifest_path}")

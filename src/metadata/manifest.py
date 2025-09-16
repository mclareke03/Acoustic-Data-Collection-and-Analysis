import json
import os
import tkinter as tk
from tkinter import simpledialog

def save_manifest_and_notes(session_info, session_path, instance_folder_name, chunk_metadata):
    root = tk.Tk()
    root.withdraw()
    notes = simpledialog.askstring("Session Notes", "Enter any observations or notes for this instance:")
    root.destroy()

    manifest_path = os.path.join(session_path, "session_manifest.json")
    notes_path = os.path.join(session_path, "session_notes.tex")

    # === Load existing manifest if it exists ===
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
    else:
        manifest = {
            "Session": {
                "SessionName": session_info["session_name"],
                "MachineType": session_info["machine_type"],
                "RotorConfiguration": session_info["rotor_configuration"]
            },
            "Instances": []
        }

    # === Append new instance ===
    manifest["Instances"].append({
    "InstanceName": instance_folder_name,
    "FaultStatus": session_info["fault_status"],
    "RotationSpeed": session_info["rotation_speed"],
    "MicPosition": session_info["mic_position"],
    "VolumeRatio": session_info["volume_ratio"],
    "Chunks": chunk_metadata
})


    # === Save updated manifest ===
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=4)

    # === Save notes (append if exists) ===
    with open(notes_path, 'a') as f:
        f.write("\n% Notes for Instance: {}\n".format(instance_folder_name))
        f.write(notes.strip() if notes else "")
        f.write("\n")

    print(f"📁 Manifest updated: {manifest_path}")
    print(f"📝 Notes updated: {notes_path}")

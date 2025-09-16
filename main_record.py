from src.config.session_config import load_last_config, save_last_config
from src.gui.session_gui import collect_session_info
from src.recording.recorder import start_recording_session
from src.metadata.manifest import save_manifest_and_notes

def main():
    last_config = load_last_config()
    session_info = collect_session_info(last_config)
    save_last_config(session_info)

    session_path, instance_folder_name, chunk_metadata = start_recording_session(session_info)
    save_manifest_and_notes(session_info, session_path, instance_folder_name, chunk_metadata)

if __name__ == "__main__":
    main()

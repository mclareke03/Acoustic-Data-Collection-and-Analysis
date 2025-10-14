import tkinter as tk
from tkinter import simpledialog, ttk

def get_dropdown_input(title, prompt, options, initial_value):
    dropdown_win = tk.Toplevel()
    dropdown_win.title(title)
    dropdown_win.geometry("300x150")
    dropdown_win.grab_set()

    label = ttk.Label(dropdown_win, text=prompt)
    label.pack(pady=10)

    combo = ttk.Combobox(dropdown_win, values=options, state="readonly")
    combo.set(initial_value if initial_value in options else options[0])
    combo.pack(pady=10)

    selected_value = tk.StringVar()

    def confirm():
        selected_value.set(combo.get())
        dropdown_win.destroy()

    confirm_btn = ttk.Button(dropdown_win, text="Confirm", command=confirm)
    confirm_btn.pack(pady=10)

    dropdown_win.wait_window()
    return selected_value.get()

def get_percentage_dropdown(title, prompt, initial_value):
    dropdown_win = tk.Toplevel()
    dropdown_win.title(title)
    dropdown_win.geometry("300x150")
    dropdown_win.grab_set()

    label = ttk.Label(dropdown_win, text=prompt)
    label.pack(pady=10)

    options = ["N/A"] + [f"{i}%" for i in range(0, 110, 10)]
    combo = ttk.Combobox(dropdown_win, values=options, state="readonly")
    combo.set(initial_value if initial_value in options else options[0])
    combo.pack(pady=10)

    selected_value = tk.StringVar()

    def confirm():
        selected_value.set(combo.get())
        dropdown_win.destroy()

    confirm_btn = ttk.Button(dropdown_win, text="Confirm", command=confirm)
    confirm_btn.pack(pady=10)

    dropdown_win.wait_window()
    return selected_value.get()

def collect_session_info(last_config):
    root = tk.Tk()
    root.withdraw()

    machine_type = get_dropdown_input(
        "Session Setup", "Select machine type:",
        ["Oil-Free screw compressor", "Oil-Injected screw compressor", "Balanced Fan"],
        last_config["machine_type"]
    )

    fault_status = get_dropdown_input(
        "Session Setup", "Select fault status:",
        ["Healthy", "Unbalanced", "Bearing Fault", "Gear Mesh Fault", "Misalignment",
         "Looseness", "Electrical Fault", "Lubrication Issue", "Rotor Damage", "Unknown"],
        last_config["fault_status"]
    )

    volume_ratio = get_percentage_dropdown(
        "Session Setup", "Select volume ratio:",
        last_config.get("volume_ratio", "")
    )

    rotation_speed = simpledialog.askstring("Session Setup", "Enter rotation speed (RPM):", initialvalue=last_config["rotation_speed"])
    rotor_configuration = simpledialog.askstring("Session Setup", "Enter rotor configuration (M/F):", initialvalue=last_config["rotor_configuration"])
    mic_position = simpledialog.askstring("Session Setup", "Enter mic position:", initialvalue=last_config["mic_position"])
    session_name = simpledialog.askstring("Session Setup", "Enter session name:", initialvalue=last_config["session_name"])

    root.destroy()

    return {
        "machine_type": machine_type,
        "fault_status": fault_status,
        "rotation_speed": rotation_speed,
        "rotor_configuration": rotor_configuration,
        "mic_position": mic_position,
        "volume_ratio": volume_ratio,
        "session_name": session_name
    }

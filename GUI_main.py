import socket
import json
import sys_setup
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox, Toplevel, Button

# path for google vision setup key
google_key_path = '../GoogleVisionAPI/google_apikey.json'
# path for captured image storage
image_store_path = '../Data/'
# path for ocr text storage
csv_store_path = '../Data/image_ocr.csv'
# path for temp data check from server
csv_temp_path = '../Data/order_export.csv'
# path for server check tool
CLI_tool_path = '../iOrthoticsAPI/roboapi.exe'
# path for JSON file that keep diction
json_diction_path ='../Data/js_diction.json'

# build a diction for parts placement and pairing
pair_diction = sys_setup.build_diction()

# max pairs number
part_index = 0
max_pair_number = 70
terminate_code = 99

def log_message(message):
    """Function to log messages to the text area in the GUI."""
    text_area.configure(state='normal')  # Enable editing of the text area
    text_area.insert(tk.END, message + "\n")  # Append message
    text_area.configure(state='disabled')  # Disable editing of the text area
    text_area.see(tk.END)  # Scroll to the end

def start_session():
    """Custom dialog for session management."""
    def new_session():
        global pair_diction
        pair_diction = sys_setup.build_diction()
        log_message("Start new session")
        dialog.destroy()
        setup_robot_connection()
    
    def continue_session():
        global pair_diction, part_index
        log_message("Continue previous session")
        # Load saved JSON as dictionary ([0]dictionary, [1]placed part number)
        try:
            with open(json_diction_path, 'r') as js_load:
                js_read = json.load(js_load)
            part_index = int(js_read[1]) + 1
            pair_diction = {}
            for js_index in range(part_index):
                pair_diction[js_index] = js_read[0][str(js_index)]
        except FileNotFoundError:
            log_message("Error: JSON file not found. Starting a new session instead.")
            new_session()
        dialog.destroy()
        setup_robot_connection()
    
    def cancel_session():
        log_message("Session start cancelled.")
        dialog.destroy()
    
    dialog = Toplevel(root)
    dialog.title("Session")
    tk.Label(dialog, text="New session or continue a previous session?").pack(pady=10)
    
    Button(dialog, text="New", command=new_session).pack(side=tk.LEFT, padx=(20, 10), pady=20)
    Button(dialog, text="Continue", command=continue_session).pack(side=tk.LEFT, padx=10, pady=20)
    Button(dialog, text="Cancel", command=cancel_session).pack(side=tk.RIGHT, padx=(10, 20), pady=20)

    dialog.transient(root)  # Set to be on top of the main window
    dialog.grab_set()  # Modal
    root.wait_window(dialog)  # Wait here until dialog is destroyed

def setup_robot_connection():
    # Retrieve host and port from GUI inputs
    Host = host_var.get()
    Port = int(port_var.get())

    log_message("Setting up connection... Awaiting robot response.")
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Server setup
            s.bind((Host, Port))
            s.listen()
            s.settimeout(40)  # Set timeout for waiting for a connection
            
            # Accept connection from client (robot)
            conn, client_address = s.accept()
            with conn:
                log_message(f'Connected to robot by: {client_address}')
                
                # Communication with the client
                try_connection = ''
                while try_connection != 'robot start':
                    try_connection = bytes.decode(conn.recv(1024))
                log_message(f'Received from robot: {try_connection}')
                
                conn.send(str.encode('server start'))
                log_message('Connection setup, both server and robot initialized')
    except socket.timeout:
        log_message("Connection attempt timed out.")
    except Exception as e:
        log_message(f"An error occurred: {str(e)}")

# Create the main window
root = tk.Tk()
root.title("Application")

# Default values for inputs
default_values = {
    "camera_index": "0",
    "camera_resolution_width": "1920",
    "camera_resolution_height": "1080",
    "host": "192.168.0.10",
    "port": "30000",
    "max_pair_numbers": "70"
}

# Variables for inputs with default values
camera_index_var = tk.StringVar(value=default_values["camera_index"])
camera_resolution_width_var = tk.StringVar(value=default_values["camera_resolution_width"])
camera_resolution_height_var = tk.StringVar(value=default_values["camera_resolution_height"])
host_var = tk.StringVar(value=default_values["host"])
port_var = tk.StringVar(value=default_values["port"])
max_pair_numbers_var = tk.StringVar(value=default_values["max_pair_numbers"])

# Input fields layout
frame_inputs = tk.Frame(root)
frame_inputs.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

# Dynamically create input fields based on default values
for label, var in [("Camera Index:", camera_index_var),
                   ("Camera Resolution Width:", camera_resolution_width_var),
                   ("Camera Resolution Height:", camera_resolution_height_var),
                   ("Host Address:", host_var),
                   ("Port Address:", port_var),
                   ("Pair Numbers (Max 70):", max_pair_numbers_var)]:
    row = tk.Frame(frame_inputs)
    tk.Label(row, text=label, width=20, anchor='w').pack(side=tk.LEFT)
    tk.Entry(row, textvariable=var, width=20).pack(side=tk.RIGHT)
    row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

# Controls (e.g., buttons)
frame_controls = tk.Frame(root)
frame_controls.pack(fill=tk.X, padx=10, pady=5)

tk.Button(frame_controls, text="Start", command=start_session).pack(side=tk.RIGHT)

# Text area for logging messages
text_area = scrolledtext.ScrolledText(root, state='disabled', height=10)
text_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

root.mainloop()


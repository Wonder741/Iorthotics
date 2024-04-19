import socket
import json
import os
import GUI_function
import struct
import tkinter as tk
import time
from tkinter import scrolledtext, Toplevel, Button
import threading

# path for google vision setup key
google_key_path = 'D:\\A\\1 InsoleDataset\\GoogleAPI\\sanguine-link-334321-edd44f1199f6.json'

current_directory = os.getcwd()  # Get the current working directory
data_folder_path = os.path.join(current_directory, 'Data')  # Construct the path to the Data folder

if not os.path.exists(data_folder_path):
    os.makedirs(data_folder_path)

# Path for captured image storage
OB_image_store_path = os.path.join(data_folder_path, 'OB')
OCR_image_store_path = os.path.join(data_folder_path, 'OCR')

# Create the subfolders if they don't exist
if not os.path.exists(OB_image_store_path):
    os.makedirs(OB_image_store_path)

if not os.path.exists(OCR_image_store_path):
    os.makedirs(OCR_image_store_path)

# Path for OCR text storage
csv_store_path = os.path.join(OCR_image_store_path, 'image_ocr.csv')
# Path for temp data check from server
csv_temp_path = os.path.join(data_folder_path, 'order_export.csv')
# Path for JSON file that keeps dictionary
json_diction_path = os.path.join(data_folder_path, 'js_diction.json')

# Global variable to keep track of the socket
global_socket = None
# Global variable to keep sent data for resend

processed_floats = []


def log_message(message):
    """Function to log messages to the text area in the GUI."""
    text_area.configure(state='normal')  # Enable editing of the text area
    text_area.insert(tk.END, message + "\n")  # Append message
    text_area.configure(state='disabled')  # Disable editing of the text area
    text_area.see(tk.END)  # Scroll to the end

def start_session():
    """Custom dialog for session management."""
    # build a diction for parts placement and pairing
    global pair_diction
    pair_diction = GUI_function.build_diction(int(max_pair_numbers_var.get()))
    def new_session():
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

def handle_robot_communication(conn):
    global global_socket
    global_socket = conn  # Keep track of the socket
    terminate_code = 99
    part_index = 0

    try:
        while True:
            data_received = bytes.decode(conn.recv(1024))
            if not data_received:
                break  # Exit the loop if no data is received

            log_message(f'Received from robot: {data_received}')

            if data_received == 'wait pose':
                conn.send(str.encode('go pick'))
                log_message('Send message to robot: go pick')
                time.sleep(0.5)
                floats_to_send_1 = [-0.382, 0.155]
                # Multiply each float by 1000 and convert to int
                processed_floats = [int(x * 1000) for x in floats_to_send_1]
                for x in processed_floats:
                    abs_x = abs(x)
                    sign = 1 if x >= 0 else 0  # 1 for positive, 0 for negative
                    conn.send(abs_x.to_bytes(4, 'big'))
                    conn.send(sign.to_bytes(4, 'big'))  # Send the sign as 1 byte
                log_message('Send pose to robot')
                time.sleep(0.1)

            elif data_received == 'ocr pose':
                image = GUI_function.OCR_camera_capture(int(ocr_camera_index_var.get()), int(camera_resolution_width_var.get()), int(camera_resolution_height_var.get()), 255)
                image_file_name = GUI_function.image_save(image, OCR_image_store_path)
                ocr_text = GUI_function.perform_ocr(OCR_image_store_path + '\\scan.jpg', google_key_path)
                print(ocr_text)
                part_number, part_keyword = GUI_function.check_for_six_digit_number(ocr_text)
                place_position = GUI_function.diction_check_fill(part_number, part_keyword, pair_diction)
                pair_save = [pair_diction, part_index]
                # save dictionary as JSON file
                with open(json_diction_path, 'w+') as js_file:
                    json.dump(pair_save, js_file)                    
                part_index = part_index + 1

                conn.send(str.encode('go place'))
                log_message('Send message to robot: go place')
                time.sleep(0.5)

                # Avoid exceed pairing space limitation
                if place_position > 70:
                    print('Exceed the maximum pair number')
                    conn.send(terminate_code.to_bytes(4, 'big'))
                else:
                    print('Place position: ', place_position)
                    conn.send(place_position.to_bytes(4, 'big'))
                time.sleep(0.5)

            elif data_received == 'placed pose':
                conn.send(str.encode('go wait'))
                log_message('Send message to robot: go wait')
                time.sleep(0.5)

            elif data_received == 'send again':
                time.sleep(0.5)
                for x in processed_floats:
                    abs_x = abs(x)
                    sign = 1 if x >= 0 else 0  # 1 for positive, 0 for negative
                    conn.send(abs_x.to_bytes(4, 'big'))
                    conn.send(sign.to_bytes(4, 'big'))  # Send the sign as 1 byte
                log_message('Send pose to robot')
                time.sleep(0.1)

    except Exception as e:
        log_message(f"An error occurred during communication: {str(e)}")
    finally:
        conn.close()
        global_socket = None  # Reset the socket variable when done

def setup_robot_connection():
    Host = host_var.get()
    Port = int(port_var.get())

    log_message("Setting up connection... Awaiting robot response.")
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((Host, Port))
        s.listen()
        s.settimeout(40)  # Set timeout for waiting for a connection

        # Accept connection from client (robot) in a separate thread
        def accept_connection():
            try:
                conn, client_address = s.accept()
                with conn:
                    log_message(f'Connected to robot by: {client_address}')

                    try_connection = ''
                    while try_connection != 'robot start':
                        try_connection = bytes.decode(conn.recv(1024))
                    log_message(f'Received from robot: {try_connection}')

                    conn.send(str.encode('server start'))
                    log_message('Connection setup, both server and robot initialized')

                    handle_robot_communication(conn)

            except socket.timeout:
                log_message("Connection attempt timed out.")
            except Exception as e:
                log_message(f"An error occurred: {str(e)}")
            finally:
                s.close()

        # Start the thread for accepting connections
        threading.Thread(target=accept_connection).start()

    except Exception as e:
        log_message(f"An error occurred during setup: {str(e)}")

def disconnect_socket():
    """Function to disconnect the socket connection."""
    global global_socket
    if global_socket:
        try:
            global_socket.close()  # Close the socket
            log_message("Socket connection closed.")
        except Exception as e:
            log_message(f"An error occurred while closing the socket: {str(e)}")
        finally:
            global_socket = None
    else:
        log_message("No active socket connection to close.")

# Create the main window
root = tk.Tk()
root.title("Application")

# Default values for inputs
default_values = {
    "OB_camera_index": "2",
    "OCR_camera_index": "1",
    "camera_resolution_width": "1920",
    "camera_resolution_height": "1080",
    "host": "192.168.0.10",
    "port": "30000",
    "max_pair_numbers": "70"
}

# Variables for inputs with default values
ob_camera_index_var = tk.StringVar(value=default_values["OB_camera_index"])
ocr_camera_index_var = tk.StringVar(value=default_values["OCR_camera_index"])
camera_resolution_width_var = tk.StringVar(value=default_values["camera_resolution_width"])
camera_resolution_height_var = tk.StringVar(value=default_values["camera_resolution_height"])
host_var = tk.StringVar(value=default_values["host"])
port_var = tk.StringVar(value=default_values["port"])
max_pair_numbers_var = tk.StringVar(value=default_values["max_pair_numbers"])

# Input fields layout
frame_inputs = tk.Frame(root)
frame_inputs.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

# Dynamically create input fields based on default values
for label, var in [("OB Camera Index:", ob_camera_index_var),
                   ("OCR Camera Index:", ocr_camera_index_var),
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
# Add the "Disconnect" button to the GUI
tk.Button(frame_controls, text="Disconnect", command=disconnect_socket).pack(side=tk.RIGHT, padx=5)

# Text area for logging messages
text_area = scrolledtext.ScrolledText(root, state='disabled', height=10)
text_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

root.mainloop()

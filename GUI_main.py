import socket
import json
import os
import GUI_function
import struct
import tkinter as tk
import time
from tkinter import simpledialog, scrolledtext, messagebox, Toplevel, Button
import threading

Folder_path = 'D://A//1 InsoleDataset//Data//'
# path for google vision setup key
google_key_path = 'D://A//1 InsoleDataset//Data//GoogleAPI//'
# path for captured image storage
OB_image_path = 'D://A//1 InsoleDataset//Data//OB//'
OCR_image_path = 'D://A//1 InsoleDataset//Data//OCR//'
# path for ocr text storage
csv_store_path = 'D://A//1 InsoleDataset//Data//image_ocr.csv'
# path for JSON file that keep diction
json_diction_path ='D://A//1 InsoleDataset//Data//js_diction.json'

# Global variable to keep track of the socket
global_socket = None
# Global variable to keep sent data for resend
processed_floats = []

current_position = [0, 0, 0, 0, 0, 0]  # [x, y, z, rx, ry, rz]


def log_message(message):
    """Function to log messages to the text area in the GUI."""
    text_area.configure(state='normal')  # Enable editing of the text area
    text_area.insert(tk.END, message + "\n")  # Append message
    text_area.configure(state='disabled')  # Disable editing of the text area
    text_area.see(tk.END)  # Scroll to the end

def start_session():
    """Custom dialog for session management."""
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

    try:
        while True:
            data_received = bytes.decode(conn.recv(1024))
            if not data_received:
                break  # Exit the loop if no data is received

            log_message(f'Received from robot: {data_received}')

            if data_received == 'wait pose':
                conn.send(str.encode('go place'))
                log_message('Send to robot: go pick')
                time.sleep(0.5)
                send_coordinates(current_position)

            elif data_received == 'ocr pose':
                conn.send(str.encode('go place'))
                log_message('Send to robot: go place')
                time.sleep(0.5)
                send_coordinates(current_position)

            elif data_received == 'send again':
                time.sleep(0.5)
                send_coordinates(current_position)

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

top_left_camera = (0, 0)
top_right_camera = (1, 0)
bottom_left_camera = (0, 1)
bottom_right_camera = (1, 1)

top_left_robot = (0.1, 0.1, 0.1)  # Replace with actual recorded coordinates
top_right_robot = (0.9, 0.1, 0.1)  # Replace with actual recorded coordinates
bottom_left_robot = (0.1, 0.9, 0.1)  # Replace with actual recorded coordinates
bottom_right_robot = (0.9, 0.9, 0.1)  # Replace with actual recorded coordinates

def transform_coordinates(x, y):
    # Calculate the scaling factors
    scale_x = (top_right_robot[0] - top_left_robot[0]) / (top_right_camera[0] - top_left_camera[0])
    scale_y = (bottom_left_robot[1] - top_left_robot[1]) / (bottom_left_camera[1] - top_left_camera[1])

    # Calculate the offset
    offset_x = top_left_robot[0] - top_left_camera[0] * scale_x
    offset_y = top_left_robot[1] - top_left_camera[1] * scale_y

    # Transform the coordinates
    robot_x = x * scale_x + offset_x
    robot_y = y * scale_y + offset_y
    robot_z = top_left_robot[2]  # Assume a constant z-coordinate

    return robot_x, robot_y, robot_z


def move_x_positive():
    global current_position
    current_position[0] += 0.1  # Increase x-coordinate by 10cm (0.1 meters)
    send_coordinates(current_position)

def send_coordinates(coordinates):
    global global_socket
    if global_socket:
        try:
            processed_floats = [int(x * 1000) for x in coordinates]
            for x in processed_floats:
                abs_x = abs(x)
                sign = 1 if x >= 0 else 0  # 1 for positive, 0 for negative
                global_socket.send(abs_x.to_bytes(4, 'big'))
                global_socket.send(sign.to_bytes(4, 'big'))  # Send the sign as 1 byte
            log_message('Send coordinates to robot')
            time.sleep(0.1)
        except Exception as e:
            log_message(f"An error occurred while sending coordinates: {str(e)}")
    else:
        log_message("No active socket connection.")

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

# build a diction for parts placement and pairing
global pair_diction
pair_diction = GUI_function.build_diction(int(max_pair_numbers_var.get()))
pair_index = 0

current_directory = os.getcwd()  # Get the current working directory
data_folder_path = os.path.join(current_directory, 'Data')  # Construct the path to the Data folder

if not os.path.exists(data_folder_path):
    os.makedirs(data_folder_path)

# path for captured image storage
image_store_path = data_folder_path
# path for ocr text storage
csv_store_path = data_folder_path + '//image_ocr.csv'
# path for temp data check from server
csv_temp_path = data_folder_path + '//order_export.csv'
# path for JSON file that keep diction
json_diction_path =data_folder_path + '//js_diction.json'

# Controls (e.g., buttons)
frame_controls = tk.Frame(root)
frame_controls.pack(fill=tk.X, padx=10, pady=5)

tk.Button(frame_controls, text="Start", command=start_session).pack(side=tk.RIGHT)
# Add the "Disconnect" button to the GUI
tk.Button(frame_controls, text="Disconnect", command=disconnect_socket).pack(side=tk.RIGHT, padx=5)
tk.Button(frame_controls, text="+X", command=move_x_positive).pack(side=tk.LEFT)


# Text area for logging messages
text_area = scrolledtext.ScrolledText(root, state='disabled', height=10)
text_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

root.mainloop()

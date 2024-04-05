import socket
import struct
import tkinter as tk
from tkinter import scrolledtext
import threading

global_socket = None
processed_floats = []

def log_message(message):
    text_area.configure(state='normal')
    text_area.insert(tk.END, message + "\n")
    text_area.configure(state='disabled')
    text_area.see(tk.END)

def setup_robot_connection():
    host = host_var.get()
    port = int(port_var.get())

    log_message("Setting up connection... Awaiting robot response.")
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen()
        s.settimeout(40)

        def accept_connection():
            try:
                conn, _ = s.accept()
                with conn:
                    log_message('Connected to robot')
                    handle_robot_communication(conn)
            except socket.timeout:
                log_message("Connection attempt timed out.")
            except Exception as e:
                log_message(f"An error occurred: {str(e)}")
            finally:
                s.close()

        threading.Thread(target=accept_connection).start()

    except Exception as e:
        log_message(f"An error occurred during setup: {str(e)}")

def handle_robot_communication(conn):
    global global_socket
    global_socket = conn

    try:
        while True:
            data_received = bytes.decode(conn.recv(1024))
            if not data_received:
                break

            log_message(f'Received from robot: {data_received}')

            if data_received == 'ready':
                log_message('Robot is ready for commands')

    except Exception as e:
        log_message(f"An error occurred during communication: {str(e)}")
    finally:
        conn.close()
        global_socket = None

def disconnect_socket():
    global global_socket
    if global_socket:
        try:
            global_socket.close()
            log_message("Socket connection closed.")
        except Exception as e:
            log_message(f"An error occurred while closing the socket: {str(e)}")
        finally:
            global_socket = None
    else:
        log_message("No active socket connection to close.")

def move_arm(x, y, z):
    global processed_floats
    if global_socket:
        current_pose = processed_floats[:3]
        new_pose = [current_pose[i] + [x, y, z][i] for i in range(3)]
        new_pose.extend(processed_floats[3:])
        processed_floats = new_pose
        
        conn = global_socket
        for value in processed_floats:
            conn.send(struct.pack('f', value))
        log_message('Send new pose to robot')
    else:
        log_message("No active socket connection. Please connect to the robot first.")

root = tk.Tk()
root.title("Robot Control")

host_var = tk.StringVar(value="192.168.0.10")
port_var = tk.StringVar(value="30000")

frame_inputs = tk.Frame(root)
frame_inputs.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

tk.Label(frame_inputs, text="Host Address:").grid(row=0, column=0)
tk.Entry(frame_inputs, textvariable=host_var).grid(row=0, column=1)
tk.Label(frame_inputs, text="Port Address:").grid(row=1, column=0)
tk.Entry(frame_inputs, textvariable=port_var).grid(row=1, column=1)

frame_controls = tk.Frame(root)
frame_controls.pack(fill=tk.X, padx=10, pady=5)

tk.Button(frame_controls, text="Move +X", command=lambda: move_arm(0.1, 0, 0)).pack(side=tk.LEFT, padx=5)
tk.Button(frame_controls, text="Move -X", command=lambda: move_arm(-0.1, 0, 0)).pack(side=tk.LEFT, padx=5)
tk.Button(frame_controls, text="Move +Y", command=lambda: move_arm(0, 0.1, 0)).pack(side=tk.LEFT, padx=5)
tk.Button(frame_controls, text="Move -Y", command=lambda: move_arm(0, -0.1, 0)).pack(side=tk.LEFT, padx=5)
tk.Button(frame_controls, text="Move +Z", command=lambda: move_arm(0, 0, 0.1)).pack(side=tk.LEFT, padx=5)
tk.Button(frame_controls, text="Move -Z", command=lambda: move_arm(0, 0, -0.1)).pack(side=tk.LEFT, padx=5)

tk.Button(frame_controls, text="Connect", command=setup_robot_connection).pack(side=tk.RIGHT)
tk.Button(frame_controls, text="Disconnect", command=disconnect_socket).pack(side=tk.RIGHT, padx=5)

text_area = scrolledtext.ScrolledText(root, state='disabled', height=10)
text_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

processed_floats = [-0.382, 0.155, 0.374, 2.22, 2.22, 0]

root.mainloop()
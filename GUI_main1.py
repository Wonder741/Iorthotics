import socket
import json
import os
import GUI_function
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox, Toplevel, Button
import threading
import time

class StateMachine:
    def __init__(self):
        self.state = "Idle"
        self.conn = None
        self.client_address = None

    def to_idle(self):
        self.state = "Idle"
        log_message("State: Idle")

    def to_monitor(self):
        self.state = "Monitor"
        log_message("State: Monitor")
        self.monitor()

    def to_find(self):
        self.state = "Find"
        log_message("State: Find")
        # Implement find logic here

    # Add additional state transition methods as needed
    
    def monitor(self):
        if self.state != "Monitor":
            return  # Ensures this runs only if in Monitor state
        try:
            self.conn.settimeout(120)  # Set a timeout for receiving data
            data_received = bytes.decode(self.conn.recv(1024))
            log_message(f"Data received: {data_received}")
            # Transition to specific states based on data_received
            if data_received == "find":
                self.to_find()
            # Add additional conditionals for other states
        except socket.timeout:
            self.to_idle()

    def start_monitoring(self):
        threading.Thread(target=self.to_monitor).start()

# Modify setup_robot_connection to use state machine and accept connections
def setup_robot_connection(state_machine):
    Host = host_var.get()
    Port = int(port_var.get())
    log_message("Setting up connection... Awaiting robot response.")
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((Host, Port))
            s.listen()
            s.settimeout(40)  # Set timeout for waiting for a connection
            
            conn, client_address = s.accept()
            state_machine.conn = conn
            state_machine.client_address = client_address
            log_message(f'Connected to robot by: {client_address}')
            state_machine.to_monitor()
    except socket.timeout:
        log_message("Connection attempt timed out.")
    except Exception as e:
        log_message(f"An error occurred: {str(e)}")

# You will need to instantiate the state machine and modify the start_session function
# to initiate the connection and start monitoring based on the state machine logic.

state_machine = StateMachine()
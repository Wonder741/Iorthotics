import cv2
import tkinter as tk
from tkinter import ttk

# Function to find available cameras
def find_available_cameras(max_tests=10):
    available_indices = []
    for index in range(max_tests):
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if cap.isOpened():
            available_indices.append(f"Camera {index}")
            cap.release()
    return available_indices

# Create the main window
root = tk.Tk()
root.title("Camera Selector")

# Get available cameras
cameras = find_available_cameras()

# Create a StringVar to hold the selected camera
selected_camera = tk.StringVar()

# Create and pack a dropdown menu
camera_menu = ttk.Combobox(root, textvariable=selected_camera, values=cameras)
camera_menu.pack(pady=20, padx=10)

# Function to handle selection
def select_camera():
    print(f"Selected Camera: {selected_camera.get()}")

# Button to confirm selection
select_button = tk.Button(root, text="Select Camera", command=select_camera)
select_button.pack(pady=10)

# Start the GUI event loop
root.mainloop()

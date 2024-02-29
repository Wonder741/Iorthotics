import os
import io
import cv2
from datetime import datetime
from google.cloud import vision
import csv
import subprocess
import tkinter as tk
from tkinter import ttk

def google_vision_setup(env_var_value):
    env_var = 'GOOGLE_APPLICATION_CREDENTIALS'
    os.environ[env_var] = env_var_value

def OCR_google_vision(google_vision_path):
    try:
        # Detect text in image
        google_vision_text = []
        with io.open(google_vision_path, 'rb') as image_file:
            content = image_file.read()

        client = vision.ImageAnnotatorClient()
        image = vision.Image(content=content)

        response = client.text_detection(image=image)
        annotations = response.text_annotations

        if len(annotations) < 1:
            print('NO characters detected')
            return None
        else:
            print('characters detected')
            for i in range(1, len(annotations)):
                google_vision_text.append(annotations[i].description)
        return google_vision_text
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
# Function to capture image from the usb camera. Subject to change if camera changes.
def OCR_camera_capture(capture_camera_index, capture_frame_width, capture_frame_height):
    # initialize the camera
    capture_cam = cv2.VideoCapture(capture_camera_index, cv2.CAP_DSHOW)  # 0,1 -> index of camera
    capture_cam.set(cv2.CAP_PROP_FRAME_WIDTH, capture_frame_width)
    capture_cam.set(cv2.CAP_PROP_FRAME_WIDTH, capture_frame_height)
    capture_cam.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    #  capture_cam.set(cv2.CAP_PROP_BRIGHTNESS, 0)
    #  capture_cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)

    capture_success, capture_camera_image = capture_cam.read()
    capture_cam.release()
    if capture_success:  # frame captured without any errors
        print('capture success')
        return capture_camera_image
    else:
        print('capture FAILED')
        return None
    
def image_save(image_to_save, save_path, image_index):
    date_hour = datetime.now().strftime('%Y%m%d%H%M%S')
    image_file_name = f"{save_path}{date_hour}{image_index}.jpg"

    cv2.imwrite(save_path + 'scan.jpg', image_to_save)
    cv2.imwrite(image_file_name, image_to_save)

    print(f'image saved as: {image_file_name}')
    return image_file_name

def check_for_six_digit_number(lst):
    for element in lst:
        if element.isdigit() and len(element) == 6:
            print('find order number: ', element)
            return element, None
    cleaned_str = ''.join(filter(lambda x: x.isdigit() or x.isalpha(), ''.join(lst)))
    print('NO order number found, use keyword instead: ', cleaned_str)
    return None, cleaned_str

def build_diction(part_count):
    return {
        diction_index: {
            'order_id': '',
            'location_placed': False,
            'source': None,
            'state': None,
            'pair_found': False,
            'keyword': ''
        } for diction_index in range(part_count)
    }

def diction_check_fill(element, cleaned_str, diction):
    if element:
        for index, item in diction.items():
            if item['order_id'] == element:
                diction[index]['pair_found'] = True
                diction[index]['source'] = 'Internal'
                print(f'Order number {element} found, pair found at index {index}')
                return index
        for index, item in diction.items():
            if not item['location_placed']:
                diction[index]['location_placed'] = True
                diction[index]['order_id'] = element
                diction[index]['source'] = 'Internal'
                print(f'Order number {element} not found, placed at new location index {index}')
                return index
    else:
        for index, item in diction.items():
            if item['keyword'] == cleaned_str:
                diction[index]['pair_found'] = True
                diction[index]['source'] = 'External'
                print(f'Keyword {cleaned_str} found, pair found at index {index}')
                return index
        for index, item in diction.items():
            if not item['location_placed']:
                diction[index]['location_placed'] = True
                diction[index]['keyword'] = cleaned_str
                diction[index]['source'] = 'External'
                print(f'Keyword {cleaned_str} not found, placed at new location index {index}')
                return index

def display_diction_table_gui(diction, rows=10, cols=7):
    root = tk.Tk()
    root.title("Diction Table")

    # Create a frame for the table
    frame = ttk.Frame(root)
    frame.pack(padx=10, pady=10)

    # Create the table headers
    for col in range(cols):
        ttk.Label(frame, text=f"Column {col + 1}", font=("Arial", 10, "bold")).grid(row=0, column=col, padx=5, pady=5, sticky="ew")

    # Populate the table with data from the diction
    sorted_keys = sorted(diction.keys(), key=int)
    for row in range(1, rows + 1):
        for col in range(cols):
            index = (row - 1) * cols + col
            if index < len(sorted_keys):
                key = sorted_keys[index]
                item = diction[key]
                if item['location_placed']:
                    order_id = item['order_id'] if item['order_id'] else "None"
                    keyword = item['keyword'] if item['keyword'] else "None"
                    source_state = (item['source'] if item['source'] else "None") + "/" + (item['state'] if item['state'] else "None")
                    cell_text = f"{order_id}\n{keyword}\n{source_state}"
                else:
                    cell_text = ""
                ttk.Label(frame, text=cell_text, font=("Arial", 9), anchor="center").grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            else:
                ttk.Label(frame, text="", font=("Arial", 9), anchor="center").grid(row=row, column=col, padx=5, pady=5, sticky="ew")

    # Start the Tkinter event loop
    root.mainloop()
import os
import cv2
import re
from datetime import datetime
from google.cloud import vision
import csv
import tkinter as tk
from tkinter import ttk

def perform_ocr(image_path, json_key_path):
    """
    Performs OCR using Google Cloud Vision API on the given image.

    Args:
        image_path (str): The path to the image file.
        json_key_path (str): The path to the JSON key file for the service account.

    Returns:
        str: The extracted text from the image.
    """
    # Set the environment variable for authentication
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_key_path

    # Instantiate a client
    client = vision.ImageAnnotatorClient()

    # Load the image file
    with open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    # Perform text detection
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if response.error.message:
        raise Exception(f'{response.error.message}\nFor more info on error messages, check: https://cloud.google.com/apis/design/errors')

    # Extract the first text annotation (the entire text block)
    if texts:
        return texts[0].description.strip()
    else:
        return "No Text"

# Function to capture image from the usb camera. Subject to change if camera changes.
def OCR_camera_capture(capture_camera_index, capture_frame_width, capture_frame_height, capture_frame_focus):
    # initialize the camera
    capture_cam = cv2.VideoCapture(capture_camera_index, cv2.CAP_DSHOW)  # 0,1 -> index of camera
    capture_cam.set(cv2.CAP_PROP_FRAME_WIDTH, capture_frame_width)
    capture_cam.set(cv2.CAP_PROP_FRAME_HEIGHT, capture_frame_height)
    capture_cam.set(cv2.CAP_PROP_FOCUS, capture_frame_focus)

    capture_success, capture_camera_image = capture_cam.read()
    capture_cam.release()
    if capture_success:  # frame captured without any errors
        print('capture success')
        return capture_camera_image
    else:
        print('capture FAILED')
        return None

    
def image_save(image_to_save, save_path):
    date_hour = datetime.now().strftime('%Y%m%d%H%M%S')
    image_file_name = f"{save_path}\\{date_hour}.jpg"

    cv2.imwrite(save_path + '\\scan.jpg', image_to_save)
    cv2.imwrite(image_file_name, image_to_save)

    print(f'image saved as: {image_file_name}')
    return image_file_name

def check_for_six_digit_number(input_str):
    # Split the input string into a list of elements separated by newlines
    lst = input_str.split('\n')
    cleaned_str = ''.join(filter(lambda x: x.isdigit() or x.isalpha(), input_str))
    for element in lst:
        match = re.search(r'\b\d{6}\b', element)
        if match:
            print('find order number: ', match.group())
            return match.group(), cleaned_str
    print('NO order number found, use keyword instead: ', cleaned_str)
    return None, cleaned_str

def build_diction(part_count):
    return {
        diction_index: {
            'order_id': '',
            'location_placed': False,
            'source': None,
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

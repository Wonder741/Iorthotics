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
google_key_path = 'D:\\A\\1 InsoleDataset\\Data\\GoogleAPI\\sanguine-link-334321-edd44f1199f6.json'

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

# Global variable to keep sent data for resend
processed_floats = []


# build a diction for parts placement and pairing
pair_diction = GUI_function.build_diction(70)
part_index = 0

# Simulated data for testing
simulated_data = ['wait pose', 'ocr pose', 'placed pose', 'ocr pose', 'placed pose', 'send again']
for data_received in simulated_data:

    print(f'Received from robot: {data_received}')

    if data_received == 'wait pose':
        #conn.send(str.encode('go pick'))
        print('Send message to robot: go pick')
        time.sleep(0.5)
        floats_to_send_1 = [-0.382, 0.155, 0.374, 2.22, 2.22, 0]
        # Multiply each float by 1000 and convert to int
        processed_floats = [int(x * 1000) for x in floats_to_send_1]
        for x in processed_floats:
            abs_x = abs(x)
            sign = 1 if x >= 0 else 0  # 1 for positive, 0 for negative
            #conn.send(abs_x.to_bytes(4, 'big'))
            #conn.send(sign.to_bytes(4, 'big'))  # Send the sign as 1 byte
        print('Send pose to robot')
        time.sleep(0.1)

    elif data_received == 'ocr pose':
        image = GUI_function.OCR_camera_capture(0, 1920, 1080, 255)
        image_file_name = GUI_function.image_save(image, OCR_image_store_path)
        ocr_text = GUI_function.perform_ocr(OCR_image_store_path + '\\scan.jpg', google_key_path)
        print('OCR recognized text: ', ocr_text)
        part_number, part_keyword = GUI_function.check_for_six_digit_number(ocr_text)
        place_position = GUI_function.diction_check_fill(part_number, part_keyword, pair_diction)
        pair_save = [pair_diction, part_index]
        # save dictionary as JSON file
        with open(json_diction_path, 'w+') as js_file:
            json.dump(pair_save, js_file)                    
        part_index = part_index + 1

        #conn.send(str.encode('go place'))
        print('Send message to robot: go place')
        time.sleep(0.5)

        # Avoid exceed pairing space limitation
        if place_position > 70:
            print('Exceed the maximum pair number')
            #conn.send(terminate_code.to_bytes(4, 'big'))
        else:
            print('Place position: ', place_position)
            #conn.send(place_position.to_bytes(4, 'big'))
        time.sleep(0.5)

    elif data_received == 'placed pose':
        #conn.send(str.encode('go wait'))
        print('Send message to robot: go wait')
        time.sleep(0.5)

    elif data_received == 'send again':
        time.sleep(0.5)
        for x in processed_floats:
            abs_x = abs(x)
            sign = 1 if x >= 0 else 0  # 1 for positive, 0 for negative
            #conn.send(abs_x.to_bytes(4, 'big'))
            #conn.send(sign.to_bytes(4, 'big'))  # Send the sign as 1 byte
        print('Send pose to robot')
        time.sleep(0.1)
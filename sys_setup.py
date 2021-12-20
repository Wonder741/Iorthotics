import os
import io
import cv2
import datetime
import csv
import re
import subprocess
import tkinter as tk
from google.cloud import vision


def google_vision_setup(env_var_value):
    env_var = 'GOOGLE_APPLICATION_CREDENTIALS'
    os.environ[env_var] = env_var_value


def google_vision(google_vision_path):
    #  detect text in image
    google_vision_text = []
    with io.open(google_vision_path, 'rb') as image_file:
        content = image_file.read()

    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    annotations = response.text_annotations

    if len(annotations) < 1:
        print('NO characters detected')
    else:
        print('characters detected')
        for i in range(1, len(annotations)):
            google_vision_text.append(annotations[i].description)
    return google_vision_text


# Function to capture image from the usb camera. Subject to change if camera changes.
def camera_capture(capture_camera_index, capture_frame_width, capture_frame_height):
    # initialize the camera
    capture_cam = cv2.VideoCapture(capture_camera_index, cv2.CAP_DSHOW)  # 0,1 -> index of camera

    capture_cam.set(cv2.CAP_PROP_FRAME_WIDTH, capture_frame_width)
    capture_cam.set(cv2.CAP_PROP_FRAME_WIDTH, capture_frame_height)
    capture_cam.set(cv2.CAP_PROP_AUTOFOCUS, 0.5)
    #  capture_cam.set(cv2.CAP_PROP_FOCUS, 0)
    #  capture_cam.set(cv2.CAP_PROP_BRIGHTNESS, 0)
    #  capture_cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)

    capture_success, capture_camera_image = capture_cam.read()
    if capture_success:  # frame captured without any errors
        print('capture success')
        return capture_camera_image
    else:
        print('capture FAILED')
    capture_cam.release()


def image_save(image_to_save, save_path, image_index):
    current_date = datetime.datetime.now()
    date_hour = str(current_date.year) + str(current_date.month) + str(current_date.day) + str(current_date.hour)

    # save image for ocr
    cv2.imwrite(save_path + 'scan.jpg', image_to_save)
    # copy image as backup
    image_file_name = save_path + date_hour + str(image_index) + '.jpg'
    cv2.imwrite(image_file_name, image_to_save)
    print('image saved as: ' + image_file_name)
    return image_file_name


# Function to display matched order id or order key word on computer
# Inputs: order_diction
def display_grid(order_diction):
    root = tk.Tk()
    root.title("Sorted Grid")
    cols = ["", "A", "B", "C", "D", "E", "F", "G"]
    rows = ["", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    od_index = 0

    for grid_i in range(11):
        for grid_j in range(8):
            if grid_i == 0:
                tk.Label(root, relief='groove', height=2, width=10,
                         text=cols[grid_j]).grid(row=grid_i, column=grid_j, sticky='NSEW')
            elif grid_j == 0:
                tk.Label(root, relief='groove', height=2, width=10,
                         text=rows[grid_i]).grid(row=grid_i, column=grid_j, sticky='NSEW')
            else:
                filled_words = str(order_diction[od_index]['order_id']) + str(order_diction[od_index]['source']) + \
                               '\n' + str(order_diction[od_index]['keyword_1']) + \
                               '\n' + str(order_diction[od_index]['keyword_2'])
                tk.Label(root, bg="white", height=3, width=18, relief='ridge',
                         text=filled_words).grid(row=grid_i, column=grid_j, sticky='NSEW')
                od_index = od_index + 1
    root.mainloop()


def build_diction():
    part_count = 70
    diction = {}
    for diction_index in range(part_count):
        diction[diction_index] = {'order_id': '0', 'location_placed': False, 'source': None, 'state': None,
                                  'pair_found': False, 'keyword_1': [], 'keyword_2': [],
                                  'top_type': [], 'top_colour': [], 'top_thick': []}
    return diction


def write_csv(image_name, csv_orc_words):
    data = [image_name, csv_orc_words]

    with open('C:/Google Cloud/ocr_data/image_ocr.csv', 'a', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        # write the data
        writer.writerow(data)


def words_process(string_list):
    # find 6 digital number
    result_number = re.findall(r'\d{6}', str(string_list))
    # find non-digital characters and remove symbols
    if result_number is not None:
        print('find order number: ', result_number)
        result_word = re.findall(r'\D+', str(string_list))
        result_word = re.findall(r'\w+', str(result_word))
        result_word = str(result_word).lower()
    else:
        result_word = re.findall(r'\w+', str(string_list))
        result_word = str(result_word).lower()
        print('NOT find order number')
        print('use keyword instead: ', result_word)

    return result_number, result_word


# Function to check the order id against the server using the CLI tool developed
# Inputs: Order number (Checks for 'cooling')
def server_check(sc_order_number, sc_csv_path, sc_tool_path):
    args = [sc_tool_path, 'get-order', '-s', 'aus', '-k', '1LpGQMtIo3oHy6D174fmj40p',
            '--order-number', str(sc_order_number), '-f', sc_csv_path, '-q']
    subprocess.call(args)
    with open(sc_csv_path) as csvDataFile:
        sc_data = list(csv.reader(csvDataFile))
        sc_order_state = None
        sc_data_colour = None
        sc_data_thick = None
        sc_data_type = None

        for sc_data_index in range(len(sc_data)):
            sc_data_name = sc_data[sc_data_index][0]
            sc_data_data = sc_data[sc_data_index][1]
            if sc_data_name == 'OrderNumber' and str(sc_data_data) == '00217':
                sc_order_id_flag = False
                print("ORDER ID INCORRECT:", sc_order_number)
                return sc_order_id_flag, sc_order_state, sc_data_type, sc_data_colour, sc_data_thick
            else:
                if sc_data_name == 'Status':
                    sc_order_state = str(sc_data_data).lower()
                # search for colour information
                if sc_data_name == 'FootOrthotic.finishing.top_covers.color':
                    sc_data_colour = str(sc_data_data).lower()
                if sc_data_name == 'FootOrthotic.finishing.top_covers.cover':
                    sc_data_type = str(sc_data_data).lower()
                if sc_data_name == 'FootOrthotic.finishing.top_covers.content':
                    sc_data_thick = str(sc_data_data).lower()
    sc_order_id_flag = True
    print('ORDER ID found: ', sc_order_number)
    return sc_order_id_flag, sc_order_state, sc_data_type, sc_data_colour, sc_data_thick


def diction_fill_up(df_diction, df_part_index, df_pair_number, df_part_number, df_part_keyword, df_order_flag,
                    df_order_state, df_order_type, df_order_colour, df_order_thick):
    df_diction_index = 0
    if df_order_flag:
        for df_diction_index in range(df_part_index + 1):
            if df_diction[df_diction_index]['order_id'] == df_part_number \
                    and not df_diction[df_diction_index]['pair_found']:
                df_diction[df_diction_index]['pair_found'] = True
                df_pair_number = df_pair_number + 1
                df_diction[df_diction_index]['source'] = 'IN'
                df_diction[df_diction_index]['keyword_2'] = df_part_keyword
                df_diction[df_diction_index]['state'] = df_order_state
                df_diction[df_diction_index]['top_type'] = df_order_type
                df_diction[df_diction_index]['top_colour'] = df_order_colour
                df_diction[df_diction_index]['top_thick'] = df_order_thick
                print('TWO internal parts paired at position: ', df_diction_index)
                break
            if df_diction[df_diction_index]['order_id'] != df_part_number \
                    and not df_diction[df_diction_index]['location_placed'] \
                    and not df_diction[df_diction_index]['pair_found']:
                df_diction[df_diction_index]['order_id'] = df_part_number
                df_diction[df_diction_index]['keyword_1'] = df_part_keyword
                df_diction[df_diction_index]['location_placed'] = True
                df_diction[df_diction_index]['source'] = 'IN'
                print('Single internal part placed at position: ', df_diction_index)
                break
    else:
        for df_diction_index in range(df_part_index + 1):
            if df_diction[df_diction_index]['keyword_1'] == df_part_keyword \
                    and not df_diction[df_diction_index]['pair_found']:
                df_diction[df_diction_index]['pair_found'] = True
                df_pair_number = df_pair_number + 1
                df_diction[df_diction_index]['source'] = 'EX'
                df_diction[df_diction_index]['keyword_2'] = df_part_keyword
                print('TWO external parts paired at position: ', df_diction_index)
                break
            if df_diction[df_diction_index]['keyword_1'] != df_part_keyword \
                    and not df_diction[df_diction_index]['location_placed'] \
                    and not df_diction[df_diction_index]['pair_found']:
                df_diction[df_diction_index]['keyword_1'] = df_part_keyword
                df_diction[df_diction_index]['location_placed'] = True
                df_diction[df_diction_index]['source'] = 'EX'
                print('Single internal part placed at position: ', df_diction_index)
                break
    print("Diction filled")
    return df_diction, df_diction_index, df_pair_number


if __name__ == '__main__':
    # camera and OCR test
    google_key_path = 'C:/Google Cloud/sanguine-link-334321-c27b40c6071a.json'
    image_store_path = 'C:/Google Cloud/ocr_data/'
    csv_temp_path = 'C:/Google Cloud/ocr_data/order_export.csv'
    CLI_tool_path = 'C:/iOrthotics/iorthoticsserver/roboapi.exe'
    camera_index = 1
    camera_resolution_width = 1920
    camera_resolution_height = 1080
    # build a diction
    pair_diction = build_diction()

    for capture_index in range(2):
        # capture image from camera
        capture_image = camera_capture(camera_index, camera_resolution_width, camera_resolution_height)
        # save image for ocr and backup
        saved_image_name = image_save(capture_image, image_store_path, capture_index)
        # initialize google vision
        google_vision_setup(google_key_path)
        # ocr by google vision
        ocr_text = google_vision(image_store_path + 'scan.jpg')
        print(ocr_text)
        # save ocr text on csv file
        write_csv(saved_image_name, ocr_text)
        # process ocr strings
        part_number, part_keyword = words_process(ocr_text)
        # check order id from server
        order_id_flag, order_state, order_type, order_colour, order_thick = server_check(part_number)
        # fill up dictionary
        if order_id_flag:
            pair_diction[capture_index]['order_id'] = str(part_number)
            pair_diction[capture_index]['keyword_1'] = part_keyword[1]
            pair_diction[capture_index]['keyword_2'] = part_keyword
            pair_diction[capture_index]['type'] = order_type
            pair_diction[capture_index]['colour'] = order_colour
            pair_diction[capture_index]['thick'] = order_thick
        else:
            pair_diction[capture_index]['keyword_1'] = part_keyword[0]
            pair_diction[capture_index]['keyword_2'] = part_keyword[1]
    # display dictionary on table
    display_grid(pair_diction)

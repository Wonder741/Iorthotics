# Use with UR_Pickplace_mixedorient URCAP

import socket
import time
import warnings
import numpy as np

import os
from google.cloud import vision
import io

import subprocess
import csv
import json
import tkinter as tk

from cv2 import cv2


def googleread_setup():
    env_var = 'GOOGLE_APPLICATION_CREDENTIALS'
    env_var_value = 'C:/Users/Healthia/Desktop/Workspace/iOrthotics/google_apikey.json'
    os.environ[env_var] = env_var_value
    client = vision.ImageAnnotatorClient()


def googleread():
    path = 'C:/Users/Healthia/Desktop/Workspace/iOrthotics/scan.jpg'
    recognizedwords = []
    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    annotations = response.text_annotations
    num_read = len(annotations)
    if (num_read == 0 or num_read == 1):
        return recognizedwords
    else:
        for i in range(1, num_read):
            recognizedwords.append(annotations[i].description)
        return recognizedwords


def date_check(no_date):
    if len(no_date) <= 4 and no_date.isdigit():
        no_date = ''
    return no_date


def blacklist_check(word):
    names = ["the", "foot", "people", "sydney", "sydneycity", "citypodiatry", "sydneycitypodiatry", "podiatry",
             "myfootdr", "feet", 'townsville', 'clinic', 'performancepodiatry', "my"]
    for name in names:
        if word == name:
            word = ''
            break
    return word


# Function to remove punctuation from all words
def punc_check(recognizedwords):
    # Punctuations
    punctuations = '''!()-[]{};:'"\,<>./?@#$%^&;*_~'''

    word_ctr = 0
    for word in recognizedwords:
        no_punc = ""
        word = word.lower()
        if (len(word) == 1 and word.isalpha()):
            if (word_ctr + 1 == len(recognizedwords)):
                word = ''
            else:
                recognizedwords.insert(word_ctr + 1, word + recognizedwords[word_ctr + 1])
                word = ''
        for char in word:
            if char not in punctuations:
                no_punc = no_punc + char
        word = date_check(no_punc)
        word = blacklist_check(word)
        recognizedwords[word_ctr] = word
        word_ctr = word_ctr + 1
    return recognizedwords


# Function to capture image from the usb camera. Subject to change if camera changes.
def capture():
    # initialize the camera
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # 0,1 -> index of camera
    # cap_for_exposure = cam.read()
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 4064)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 2704)
    cam.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    cam.set(cv2.CAP_PROP_FOCUS, 320)
    # cam.set(cv2.CAP_PROP_AUTO_EXPOSURE,0.75)
    # cam.set(cv2.CAP_PROP_EXPOSURE,2)
    # print(cam.get(cv2.CAP_PROP_EXPOSURE))
    s, img = cam.read()
    if s:  # frame captured without any errors
        img = cv2.rotate(img, 0)
        cv2.imwrite("C:/Users/Healthia/Desktop/Workspace/iOrthotics/scan.jpg", img)  # save image


# Function to check the ordernumber against the server using the CLI tool developed
# Inputs: Order number, testflag(Checks for 'cooling')
def server_check(test_flag, orderno):
    if orderno == None:
        orderno_flag = False
        return orderno, orderno_flag
    args = ['C:/Users/Healthia/Desktop/iorthoticsserver/roboapi.exe', 'get-order', '-s', 'aus', '-k',
            '1LpGQMtIo3oHy6D174fmj40p', '--order-number', str(orderno), '-f', 'order_export.csv', '-q']
    subprocess.call(args)
    with open('C:/Users/Healthia/Desktop/iorthoticsserver/order_export.csv') as csvDataFile:
        data = list(csv.reader(csvDataFile))
        # Does not check for 'cooling'
        if (test_flag == True):
            if data[1][1] == "Yes":
                orderno = word
                orderno_flag = True
                return orderno, orderno_flag
            else:
                print("\n")
                print("INCORRECT READ")
                orderno = None
                orderno_flag = False
                return orderno, orderno_flag
        # Checks for cooling
        elif (test_flag == False):
            if data[1][1] == "Yes":  # and data[8][1] == "Cooling":
                orderno = word
                orderno_flag = True
                return orderno, orderno_flag
            else:
                print("\n")
                print("INCORRECT READ")
                orderno_flag = False
                orderno = None
                return orderno, orderno_flag


def display_grid(d):
    root = tk.Tk()
    root.title("Sorted Grid")
    cols = ["", "A", "B", "C", "D", "E", "F", "G"]
    rows = ["", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    pos_ctr = 0
    for i in range(10):
        for j in range(8):
            if i == 0:
                e = tk.Label(root, relief='groove', height=2, width=6, text=cols[j]).grid(row=i, column=j,
                                                                                          sticky='NSEW')
            elif j == 0:
                e = tk.Label(root, relief='groove', height=2, width=6, text=rows[i]).grid(row=i, column=j,
                                                                                          sticky='NSEW')
            else:
                e = tk.Label(root, bg="white", height=2, width=6, relief='ridge',
                             text=d['POS ' + str(pos_ctr)]['matchedword']).grid(row=i, column=j, sticky='NSEW')
                pos_ctr = pos_ctr + 1

    for i in range(10):
        root.grid_columnconfigure(i, weight=10)
        root.grid_rowconfigure(i, weight=10)

    root.mainloop()


def find_match(diction, m):
    position = {}
    order_number = {}
    paired = {}
    for i in range(m):
        paired[i] = diction['POS ' + str(i)]['pairfound']
        if diction['POS ' + str(i)]['pairfound']:
            position[i] = str(i)
            order_number[i] = diction['POS ' + str(i)]['matchedword']
        else:
            position[i] = str(i)
            order_number[i] = None
    return position, order_number, paired


def server_colour(orderno):
    args = ["C:/Users/Healthia/Desktop/iorthoticsserver/roboapi.exe", 'get-order', '-s', 'aus', '-k',
        '1LpGQMtIo3oHy6D174fmj40p', '--order-number', str(orderno), '-f', 'order_export.csv', '-q']
    subprocess.call(args)
    with open("C:/Users/Healthia/Desktop/iorthoticsserver/order_export.csv") as csvDataFile:
        server_data = list(csv.reader(csvDataFile))

    colour_found_flag = False
    for i in range(len(server_data)):
        # search for colour information
        data_name = server_data[i][0]
        if data_name == "FootOrthotic.finishing.top_covers.color":
            data_value = str(server_data[i][1]).lower()
            colour_found_flag = True
            return data_value, colour_found_flag
            print(data_value)
            break
    if not colour_found_flag:
        return "error", colour_found_flag


# MAIN

# Setup Deep ocr handler
googleread_setup()

# Setup Host and port
Host = "192.168.0.10"
Port = 30000

# n = Number of pairs
n = 63

# mis_no = misread numbers
mis_no = 0

print("\nSTARTING PROGRAM")

# Session type check

while True:
    sess = input("\nNew session or continue previous session? (Enter n for new or c for continue)")
    if sess == 'n':
        # Clear old file
        # Init new dict
        d = {}
        for i in range(n):
            str_conc = '%s %s' % ('POS', i)
            d[str_conc] = {'location': i, 'type': None, 'ordernumber': None, 'pairfound': False, 'matchedword': None,
                           'foot1': {'found_words_pose1': {}, 'found_words_pose2': {}, 'found_words_pose3': {}},
                           'foot2': {'found_words_pose1': {}, 'found_words_pose2': {}, 'found_words_pose3': {}}}
        break

    elif sess == 'c':
        with open('./scanned.json', 'r') as f:
            d = json.load(f)
        break
    else:
        print("\nInvalid input, try again")

while True:
    testinput = input("Run in test mode? (Enter y for yes or n for no)")
    if testinput == 'n':
        test_flag = False
        break
    elif testinput == 'y':
        test_flag = True
        break
    else:
        print("\nInvalid input, try again")

print("\nAWAITING UR10 RESPONSE")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Establishes connection with UR10
try:
    s.bind((Host, Port))
except:
    print("\n")
    print("UR10 hasn't been powered on. Power on UR10 and try again")
    exit(0)
s.listen(5)
s.settimeout(40)

try:
    c, addr = s.accept()
except socket.timeout:
    print("\n")
    print("COULD NOT CONNECT TO CLIENT")
    print("EXITING")
    exit(0)

s.settimeout(None)

while True:
    try:
        i = 0
        orderno = None
        orderno_flag = False
        num_flag = False
        wordsfound_pose1 = []
        wordsfound_pose2 = []
        wordsfound_pose3 = []
        found_flag = False

        msg_chk_start = str.encode("asking_to_start")
        msg_chk_partfound = str.encode("part_found")
        msg_chk_part_in_pos = str.encode("part_in_pos")
        msg_progcomplete = str.encode("progcomplete")

        msg = c.recv(1024)
        time.sleep(0.5)

        # Synchronizes and starts both programs
        if msg == msg_chk_start:
            time.sleep(0.5)
            start_stop = str.encode("(1)")
            c.send(start_stop)
            print("\n")
            print("Command to start sent")

        # Display message that the part is found
        elif msg == msg_chk_partfound:
            time.sleep(0.5)
            print("\n")
            print("******************************************************")
            print("\nPart found, commencing pick up\n")

        # Part is held in the capture position (-90 deg position)
        elif msg == msg_chk_part_in_pos:
            # Capture image
            capture()
            print("IMAGE CAPTURED")

            recognizedwords = googleread()
            print("OCR APPLIED")
            if len(recognizedwords) != 0:
                # Remove punctuation from all words
                recognizedwords = punc_check(recognizedwords)
                print(recognizedwords)

                # Check if a number exists and check with server
                for word in recognizedwords:
                    # Check if the word is an internal order and has a number
                    if word.isdigit() and len(word) == 6:
                        print('\n')
                        print("Number found: " + word)
                        orderno, orderno_flag = server_check(test_flag, word)
                        num_flag = True
                        break
                    if word.isdigit() and len(word) == 10:
                        print('\n')
                        word = word[0:6]
                        print("Number found: " + word)
                        orderno, orderno_flag = server_check(test_flag, word)
                        num_flag = True
                        break                 
                    else:
                        num_flag = False
                        orderno_flag = False

                # Add all found words to the dict
                wordsfound_pose1 = recognizedwords

                if not orderno_flag:
                    print("\n")
                    print("Retrying with next pose")
                    print('\n')

            else:
                print("Failed")
                print('\n')
                orderno_flag = False

            # move to 0 deg position
            if not orderno_flag:
                # Questionable below
                num_flag = False

                cont = str.encode("100")
                c.send(cont)
                time.sleep(0.5)
                if c.recv(1024) == str.encode("part_in_pos"):
                    capture()
                    print("IMAGE CAPTURED")
                    recognizedwords = googleread()
                    print("OCR APPLIED")
                    if len(recognizedwords) != 0:

                        recognizedwords = punc_check(recognizedwords)

                        for word in recognizedwords:
                            # Check if the word is an internal order and has a number

                            if word.isdigit() and len(word) == 6:
                                print('\n')
                                print("Number found: " + word)
                                orderno, orderno_flag = server_check(test_flag, word)
                                num_flag = True
                                break
                            if word.isdigit() and len(word) == 10:
                                print('\n')
                                word = word[1:6]
                                print("Number found: " + word)
                                orderno, orderno_flag = server_check(test_flag, word)
                                num_flag = True
                                break
                            else:
                                num_flag = False
                                orderno_flag = False

                        wordsfound_pose2 = recognizedwords

                        if not orderno_flag:
                            print("\n")
                            print("Retrying with next pose")
                            print('\n')

                    else:
                        print("Failed")
                        print('\n')
                        orderno_flag = False

                        # Move to +90 deg position
            if not orderno_flag:
                num_flag = False

                cont = str.encode("101")
                c.send(cont)
                time.sleep(0.5)
                if c.recv(1024) == str.encode("part_in_pos"):
                    capture()
                    print("IMAGE CAPTURED")
                    recognizedwords = googleread()
                    print("OCR APPLIED")
                    if len(recognizedwords) != 0:
                        recognizedwords = punc_check(recognizedwords)

                        for word in recognizedwords:
                            # Check if the word is an internal order and has a number
                            if word.isdigit() and len(word) == 6:
                                print('\n')
                                print("Number found: " + word)
                                orderno, orderno_flag = server_check(test_flag, word)
                                num_flag = True
                                break
                            if word.isdigit() and len(word) == 10:
                                print('\n')
                                word = word[1:6]
                                print("Number found: " + word)
                                orderno, orderno_flag = server_check(test_flag, word)
                                num_flag = True
                                break
                            else:
                                num_flag = False
                                orderno_flag = False

                        wordsfound_pose3 = recognizedwords

                        if not orderno_flag:
                            print("\n")
                            print("Three Poses read")

                    else:
                        print("Failed")
                        print('\n')
                        orderno_flag = False

            # If only characters were found, check if the characters exist in the array.
            # If not, create a new line and add new characters
            if (orderno_flag == False and ((len(wordsfound_pose1) != 0 and len(wordsfound_pose2) != 0) or (
                    len(wordsfound_pose2) != 0 and len(wordsfound_pose3) != 0) or (
                                                   len(wordsfound_pose3) != 0 and len(wordsfound_pose1) != 0))):
                for i in range(n + 1):
                    str_conc = '%s %s' % ('POS', i)
                    if d[str_conc]['type'] == 'type2' and d[str_conc]['pairfound'] == False:
                        # If a type2 single has been found
                        for word in d[str_conc]['foot1']['found_words_pose1'].values():
                            for words in wordsfound_pose1:
                                if words == word and (word != '' and words != ''):

                                    d[str_conc]['matchedword'] = words

                                    j = 1
                                    word_list = []
                                    read_list = []
                                    for read1 in wordsfound_pose1:
                                        word_conc = '%s %s' % ('word', j)
                                        word_list.append(word_conc)
                                        read_list.append(read1)
                                        j = j + 1

                                    d[str_conc]['foot2']['found_words_pose1'] = dict(zip(word_list, read_list))

                                    j = 1
                                    word_list = []
                                    read_list = []
                                    for read2 in wordsfound_pose2:
                                        word_conc = '%s %s' % ('word', j)
                                        word_list.append(word_conc)
                                        read_list.append(read2)
                                        j = j + 1

                                    d[str_conc]['foot2']['found_words_pose2'] = dict(zip(word_list, read_list))

                                    j = 1
                                    word_list = []
                                    read_list = []
                                    for read3 in wordsfound_pose3:
                                        word_conc = '%s %s' % ('word', j)
                                        word_list.append(word_conc)
                                        read_list.append(read3)
                                        j = j + 1

                                    d[str_conc]['foot2']['found_words_pose3'] = dict(zip(word_list, read_list))
                                    found_flag = True
                                    break

                            if found_flag:
                                d[str_conc]['pairfound'] = True
                                break

                            for words in wordsfound_pose2:
                                if words == word and (word != '' and words != ''):
                                    d[str_conc]['matchedword'] = words
                                    j = 1
                                    word_list = []
                                    read_list = []
                                    for read1 in wordsfound_pose1:
                                        word_conc = '%s %s' % ('word', j)
                                        word_list.append(word_conc)
                                        read_list.append(read1)
                                        j = j + 1

                                    d[str_conc]['foot2']['found_words_pose1'] = dict(zip(word_list, read_list))

                                    j = 1
                                    word_list = []
                                    read_list = []
                                    for read2 in wordsfound_pose2:
                                        word_conc = '%s %s' % ('word', j)
                                        word_list.append(word_conc)
                                        read_list.append(read2)
                                        j = j + 1

                                    d[str_conc]['foot2']['found_words_pose2'] = dict(zip(word_list, read_list))

                                    j = 1
                                    word_list = []
                                    read_list = []
                                    for read3 in wordsfound_pose3:
                                        word_conc = '%s %s' % ('word', j)
                                        word_list.append(word_conc)
                                        read_list.append(read3)
                                        j = j + 1

                                    d[str_conc]['foot2']['found_words_pose3'] = dict(zip(word_list, read_list))
                                    found_flag = True
                                    break

                            if found_flag:
                                d[str_conc]['pairfound'] = True
                                break

                            for words in wordsfound_pose3:
                                if words == word and (word != '' and words != ''):
                                    d[str_conc]['matchedword'] = words
                                    j = 1
                                    word_list = []
                                    read_list = []
                                    for read1 in wordsfound_pose1:
                                        word_conc = '%s %s' % ('word', j)
                                        word_list.append(word_conc)
                                        read_list.append(read1)
                                        j = j + 1

                                    d[str_conc]['foot2']['found_words_pose1'] = dict(zip(word_list, read_list))

                                    j = 1
                                    word_list = []
                                    read_list = []
                                    for read2 in wordsfound_pose2:
                                        word_conc = '%s %s' % ('word', j)
                                        word_list.append(word_conc)
                                        read_list.append(read2)
                                        j = j + 1

                                    d[str_conc]['foot2']['found_words_pose2'] = dict(zip(word_list, read_list))

                                    j = 1
                                    word_list = []
                                    read_list = []
                                    for read3 in wordsfound_pose3:
                                        word_conc = '%s %s' % ('word', j)
                                        word_list.append(word_conc)
                                        read_list.append(read3)
                                        j = j + 1

                                    d[str_conc]['foot2']['found_words_pose3'] = dict(zip(word_list, read_list))
                                    found_flag = True
                                    break

                            if found_flag:
                                d[str_conc]['pairfound'] = True
                                break

                        if not found_flag:
                            for word in d[str_conc]['foot1']['found_words_pose2'].values():
                                for words in wordsfound_pose1:
                                    if words == word and (word != '' and words != ''):
                                        d[str_conc]['matchedword'] = words
                                        j = 1
                                        word_list = []
                                        read_list = []
                                        for read1 in wordsfound_pose1:
                                            word_conc = '%s %s' % ('word', j)
                                            word_list.append(word_conc)
                                            read_list.append(read1)
                                            j = j + 1

                                        d[str_conc]['foot2']['found_words_pose1'] = dict(zip(word_list, read_list))

                                        j = 1
                                        word_list = []
                                        read_list = []
                                        for read2 in wordsfound_pose2:
                                            word_conc = '%s %s' % ('word', j)
                                            word_list.append(word_conc)
                                            read_list.append(read2)
                                            j = j + 1

                                        d[str_conc]['foot2']['found_words_pose2'] = dict(zip(word_list, read_list))

                                        j = 1
                                        word_list = []
                                        read_list = []
                                        for read3 in wordsfound_pose3:
                                            word_conc = '%s %s' % ('word', j)
                                            word_list.append(word_conc)
                                            read_list.append(read3)
                                            j = j + 1

                                        d[str_conc]['foot2']['found_words_pose3'] = dict(zip(word_list, read_list))
                                        found_flag = True
                                        break
                                if found_flag:
                                    d[str_conc]['pairfound'] = True
                                    break

                                for words in wordsfound_pose2:
                                    if words == word and (word != '' and words != ''):
                                        d[str_conc]['matchedword'] = words
                                        j = 1
                                        word_list = []
                                        read_list = []
                                        for read1 in wordsfound_pose1:
                                            word_conc = '%s %s' % ('word', j)
                                            word_list.append(word_conc)
                                            read_list.append(read1)
                                            j = j + 1

                                        d[str_conc]['foot2']['found_words_pose1'] = dict(zip(word_list, read_list))

                                        j = 1
                                        word_list = []
                                        read_list = []
                                        for read2 in wordsfound_pose2:
                                            word_conc = '%s %s' % ('word', j)
                                            word_list.append(word_conc)
                                            read_list.append(read2)
                                            j = j + 1

                                        d[str_conc]['foot2']['found_words_pose2'] = dict(zip(word_list, read_list))

                                        j = 1
                                        word_list = []
                                        read_list = []
                                        for read3 in wordsfound_pose3:
                                            word_conc = '%s %s' % ('word', j)
                                            word_list.append(word_conc)
                                            read_list.append(read3)
                                            j = j + 1

                                        d[str_conc]['foot2']['found_words_pose3'] = dict(zip(word_list, read_list))
                                        found_flag = True
                                        break
                                if found_flag:
                                    d[str_conc]['pairfound'] = True
                                    break

                                for words in wordsfound_pose3:
                                    if words == word and (word != '' and words != ''):
                                        d[str_conc]['matchedword'] = words
                                        j = 1
                                        word_list = []
                                        read_list = []
                                        for read1 in wordsfound_pose1:
                                            word_conc = '%s %s' % ('word', j)
                                            word_list.append(word_conc)
                                            read_list.append(read1)
                                            j = j + 1

                                        d[str_conc]['foot2']['found_words_pose1'] = dict(zip(word_list, read_list))

                                        j = 1
                                        word_list = []
                                        read_list = []
                                        for read2 in wordsfound_pose2:
                                            word_conc = '%s %s' % ('word', j)
                                            word_list.append(word_conc)
                                            read_list.append(read2)
                                            j = j + 1

                                        d[str_conc]['foot2']['found_words_pose2'] = dict(zip(word_list, read_list))

                                        j = 1
                                        word_list = []
                                        read_list = []
                                        for read3 in wordsfound_pose3:
                                            word_conc = '%s %s' % ('word', j)
                                            word_list.append(word_conc)
                                            read_list.append(read3)
                                            j = j + 1

                                        d[str_conc]['foot2']['found_words_pose3'] = dict(zip(word_list, read_list))
                                        found_flag = True
                                        break
                                if found_flag:
                                    d[str_conc]['pairfound'] = True
                                    break

                        if not found_flag:
                            for word in d[str_conc]['foot1']['found_words_pose3'].values():
                                for words in wordsfound_pose1:
                                    if words == word and (word != '' and words != ''):
                                        d[str_conc]['matchedword'] = words
                                        j = 1
                                        word_list = []
                                        read_list = []
                                        for read1 in wordsfound_pose1:
                                            word_conc = '%s %s' % ('word', j)
                                            word_list.append(word_conc)
                                            read_list.append(read1)
                                            j = j + 1

                                        d[str_conc]['foot2']['found_words_pose1'] = dict(zip(word_list, read_list))

                                        j = 1
                                        word_list = []
                                        read_list = []
                                        for read2 in wordsfound_pose2:
                                            word_conc = '%s %s' % ('word', j)
                                            word_list.append(word_conc)
                                            read_list.append(read2)
                                            j = j + 1

                                        d[str_conc]['foot2']['found_words_pose2'] = dict(zip(word_list, read_list))

                                        j = 1
                                        word_list = []
                                        read_list = []
                                        for read3 in wordsfound_pose3:
                                            word_conc = '%s %s' % ('word', j)
                                            word_list.append(word_conc)
                                            read_list.append(read3)
                                            j = j + 1

                                        d[str_conc]['foot2']['found_words_pose3'] = dict(zip(word_list, read_list))
                                        found_flag = True
                                        break
                                if found_flag:
                                    d[str_conc]['pairfound'] = True
                                    break

                                for words in wordsfound_pose2:
                                    if words == word and (word != '' and words != ''):
                                        d[str_conc]['matchedword'] = words
                                        j = 1
                                        word_list = []
                                        read_list = []
                                        for read1 in wordsfound_pose1:
                                            word_conc = '%s %s' % ('word', j)
                                            word_list.append(word_conc)
                                            read_list.append(read1)
                                            j = j + 1

                                        d[str_conc]['foot2']['found_words_pose1'] = dict(zip(word_list, read_list))

                                        j = 1
                                        word_list = []
                                        read_list = []
                                        for read2 in wordsfound_pose2:
                                            word_conc = '%s %s' % ('word', j)
                                            word_list.append(word_conc)
                                            read_list.append(read2)
                                            j = j + 1

                                        d[str_conc]['foot2']['found_words_pose2'] = dict(zip(word_list, read_list))

                                        j = 1
                                        word_list = []
                                        read_list = []
                                        for read3 in wordsfound_pose3:
                                            word_conc = '%s %s' % ('word', j)
                                            word_list.append(word_conc)
                                            read_list.append(read3)
                                            j = j + 1

                                        d[str_conc]['foot2']['found_words_pose3'] = dict(zip(word_list, read_list))
                                        found_flag = True
                                        break
                                if found_flag:
                                    d[str_conc]['pairfound'] = True
                                    break

                                for words in wordsfound_pose3:
                                    if words == word and (word != '' and words != ''):
                                        d[str_conc]['matchedword'] = words
                                        j = 1
                                        word_list = []
                                        read_list = []
                                        for read1 in wordsfound_pose1:
                                            word_conc = '%s %s' % ('word', j)
                                            word_list.append(word_conc)
                                            read_list.append(read1)
                                            j = j + 1

                                        d[str_conc]['foot2']['found_words_pose1'] = dict(zip(word_list, read_list))

                                        j = 1
                                        word_list = []
                                        read_list = []
                                        for read2 in wordsfound_pose2:
                                            word_conc = '%s %s' % ('word', j)
                                            word_list.append(word_conc)
                                            read_list.append(read2)
                                            j = j + 1

                                        d[str_conc]['foot2']['found_words_pose2'] = dict(zip(word_list, read_list))

                                        j = 1
                                        word_list = []
                                        read_list = []
                                        for read3 in wordsfound_pose3:
                                            word_conc = '%s %s' % ('word', j)
                                            word_list.append(word_conc)
                                            read_list.append(read3)
                                            j = j + 1

                                        d[str_conc]['foot2']['found_words_pose3'] = dict(zip(word_list, read_list))
                                        found_flag = True
                                        break

                                if found_flag:
                                    d[str_conc]['pairfound'] = True
                                    break

                    if found_flag:
                        print("\n")
                        print("External or Older order: Pair found at: " + str(i))
                        cont = str.encode(str(i))
                        c.send(cont)
                        time.sleep(0.5)
                        break

                    else:

                        str_conc = '%s %s' % ('POS', i)
                        if d[str_conc]['type'] is None:
                            found_flag = True
                            d[str_conc]['type'] = 'type2'
                            j = 1
                            word_list = []
                            read_list = []
                            for words in wordsfound_pose1:
                                word_conc = '%s %s' % ('word', j)
                                word_list.append(word_conc)
                                read_list.append(words)
                                j = j + 1
                            d[str_conc]['foot1']['found_words_pose1'] = dict(zip(word_list, read_list))
                            j = 1
                            word_list = []
                            read_list = []
                            for words in wordsfound_pose2:
                                word_conc = '%s %s' % ('word', j)
                                word_list.append(word_conc)
                                read_list.append(words)
                                j = j + 1
                            d[str_conc]['foot1']['found_words_pose2'] = dict(zip(word_list, read_list))
                            j = 1
                            word_list = []
                            read_list = []
                            for words in wordsfound_pose3:
                                word_conc = '%s %s' % ('word', j)
                                word_list.append(word_conc)
                                read_list.append(words)
                                j = j + 1
                            d[str_conc]['foot1']['found_words_pose3'] = dict(zip(word_list, read_list))

                        if found_flag:
                            print("\n")
                            print("External order or Older order: Single found at: " + str(i))
                            cont = str.encode(str(i))
                            c.send(cont)
                            time.sleep(0.5)
                            break
                print(wordsfound_pose1)
                print(wordsfound_pose2)
                print(wordsfound_pose3)

            # If the number exists, check if the number is previously idenetified.
            # If it has been, place pair together. If not, create new line and place pair.

            if orderno_flag:
                for i in range(n + 1):
                    if i >= n:
                        cont = str.encode("99")
                        c.send(cont)
                        time.sleep(0.5)
                        mis_no = mis_no + 1
                        print("\n")
                        print("Insole has been misread")
                        print("Please verify")
                        break

                    str_conc = '%s %s' % ('POS', i)
                    if d[str_conc]['type'] == 'type1' and d[str_conc]['pairfound'] == False:
                        # If a type1 single has been found
                        if d[str_conc]['ordernumber'] == orderno:

                            d[str_conc]['matchedword'] = orderno

                            j = 1
                            word_list = []
                            read_list = []
                            for read1 in wordsfound_pose1:
                                word_conc = '%s %s' % ('word', j)
                                word_list.append(word_conc)
                                read_list.append(read1)
                                j = j + 1

                            d[str_conc]['foot2']['found_words_pose1'] = dict(zip(word_list, read_list))

                            j = 1
                            word_list = []
                            read_list = []
                            for read2 in wordsfound_pose2:
                                word_conc = '%s %s' % ('word', j)
                                word_list.append(word_conc)
                                read_list.append(read2)
                                j = j + 1

                            d[str_conc]['foot2']['found_words_pose2'] = dict(zip(word_list, read_list))

                            j = 1
                            word_list = []
                            read_list = []
                            for read3 in wordsfound_pose3:
                                word_conc = '%s %s' % ('word', j)
                                word_list.append(word_conc)
                                read_list.append(read3)
                                j = j + 1

                            d[str_conc]['foot2']['found_words_pose3'] = dict(zip(word_list, read_list))
                            found_flag = True
                            d[str_conc]['pairfound'] = True

                    if found_flag == True and d[str_conc]['pairfound'] == True:
                        print("\n")
                        print("Internal order: Pair found at: " + str(i))
                        cont = str.encode(str(i))
                        c.send(cont)
                        time.sleep(0.5)
                        break

                    str_conc = '%s %s' % ('POS', i)
                    if d[str_conc]['type'] is None:
                        d[str_conc]['ordernumber'] = orderno
                        d[str_conc]['type'] = 'type1'
                        j = 1
                        word_list = []
                        read_list = []
                        for words in wordsfound_pose1:
                            word_conc = '%s %s' % ('word', j)
                            word_list.append(word_conc)
                            read_list.append(words)
                            j = j + 1
                        d[str_conc]['foot1']['found_words_pose1'] = dict(zip(word_list, read_list))
                        j = 1
                        word_list = []
                        read_list = []
                        for words in wordsfound_pose2:
                            word_conc = '%s %s' % ('word', j)
                            word_list.append(word_conc)
                            read_list.append(words)
                            j = j + 1
                        d[str_conc]['foot1']['found_words_pose2'] = dict(zip(word_list, read_list))
                        j = 1
                        word_list = []
                        read_list = []
                        for words in wordsfound_pose3:
                            word_conc = '%s %s' % ('word', j)
                            word_list.append(word_conc)
                            read_list.append(words)
                            j = j + 1
                        d[str_conc]['foot1']['found_words_pose3'] = dict(zip(word_list, read_list))
                        found_flag = True

                    if found_flag == True and d[str_conc]['pairfound'] == False:
                        print("\n")
                        print("Internal order: Single found at: " + str(i))
                        cont = str.encode(str(i))
                        c.send(cont)
                        time.sleep(0.5)
                        break

            # If the number does not exist, place aside
            if not found_flag:
                cont = str.encode("99")
                c.send(cont)
                time.sleep(0.5)
                mis_no = mis_no + 1
                print("\n")
                print("Part not identified, leaving aside")

            print('\n')
            print("Insole being placed")
            print("******************************************************")

        # Check if the Ur10 has finished identifying all parts
        elif msg == msg_progcomplete:
            print("\n")
            print("PROGRAM COMPLETE")

            # Save all the text to a json file
            with open('./scanned.json', 'w') as f:
                json.dump(d, f, indent=4)
            break

    except socket.error:
        print("\n")
        print("SOCKET ERROR")
        with open('./scanned.json', 'w') as f:
            json.dump(d, f, indent=4)
        break
    except KeyboardInterrupt:
        print("\n")
        print("SERVER INTERRUPTED VIA KEYPRESS")
        with open('./scanned.json', 'w') as f:
            json.dump(d, f, indent=4)
        break


paired_order_position, paired_order_number, order_paired = find_match(d, n)


for i in range(6):
    print(paired_order_position[i], paired_order_number[i], order_paired[i])
    if order_paired[i]:
        order_colour, colour_flag = server_colour(paired_order_number[i])
        print(order_colour)
        if colour_flag and order_colour == "red":        
            c.send(str.encode("201"))
        if colour_flag and order_colour == "blue":
            c.send(str.encode("202"))
        if colour_flag and order_colour == "black":
            c.send(str.encode("203"))
    else:
        c.send(str.encode("204"))

        while True:
            msg = c.recv(1024)
            print(msg)
            print(str.encode("colour_rec"))
            if msg == str.encode("colour_rec"):
                c.send(str.encode(str(i)))
                msg = str.encode("0")
                break

print("All parts and tops are in box")
print("Insoles with error = " + str(mis_no))
print("DISPLAYING GRID")
display_grid(d)
print("EXITING")

c.close()
s.close()

exit_key = input("\nPress any key to exit......")

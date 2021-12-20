import socket
from sys_setup import google_vision_setup
from sys_setup import google_vision
from sys_setup import camera_capture
from sys_setup import image_save
from sys_setup import build_diction
from sys_setup import write_csv
from sys_setup import words_process
from sys_setup import server_check
from sys_setup import diction_fill_up
from sys_setup import display_grid


if __name__ == '__main__':
    # path for google vision setup key
    google_key_path = 'C:/Google Cloud/sanguine-link-334321-c27b40c6071a.json'
    # path for captured image storage
    image_store_path = 'C:/Google Cloud/ocr_data/'
    # path for ocr text storage
    csv_store_path = 'C:/Google Cloud/ocr_data/image_ocr.csv'
    # path for temp data check from server
    csv_temp_path = 'C:/Google Cloud/ocr_data/order_export.csv'
    # path for server check tool
    CLI_tool_path = 'C:/iOrthotics/iorthoticsserver/roboapi.exe'

    # camera index and resolution setting
    camera_index = 1
    camera_resolution_width = 1920
    camera_resolution_height = 1080

    # initialize google vision
    google_vision_setup(google_key_path)

    # computer IP address as server
    Host = "192.168.0.10"
    Port = 30000

    # build a diction for parts placement and pairing
    pair_diction = build_diction()

    # max pairs number
    pair_index = 0
    part_index = 0
    max_pair_number = 70

    # Input "n" to start new session
    while True:
        sess = input('\nStart new session? (Enter n for new or any other key to exit)')
        if sess == 'n':
            print('Start new session')
            break
        else:
            print('Exiting')
            exit(0)

    # setup connection between computer and client robot using TCP/IPV4
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # server setup
        s.bind((Host, Port))
        s.listen()
        s.settimeout(40)
        print("Awaiting robot response")

        # create object for send and receive data
        conn, client_address = s.accept()
        with conn:
            # communication between server and client
            print('Connected to robot by: ', client_address)
            try_connection = ''
            while try_connection != 'robot start':
                try_connection = bytes. decode(conn.recv(1024))
            print('Received from robot: ', try_connection)
            conn.send(str.encode('server start'))
            print('Connection setup, both server and robot initialized')

            # system start picking and placing operation
            while pair_index <= max_pair_number:
                data_received = ''
                while data_received == '':
                    data_received = bytes. decode(conn.recv(1024))
                print('Receive message from robot: ', data_received)

                if data_received == 'part found':
                    # Robot camera try to find part in raw area
                    conn.send(str.encode('go ocr'))

                if data_received == 'part not found':
                    # nothing found in raw area, go next operation
                    break

                if data_received == 'ocr position':
                    # ocr camera capture image
                    capture_image = camera_capture(camera_index, camera_resolution_width, camera_resolution_height)
                    # save image for ocr and backup
                    saved_image_name = image_save(capture_image, image_store_path, part_index)
                    # ocr by google vision
                    ocr_text = google_vision(image_store_path + 'scan.jpg')
                    print('OCR recognized text: ', ocr_text)
                    # save ocr text on csv file
                    write_csv(saved_image_name, ocr_text)
                    # process ocr strings
                    part_number, part_keyword = words_process(ocr_text)
                    if part_number is not None:
                        # check order id from server
                        order_id_flag, order_state, order_type, order_colour, order_thick \
                            = server_check(part_number, csv_store_path, csv_temp_path)
                    else:
                        order_id_flag = False
                        order_state = None
                        order_type = None
                        order_colour = None
                        order_thick = None
                    # fill up and update "pair_diction"
                    pair_diction, pair_diction_index, pair_index = \
                        diction_fill_up(pair_diction, part_index, part_number, pair_index, part_keyword, order_id_flag,
                                        order_state, order_type, order_colour, order_thick)
                    conn.send(str.encode(pair_diction_index))

                if data_received == 'part placed':
                    # go back to pick area
                    conn.send(str.encode('go pick'))

            if pair_index >= max_pair_number:
                print('Reach maximum pair number')
            else:
                print('No part found, go next operation')

    print("DISPLAYING GRID")
    display_grid(pair_diction)
    exit_key = input("\nPress any key to exit......")

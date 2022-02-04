import socket
import json
import sys_setup

# from sys_setup import display_table

if __name__ == '__main__':
    # path for google vision setup key
    google_key_path = 'C:/Users/Healthia/Desktop/Robot/GoogleVisionAPI/google_apikey.json'
    # path for captured image storage
    image_store_path = 'C:/Users/Healthia/Desktop/Robot/Data/'
    # path for ocr text storage
    csv_store_path = 'C:/Users/Healthia/Desktop/Robot/Data/image_ocr.csv'
    # path for temp data check from server
    csv_temp_path = 'C:/Users/Healthia/Desktop/Robot/Data/order_export.csv'
    # path for server check tool
    CLI_tool_path = 'C:/Users/Healthia/Desktop/Robot/iOrthoticsAPI/roboapi.exe'
    # path for JSON file that keep diction
    json_diction_path = 'C:/Users/Healthia/Desktop//Robot/Data/js_diction.json'

    # camera index and resolution setting
    camera_index = 0
    camera_resolution_width = 3224
    camera_resolution_height = 2448

    # initialize google vision
    sys_setup.google_vision_setup(google_key_path)

    # computer IP address as server
    Host = "192.168.0.10"
    Port = 30000

    # build a diction for parts placement and pairing
    pair_diction = sys_setup.build_diction()

    # max pairs number
    part_index = 0
    max_pair_number = 70
    terminate_code = 99
    top_missed = 98
    top_error = 97
    max_position = 0

    # Input "n" to start new session
    while True:
        sess = input('\nStart new session? (Enter n for new, c to continue previous, or any other key to exit)')
        if sess == 'n':
            print('Start new session')
            break
        if sess == 'c':
            print('Continue previous session')
            # load saved JSON as dictionary ([0]dictionary, [1]placed part number)
            with open(json_diction_path, 'r') as js_load:
                js_read = json.load(js_load)
            part_index = int(js_read[1]) + 1
            for js_index in range(part_index):
                pair_diction[js_index] = js_read[0][str(js_index)]
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
                try_connection = bytes.decode(conn.recv(1024))
            print('Received from robot: ', try_connection)
            conn.send(str.encode('server start'))
            print('Connection setup, both server and robot initialized')

            # system start picking and placing operation
            while True:
                data_received = ''
                while data_received == '':
                    data_received = bytes.decode(conn.recv(1024))
                print('Receive message from robot: ', data_received)

                '''if data_received == 'part found':
                    # Robot camera try to find part in raw area
                    conn.send(str.encode('go ocr'))'''

                if data_received == 'part not found':
                    # nothing found in raw area, go next operation
                    break

                if data_received == 'ocr position':
                    # ocr camera capture image
                    capture_image = sys_setup.camera_capture(camera_index, camera_resolution_width,
                                                             camera_resolution_height)
                    # save image for ocr and backup
                    saved_image_name = sys_setup.image_save(capture_image, image_store_path, part_index)
                    # ocr by google vision
                    ocr_text = sys_setup.google_vision(image_store_path + 'scan.jpg')
                    print('OCR recognized text: ', ocr_text)
                    # save ocr text on csv file
                    sys_setup.write_csv(csv_store_path, saved_image_name, ocr_text)
                    # process ocr strings
                    part_number, part_keyword, order_id_flag = sys_setup.words_process(ocr_text)

                    if order_id_flag:
                        # check order id from server
                        order_state, order_list = sys_setup.server_check(part_number[0], csv_temp_path, CLI_tool_path)
                    else:
                        order_state = None
                        order_list = []
                    # fill up and update "pair_diction"
                    pair_diction, place_position = sys_setup.diction_fill_up(pair_diction, part_index, part_number,
                                                                             part_keyword,
                                                                             order_id_flag, order_state, order_list)
                    # record the largest pair number
                    if place_position > max_position:
                        max_position = place_position
                    pair_save = [pair_diction, max_position]
                    # save dictionary as JSON file
                    with open(json_diction_path, 'w+') as js_file:
                        json.dump(pair_save, js_file)

                    part_index = part_index + 1

                    # Avoid exceed pairing space limitation
                    if place_position > 69:
                        print('Exceed the maximum pair number')
                        conn.send(terminate_code.to_bytes(4, 'big'))
                    else:
                        print('Place position: ', place_position)
                        conn.send(place_position.to_bytes(4, 'big'))

                if data_received == 'part placed':
                    # go back to pick area
                    conn.send(str.encode('go pick'))

            for top_index in range(max_position + 1):
                top_flag, top_code = sys_setup.check_diction(pair_diction, top_index)
                if top_flag and top_code < 116:
                    print('Start match top')
                    conn.send(top_code.to_bytes(4, 'big'))
                    data_received = ''
                    while data_received == '':
                        data_received = bytes.decode(conn.recv(1024))
                    print('Receive message from robot: ', data_received)

                    if data_received == 'top found':
                        conn.send(top_index.to_bytes(4, 'big'))
                    if data_received == 'top missed':
                        conn.send(top_missed.to_bytes(4, 'big'))
                    else:
                        conn.send(top_error.to_bytes(4, 'big'))
                else:
                    print('External or Previous order, CANNOT find top matches order')

            conn.send(str.encode('process end'))

    print("DISPLAYING GRID")
    sys_setup.display_grid(pair_diction)
    exit_key = input("\nPress any key to exit......")

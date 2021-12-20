import socket
import time


Robot_HOST = '192.168.1.100'
Robot_PORT = 30000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((Robot_HOST, Robot_PORT))
    s.listen()
    conn, addr = s.accept()

    s.send(('set_digital_out(0, True)'+'\n').encode('utf8'))
    time.sleep(1)
    s.send(('movej(0.5, 0.5, 0.5, 0, 0, 0)'+'\n').encode('utf8'))

ur_file = open('C:/Google Cloud/ocr_data/test.script', 'rb')
ur_l = ur_file.read(1024)

while ur_l:
    s.send(ur_l)
    ur_l = ur_file.read(1024)

import socket


Host = "192.168.0.10"
Port = 30000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    #Establishes connection with UR10
    s.bind((Host, Port))
    s.listen()
    s.settimeout(40)
    s_count = 22

    conn, addr = s.accept()
    with conn:
        print('Connected by ', addr)
        rec = conn.recv(1024)
        print(rec)
        conn.send((s_count).to_bytes(1,'big'))
print('end')

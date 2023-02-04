import socket
import threading
import time, traceback
import random
import blockchain
import requests
import json

IP = socket.gethostbyname(socket.gethostname())
PORT = 5566
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
blockchain = blockchain.Blockchain()

response = requests.get("http://127.0.0.1:8080/validators")
validators = response.json()["validators"]

queue = list()


def handle_client(conn, addr):
    print(f"[CONNECTED] {addr} connected")
    connected = True
    msg = conn.recv(SIZE).decode(FORMAT)

    while connected:
        if msg == "!CHAIN":
            conn.send(blockchain.display_chain().encode(FORMAT))
        connected = False
    conn.close()


def main():
    print("[STARTING] Server is starting...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server is listening on {IP}:{PORT}")

    number_thread = threading.Thread(target=lambda: every(30, pick_winner))
    number_thread.start()

    add_data = threading.Thread(target=lambda: every(2, add_to_queue))
    add_data.start()

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


def pick_winner():
    length = len(validators)
    if length > 0:
        random_winner = random.randint(1, length)
    else:
        random_winner = 0

    url = "http://127.0.0.1:8080/winner"

    if len(queue) > 0:
        temp = queue
        obj = {'id': str(random_winner), 'data': temp}
        print(temp)
        requests.post(url, json=obj)

    queue.clear()



def add_to_queue():
    random_number = random.randint(0, 1000)
    queue.append(random_number)


def every(delay, task):
    next_time = time.time() + delay
    while True:
        time.sleep(max(0, next_time - time.time()))
        try:
            task()
        except Exception:
            traceback.print_exc()
        next_time += (time.time() - next_time) // delay * delay + delay


if __name__ == "__main__":
    main()

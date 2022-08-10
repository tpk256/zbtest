from threading import Thread
import socket
import json

data = []


class Socket(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True

    def run(self):
        sock = socket.create_server(('', 49001), family=socket.AF_INET, backlog=3)

        while True:
            out_socket, ip = sock.accept()

            data.append(json.loads(str(out_socket.recv(1024), "UTF-8")))
            print(data)


if __name__ == "__main__":
    thread = Socket()
    thread.start()
    thread.join()





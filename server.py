import socket
import sys
import time
import re
from clientthread import ClientListener

class Server():
    def __init__(self, port):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.bind(('', port))
        self.listener.listen(1)
        print("Listening on port", port)
        self.clients_sockets = []

    def run(self):
        while True:
            print("Listening new customers")
            try:
            except socket.error:
                sys.exit("Cannot connect clients")
            self.clients_sockets.append(client_socket)
            print("Start the thread for client:", client_adress)
            client_thread = ClientListener(self, client_socket, client_adress)
            client_thread.start()
            time.sleep(0.1)

            
            if(re.search('MDP (.*)$', client_socket.recv(1024).decode('UTF-8')).group(1) == "hello"):
                print("connection")
                self.clients_sockets.append(client_socket)
                print("Start the thread for client:", client_adress)
                client_thread = ClientListener(self, client_socket, client_adress)
                client_thread.start()
                time.sleep(0.1)
            else:
                print("no connection")
                client_socket.close()
                

    def remove_socket(self, socket):
        self.clients_sockets.remove(socket)

    def echo(self, data):
        print("echoing:", data)
        for sock in self.clients_sockets:
            try:
                sock.sendall(data.encode("UTF_8"))
            except socket.error:
                print("Cannot send the message")

if __name__ == "__main__":
    server = Server(59001)
    server.run()

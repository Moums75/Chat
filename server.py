import socket
import sys
import time
import ssl
from clientthread import ClientListener

class Server:
    def __init__(self, port):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.bind(('', port))
        self.listener.listen(5)
        print("Listening on port", port)

        # SSL 
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')

        self.clients_sockets = []

    def run(self):
        while True:
            print("Listening new customers...")
            try:
                client_socket, client_address = self.listener.accept()
                secure_socket = self.context.wrap_socket(client_socket, server_side=True)

                print("Start the thread for client:", client_address)
                self.clients_sockets.append(secure_socket)

                client_thread = ClientListener(self, secure_socket, client_address)
                client_thread.start()

            except socket.error as e:
                print("Cannot connect clients:", e)

            time.sleep(0.1)

    def remove_socket(self, sock):
        if sock in self.clients_sockets:
            print("Removing socket")
            self.clients_sockets.remove(sock)
            try:
                sock.close()
            except:
                pass

    def echo(self, data):
        print("Echoing:", data)
        for sock in list(self.clients_sockets):
            try:
                sock.sendall(data.encode("UTF-8"))
            except Exception as e:
                print("Cannot send the message:", e)
                self.remove_socket(sock)

if __name__ == "__main__":
    server = Server(59001)
    server.run()

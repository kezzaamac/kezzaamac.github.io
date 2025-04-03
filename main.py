
import socket
import threading
import sys
from colorama import Fore, init

init()  # Initialize colorama

class ChatClient:
    def __init__(self, host='0.0.0.0', port=5000):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.username = input("Enter your username: ")
        try:
            self.sock.connect((host, port))
            print(f"{Fore.GREEN}Connected to chat server!{Fore.RESET}")
            self.sock.send(self.username.encode())
        except:
            print(f"{Fore.RED}Couldn't connect to server{Fore.RESET}")
            sys.exit()

    def receive_messages(self):
        while True:
            try:
                message = self.sock.recv(1024).decode()
                if message:
                    print(message)
            except:
                print(f"{Fore.RED}Lost connection to server{Fore.RESET}")
                self.sock.close()
                break

    def send_messages(self):
        while True:
            try:
                message = input()
                if message.lower() == 'quit':
                    self.sock.close()
                    sys.exit()
                self.sock.send(f"{self.username}: {message}".encode())
            except:
                break

    def start(self):
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()
        
        send_thread = threading.Thread(target=self.send_messages)
        send_thread.daemon = True
        send_thread.start()
        
        try:
            send_thread.join()
        except KeyboardInterrupt:
            print("\nExiting chat...")
            self.sock.close()
            sys.exit()

class ChatServer:
    def __init__(self, host='0.0.0.0', port=5000):
        self.clients = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))
        self.sock.listen(5)
        print(f"{Fore.GREEN}Chat server started on {host}:{port}{Fore.RESET}")

    def broadcast(self, message, sender=None):
        for client in self.clients:
            if client != sender:
                try:
                    client.send(message.encode())
                except:
                    self.clients.remove(client)

    def handle_client(self, client):
        username = client.recv(1024).decode()
        self.broadcast(f"{Fore.YELLOW}{username} joined the chat!{Fore.RESET}")
        
        while True:
            try:
                message = client.recv(1024).decode()
                if message:
                    self.broadcast(message, client)
            except:
                self.clients.remove(client)
                self.broadcast(f"{Fore.YELLOW}{username} left the chat{Fore.RESET}")
                break

    def start(self):
        while True:
            client, address = self.sock.accept()
            self.clients.append(client)
            thread = threading.Thread(target=self.handle_client, args=(client,))
            thread.daemon = True
            thread.start()

if __name__ == "__main__":
    mode = input("Enter 's' for server, 'c' for client: ").lower()
    
    if mode == 's':
        server = ChatServer()
        server.start()
    elif mode == 'c':
        client = ChatClient()
        client.start()
    else:
        print("Invalid mode selected")

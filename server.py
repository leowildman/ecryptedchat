import socket
import threading
import rsa
from typing import Union


def is_socket_closed(sock: socket.socket) -> bool:
    try:
        # this will try to read bytes without blocking and also without removing them from buffer (peek only)
        data = sock.recv(16, socket.MSG_DONTWAIT | socket.MSG_PEEK)
        if len(data) == 0:
            return True
    except BlockingIOError:
        return False  # socket is open and reading from it would block
    except ConnectionResetError:
        return True  # socket was closed for some other reason
    except Exception as e:
        return False
    return False


class server_client:
    def __init__(self, nickname:str, client:socket.socket, public_key:rsa.PublicKey):
        self.nickname = nickname
        self.client = client
        self.public_key = public_key
        
    def __repr__(self) -> str:
        return self.nickname
    
    def send_message(self, message, nick=""):
        if type(message) == bytes: message = message.decode()
        message = f"{nick}: {message}"
        if type(message) == str: message = message.encode()
        
        
        encoded_encrypted_message = rsa.encrypt(message, self.public_key)
        self.client.send(encoded_encrypted_message)
        
    def recieve_message(self, private_key) -> str:
        try:
            data = self.client.recv(2048)
            message = rsa.decrypt(data, private_key).decode()
            print(message)
            return message
        except Exception as e:
            self.client.close()
            return f"Error:{e}"

class server:
    def __init__(self, host:str, port:int) -> None:
        
    
        self.host = host
        self.port = port

        #keygen
        self.public_key, self.private_key = rsa.newkeys(2048)

        self.socketServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socketServer.bind((self.host, self.port))
        self.socketServer.listen()

        # Lists For Clients and Their Nicknames
        self.clients = []
        self.nicknames = []

    def broadcast(self, clients, message, send_nick = "") -> None:
        if (clients != []) and (type(clients) == list):
            for client in clients:
                client.send_message(message, send_nick)
            
    def handle(self, client_obj) :
        while True:
            print(self.clients)
            try:
                message = client_obj.recieve_message(self.private_key)
                self.broadcast([x for x in self.clients if x != client_obj], message, client_obj.nickname)
            except Exception as e:
                print(e)
                break
                
            
    def receive(self):
        while True:
            # Accept Connection
            client, address = self.socketServer.accept()
            print("Connected with {}".format(str(address)))

            client.send(self.public_key.save_pkcs1("PEM"))
            partner_public_key = rsa.PublicKey.load_pkcs1(client.recv(2048))
            print(partner_public_key)
            
            new_client = server_client(nickname="", client=client, public_key=partner_public_key)

            # Request And Store Nickname
            new_client.send_message('NICK:')
            nickname = new_client.recieve_message(self.private_key)
            
            new_client.nickname = nickname
            
            self.clients.append(new_client)

            # Print And Broadcast Nickname
            print("Nickname is {}".format(nickname))
            self.broadcast(self.clients, "{} joined!".format(nickname), "Server")
            new_client.send_message('Connected to server!')

            # Start Handling Thread For Client
            thread = threading.Thread(target=self.handle, args=(new_client,))
            thread.start()


s = server(host="romeo-juliet.herokuapp.com", port=8889)
s.receive()
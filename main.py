import socket

import rsa

class chat:
    def __init__(self, is_server:bool, address:str, port:int, logging, message_bytes:int=2048) -> None:
        """Encrypted Chat Class, Generates private and public keys automatically.

        Args:
            is_server (bool): If this is a server, true. if this is a client, false.
            address (str): address of server
            port (int): port of server
        """        
        self.address = address
        self.port = port
        self.is_server = is_server
        self.message_bytes = message_bytes
        self.public_key, self.private_key = rsa.newkeys(self.message_bytes)
        self.partner_public_key = None
        self.server = None
        self.logging = logging
        
    def start(self) -> None:
        """
        Begins server/client
        """
        if self.is_server == True:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.address, self.port))
            self.server.listen()
            self.logging("Server started! Listening...\n", "log")
            
            self.client, _ = self.server.accept()
            self.client.send(self.public_key.save_pkcs1("PEM"))
            self.partner_public_key = rsa.PublicKey.load_pkcs1(self.client.recv(self.message_bytes))
            self.logging("Keys Exchanged... Ready.\n", "log")
    
        elif self.is_server == False:
            tries = 0
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.logging("Client started! Searching for server...\n", "log")
            while 1:
                try:
                    self.client.connect((self.address,self.port))
                    break
                except ConnectionRefusedError:
                    if tries > 50:
                        exit()
                    else:
                        tries += 1
                        continue
            
            self.partner_public_key = rsa.PublicKey.load_pkcs1(self.client.recv(self.message_bytes))
            self.client.send(self.public_key.save_pkcs1("PEM"))
            self.logging("Keys Exchanged... Ready.\n", "log")
            
        self.logging(f"Connected to {self.client.getpeername()}\n", "log")
            
    def send_message(self, message):
        self.client.send(rsa.encrypt(message.encode(), self.partner_public_key))
        
    def recieve_message(self):
        try:
            data = self.client.recv(int(self.message_bytes))
            message = rsa.decrypt(data, self.private_key).decode()
            return message
        except Exception as e:
            self.client.close()
            return e
    
    def close_connection(self) -> None:
        self.client.close()
        if self.server is not None:
            self.server.close()
    



        
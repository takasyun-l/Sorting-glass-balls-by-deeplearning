import socket

class SocketClient:
    def __init__(self, server_address, message):
        # 标志位初始化
        self.recv_terminate = True
        
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = server_address
        self.message = message

    def send_receive(self):
        self.client_socket.connect(self.server_address)
        self.client_socket.sendall(self.message.encode())
        data = self.client_socket.recv(1024)
        self.client_socket.close()
        return data.decode()

class SocketServer:
    def __init__(self, server_address, qwindow):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = server_address
        self.qwindow = qwindow
        self.server_socket.bind(self.server_address)
        self.server_socket.listen(128)
        
    def getID(self):
        if hasattr(self, 'server_socket'):
            self.client_socket, self.client_address = self.server_socket.accept()
        
    def receive(self):
        self.recv_terminate = True
        if hasattr(self, 'client_socket'):
            while self.recv_terminate:
                self.data = self.client_socket.recv(1024)
                self.qwindow.recvmsg.emit(self.data)
                # print(self.data)
                if not self.data:
                    break
    
    def terminate(self):
        self.recv_terminate = False
        
    def send(self, message):
        if hasattr(self, 'client_socket'):
            self.client_socket.sendall(message.encode())
        
    def __del__(self):
        if hasattr(self, 'client_socket'):
            self.client_socket.close()
        if hasattr(self, 'server_socket'):
            self.server_socket.close()
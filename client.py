# client.py
# Network Communication Logic

import socket
import threading


class TCPClient:
    def __init__(self, server_ip, server_port, buffer_size):
        self.server_ip = server_ip
        self.server_port = server_port
        self.buffer_size = buffer_size
        self.client_socket = None
        self.is_connected = False
        self.receive_thread = None

    def connect(self, callback):
        """
        Connect to the server and start the receive thread.
        :param callback: A callback function to handle received messages.
        """
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.server_ip, self.server_port))
            self.client_socket.settimeout(1.0)  # Set a timeout for recv
            self.is_connected = True
            self.receive_thread = threading.Thread(target=self.receive_messages, args=(callback,), daemon=True)
            self.receive_thread.start()
            return True
        except Exception as e:
            return f"Connection failed: {e}"

    def disconnect(self):
        """
        Disconnect from the server and close the socket.
        """
        if self.client_socket:
            try:
                self.client_socket.shutdown(socket.SHUT_RDWR)
            except (OSError, socket.error):
                pass
            finally:
                self.client_socket.close()
                self.client_socket = None
        self.is_connected = False

    def send_state(self, state):
        """
        Send a state message to the server.
        :param state: State string to send.
        """
        if self.is_connected:
            try:
                gear_id = 5003
                message = f"ID={gear_id};DATA={state}"
                self.client_socket.sendall(message.encode('utf-8'))
                print(f"Sent: {message}")
                return f"Sent state: {message}"
            except Exception as e:
                self.disconnect()
                return f"Send failed: {e}"
        return "Client is not connected."

    def receive_messages(self, callback):
        """
        Listen for incoming messages and pass them to a callback.
        :param callback: Function to handle received messages.
        """
        try:
            while self.is_connected:
                try:
                    response = self.client_socket.recv(self.buffer_size)
                    if response:
                        callback(response.decode('utf-8'))
                    else:
                        self.disconnect()
                        break
                except socket.timeout:
                    continue
        except (socket.error, OSError) as e:
            self.disconnect()

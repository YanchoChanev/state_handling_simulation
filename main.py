import tkinter as tk
from tkinter import scrolledtext, messagebox
import socket
import threading

# TCP Client Configuration
SERVER_IP = "127.0.0.1"
SERVER_PORT = 5001
BUFFER_SIZE = 1024


# TCP Client Class
class TCPClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FreeRTOS TCP Client")
        self.root.geometry("500x400")

        # Connection Status
        self.connection_status = tk.StringVar(value="Disconnected")
        self.client_socket = None
        self.is_connected = False
        self.receive_thread = None

        # UI Components
        self.setup_ui()

    def setup_ui(self):
        # Connection Frame
        connection_frame = tk.Frame(self.root)
        connection_frame.pack(pady=10)

        tk.Label(connection_frame, text="Server IP:").grid(row=0, column=0)
        self.server_ip_entry = tk.Entry(connection_frame, width=15)
        self.server_ip_entry.insert(0, SERVER_IP)
        self.server_ip_entry.grid(row=0, column=1)

        tk.Label(connection_frame, text="Port:").grid(row=0, column=2)
        self.server_port_entry = tk.Entry(connection_frame, width=5)
        self.server_port_entry.insert(0, SERVER_PORT)
        self.server_port_entry.grid(row=0, column=3)

        self.connect_button = tk.Button(connection_frame, text="Connect", command=self.connect_to_server)
        self.connect_button.grid(row=0, column=4, padx=5)

        self.status_label = tk.Label(connection_frame, textvariable=self.connection_status, fg="red")
        self.status_label.grid(row=0, column=5)

        # Chat Frame
        self.chat_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=15, state='disabled')
        self.chat_area.pack(pady=10, fill=tk.BOTH, expand=True)

        # Message Frame
        message_frame = tk.Frame(self.root)
        message_frame.pack(pady=5)

        self.message_entry = tk.Entry(message_frame, width=40)
        self.message_entry.pack(side=tk.LEFT, padx=5)

        self.send_button = tk.Button(message_frame, text="Send", command=self.send_message, state='disabled')
        self.send_button.pack(side=tk.RIGHT)

    def connect_to_server(self):
        if not self.is_connected:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((self.server_ip_entry.get(), int(self.server_port_entry.get())))
                self.client_socket.settimeout(1.0)  # Set a timeout for recv
                self.is_connected = True

                # Update GUI in the main thread
                self.root.after(0, self.update_connection_state, True)

                # Start listening thread
                self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
                self.receive_thread.start()

            except Exception as e:
                messagebox.showerror("Connection Error", f"Failed to connect: {e}")
                self.root.after(0, self.update_connection_state, False)
        else:
            self.disconnect_from_server()

    def disconnect_from_server(self):
        if self.client_socket:
            try:
                self.client_socket.shutdown(socket.SHUT_RDWR)
            except (OSError, socket.error):
                pass  # Ignore errors if socket is already closed
            finally:
                self.client_socket.close()
                self.client_socket = None

        self.is_connected = False
        self.root.after(0, self.update_connection_state, False)

    def update_connection_state(self, connected):
        if connected:
            self.connection_status.set("Connected")
            self.status_label.config(fg="green")
            self.connect_button.config(text="Disconnect")
            self.send_button.config(state='normal')
        else:
            self.connection_status.set("Disconnected")
            self.status_label.config(fg="red")
            self.connect_button.config(text="Connect")
            self.send_button.config(state='disabled')

    def send_message(self):
        message = self.message_entry.get()
        if message and self.is_connected:
            try:
                self.client_socket.sendall(message.encode('utf-8'))
                self.update_chat_area(f"You: {message}")
                self.message_entry.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Send Error", f"Failed to send message: {e}")
                self.disconnect_from_server()

    def receive_messages(self):
        try:
            while self.is_connected:
                try:
                    response = self.client_socket.recv(BUFFER_SIZE)
                    if response:
                        decoded_message = response.decode('utf-8')
                        self.root.after(0, self.update_chat_area, f"Server: {decoded_message}")
                    else:
                        self.root.after(0, self.disconnect_from_server)
                        break
                except socket.timeout:
                    continue
        except (socket.error, OSError) as e:
            self.root.after(0, self.disconnect_from_server)
        finally:
            self.root.after(0, self.disconnect_from_server)

    def update_chat_area(self, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, message + '\n')
        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END)

    def on_close(self):
        self.disconnect_from_server()
        self.root.destroy()


# Start GUI Application
if __name__ == "__main__":
    root = tk.Tk()
    app = TCPClientApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

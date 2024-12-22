# ui.py
# GUI Logic with Tkinter

import tkinter as tk
from tkinter import scrolledtext, messagebox
from config import *
from client import TCPClient
from tests import run_test_cases


class TCPClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FreeRTOS TCP Client")
        self.root.geometry("600x600")
        self.client = TCPClient(SERVER_IP, SERVER_PORT, BUFFER_SIZE)

        # Connection Status
        self.connection_status = tk.StringVar(value="Disconnected")

        # UI Components
        self.setup_ui()

    def setup_ui(self):
        # Connection Frame
        connection_frame = tk.Frame(self.root)
        connection_frame.pack(pady=10)

        self.connect_button = tk.Button(connection_frame, text="Connect", command=self.connect_to_server)
        self.connect_button.grid(row=0, column=0, padx=5)

        self.status_label = tk.Label(connection_frame, textvariable=self.connection_status, fg="red")
        self.status_label.grid(row=0, column=1)

        # Chat Frame
        self.chat_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=15, state='disabled')
        self.chat_area.pack(pady=10, fill=tk.BOTH, expand=True)

        # State Control Frame
        state_frame = tk.LabelFrame(self.root, text="State Control")
        state_frame.pack(pady=10, fill=tk.X)

        self.state_var = tk.StringVar(value=STATE_SLEEP)
        for state, label in STATE_MAP.items():
            tk.Radiobutton(state_frame, text=label, variable=self.state_var, value=state).pack(side=tk.LEFT, padx=5)

        self.send_state_button = tk.Button(state_frame, text="Send State", command=self.send_state, state='disabled')
        self.send_state_button.pack(side=tk.RIGHT, padx=10)

        # Test Case Frame
        test_frame = tk.LabelFrame(self.root, text="Test Cases")
        test_frame.pack(pady=10, fill=tk.X)

        self.run_tests_button = tk.Button(test_frame, text="Run Test Cases", command=self.run_tests, state='disabled')
        self.run_tests_button.pack(padx=5)

    def connect_to_server(self):
        if not self.client.is_connected:
            result = self.client.connect(self.update_chat_area)
            if result is True:
                self.connection_status.set("Connected")
                self.status_label.config(fg="green")
                self.send_state_button.config(state='normal')
                self.run_tests_button.config(state='normal')
            else:
                messagebox.showerror("Connection Error", result)
        else:
            self.client.disconnect()
            self.connection_status.set("Disconnected")
            self.status_label.config(fg="red")

    def send_state(self):
        state = self.state_var.get()
        result = self.client.send_state(state)
        if result:
            self.update_chat_area(result)
        else:
            self.update_chat_area("Failed to send state.")

    def run_tests(self):
        run_test_cases(self.client, self.update_chat_area)

    def update_chat_area(self, message):
        if message:
            self.chat_area.config(state='normal')
            self.chat_area.insert(tk.END, message + '\n')
            self.chat_area.config(state='disabled')
            self.chat_area.see(tk.END)

    def on_close(self):
        self.client.disconnect()
        self.root.destroy()

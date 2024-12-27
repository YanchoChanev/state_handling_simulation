import tkinter as tk
from tkinter import scrolledtext, messagebox
from config import *
from client import TCPClient
from tests import run_smoke_tests, run_stress_test
import threading


class TCPClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FreeRTOS TCP Client")
        self.root.geometry("600x600")
        self.client = TCPClient(SERVER_IP, SERVER_PORT, BUFFER_SIZE)
        self.stress_test_running = False

        # Connection Status
        self.connection_status = tk.StringVar(value="Disconnected")
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

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

        # Stress Test Iterations
        stress_test_frame = tk.Frame(self.root)
        stress_test_frame.pack(pady=5)
        tk.Label(stress_test_frame, text="Stress Test Iterations:").grid(row=0, column=0)
        self.stress_test_iterations_var = tk.StringVar(value="5")
        tk.Entry(stress_test_frame, textvariable=self.stress_test_iterations_var, width=10).grid(row=0, column=1)

        # Fault Sleep Time
        tk.Label(stress_test_frame, text="Sleep Time After FAULT (sec):").grid(row=1, column=0)
        self.fault_sleep_time_var = tk.StringVar(value="30")
        tk.Entry(stress_test_frame, textvariable=self.fault_sleep_time_var, width=10).grid(row=1, column=1)

        # Test Case Buttons
        test_frame = tk.LabelFrame(self.root, text="Test Cases")
        test_frame.pack(pady=10, fill=tk.X)

        self.run_smoke_tests_button = tk.Button(test_frame, text="Run Smoke Tests", command=self.run_smoke_tests)
        self.run_smoke_tests_button.pack(padx=5)

        self.run_stress_test_button = tk.Button(test_frame, text="Run Stress Test", command=self.run_stress_test)
        self.run_stress_test_button.pack(padx=5)

        self.stop_stress_test_button = tk.Button(test_frame, text="Stop Stress Test", command=self.stop_stress_test, state='disabled')
        self.stop_stress_test_button.pack(padx=5)

    def connect_to_server(self):
        if not self.client.is_connected:
            result = self.client.connect(self.update_chat_area)
            if result is True:
                self.connection_status.set("Connected")
                self.status_label.config(fg="green")
                self.send_state_button.config(state='normal')
                self.run_smoke_tests_button.config(state='normal')
                self.run_stress_test_button.config(state='normal')
            else:
                self.update_chat_area(f"Connection failed: {result}")
                self.schedule_reconnect()
            return
        else:
            self.client.disconnect()
            self.connection_status.set("Disconnected")
            self.status_label.config(fg="red")
            self.send_state_button.config(state='disabled')
            self.run_smoke_tests_button.config(state='disabled')
            self.run_stress_test_button.config(state='disabled')

    def send_state(self):
        state = self.state_var.get()
        result = self.client.send_state(state)
        if result:
            self.update_chat_area(result)
        else:
            self.update_chat_area("Failed to send state.")

    def run_smoke_tests(self):
        threading.Thread(target=run_smoke_tests, args=(self.client, self.update_chat_area), daemon=True).start()

    def run_stress_test(self):
        try:
            iterations = int(self.stress_test_iterations_var.get())
            fault_sleep_time = int(self.fault_sleep_time_var.get())
            self.stress_test_running = True
            self.stop_stress_test_button.config(state='normal')
            threading.Thread(target=run_stress_test, args=(self.client, self.update_chat_area, iterations, fault_sleep_time, lambda: self.stress_test_running), daemon=True).start()
        except ValueError:
            messagebox.showerror("Error", "Invalid input for stress test iterations or fault sleep time.")

    def stop_stress_test(self):
        self.stress_test_running = False
        self.stop_stress_test_button.config(state='disabled')
        self.update_chat_area("Stress Test Stopped by User.")

    def update_chat_area(self, message):
        if message:
            self.chat_area.config(state='normal')
            self.chat_area.insert(tk.END, message + '\n')
            self.chat_area.config(state='disabled')
            self.chat_area.see(tk.END)

    def schedule_reconnect(self):
        self.root.after(5000, self.connect_to_server)

    def on_close(self):
        if self.client.is_connected:
            self.client.disconnect()
            self.update_chat_area("Client disconnected successfully.")
        self.root.destroy()

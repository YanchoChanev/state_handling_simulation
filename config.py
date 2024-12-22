# config.py
# Configuration and Constants

# TCP Client Configuration
SERVER_IP = "127.0.0.1"
SERVER_PORT = 5001
BUFFER_SIZE = 1024

# States Definition
STATE_SLEEP = "0"
STATE_ACTIVE = "1"
STATE_FAULT = "2"

STATE_MAP = {
    STATE_SLEEP: "SLEEP",
    STATE_ACTIVE: "ACTIVE",
    STATE_FAULT: "FAULT"
}

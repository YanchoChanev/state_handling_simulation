import time
import random
from config import STATE_SLEEP, STATE_ACTIVE, STATE_FAULT, STATE_MAP


def run_smoke_tests(client, update_chat_area):
    gear_id = 5003
    update_chat_area("**Starting Smoke Tests...**")

    # Disconnect and reconnect before proceeding
    client.disconnect()
    
    while not client.is_connected:
        try:
            client.connect(lambda msg: update_chat_area(f"[Server] {msg}"))
            update_chat_area("[Connection Restored] Client reconnected successfully.")
            time.sleep(1)
        except Exception as e:
            update_chat_area(f"[Connection Failed] {str(e)}")
            time.sleep(5)

    smoke_test_cases = [
        (STATE_SLEEP, "Smoke Test: Successful Connection & State Sending (SLEEP)"),
        (STATE_ACTIVE, "Smoke Test: Successful State Sending (ACTIVE)"),
        (STATE_FAULT, "Smoke Test: Successful State Sending (FAULT)"),
    ]

    for state, description in smoke_test_cases:
        update_chat_area(f"🔄 Test Case: {description}")
        result = client.send_state(state)
        update_chat_area(result)
        time.sleep(1)

    update_chat_area("**Smoke Tests Completed Successfully.**")


def run_stress_test(client, update_chat_area, iterations=5, speep_on_fault = 30, stop_condition=lambda: True):
    """
    Perform sequential stress test with specified iterations:
    1. Send ACTIVE → Wait 3 sec
    2. Send SLEEP → Wait 3 sec
    3. Send ACTIVE → Wait 3 sec
    4. Send FAULT → Wait 30 sec
    Verify connection on every iteration before proceeding.
    :param client: TCPClient instance.
    :param update_chat_area: Function to log messages.
    :param iterations: Number of iterations to run.
    """
    update_chat_area("**Starting Sequential Stress Test...**")
    gear_id = 5003
    try:
        for iteration in range(0, iterations + 1):
            update_chat_area(f"**Iteration {iteration}: Verifying Connection...**")

            if not stop_condition():
                update_chat_area("⚠️ **Stress Test Stopped by User.**")
                break
            
            if iteration > 0:
                # Disconnect and reconnect before proceeding
                client.disconnect()
                
                while not client.is_connected:
                    try:
                        client.connect(lambda msg: update_chat_area(f"[Server] {msg}"))
                        update_chat_area("[Connection Restored] Client reconnected successfully.")
                        time.sleep(1)
                    except Exception as e:
                        update_chat_area(f"[Connection Failed] {str(e)}")
                        time.sleep(5)
            
            # Step 1: Send ACTIVE
            update_chat_area("[Step 1] Sending ACTIVE state")
            message = f"ID={gear_id};DATA={STATE_ACTIVE}"
            client.client_socket.sendall(message.encode())
            update_chat_area(f"Sent: {message}")
            time.sleep(3)

            # Step 2: Send SLEEP
            update_chat_area("[Step 2] Sending SLEEP state")
            message = f"ID={gear_id};DATA={STATE_SLEEP}"
            client.client_socket.sendall(message.encode())
            update_chat_area(f"Sent: {message}")
            time.sleep(3)

            # Step 3: Send ACTIVE
            update_chat_area("[Step 3] Sending ACTIVE state")
            message = f"ID={gear_id};DATA={STATE_ACTIVE}"
            client.client_socket.sendall(message.encode())
            update_chat_area(f"Sent: {message}")
            time.sleep(3)

            # Step 4: Send FAULT
            update_chat_area("[Step 4] Sending FAULT state")
            message = f"ID={gear_id};DATA={STATE_FAULT}"
            update_chat_area(f"Sent: {message}")
                
            client.client_socket.sendall(message.encode())
            update_chat_area(f"⏳ [Step 4] Waiting {speep_on_fault} seconds after FAULT state")
            time.sleep(speep_on_fault)

            update_chat_area(f"**Iteration {iteration} Completed Successfully.**")
    except KeyboardInterrupt:
        update_chat_area("**Stress Test Interrupted by User.**")

    except Exception as e:
        update_chat_area(f"**Stress Test Failed: {str(e)}**")

    finally:
        update_chat_area("**Stress Test Completed.**")

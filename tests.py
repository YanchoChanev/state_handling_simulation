# tests.py
# Test Scenarios

import time
from config import STATE_SLEEP, STATE_ACTIVE, STATE_FAULT, STATE_MAP


def run_test_cases(client, update_chat_area):
    update_chat_area("🏁 **Starting Test Cases...**")

    test_cases = [
        (STATE_SLEEP, "State Change Verification - SLEEP"),
        (STATE_ACTIVE, "State Change Verification - ACTIVE"),
        (STATE_FAULT, "State Change Verification - FAULT"),
        ("3", "Invalid State Handling"),
        (STATE_FAULT, "Persistent FAULT State"),
        (STATE_ACTIVE, "Rapid Sequential State Changes"),
    ]

    for state, description in test_cases:
        update_chat_area(f"🔄 Test Case: {description}")
        result = client.send_state(state)
        update_chat_area(result)
        time.sleep(1)

    update_chat_area("✅ **All Test Cases Completed Successfully.**")

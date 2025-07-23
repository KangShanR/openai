import socket
import time
import sys

# --- Configuration Parameters ---
# Host Controller's IP address and port.
# If host_controller.py is running on the same machine, '127.0.0.1' (localhost) is fine.
HOST = '127.0.0.1'
# This must match the PORT configured in your host_controller.py
PORT = 12345

# --- Test Commands ---
# A list of commands to send to the host controller.
# Make sure these match the keys in your host_controller.py's COMMAND_MAP
TEST_COMMANDS = [
        # System/Application Control
    # "open terminal",
    # "open folder",
    # "close application",
    # "screenshot",
    # "lock computer",
    # "minimize all window",
    # "open task manage",
    # "show applications",

    # # Media Contro,
    # "volume up",
    # "volume down",
    # "mute",
    # "play pause",
    # "next track",
    # "previous track",

    # # Basic Navigatio,
    # "scroll down",
    # "scroll up",
    # "click",
    # "double click",
    # "right click",
    # "enter",
    # "backspace",
    # "type",

    # # Added Commo,
    # "Up",
    # "Up",
    "Down.",
    "left",
    # "right",
    # "page down",
    # "page up",
    # "go to start",
    # "go to end",
    # "switch window",
    # "switch tab",
    # "switch tab back",
    
    # "tab"
]

def send_test_commands():
    """Connects to the host controller and sends a series of test commands."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print(f"Attempting to connect to {HOST}:{PORT}...")
            s.connect((HOST, PORT))
            print("Successfully connected to Host Controller!")

            # --- 新增：在發送第一個命令前添加短暫延遲 ---
            time.sleep(0.3) # 延遲 100 毫秒 (0.1秒)，可以嘗試 0.05 到 0.2 秒

            for i, cmd in enumerate(TEST_COMMANDS):
                print(f"\n[{i+1}/{len(TEST_COMMANDS)}] Sending command: '{cmd}'")
                s.sendall(cmd.encode('utf-8')) # Send the command as bytes
                time.sleep(2) # Wait a bit between commands to observe actions

            print("\nAll test commands sent. Disconnecting.")

    except ConnectionRefusedError:
        print(f"Error: Connection refused. Is host_controller.py running on {HOST}:{PORT}?", file=sys.stderr)
        print("Please ensure 'host_controller.py' is running and accessible.", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    print("--- Starting Local Test Client ---")
    send_test_commands()
    print("--- Local Test Client Finished ---")
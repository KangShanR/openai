import socket
import pyautogui
import sys
import time

# --- Configuration Parameters ---
# HOST: Listen on all available network interfaces.
#       This allows connections from Docker containers (using host.docker.internal or host network mode).
HOST = '0.0.0.0'
# PORT: The port number for communication. Must match the port used by the Docker container.
PORT = 12345

# --- PyAutoGUI Settings ---
# FAILSAFE: If the mouse is moved to the top-left corner (0,0), PyAutoGUI will raise an exception and terminate.
#           This is a safety feature to stop the script if it goes rogue.
#           Highly recommended to keep True during testing.
pyautogui.FAILSAFE = True
# PAUSE: The delay in seconds after each PyAutoGUI call.
#        Helps prevent operations from being too fast for the system to react.
pyautogui.PAUSE = 0.5

# --- Command Mapping ---
# This dictionary maps recognized voice commands (strings) to PyAutoGUI actions (functions).
# You can easily add, remove, or modify commands here.
COMMAND_MAP = {
    # System/Application Control
    "打開瀏覽器": lambda: (pyautogui.hotkey('win', 'r'), pyautogui.write('microsoft-edge'), pyautogui.press('enter')),
    "打開記事本": lambda: (pyautogui.hotkey('win', 'r'), pyautogui.write('notepad'), pyautogui.press('enter')),
    "關閉應用": lambda: pyautogui.hotkey('alt', 'f4'),
    "截圖": lambda: pyautogui.screenshot(f'screenshot_{int(time.time())}.png'), # Adds timestamp to filename
    "鎖定電腦": lambda: pyautogui.hotkey('win', 'l'),
    "最小化所有窗口": lambda: pyautogui.hotkey('win', 'd'),
    "打開任務管理器": lambda: pyautogui.hotkey('ctrl', 'shift', 'esc'),

    # Media Control
    "音量調高": lambda: pyautogui.press('volumeup'),
    "音量調低": lambda: pyautogui.press('volumedown'),
    "靜音": lambda: pyautogui.press('volumemute'),
    "播放暫停": lambda: pyautogui.press('playpause'),
    "下一曲": lambda: pyautogui.press('nexttrack'),
    "上一曲": lambda: pyautogui.press('prevtrack'),

    # Navigation/Typing
    "向下滾動": lambda: pyautogui.scroll(-500),
    "向上滾動": lambda: pyautogui.scroll(500),
    "點擊": lambda: pyautogui.click(),
    "雙擊": lambda: pyautogui.doubleClick(),
    "右擊": lambda: pyautogui.rightClick(),
    "回車": lambda: pyautogui.press('enter'),
    "退格": lambda: pyautogui.press('backspace'),
    "輸入": lambda: print("準備接收輸入內容..."), # Placeholder for commands that need further input
    "清空搜索框": lambda: pyautogui.hotkey('ctrl', 'a', 'backspace'),

    # Example for text input (you'd need to send the text after "輸入")
    "輸入 hello world": lambda: pyautogui.write('hello world'),
    "輸入百度": lambda: pyautogui.write('baidu.com'),

    # You can add more complex sequences or prompts for user input
}

def execute_command(command_text: str):
    """
    Executes a PyAutoGUI action based on the recognized command text.
    Handles exact matches and simple "input text" commands.
    """
    command_text = command_text.strip().lower() # Normalize command for matching

    # Handle explicit "input" commands
    if command_text.startswith("輸入"):
        text_to_type = command_text[2:].strip() # Extract text after "輸入"
        if text_to_type:
            print(f"Typing: '{text_to_type}'")
            pyautogui.write(text_to_type)
            print("Text typed successfully.")
        else:
            print("Command '輸入' received, but no text provided.")
        return # Command handled

    # Handle other predefined commands
    action = COMMAND_MAP.get(command_text)
    if action:
        print(f"Executing command: '{command_text}'")
        try:
            action()
            print("Command executed successfully.")
        except Exception as e:
            print(f"Error executing command '{command_text}': {e}", file=sys.stderr)
    else:
        print(f"Unknown command: '{command_text}'")

def start_server():
    """
    Starts the Socket server to listen for commands from the Docker container.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Allows reusing the socket address (important if the script restarts quickly)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Host Controller: Listening for commands on {HOST}:{PORT}...")

        while True:
            conn, addr = s.accept() # Accept a new connection
            with conn: # Use 'with' statement for automatic closing
                print(f"Host Controller: Connected by {addr}")
                while True:
                    data = conn.recv(1024) # Receive data (up to 1024 bytes)
                    if not data:
                        # No data means the client has disconnected
                        break
                    command = data.decode('utf-8').strip()
                    print(f"Host Controller: Received command: '{command}'")
                    execute_command(command)
            print(f"Host Controller: Connection from {addr} closed.")

if __name__ == "__main__":
    # --- IMPORTANT: Install pyautogui on your host machine ---
    # pip install pyautogui

    # --- Consider dependencies for PyAutoGUI ---
    # For Linux:
    # sudo apt-get install scrot # For screenshot functionality (Linux only)
    # sudo apt-get install python3-tk python3-dev # For cross-platform support of message boxes (optional)

    print("--- Starting Host Controller ---")
    try:
        start_server()
    except KeyboardInterrupt:
        print("\nHost Controller: Server stopped by user (Ctrl+C).")
    except Exception as e:
        print(f"Host Controller: An unexpected error occurred: {e}", file=sys.stderr)
    finally:
        print("--- Host Controller Finished ---")
import socket
import pyautogui
import sys
import re

# --- Configuration Parameters ---
# HOST: Listen on all available network interfaces.
#       This allows connections from Docker containers (using host.docker.internal or host network mode).
HOST = '127.0.0.1'
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
    "open browser": lambda: (pyautogui.hotkey('ctrl', 'alt', 't'),
                             pyautogui.write('firefox'), # Adjust to your browser: 'google-chrome', 'brave-browser' etc.
                             pyautogui.press('enter')),
    "open terminal": lambda: pyautogui.hotkey('ctrl', 'alt', 't'),
    "open folder": lambda: pyautogui.hotkey('win', 'e'), # Super+E often opens file manager (Nautilus)
    "close application": lambda: pyautogui.hotkey('alt', 'f4'),
    "screenshot": lambda: pyautogui.press('printscreen'), # Full screen screenshot
    "lock computer": lambda: pyautogui.hotkey('ctrl', 'alt', 'l'),
    "minimize all windows": lambda: pyautogui.hotkey('win', 'd'), # Super+D (Windows key equivalent)
    "open task manager": lambda: pyautogui.hotkey('ctrl', 'shift', 'esc'),
    "show applications": lambda: pyautogui.press('win'), # Press Super key to open Activities overview/Applications

    # Media Control (often universal via media keys)
    "volume up": lambda: pyautogui.press('volumeup'),
    "volume down": lambda: pyautogui.press('volumedown'),
    "mute": lambda: pyautogui.press('volumemute'),
    "play pause": lambda: pyautogui.press('playpause'),
    "next track": lambda: pyautogui.press('nexttrack'),
    "previous track": lambda: pyautogui.press('prevtrack'),

    # Basic Navigation/Typing
    "scroll down": lambda: pyautogui.scroll(-500),
    "scroll up": lambda: pyautogui.scroll(500),
    "click": lambda: pyautogui.click(),
    "double click": lambda: pyautogui.doubleClick(),
    "right click": lambda: pyautogui.rightClick(),
    "enter": lambda: pyautogui.press('enter'),
    "backspace": lambda: pyautogui.press('backspace'),
    "type": lambda: print("Ready to receive text input..."), # Placeholder for commands that need further input

    # Added Common Keys for Navigation and Control
    "up": lambda: pyautogui.press('up'),         # Up Arrow Key
    "down": lambda: pyautogui.press('down'),       # Down Arrow Key
    "left": lambda: pyautogui.press('left'),       # Left Arrow Key
    "right": lambda: pyautogui.press('right'),      # Right Arrow Key
    "switch window": lambda: pyautogui.hotkey('alt', 'tab'), # Alt+Tab for switching applications
    "switch tab": lambda: pyautogui.hotkey('ctrl', 'tab'), # Ctrl+Tab for switching tabs in browsers/editors
    "switch tab back": lambda: pyautogui.hotkey('ctrl', 'shift', 'tab'), # Ctrl+Shift+Tab for reverse tab switching
    "page down": lambda: pyautogui.press('pagedown'), # Page Down
    "page up": lambda: pyautogui.press('pageup'),   # Page Up
    "go to start": lambda: pyautogui.press('home'),     # Home Key
    "go to end": lambda: pyautogui.press('end'),       # End Key
    "tab": lambda: pyautogui.press('tab'),       # Tab Key
    # You can add more complex sequences or prompts for user input
}

def execute_command(command_text: str):
    """
    Executes a PyAutoGUI action based on the recognized command text.
    Handles exact matches and simple "input text" commands.
    """
     # 1. 清理命令文本：轉換為小寫，移除所有非字母數字和非空格字符
    #    這會移除標點符號，但保留單詞之間的空格。
    cleaned_command_text = re.sub(r'[^\w\s]', '', command_text).strip().lower()

    # 2. 處理以 "type " 開頭的命令
    if cleaned_command_text.startswith("type "):
        # 對於 "type" 命令，我們不應該對後面要輸入的文本進行標點符號移除，
        # 因為輸入文本本身可能包含標點符號。
        # 因此，這裡直接從原始 command_text 中提取，並只轉換為小寫。
        original_command_text_lower = command_text.strip().lower()
        text_to_type = original_command_text_lower[len("type "):].strip()
        if text_to_type:
            print(f"Typing: '{text_to_type}'")
            pyautogui.write(text_to_type)
            print("Text typed successfully.")
        else:
            print("Command 'type' received, but no text provided.")
        return # Command handled, exit function

    # 3. 處理其他預定義命令
    # 現在使用清理後的命令文本進行匹配
    action = COMMAND_MAP.get(cleaned_command_text)
    if action:
        print(f"Executing command: '{cleaned_command_text}' (from original: '{command_text}')")
        try:
            action()
            print("Command executed successfully.")
        except Exception as e:
            print(f"Error executing command '{cleaned_command_text}': {e}", file=sys.stderr)
    else:
        print(f"Unknown command: '{cleaned_command_text}' (original: '{command_text}')")

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
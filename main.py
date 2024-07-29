from pynput import keyboard
from pynput.keyboard import Key, Controller
import pyperclip
import time
import httpx
from string import Template
import signal

controller = Controller()

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
OLLAMA_CONFIG = {"model": "mistral:7b-instruct-v0.3-q4_K_S",
                 "keep_alive": "5m",
                 "stream": False
                }

PROMPT_TEMPLATE = Template(
    """Fix all typos and casing and punctuation in this text, but preserve all new line characters:
    
    $text
    
    Return only the corrected text, don't include a preamble.
    """
)

print("Offline Text Autocorrector")
print("This script composed by @eRgo35")
print("Heavly Inspired by https://patloeber.com/typing-assistant-llm/")
print("-------------------------------")
print("Press F9 to fix the current line.")
print("Press F10 to fix the selection.")
print("Press Ctrl-C to exit.")

def fix_text(text):
    prompt = PROMPT_TEMPLATE.substitute(text=text)
    response = httpx.post(OLLAMA_ENDPOINT, 
                          json={"prompt": prompt, **OLLAMA_CONFIG}, 
                          headers={"Content-Type": "application/json"}, 
                          timeout=10)
    if response.status_code != 200:
        return None
    return response.json()["response"].strip()

def fix_current_line():
    controller.tap(Key.home)
    with controller.pressed(Key.shift):
        controller.tap(Key.end)
    
    fix_selection()
    

def fix_selection():
    with controller.pressed(Key.ctrl):
        controller.tap('c')
    
    time.sleep(0.01)
    text = pyperclip.paste()
    
    fixed_text = fix_text(text)
    
    pyperclip.copy(fixed_text)
    time.sleep(0.01)
    
    with controller.pressed(Key.ctrl):
        controller.tap('v')

def on_f9():
    fix_current_line()

def on_f10():
    fix_selection()

# used to detect f9 and f10 key value
# from pynput.keyboard import Key
# print(Key.f9.value, Key.f10.value)

with keyboard.GlobalHotKeys({
  '<65478>': on_f9,                           
  '<65479>': on_f10
}) as h:
    try:
        h.join()
    except KeyboardInterrupt:
        print("Ctrl-c was pressed. Exiting...")
        exit(0)

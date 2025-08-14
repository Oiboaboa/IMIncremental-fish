# cd 
# python macro.py


import mss
import numpy as np
from pynput.mouse import Controller, Button
import time
import keyboard
import threading

mouse = Controller()

line_color = np.array([148, 148, 148])  # BGR
color_tolerance = 10

block_x, block_y = 956, 981
block_color_target = np.array([36, 67, 242])  # BGR
block_color_tolerance = 20

running = False
program_running = True
blocked = False  # Shared status between threads

def get_pixel_color(sct, x, y):
    monitor = {"top": y, "left": x, "width": 1, "height": 1}
    img = np.array(sct.grab(monitor))
    return img[0, 0, :3]

def colors_close(c1, c2, tolerance):
    return np.all(np.abs(c1 - c2) <= tolerance)

def block_check_loop():
    global blocked, program_running
    with mss.mss() as sct:
        while program_running:
            block_color = get_pixel_color(sct, block_x, block_y)
            blocked = colors_close(block_color, block_color_target, block_color_tolerance)
            
            # Se não está bloqueado, espera 0.02s para próxima verificação
            if not blocked:
                time.sleep(0.01)


def line_check_loop():
    global running, program_running, blocked
    with mss.mss() as sct:
        monitor = {"top": 864, "left": 699, "width": 522, "height": 1}
        while program_running:
            if not running or blocked:
                time.sleep(0.01)
                continue

            img = np.array(sct.grab(monitor))
            line = img[0]

            diffs = np.abs(line[:, :3] - line_color)
            mask = np.all(diffs <= color_tolerance, axis=1)
            line_visible = np.any(mask)

            if not line_visible:
                # Line disappeared and not blocked → Click
                for _ in range(8):
                    mouse.click(Button.left)
                    time.sleep(0.01)
                
                time.sleep(0.6)
                    


            time.sleep(0)

def toggle_running():
    global running
    running = not running
    print("Macro ACTIVE" if running else "Macro PAUSED")

def exit_program():
    global program_running
    program_running = False
    print("Exiting...")

keyboard.add_hotkey('f3', toggle_running)
keyboard.add_hotkey('f4', exit_program)

print("Press F3 to start/pause.")
print("Press F4 to exit.")

# Start both threads
threading.Thread(target=block_check_loop, daemon=True).start()
threading.Thread(target=line_check_loop, daemon=True).start()

keyboard.wait('f4')

import sys
# Create a monkey patch for pygame.display.flip to exit after 10 frames
import pygame
import threading
import time
import os

def kill_if_hung():
    time.sleep(10)
    print("HUNG DETECTED! Printing stack trace:")
    import traceback, sys
    for thread_id, frame in sys._current_frames().items():
        print(f"Thread {thread_id}:")
        traceback.print_stack(frame)
    os._exit(1)

threading.Thread(target=kill_if_hung, daemon=True).start()

# Load game
with open('code/game.py', 'r') as f:
    code = f.read()

# Replace event loop to simulate zoom out rapidly
code = code.replace('for event in pygame.event.get():', 'zoom *= 0.8\n        for event in pygame.event.get():')

# we don't want to actually launch the main loop fully indefinitely, just 100 frames
code = code.replace('while running:', 'frame_count = 0\n    while running:\n        frame_count += 1\n        print(f"Frame {frame_count}, zoom={zoom}")\n        if frame_count > 100:\n            sys.exit(0)\n')

exec(code)

import math
import time

L = 1000
H = 600
zoom = 0.001
world_x = 0
world_y = 0
offset_shake_x = 0
offset_shake_y = 0

OCEAN_ZONES = [
    (-150000, -50000), # Océan Ouest (100km de large)
    (100000, 150000)   # Océan Est (50km de large)
]

def s(val):
    return int(val)

def test():
    for (ox_start, ox_end) in OCEAN_ZONES:
        vis_start = (ox_start - L/2 - offset_shake_x) / zoom + world_x
        vis_end = (ox_end + L/2 + offset_shake_x) / zoom + world_x
        
        screen_ox_start = (ox_start - world_x) * zoom + L/2 + offset_shake_x
        screen_ox_end = (ox_end - world_x) * zoom + L/2 + offset_shake_x
        
        print(f"Ocean {ox_start} to {ox_end}: screen {screen_ox_start} to {screen_ox_end}")
        
        if screen_ox_end > -100 and screen_ox_start < L + 100:
            pts_ocean = [(max(-100, screen_ox_start), H)]
            
            step_x = 20 if zoom > 0.2 else 50
            for cx in range(int(max(-100, screen_ox_start)), int(min(L + 200, screen_ox_end)), step_x):
                wx_vo = (cx - L/2 - offset_shake_x) / zoom + world_x
                vague_y = math.sin((wx_vo * 0.05) + time.time() * 2) * 5 * zoom + math.cos((wx_vo * 0.02) + time.time() * 1.5) * 8 * zoom
                cy_vo = (vague_y - world_y) * zoom + (H // 2) + offset_shake_y
                pts_ocean.append((cx, cy_vo))
                
            last_ocean_cy = pts_ocean[-1][1]
            print(f"Computed {len(pts_ocean)} points")

test()

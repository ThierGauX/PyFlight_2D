import math
import random

explosions = []
args_no_particles = False
world_x = 1000
world_y = -500
vx = 50
vy = 10

def spawn_explosion(x, y, vx, vy):
    if args_no_particles: return
    for _ in range(60): # 60 particules
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(10, 50)
        p_vx = math.cos(angle) * speed + (vx * 0.3)
        p_vy = math.sin(angle) * speed + (vy * 0.3)
        life = random.uniform(0.5, 1.5)
        color = random.choice([(255,50,0), (255,100,0), (255,200,0), (80,80,80), (40,40,40)])
        explosions.append([x, y, p_vx, p_vy, life, life, color])

spawn_explosion(world_x, world_y, vx, vy)

for i in range(10):
    p = explosions[0]
    p[0] += p[2] * (1.0/60.0)
    p[1] += p[3] * (1.0/60.0)
    p[3] += 0.12 * 2
    p[4] -= 0.02
    
    px = (p[0] - world_x) * 1.0 + 1200//2 + 0
    py = (p[1] - world_y) * 1.0 + 700//2 + 0
    
    print(f"Step {i}: p=({p[0]:.1f}, {p[1]:.1f}) -> px={px:.1f}, py={py:.1f}")

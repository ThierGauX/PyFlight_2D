import pygame
pygame.init()
fenetre = pygame.display.set_mode((800, 600))
explosions = []
explosions.append([400, 300, 0, 0, 1.5, 1.5, (255,100,0)])

clock = pygame.time.Clock()
running = True
world_x, world_y = 0, 0
zoom = 1.0
L, H = 800, 600
offset_shake_x, offset_shake_y = 0, 0

frames = 0
while running and frames < 120:
    fenetre.fill((0, 0, 0))
    for p in explosions:
        p[0] += p[2] * (1.0/60.0)
        p[1] += p[3] * (1.0/60.0)
        p[3] += 0.12 * 2
        p[4] -= 0.02
        
        if p[4] > 0:
            px = (p[0] - world_x) * zoom + L//2 + offset_shake_x
            py = (p[1] - world_y) * zoom + H//2 + offset_shake_y
            
            if px > -200 and px < L+200 and py > -200 and py < H+200:
                ratio_vie = p[4] / p[5]
                radius = int(30 * (1 - ratio_vie) * zoom) + 2
                alpha = int(255 * ratio_vie)
                
                s_exp = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                col = p[6]
                if ratio_vie < 0.5: col = (40, 40, 40)
                
                pygame.draw.circle(s_exp, col + (alpha,), (radius, radius), radius)
                fenetre.blit(s_exp, (px - radius, py - radius))
                print(f"Frame {frames}: Drawn circle at {px}, {py} with r={radius}, A={alpha} color={col}")

    pygame.display.flip()
    frames += 1
    clock.tick(60)

pygame.quit()

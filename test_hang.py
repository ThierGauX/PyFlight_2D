import pygame
pygame.init()
fen = pygame.display.set_mode((100, 100))
print("Drawing rect")
pygame.draw.polygon(fen, (255, 0, 0), [(50, 50), (60, 50), (60, 50), (50, 50)])
print("Done rect")

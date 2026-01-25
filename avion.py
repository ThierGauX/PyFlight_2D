import pygame


pygame.init()
fenetre = pygame.display.set_mode((600, 400))
avion = pygame.Rect(100, 200, 50, 30) 


while True:
    
    if pygame.event.peek(pygame.QUIT):
        break

    touches = pygame.key.get_pressed()
    if touches[pygame.K_RIGHT]: avion.x += 5
    if touches[pygame.K_LEFT]:  avion.x -= 5
    if touches[pygame.K_UP]:    avion.y -= 5
    if touches[pygame.K_DOWN]:  avion.y += 5

    
    fenetre.fill("skyblue")              
    pygame.draw.rect(fenetre, "red", avion)
    pygame.display.flip()                 

    
    pygame.time.Clock().tick(60)

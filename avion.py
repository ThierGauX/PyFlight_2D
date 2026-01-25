import pygame
import os  


pygame.init()


DOSSIER_COURANT = os.path.dirname(__file__)

largeur, hauteur = 600, 400
fenetre = pygame.display.set_mode((largeur, hauteur))


chemin_image = os.path.join(DOSSIER_COURANT, "fond_ecran.jpg")
fond = pygame.image.load(chemin_image)
fond = pygame.transform.scale(fond, (largeur, hauteur))



avion = pygame.Rect(100, 200, 50, 30) 
horloge = pygame.time.Clock()

while True:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    # Mouvements
    touches = pygame.key.get_pressed()
    if touches[pygame.K_RIGHT]: avion.x += 5
    if touches[pygame.K_LEFT]:  avion.x -= 5
    if touches[pygame.K_UP]:    avion.y -= 5
    if touches[pygame.K_DOWN]:  avion.y += 5

   
    fenetre.blit(fond, (0, 0))
    
    
    pygame.draw.rect(fenetre, "red", avion)
    
    pygame.display.flip()
    horloge.tick(60)

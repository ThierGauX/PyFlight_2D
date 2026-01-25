import pygame

pygame.init()
fenetre = pygame.display.set_mode((600, 400))
avion = pygame.Rect(300, 200, 40, 20) # x, y, largeur, hauteur

while True:
    if pygame.event.peek(pygame.QUIT): break # Quitter si on ferme la fenêtre

    # Mouvement ultra-rapide : (Touche Droite - Touche Gauche) donne la direction
    touches = pygame.key.get_pressed()
    avion.x += (touches[pygame.K_RIGHT] - touches[pygame.K_LEFT]) * 5
    avion.y += (touches[pygame.K_DOWN] - touches[pygame.K_UP]) * 5

    fenetre.fill("skyblue")            # Fond bleu
    pygame.draw.rect(fenetre, "white", avion) # Dessine l'avion en blanc
    pygame.display.flip()              # Met à jour l'image
    pygame.time.Clock().tick(60)       # 60 images par seconde
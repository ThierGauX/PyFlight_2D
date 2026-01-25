import pygame

# 1. On prépare le jeu
pygame.init()
fenetre = pygame.display.set_mode((600, 400))
avion = pygame.Rect(100, 200, 50, 30) # Un rectangle (x, y, largeur, hauteur)

# 2. La boucle du jeu (le moteur)
while True:
    # On regarde si l'utilisateur veut fermer la fenêtre
    if pygame.event.peek(pygame.QUIT):
        break

    # On regarde sur quelles touches on appuie
    touches = pygame.key.get_pressed()
    if touches[pygame.K_RIGHT]: avion.x += 5
    if touches[pygame.K_LEFT]:  avion.x -= 5
    if touches[pygame.K_UP]:    avion.y -= 5
    if touches[pygame.K_DOWN]:  avion.y += 5

    # On dessine tout
    fenetre.fill("skyblue")               # On peint le fond en bleu
    pygame.draw.rect(fenetre, "red", avion) # On dessine l'avion en rouge
    pygame.display.flip()                 # On montre le dessin à l'écran

    # On attend un tout petit peu (60 images par seconde)
    pygame.time.Clock().tick(60)

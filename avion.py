import pygame

# 1. Initialisation
pygame.init()
largeur, hauteur = 600, 400
fenetre = pygame.display.set_mode((largeur, hauteur))
pygame.display.set_caption("Mon Jeu Futuriste")

# 2. Chargement du fond d'écran
# On charge l'image et on la redimensionne à la taille de la fenêtre
fond = pygame.image.load("fond_ecran.jpg")
fond = pygame.transform.scale(fond, (largeur, hauteur))

avion = pygame.Rect(100, 200, 50, 30) 
horloge = pygame.time.Clock()

while True:
    # Gestion des événements
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

    # --- DESSIN ---
    
    # 3. On remplace fenetre.fill("skyblue") par l'image de fond
    # On dessine le fond en haut à gauche (0, 0)
    fenetre.blit(fond, (0, 0))
    
    # On dessine le joueur par-dessus
    pygame.draw.rect(fenetre, "red", avion)
    
    pygame.display.flip()
    horloge.tick(60)

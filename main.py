import pygame
import math
import os
import random

pygame.init()

# --- FENETRE ---
L, H = 1200, 700
fenetre = pygame.display.set_mode((L, H))
pygame.display.set_caption("Simulateur - Speed FX & Smooth Auto-Pilot")

# --- CHARGEMENT IMAGES ---
dossier = os.path.dirname(__file__)
try:
    chemin_arret = os.path.join(dossier, "avion_arret.jpg")
    img_avion_normal = pygame.image.load(chemin_arret).convert() 
    chemin_marche = os.path.join(dossier, "avion_marche.jpg")
    img_avion_feu = pygame.image.load(chemin_marche).convert()
    
    img_avion_normal.set_colorkey((255, 255, 255))
    img_avion_feu.set_colorkey((255, 255, 255))
    img_avion_normal = pygame.transform.scale(img_avion_normal, (90, 35))
    img_avion_feu = pygame.transform.scale(img_avion_feu, (90, 35))
    images_ok = True
except Exception as e:
    print(f"Erreur image: {e}")
    images_ok = False

# --- COULEURS ---
COULEUR_CIEL_HAUT = (5, 15, 30)    
COULEUR_CIEL_BAS = (80, 120, 180) 
COULEUR_SOL = (40, 50, 40)         
COULEUR_HUD = (0, 255, 100)          
COULEUR_ALERTE = (255, 50, 0)
COULEUR_AUTO = (0, 150, 255)

police = pygame.font.SysFont("consolas", 18, bold=True)
police_grosse = pygame.font.SysFont("consolas", 40, bold=True)

# --- VARIABLES ---
world_y = 0      
world_x = 0
vx, vy = 0, 0
angle = 0        
vitesse_rotation_actuelle = 0 
en_decrochage = False 
altitude = 0 
vitesse_kph = 0
postcombustion = False 
pilote_auto_actif = False

# Gestion des particules (Effet de vitesse)
particules = []
for _ in range(50): # 50 traits de vent
    particules.append([random.randint(0, L), random.randint(0, H), random.randint(5, 15)])

# --- PERFORMANCES ---
V_DECOLLAGE = 220
V_DECROCHAGE = 160
V_VNE = 2200 

# --- PHYSIQUE ---
GRAVITE = 0.20             
PUISSANCE_MOTEUR = 1.3     
FRICTION_AIR = 0.997       
FRICTION_VERTICALE = 0.95  
ACCEL_ROTATION = 0.2       
MAX_ROTATION = 3.0         
FRICTION_ROTATION = 0.90   
COEFF_PORTANCE = 0.0035    

horloge = pygame.time.Clock()

def obtenir_couleur_ciel(alt):
    plafond = 15000 
    ratio = min(max(alt, 0), plafond) / plafond
    r = int(COULEUR_CIEL_BAS[0] * (1 - ratio) + COULEUR_CIEL_HAUT[0] * ratio)
    g = int(COULEUR_CIEL_BAS[1] * (1 - ratio) + COULEUR_CIEL_HAUT[1] * ratio)
    b = int(COULEUR_CIEL_BAS[2] * (1 - ratio) + COULEUR_CIEL_HAUT[2] * ratio)
    return (r, g, b)

def dessiner_jauge_vitesse(surface, x, y, vitesse):
    """Dessine un cadran analogique (le moyeu)"""
    rayon = 60
    # Fond du cadran
    pygame.draw.circle(surface, (0, 20, 0), (x, y), rayon)
    pygame.draw.circle(surface, COULEUR_HUD, (x, y), rayon, 2)
    
    # Graduations
    for i in range(0, 360, 30):
        rad = math.radians(i)
        x1 = x + math.cos(rad) * (rayon - 10)
        y1 = y + math.sin(rad) * (rayon - 10)
        x2 = x + math.cos(rad) * rayon
        y2 = y + math.sin(rad) * rayon
        pygame.draw.line(surface, COULEUR_HUD, (x1, y1), (x2, y2), 1)

    # Aiguille (Moyeu tournant)
    # 0 km/h = -135 degrés, 2500 km/h = +135 degrés
    ratio_vitesse = min(vitesse, 2500) / 2500
    angle_aiguille = -135 + (ratio_vitesse * 270)
    rad_aiguille = math.radians(angle_aiguille)
    
    x_fin = x + math.cos(rad_aiguille) * (rayon - 15)
    y_fin = y + math.sin(rad_aiguille) * (rayon - 15)
    
    pygame.draw.line(surface, (255, 50, 50), (x, y), (x_fin, y_fin), 3)
    pygame.draw.circle(surface, (200, 200, 200), (x, y), 5) # Le centre du moyeu
    
    # Texte Vitesse
    txt = police.render(f"{int(vitesse)}", True, (255, 255, 255))
    surface.blit(txt, (x - 15, y + 20))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    touches = pygame.key.get_pressed()

    # --- 1. COMMANDES & PILOTE AUTO ---
    
    target_rotation = 0
    action_manche = False 
    pilote_auto_actif = False

    if touches[pygame.K_UP]:    
        target_rotation = -MAX_ROTATION
        action_manche = True
    if touches[pygame.K_DOWN]:  
        target_rotation = MAX_ROTATION
        action_manche = True
    
    if action_manche:
        # Inertie manuelle
        if target_rotation > vitesse_rotation_actuelle:
            vitesse_rotation_actuelle += ACCEL_ROTATION
        elif target_rotation < vitesse_rotation_actuelle:
            vitesse_rotation_actuelle -= ACCEL_ROTATION
    else:
        # --- PILOTE AUTOMATIQUE FLUIDIFIÉ ---
        vitesse_rotation_actuelle *= FRICTION_ROTATION
        
        if vitesse_kph > V_DECOLLAGE and not en_decrochage:
            pilote_auto_actif = True
            
            # Au lieu de corriger l'angle directement, on calcule une CIBLE d'angle
            # Si vy > 0 (descend), on veut un angle positif.
            angle_cible = vy * 2.0 # Gain proportionnel
            
            # Limite de l'angle cible pour ne pas cabrer violemment
            angle_cible = max(-15, min(15, angle_cible))
            
            # LISSAGE (FLUIDIFICATION) :
            # On déplace l'angle actuel vers l'angle cible doucement (5% par frame)
            # C'est la fonction "Lerp" (Linear Interpolation)
            angle += (angle_cible - angle) * 0.05
            
    angle += vitesse_rotation_actuelle

    # MOTEUR
    postcombustion = False
    if touches[pygame.K_RIGHT]:
        postcombustion = True
        rad = math.radians(angle)
        vx += math.cos(rad) * PUISSANCE_MOTEUR
        vy -= math.sin(rad) * PUISSANCE_MOTEUR

    # --- 2. PHYSIQUE ---
    altitude = -world_y 
    vitesse_totale = math.sqrt(vx**2 + vy**2)
    vitesse_kph = int(vitesse_totale * 15)
    
    if vitesse_kph < V_DECROCHAGE and altitude > 10:
        en_decrochage = True
    elif vitesse_kph > V_DECROCHAGE + 40:
        en_decrochage = False

    vy += GRAVITE

    portance = 0
    if not en_decrochage:
        if vitesse_kph > 100: 
            angle_attaque = abs(angle)
            if angle_attaque > 5:
                perte = (angle_attaque * 0.0004)
                vx *= (1.0 - perte)
                vy *= (1.0 - perte)
            if angle > 0:
                portance = abs(vx) * (angle * COEFF_PORTANCE)
            vx *= FRICTION_AIR
            vy *= FRICTION_VERTICALE
    else:
        vx *= 0.99
        vy *= 0.99
        if angle > 0: angle -= 0.4 

    vy -= portance
    world_x += vx
    world_y += vy
    
    if -world_y <= 0:
        world_y = 0
        en_decrochage = False 
        if vy > 0: 
            vy = -vy * 0.15 
            vx *= 0.98 
    altitude = -world_y

    # --- 3. DESSIN ---
    fenetre.fill(obtenir_couleur_ciel(altitude))
    
    # A. EFFET DE VITESSE (PARTICULES DE VENT)
    # Plus on va vite, plus les lignes sont longues et transparentes
    coeff_vitesse = max(0, vitesse_kph - 100) / 1000 # 0 à basse vitesse, augmente après
    
    if coeff_vitesse > 0:
        for p in particules:
            # p[0]=x, p[1]=y, p[2]=longueur_base
            
            # Mouvement: Elles reculent selon la vitesse de l'avion
            p[0] -= (vitesse_kph * 0.15) 
            
            # Reset si sort de l'écran
            if p[0] < 0:
                p[0] = L + random.randint(0, 200)
                p[1] = random.randint(0, H)
            
            # Dessin
            longueur = p[2] + (vitesse_kph * 0.1) # S'allonge avec la vitesse
            epaisseur = 1 if vitesse_kph < 1000 else 2
            
            # Transparence (Simulée par nuance de gris)
            gris = min(255, int(50 + coeff_vitesse * 100))
            couleur_vent = (gris, gris, gris)
            
            pygame.draw.line(fenetre, couleur_vent, (p[0], p[1]), (p[0] - longueur, p[1]), epaisseur)

    # B. Sol
    offset_sol = int(world_x % 150)
    pos_sol_y = (H // 2) + altitude
    pygame.draw.rect(fenetre, COULEUR_SOL, (-100, pos_sol_y + 15, L+200, H))
    for i in range(-150, L + 150, 150):
        x_ligne = i - offset_sol
        pygame.draw.line(fenetre, (70, 80, 70), (x_ligne, pos_sol_y + 15), (x_ligne + 80, pos_sol_y + 15), 4)

    # C. Avion
    if images_ok:
        img_actuelle = img_avion_feu if postcombustion else img_avion_normal
        avion_rot = pygame.transform.rotate(img_actuelle, angle)
        rect_rot = avion_rot.get_rect(center=(L // 2, H // 2))
        fenetre.blit(avion_rot, rect_rot)
    else:
        pts = [(L//2+30, H//2), (L//2-10, H//2-10), (L//2-10, H//2+10)]
        pygame.draw.polygon(fenetre, (150, 150, 150), pts)

    # D. HUD & CADRAN
    vario = -vy * 1.5 
    mach = vitesse_kph / 1225.0 
    
    # Affichage du "Moyeu" (Cadran Vitesse) en bas à gauche
    dessiner_jauge_vitesse(fenetre, 80, H - 80, vitesse_kph)

    # Infos HUD Texte
    infos = [
        f"ALT  : {int(altitude)} FT", 
        f"MACH : {mach:.2f}",
        f"V/S  : {vario:.1f}",
        f"AUTO : {'ON' if pilote_auto_actif else 'OFF'}"
    ]

    x_base = L - 200
    y_base = H - 200
    
    # Petit fond pour le HUD texte
    s = pygame.Surface((190, 120))
    s.set_alpha(80)
    s.fill((0, 0, 0))
    fenetre.blit(s, (x_base - 10, y_base - 10))

    for i, ligne in enumerate(infos):
        c_txt = COULEUR_HUD
        if "AUTO" in ligne and pilote_auto_actif: c_txt = COULEUR_AUTO
        fenetre.blit(police.render(ligne, True, c_txt), (x_base, y_base + i*25))

    msg = ""
    c_msg = COULEUR_HUD
    if en_decrochage:
        msg = "[ STALL ]"
        c_msg = COULEUR_ALERTE
    elif pilote_auto_actif and abs(vy) < 1.0 and altitude > 50:
        msg = "FLIGHT PATH STABLE" 
        c_msg = COULEUR_AUTO

    if msg:
        y_pos = H//2 - 120
        txt_msg = police_grosse.render(msg, True, c_msg)
        rect_msg = txt_msg.get_rect(center=(L//2, y_pos))
        fenetre.blit(txt_msg, rect_msg)

    pygame.display.flip()
    horloge.tick(60)

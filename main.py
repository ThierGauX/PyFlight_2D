import pygame
import math

pygame.init()

# --- FENETRE ---
L, H = 1200, 700
fenetre = pygame.display.set_mode((L, H))
pygame.display.set_caption("Simulateur - Accélération Corrigée")

# --- COULEURS ---
COULEUR_CIEL_SOL = (190, 200, 210) 
COULEUR_CIEL_ESPACE = (20, 30, 40) 
COULEUR_SOL = (100, 115, 100)      
COULEUR_TEXTE = (10, 10, 10)       
COULEUR_AVION = (240, 240, 240)    
COULEUR_ALERTE = (220, 50, 50)     
COULEUR_INFO = (0, 80, 180)       

police = pygame.font.SysFont("consolas", 20, bold=True)
police_grosse = pygame.font.SysFont("consolas", 40, bold=True)

# --- AVION ---
avion_surf = pygame.Surface((60, 20), pygame.SRCALPHA)
avion_surf.fill(COULEUR_AVION)
pygame.draw.rect(avion_surf, (50, 50, 50), (40, 5, 20, 10)) 

# --- VARIABLES ---
world_y = 0      
world_x = 0
vx, vy = 0, 0
angle = 0        
en_decrochage = False 
altitude = 0 
vitesse_kph = 0

# --- DONNÉES DE PERFORMANCE ---
V_DECOLLAGE = 79
V_DECROCHAGE = 89
V_VNE = 302

# --- RÉGLAGES PHYSIQUES (CORRIGÉS) ---
GRAVITE = 0.15           
PUISSANCE_MOTEUR = 0.25  # Assez puissant pour décoller
FRICTION_ROUES = 0.995   # Ça roule bien au sol (plus de frein à main)
FRICTION_AIR = 0.99      # Freine l'avion en l'air pour ne pas dépasser 300 km/h
FRICTION_VERTICALE = 0.92 
VITESSE_ROTATION = 0.5   

COEFF_PORTANCE = 0.0035   

horloge = pygame.time.Clock()

def obtenir_couleur_ciel(alt):
    plafond = 6000
    ratio = min(max(alt, 0), plafond) / plafond
    r = int(COULEUR_CIEL_SOL[0] * (1 - ratio) + COULEUR_CIEL_ESPACE[0] * ratio)
    g = int(COULEUR_CIEL_SOL[1] * (1 - ratio) + COULEUR_CIEL_ESPACE[1] * ratio)
    b = int(COULEUR_CIEL_SOL[2] * (1 - ratio) + COULEUR_CIEL_ESPACE[2] * ratio)
    return (r, g, b)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    touches = pygame.key.get_pressed()

    # --- 1. COMMANDES INVERSÉES ---
    if touches[pygame.K_UP]:    
        angle -= VITESSE_ROTATION 
    if touches[pygame.K_DOWN]:  
        angle += VITESSE_ROTATION 
    
    # MOTEUR
    if touches[pygame.K_RIGHT]:
        rad = math.radians(angle)
        # Légère perte de puissance en forte montée
        facteur_pente = 1.0
        if angle > 10: facteur_pente = 0.9
        
        vx += math.cos(rad) * PUISSANCE_MOTEUR * facteur_pente
        vy -= math.sin(rad) * PUISSANCE_MOTEUR * facteur_pente

    # --- 2. CALCULS ---
    altitude = -world_y 
    vitesse_totale = math.sqrt(vx**2 + vy**2)
    vitesse_kph = int(vitesse_totale * 15)
    
    # --- 3. DÉCROCHAGE ---
    if (abs(angle) > 25) or (vitesse_kph < V_DECROCHAGE and altitude > 5):
        en_decrochage = True
    elif abs(angle) < 10 and vitesse_kph > V_DECROCHAGE + 10:
        en_decrochage = False 

    # --- 4. PHYSIQUE ---
    vy += GRAVITE

    portance_actuelle = 0
    if not en_decrochage:
        # En l'air (ou vitesse suffisante pour porter)
        if vitesse_kph > (V_DECOLLAGE - 5): 
            if angle > 0:
                portance_actuelle = abs(vx) * (angle * COEFF_PORTANCE)
            
            vx *= FRICTION_AIR # Friction de l'air
            vy *= FRICTION_VERTICALE
        else:
            # AU SOL (ROULAGE)
            # C'était ici le problème : on utilise une friction douce maintenant
            vx *= FRICTION_ROUES 
    else:
        # Chute
        vx *= 0.99
        vy *= 0.98
        if angle > 0: angle -= 0.3

    vy -= portance_actuelle
    world_x += vx
    world_y += vy
    
    # --- 5. SOL ---
    altitude = -world_y
    if altitude <= 0:
        altitude = 0
        world_y = 0
        en_decrochage = False 
        if vy > 0: 
            vy = -vy * 0.1 
            # Si on touche le sol, on applique aussi la friction des roues
            vx *= FRICTION_ROUES 

    # --- 6. DESSIN ---
    fenetre.fill(obtenir_couleur_ciel(altitude))

    # Sol
    pos_sol_y = (H // 2) + altitude
    pygame.draw.rect(fenetre, COULEUR_SOL, (-100, pos_sol_y + 15, L+200, H))
    pygame.draw.line(fenetre, (80, 90, 80), (0, pos_sol_y + 15), (L, pos_sol_y + 15), 2)

    # Avion 
    couleur_navion = COULEUR_ALERTE if en_decrochage else COULEUR_AVION
    if vitesse_kph > V_VNE: couleur_navion = (255, 100, 0)

    avion_dessin = avion_surf.copy()
    avion_dessin.fill(couleur_navion)
    avion_rot = pygame.transform.rotate(avion_dessin, angle)
    rect_center = avion_rot.get_rect(center=(L//2, H//2))
    fenetre.blit(avion_rot, rect_center)

    # --- HUD ---
    vario = -vy * 1.5 
    
    infos = [
        f"ALTITUDE   : {int(altitude)} m",
        f"VARIO      : {vario:.1f} m/s", 
        f"VITESSE    : {vitesse_kph} km/h",
        f"ANGLE      : {angle:.1f}°"
    ]

    x_base = L - 280
    y_base = H - 180
    
    for i, ligne in enumerate(infos):
        c_txt = COULEUR_TEXTE
        if "VARIO" in ligne and abs(vario) > 0.5: c_txt = (0, 100, 0) if vario > 0 else (150, 50, 0)
        fenetre.blit(police.render(ligne, True, c_txt), (x_base, y_base + i*25))

    # --- AIDES ---
    msg = ""
    c_msg = COULEUR_INFO
    
    if en_decrochage:
        msg = "!! DÉCROCHAGE !!"
        c_msg = COULEUR_ALERTE
   
    elif altitude < 5:
        if vitesse_kph < 70:
            msg = f"ROULEZ... ({vitesse_kph} km/h)"
            c_msg = (100, 100, 100)
        elif vitesse_kph < V_DECOLLAGE + 5:
            msg = "ROTATION (TIREZ DOUCEMENT)"
            c_msg = (200, 150, 0)

    if msg:
        txt_msg = police_grosse.render(msg, True, c_msg)
        rect_msg = txt_msg.get_rect(center=(L//2, H//2 - 100))
        fenetre.blit(txt_msg, rect_msg)

    pygame.display.flip()
    horloge.tick(60)

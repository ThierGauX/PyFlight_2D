import pygame
import math
import os
import random

pygame.init()
pygame.mixer.init() # Initialisation du son

# --- FENETRE ---
L, H = 1200, 700
fenetre = pygame.display.set_mode((L, H))
pygame.display.set_caption("Simulateur Pro - Audio & Zoom")

# --- CHARGEMENT RESSOURCES (IMAGES + SON) ---
dossier = os.path.dirname(__file__)
images_ok = False
sound_ok = False

# 1. Chargement Images
try:
    # On charge les .png (correspond à ton dossier)
    chemin_arret = os.path.join(dossier, "avion_arret.png")
    img_avion_normal_base = pygame.image.load(chemin_arret).convert_alpha()
    
    chemin_marche = os.path.join(dossier, "avion_marche.png")
    img_avion_feu_base = pygame.image.load(chemin_marche).convert_alpha()
    
    images_ok = True
    print("Images chargées avec succès !")
except Exception as e:
    print(f"ERREUR IMAGE : {e}")
    print("Vérifie que avion_arret.png est bien dans le même dossier que ce script.")

# 2. Chargement Son [CORRIGÉ MAJUSCULE]
try:
    # ATTENTION : J'ai mis "Moteur.ogg" avec une majuscule comme sur ta capture
    chemin_son = os.path.join(dossier, "Moteur.ogg")
    son_moteur = pygame.mixer.Sound(chemin_son)
    son_moteur.play(loops=-1)
    son_moteur.set_volume(0.4) 
    sound_ok = True
    print("Son chargé avec succès !")
except Exception as e:
    print(f"ERREUR SON : {e}")
    print("Vérifie que Moteur.ogg est bien dans le même dossier.")

# --- COULEURS ---
COULEUR_CIEL_HAUT = (5, 10, 25)    
COULEUR_CIEL_BAS = (100, 140, 200) 
COULEUR_SOL = (50, 60, 50)         
COULEUR_INSTRUMENT = (20, 20, 20)  
COULEUR_AIGUILLE = (200, 50, 50)
COULEUR_TEXTE = (255, 255, 255)
COULEUR_AUTO = (0, 180, 255)

police = pygame.font.SysFont("arial", 14, bold=True)
police_compteur = pygame.font.SysFont("arial", 12)
police_grosse = pygame.font.SysFont("arial", 30, bold=True)

# --- VARIABLES ---
world_y = 0      
world_x = 0
vx, vy = 0, 0
angle = 0        
vitesse_rotation_actuelle = 0 
en_decrochage = False 
altitude = 0 
vitesse_kph = 0
pilote_auto_actif = False

# VARIABLE DE ZOOM
zoom = 1.0          
zoom_cible = 1.0    

# --- PARTICULES ---
particules = []
for _ in range(40): 
    particules.append([random.randint(0, L), random.randint(0, H), random.uniform(0.5, 1.5), random.randint(1, 2)])

# --- PERFORMANCES ---
V_DECOLLAGE = 220
V_DECROCHAGE = 160
V_VNE = 2500 

# --- PHYSIQUE LOURDE ---
GRAVITE = 0.18             
PUISSANCE_MOTEUR = 1.0     
FRICTION_AIR = 0.998       
FRICTION_VERTICALE = 0.96  
ACCEL_ROTATION = 0.05      
MAX_ROTATION = 2.0         
FRICTION_ROTATION = 0.96   
COEFF_PORTANCE = 0.0018    
COEFF_TRAINEE_MONTEE = 0.002 

horloge = pygame.time.Clock()

def obtenir_couleur_ciel(alt):
    plafond = 15000 
    ratio = min(max(alt, 0), plafond) / plafond
    r = int(COULEUR_CIEL_BAS[0] * (1 - ratio) + COULEUR_CIEL_HAUT[0] * ratio)
    g = int(COULEUR_CIEL_BAS[1] * (1 - ratio) + COULEUR_CIEL_HAUT[1] * ratio)
    b = int(COULEUR_CIEL_BAS[2] * (1 - ratio) + COULEUR_CIEL_HAUT[2] * ratio)
    return (r, g, b)

def dessiner_anemometre(surface, x, y, vitesse):
    rayon = 70
    pygame.draw.circle(surface, (50, 50, 50), (x, y), rayon + 4)
    pygame.draw.circle(surface, COULEUR_INSTRUMENT, (x, y), rayon)
    
    for v in range(0, 3001, 250):
        ratio = v / 3000
        ang_rad = math.radians(135 + (ratio * 270))
        x1 = x + math.cos(ang_rad) * (rayon - 10)
        y1 = y + math.sin(ang_rad) * (rayon - 10)
        x2 = x + math.cos(ang_rad) * rayon
        y2 = y + math.sin(ang_rad) * rayon
        
        epaisseur = 2 if v % 1000 == 0 else 1
        col = (255, 255, 255) if v < V_VNE else (255, 0, 0)
        pygame.draw.line(surface, col, (x1, y1), (x2, y2), epaisseur)
        
        if v % 1000 == 0 and v != 0:
            lbl = police_compteur.render(str(v//1000), True, (200, 200, 200))
            xr = x + math.cos(ang_rad) * (rayon - 22) - 3
            yr = y + math.sin(ang_rad) * (rayon - 22) - 5
            surface.blit(lbl, (xr, yr))

    v_aff = min(vitesse, 3000)
    ratio_v = v_aff / 3000
    ang_aiguille = math.radians(135 + (ratio_v * 270))
    xa = x + math.cos(ang_aiguille) * (rayon - 15)
    ya = y + math.sin(ang_aiguille) * (rayon - 15)
    
    pygame.draw.line(surface, COULEUR_AIGUILLE, (x, y), (xa, ya), 3)
    pygame.draw.circle(surface, (100, 100, 100), (x, y), 5) 
    
    txt_spd = police.render(f"{int(vitesse)}", True, (255, 255, 255))
    rect_spd = txt_spd.get_rect(center=(x, y + 30))
    surface.blit(txt_spd, rect_spd)
    
    lbl = police_compteur.render("KPH x1000", True, (150, 150, 150))
    surface.blit(lbl, (x - 25, y - 30))

while True:
    dt = horloge.tick(60) / 1000.0 

    # --- GESTION DES ÉVÉNEMENTS ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEWHEEL:
            zoom_cible += event.y * 0.1 

    touches = pygame.key.get_pressed()

    # --- ZOOM ---
    zoom_cible = max(0.5, min(2.0, zoom_cible))
    zoom += (zoom_cible - zoom) * 0.1

    # --- COMMANDES ---
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
        if target_rotation > vitesse_rotation_actuelle:
            vitesse_rotation_actuelle += ACCEL_ROTATION
        elif target_rotation < vitesse_rotation_actuelle:
            vitesse_rotation_actuelle -= ACCEL_ROTATION
    else:
        vitesse_rotation_actuelle *= FRICTION_ROTATION
        # Pilote Auto
        if vitesse_kph > V_DECOLLAGE and not en_decrochage:
            pilote_auto_actif = True
            angle_cible = vy * 1.5
            angle_cible = max(-10, min(10, angle_cible))
            angle += (angle_cible - angle) * 0.04
            
    angle += vitesse_rotation_actuelle

    # --- MOTEUR & SON ---
    postcombustion = False
    if touches[pygame.K_RIGHT]:
        postcombustion = True
        rad = math.radians(angle)
        vx += math.cos(rad) * PUISSANCE_MOTEUR
        vy -= math.sin(rad) * PUISSANCE_MOTEUR
        
        # Le volume augmente en postcombustion
        if sound_ok: son_moteur.set_volume(1.0)
    else:
        # Volume normal
        if sound_ok: son_moteur.set_volume(0.4)

    # --- PHYSIQUE ---
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
                vx *= 0.999 
                vy *= 0.999
            
            if angle > 0:
                vx *= (1.0 - (angle * COEFF_TRAINEE_MONTEE))
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

    # --- DESSIN ---
    fenetre.fill(obtenir_couleur_ciel(altitude))
    
    # 1. PARTICULES
    if vitesse_kph > 50:
        for p in particules:
            p[0] -= (vitesse_kph * 0.05 * p[2]) * zoom 
            if p[0] < 0:
                p[0] = L + random.randint(0, 100)
                p[1] = random.randint(0, H)
            taille_visuelle = max(1, int(p[3] * zoom))
            col_p = (200, 200, 220) 
            pygame.draw.circle(fenetre, col_p, (int(p[0]), int(p[1])), taille_visuelle)

    # 2. SOL
    grid_gap = int(150 * zoom) 
    offset_sol = int(world_x % grid_gap)
    pos_sol_y = (H // 2) + (altitude * zoom) 

    if pos_sol_y < H:
        pygame.draw.rect(fenetre, COULEUR_SOL, (-100, pos_sol_y + 10, L+200, H))
        for i in range(-grid_gap, L + grid_gap, grid_gap):
            x_ligne = i - offset_sol
            pygame.draw.line(fenetre, (70, 80, 70), (x_ligne, pos_sol_y + 10), (x_ligne + (80*zoom), pos_sol_y + 10), max(1, int(4*zoom)))

    # 3. AVION
    if images_ok:
        img_actuelle = img_avion_feu_base if postcombustion else img_avion_normal_base
        new_w = int(90 * zoom)
        new_h = int(35 * zoom)
        img_scaled = pygame.transform.scale(img_actuelle, (new_w, new_h))
        avion_rot = pygame.transform.rotate(img_scaled, angle)
        rect_rot = avion_rot.get_rect(center=(L // 2, H // 2))
        fenetre.blit(avion_rot, rect_rot)
    else:
        # Fallback (Triangle) si pas d'image
        pts = [(L//2+(30*zoom), H//2), (L//2-(10*zoom), H//2-(10*zoom)), (L//2-(10*zoom), H//2+(10*zoom))]
        pygame.draw.polygon(fenetre, (150, 150, 150), pts)

    # 4. HUD
    dessiner_anemometre(fenetre, 100, H - 100, vitesse_kph)

    vario = -vy * 1.5 
    mach = vitesse_kph / 1225.0 
    
    infos = [
        f"ALT  : {int(altitude)} FT", 
        f"MACH : {mach:.2f}",
        f"ZOOM : x{zoom:.2f}",
        f"AUTO : {'ON' if pilote_auto_actif else 'OFF'}"
    ]

    x_base = L - 200
    y_base = H - 150
    s = pygame.Surface((180, 110))
    s.set_alpha(100)
    s.fill((0, 0, 0))
    fenetre.blit(s, (x_base - 10, y_base - 10))
    pygame.draw.rect(fenetre, (100, 100, 100), (x_base - 10, y_base - 10, 180, 110), 2)

    for i, ligne in enumerate(infos):
        c_txt = COULEUR_TEXTE
        if "AUTO" in ligne and pilote_auto_actif: c_txt = COULEUR_AUTO
        fenetre.blit(police.render(ligne, True, c_txt), (x_base, y_base + i*25))

    msg = ""
    c_msg = COULEUR_AUTO
    if en_decrochage:
        msg = "!! STALL !!"
        c_msg = (255, 0, 0)
    elif pilote_auto_actif and abs(vy) < 1.0 and altitude > 50:
        msg = "STABLE"

    if msg:
        txt_msg = police_grosse.render(msg, True, c_msg)
        rect_msg = txt_msg.get_rect(center=(L//2, H//2 - 120))
        fenetre.blit(txt_msg, rect_msg)

    pygame.display.flip()

import pygame
import math
import os
import random
import datetime # Pour l'heure réelle

# --- INITIALISATION ---
pygame.init()
try:
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.mixer.init()
except: 
    print("Erreur initialisation module son")

# --- FENETRE ---
L, H = 1200, 700
fenetre = pygame.display.set_mode((L, H))
pygame.display.set_caption("Simulateur - Stabilisateur Actif")

# --- RESSOURCES ---
dossier = os.path.dirname(os.path.abspath(__file__))
images_ok = False
son_moteur = None
son_alarme = None

# 1. IMAGES
try:
    path_arret = os.path.join(dossier, "avion_arret.png")
    path_marche = os.path.join(dossier, "avion_marche.png")
    
    img_avion_normal_base = pygame.image.load(path_arret).convert_alpha()
    img_avion_feu_base = pygame.image.load(path_marche).convert_alpha()
    images_ok = True
except Exception as e:
    print(f"Erreur Images: {e}")

# 2. SONS
chemins_moteur = ["moteur.mp3", "moteur.wav", "moteur_neuf.wav", "Moteur.ogg"]
for nom in chemins_moteur:
    p = os.path.join(dossier, nom)
    if os.path.exists(p):
        try:
            son_moteur = pygame.mixer.Sound(p)
            son_moteur.set_volume(0.4)
            break
        except: pass

try:
    p_alarme = os.path.join(dossier, "alarme_decrochage.wav")
    if os.path.exists(p_alarme):
        son_alarme = pygame.mixer.Sound(p_alarme)
        son_alarme.set_volume(0.5)
except: pass


# --- PALETTE GRAPHIQUE ---
# Couleurs de base (définitions)
C_CIEL_JOUR_BAS = (135, 206, 235)
C_CIEL_JOUR_HAUT = (10, 20, 40)
C_CIEL_NUIT_BAS = (20, 20, 40)
C_CIEL_NUIT_HAUT = (0, 0, 10)
C_CIEL_COUCHER_BAS = (255, 100, 50)
C_CIEL_COUCHER_HAUT = (50, 20, 40)

C_SOL_JOUR_FONCE = (20, 60, 20)
C_SOL_JOUR_CLAIR = (50, 120, 50)
C_SOL_NUIT_FONCE = (5, 15, 5)
C_SOL_NUIT_CLAIR = (10, 30, 10)

# Variables globales de couleur (seront mises à jour)
CIEL_HAUT = C_CIEL_JOUR_HAUT      
CIEL_BAS  = C_CIEL_JOUR_BAS   
SOL_HERBE_BASE = (34, 100, 34) 
SOL_HERBE_FONCE = C_SOL_JOUR_FONCE
SOL_HERBE_CLAIR = C_SOL_JOUR_CLAIR
SOL_PISTE = (50, 50, 55)      
SOL_MARQUAGE = (240, 240, 240)

# COULEURS COCKPIT
DASH_BG = (30, 32, 36)         
DASH_PANEL = (10, 10, 12)      
HUD_VERT = (0, 255, 100)       
HUD_ROUGE = (255, 50, 50)
HUD_ORANGE = (255, 160, 0)
TXT_GRIS = (150, 150, 150)     

# Polices
police_label = pygame.font.SysFont("arial", 12, bold=True)
police_valeur = pygame.font.SysFont("consolas", 22, bold=True)
police_alarme = pygame.font.SysFont("arial", 40, bold=True)

# VARIABLES
world_y = 0      
world_x = 0      
vx, vy = 0, 0
angle = 0        
vitesse_rotation_actuelle = 0 
en_decrochage = False 
alarme_playing = False 
altitude = 0 
vitesse_kph = 0
pilote_auto_actif = False
zoom = 1.0          
zoom_cible = 1.0    

moteur_allume = False 
flaps_sortis = False
lumiere_allume = False # Landing Light

# CYCLE JOUR / NUIT (TEMPS RÉEL)
heure_actuelle = 12.0 # Heure décimale (0.0 - 24.0)
est_nuit = False

# GESTION POUSSEE
niveau_poussee_reelle = 0.0 
target_poussee = 0.0        

# DÉCOR
decor_sol = []
# On stocke juste la position et la taille, la couleur sera calculée dynamiquement
for _ in range(150):
    w = random.randint(20, 100)
    h = random.randint(4, 15)
    x_offset = random.randint(0, 2000)
    y_offset = random.randint(0, 800)
    # Type 0 = FONCE, Type 1 = CLAIR
    type_herbe = 0 if random.random() > 0.5 else 1
    decor_sol.append([x_offset, y_offset, w, h, type_herbe])

particules = []
for _ in range(50): 
    particules.append([random.randint(0, L), random.randint(0, H), random.uniform(0.5, 2.0), random.randint(1, 3)])

# --- PHYSIQUE TYPE CESSNA 172 ---
V_DECOLLAGE = 100          # Vitesse de rotation (~55 kts)
V_DECROCHAGE = 85          # Vitesse de décrochage (Stall speed)
V_VNE = 300                # Vitesse à ne jamais dépasser
V_MACH1 = 1225             # Mur du son (sécurité pour le code)
GRAVITE = 0.12             # Force de gravité
PUISSANCE_MOTEUR = 0.35    # Puissance réduite (était 0.45)
FRICTION_AIR = 0.992       # Traînée aérodynamique globale
FRICTION_VERTICALE = 0.96  
ACCEL_ROTATION = 0.04      # Sensibilité réduite (était 0.08)
MAX_ROTATION = 1.8         
COEFF_PORTANCE = 0.0015    # Portance réduite (était 0.0035)
COEFF_TRAINEE_MONTEE = 0.004

horloge = pygame.time.Clock()

def lerp_color(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t)
    )

def mettre_a_jour_couleurs(heure):
    global CIEL_BAS, CIEL_HAUT, SOL_HERBE_FONCE, SOL_HERBE_CLAIR, SOL_HERBE_BASE, est_nuit
    
    # Cycle 24h
    # 00-06h: Nuit
    # 06-08h: Aube
    # 08-18h: Jour
    # 18-20h: Crépuscule
    # 20-24h: Nuit (Sombre++)
    
    if 6 <= heure < 8: # AUBE
        est_nuit = False
        ratio = (heure - 6) / 2
        CIEL_BAS = lerp_color(C_CIEL_NUIT_BAS, C_CIEL_JOUR_BAS, ratio)
        CIEL_HAUT = lerp_color(C_CIEL_NUIT_HAUT, C_CIEL_JOUR_HAUT, ratio)
        SOL_HERBE_FONCE = lerp_color(C_SOL_NUIT_FONCE, C_SOL_JOUR_FONCE, ratio)
        SOL_HERBE_CLAIR = lerp_color(C_SOL_NUIT_CLAIR, C_SOL_JOUR_CLAIR, ratio)
        
    elif 8 <= heure < 18: # PLEIN JOUR
        est_nuit = False
        CIEL_BAS = C_CIEL_JOUR_BAS
        CIEL_HAUT = C_CIEL_JOUR_HAUT
        SOL_HERBE_FONCE = C_SOL_JOUR_FONCE
        SOL_HERBE_CLAIR = C_SOL_JOUR_CLAIR
        
    elif 18 <= heure < 20: # CRÉPUSCULE
        est_nuit = False
        # 18h-19h: Orange
        # 19h-20h: Nuit
        if heure < 19:
            ratio = (heure - 18)
            CIEL_BAS = lerp_color(C_CIEL_JOUR_BAS, C_CIEL_COUCHER_BAS, ratio)
            CIEL_HAUT = lerp_color(C_CIEL_JOUR_HAUT, C_CIEL_COUCHER_HAUT, ratio)
            SOL_HERBE_FONCE = lerp_color(C_SOL_JOUR_FONCE, C_SOL_NUIT_FONCE, ratio * 0.5)
            SOL_HERBE_CLAIR = lerp_color(C_SOL_JOUR_CLAIR, C_SOL_NUIT_CLAIR, ratio * 0.5)
        else:
            ratio = (heure - 19)
            CIEL_BAS = lerp_color(C_CIEL_COUCHER_BAS, C_CIEL_NUIT_BAS, ratio)
            CIEL_HAUT = lerp_color(C_CIEL_COUCHER_HAUT, C_CIEL_NUIT_HAUT, ratio)
            SOL_HERBE_FONCE = lerp_color(C_SOL_JOUR_FONCE, C_SOL_NUIT_FONCE, 0.5 + ratio * 0.5)
            SOL_HERBE_CLAIR = lerp_color(C_SOL_JOUR_CLAIR, C_SOL_NUIT_CLAIR, 0.5 + ratio * 0.5)
            
    else: # NUIT
        est_nuit = True
        CIEL_BAS = C_CIEL_NUIT_BAS
        CIEL_HAUT = C_CIEL_NUIT_HAUT
        SOL_HERBE_FONCE = C_SOL_NUIT_FONCE
        SOL_HERBE_CLAIR = C_SOL_NUIT_CLAIR
        
    SOL_HERBE_BASE = lerp_color(SOL_HERBE_FONCE, SOL_HERBE_CLAIR, 0.5)


def obtenir_couleur_ciel(alt):
    # Fondu avec l'altitude (plus sombre en haut)
    plafond = 20000 
    ratio = min(max(alt, 0), plafond) / plafond
    return lerp_color(CIEL_BAS, CIEL_HAUT, ratio)

# --- DASHBOARD EXPERT ---
def dessiner_dashboard(surface, vitesse, alt, moteur, flaps, auto, freins, lumiere, poussee_pct, heure_dec):
    h_dash = 140
    y_base = H - h_dash
    
    pygame.draw.rect(surface, DASH_BG, (0, y_base, L, h_dash))
    pygame.draw.line(surface, (100, 100, 100), (0, y_base), (L, y_base), 2)

    # 1. ANEMOMETRE
    x_spd = 120
    y_inst = y_base + 70
    rayon = 60
    pygame.draw.circle(surface, DASH_PANEL, (x_spd, y_inst), rayon)
    pygame.draw.circle(surface, (80, 80, 80), (x_spd, y_inst), rayon, 2)
    max_speed = 400
    for v in range(0, max_speed + 1, 1000):
        ang = 135 + (v / max_speed) * 270
        rad = math.radians(ang)
        x1 = x_spd + math.cos(rad) * (rayon - 10)
        y1 = y_inst + math.sin(rad) * (rayon - 10)
        x2 = x_spd + math.cos(rad) * rayon
        y2 = y_inst + math.sin(rad) * rayon
        pygame.draw.line(surface, TXT_GRIS, (x1, y1), (x2, y2), 2)
    val_aff = min(vitesse, max_speed)
    ang_aig = 135 + (val_aff / max_speed) * 270
    rad_aig = math.radians(ang_aig)
    xa = x_spd + math.cos(rad_aig) * (rayon - 5)
    ya = y_inst + math.sin(rad_aig) * (rayon - 5)
    pygame.draw.line(surface, HUD_ROUGE, (x_spd, y_inst), (xa, ya), 3)
    sf_spd = police_valeur.render(f"{int(vitesse)}", True, (255, 255, 255))
    surface.blit(sf_spd, sf_spd.get_rect(center=(x_spd, y_inst + 20)))
    surface.blit(police_label.render("KM/H", True, TXT_GRIS), (x_spd - 15, y_inst - 20))

    # 2. ALTIMETRE
    x_alt = 300
    pygame.draw.circle(surface, DASH_PANEL, (x_alt, y_inst), rayon)
    pygame.draw.circle(surface, (80, 80, 80), (x_alt, y_inst), rayon, 2)
    max_alt = 10000
    val_alt = min(alt, max_alt)
    ang_alt = 135 + (val_alt / max_alt) * 270
    rad_alt = math.radians(ang_alt)
    xa2 = x_alt + math.cos(rad_alt) * (rayon - 5)
    ya2 = y_alt = y_inst + math.sin(rad_alt) * (rayon - 5)
    pygame.draw.line(surface, HUD_ROUGE, (x_alt, y_inst), (xa2, ya2), 3)
    sf_alt = police_valeur.render(f"{int(alt)}", True, (255, 255, 255))
    surface.blit(sf_alt, sf_alt.get_rect(center=(x_alt, y_inst + 20)))
    surface.blit(police_label.render("ALT FT", True, TXT_GRIS), (x_alt - 20, y_inst - 20))

    # 3. ECRAN CENTRAL
    x_ecran = 420
    w_ecran = 250
    h_ecran = 100
    y_ecran = y_base + 20
    pygame.draw.rect(surface, DASH_PANEL, (x_ecran, y_ecran, w_ecran, h_ecran))
    pygame.draw.rect(surface, (60, 60, 60), (x_ecran, y_ecran, w_ecran, h_ecran), 2)
    mach = vitesse / 1225.0
    c_mach = HUD_VERT
    if mach > 1.0: c_mach = HUD_ORANGE
    if mach > 2.0: c_mach = HUD_ROUGE
    lbl_mach = police_label.render("MACH NUMBER", True, TXT_GRIS)
    val_mach = police_valeur.render(f"{mach:.2f}", True, c_mach)
    surface.blit(lbl_mach, (x_ecran + 10, y_ecran + 10))
    surface.blit(val_mach, (x_ecran + 10, y_ecran + 30))
    g_force = 1.0 + (abs(angle) * vitesse / 50000.0)
    lbl_g = police_label.render("G-FORCE", True, TXT_GRIS)
    val_g = police_valeur.render(f"{g_force:.1f} G", True, HUD_VERT)
    surface.blit(lbl_g, (x_ecran + 140, y_ecran + 10))
    surface.blit(val_g, (x_ecran + 140, y_ecran + 30))
    
    # Heure (Réelle) - Déplacée pour ne pas chevaucher les G
    heures = int(heure_dec)
    minutes = int((heure_dec - heures) * 60)
    lbl_time = police_label.render(f"FRANCE {heures:02d}:{minutes:02d}", True, HUD_ORANGE)
    surface.blit(lbl_time, (x_ecran + 80, y_ecran + 70))

    # 4. PANNEAU DROITE
    x_ctrl = L - 480 # Agrandi pour loger le bouton LIGHT
    y_ctrl = y_base + 20
    def dessiner_voyant(label, etat, x, y, col_on=HUD_VERT, col_off=HUD_ROUGE):
        couleur = col_on if etat else col_off
        pygame.draw.rect(surface, (20, 20, 20), (x, y, 90, 30))
        pygame.draw.rect(surface, couleur, (x, y, 10, 30))
        txt_etat = "ON" if etat else "OFF"
        if label == "FLAPS": txt_etat = "EXT" if etat else "RET"
        lbl = police_label.render(label, True, TXT_GRIS)
        val = police_label.render(txt_etat, True, couleur)
        surface.blit(lbl, (x + 15, y + 2))
        surface.blit(val, (x + 15, y + 16))

    dessiner_voyant("MOTEUR (A)", moteur, x_ctrl, y_ctrl)
    dessiner_voyant("FLAPS (F)", flaps, x_ctrl + 100, y_ctrl, col_on=HUD_ORANGE, col_off=HUD_VERT)
    dessiner_voyant("PILOTE", auto, x_ctrl + 200, y_ctrl, col_on=(0, 200, 255), col_off=(50, 50, 50))
    dessiner_voyant("FREINS (B)", freins, x_ctrl + 300, y_ctrl, col_on=HUD_ROUGE, col_off=(50, 50, 50))
    dessiner_voyant("LIGHT (L)", lumiere, x_ctrl + 400, y_ctrl, col_on=(255, 255, 200), col_off=(50, 50, 50))
    
    # Barre Thrust
    bar_x = x_ctrl
    bar_y = y_ctrl + 50
    bar_w = 400
    bar_h = 20
    pygame.draw.rect(surface, (10, 10, 10), (bar_x, bar_y, bar_w, bar_h))
    pygame.draw.rect(surface, (60, 60, 60), (bar_x, bar_y, bar_w, bar_h), 1)
    nb_segments = 20
    segments_allumes = int((poussee_pct / 100) * nb_segments)
    largeur_seg = (bar_w / nb_segments) - 2
    for i in range(segments_allumes):
        col = HUD_VERT
        if i > 14: col = HUD_ORANGE 
        if i > 18: col = HUD_ROUGE  
        pos_x = bar_x + 2 + (i * (largeur_seg + 2))
        pygame.draw.rect(surface, col, (pos_x, bar_y + 2, largeur_seg, bar_h - 4))
    
    surface.blit(police_label.render(f"THRUST {int(poussee_pct)}%", True, TXT_GRIS), (bar_x, bar_y - 15))


while True:
    dt = horloge.tick(60) / 1000.0 
    
    # HEURE REELLE
    now = datetime.datetime.now()
    heure_actuelle = now.hour + now.minute / 60.0 + now.second / 3600.0
    
    mettre_a_jour_couleurs(heure_actuelle) 

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEWHEEL:
            zoom_cible += event.y * 0.2 # Zoom plus rapide 
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moteur_allume = not moteur_allume
            if event.key == pygame.K_f:
                flaps_sortis = not flaps_sortis
            if event.key == pygame.K_l: # LANDING LIGHT
                lumiere_allume = not lumiere_allume
            
            if moteur_allume:
                if event.key == pygame.K_LSHIFT: # PLEIN GAZ
                    target_poussee = 100.0
                if event.key == pygame.K_LCTRL: # COUPER GAZ
                    target_poussee = 0.0
                if event.key == pygame.K_RIGHT:
                    target_poussee += 10.0 # Plus rapide
                if event.key == pygame.K_LEFT:
                    target_poussee -= 10.0 
                target_poussee = max(0.0, min(100.0, target_poussee))

    touches = pygame.key.get_pressed()
    zoom_cible = max(0.1, min(5.0, zoom_cible)) # Plage de zoom ÉNORME
    zoom += (zoom_cible - zoom) * 0.05 # Plus fluide

    # --- CONTROLE STABILISÉ (MODE FACILE) ---
    target_rotation = 0
    action_manche = False 
    pilote_auto_actif = False
    freins_actifs = False 

    if touches[pygame.K_UP]:    
        target_rotation = -MAX_ROTATION
        action_manche = True
    if touches[pygame.K_DOWN]:  
        target_rotation = MAX_ROTATION
        action_manche = True
    
    # FREINS (Espace ou B)
    if touches[pygame.K_SPACE] or touches[pygame.K_b]:
        freins_actifs = True

    if action_manche:
        # Rotation Active (Physique Améliorée)
        # 1. Efficacité des gouvernes selon la vitesse (Plus on va vite, plus ça tourne)
        efficacite_vitesse = min(1.0, max(0.1, vitesse_kph / V_DECOLLAGE))
        
        # 2. Poids du nez au sol (Difficile de lever le nez à basse vitesse)
        facteur_sol = 1.0
        # On adoucit la contrainte : progressif de 0 à 10m
        if altitude < 10:
            facteur_sol = 0.5 + (altitude / 10.0) * 0.5 # 50% min authority -> 100%
            
        accel = ACCEL_ROTATION * 0.5 * efficacite_vitesse * facteur_sol
        
        if target_rotation > vitesse_rotation_actuelle:
            vitesse_rotation_actuelle += accel
        elif target_rotation < vitesse_rotation_actuelle:
            vitesse_rotation_actuelle -= accel
    else:
        # --- STABILISATEUR RENFORCÉ (MODE FACILE) ---
        vitesse_rotation_actuelle *= 0.85 # Amortissement fort
        
        # Retour automatique à l'horizon plus agressif pour "faciliter" le vol
        if vitesse_kph > V_DECOLLAGE and not en_decrochage:
             # On ramène le nez à 0°
            if abs(angle) > 0.1:
                signe = -1 if angle > 0 else 1
                vitesse_rotation_actuelle += signe * 0.02 # Aide au redressement
            
            if abs(angle) < 1.0 and abs(vitesse_rotation_actuelle) < 0.05:
                angle = 0
                vitesse_rotation_actuelle = 0
                pilote_auto_actif = True
        
    angle += vitesse_rotation_actuelle

    # --- LIMITATION ANGLE (MODE FACILE) ---
    LIMIT_ANGLE = 35
    if angle > LIMIT_ANGLE:  
        angle = LIMIT_ANGLE
        vitesse_rotation_actuelle = 0
    if angle < -LIMIT_ANGLE:
        angle = -LIMIT_ANGLE
        vitesse_rotation_actuelle = 0

    # --- MOTEUR & THRUST & SON ---
    if not moteur_allume:
        target_poussee = 0.0
        
    if niveau_poussee_reelle < target_poussee:
        niveau_poussee_reelle += 1.0  # Montée en régime BEAUCOUP plus rapide
    elif niveau_poussee_reelle > target_poussee:
        niveau_poussee_reelle -= 1.0   
        
    # SON CONTINU
    if son_moteur:
        if moteur_allume:
            if son_moteur.get_num_channels() == 0: 
                son_moteur.play(loops=-1)
            vol = 0.3 + (niveau_poussee_reelle / 100.0) * 0.7
            son_moteur.set_volume(vol)
        else:
            son_moteur.stop()

    postcombustion = (niveau_poussee_reelle > 90)
    puissance_instantanee = (niveau_poussee_reelle / 100.0) * PUISSANCE_MOTEUR
    rad = math.radians(angle)
    vx += math.cos(rad) * puissance_instantanee
    vy -= math.sin(rad) * puissance_instantanee

    # Alarme (Moins sensible en mode facile)
    if en_decrochage and altitude > 50: # On ne sonne pas au ras du sol
        if not alarme_playing and son_alarme:
            son_alarme.play(loops=-1)
            alarme_playing = True
    else:
        if alarme_playing and son_alarme:
            son_alarme.stop()
            alarme_playing = False

    # Mur du son
    if vitesse_kph > V_MACH1:
        mur_du_son_franchi = True
    elif vitesse_kph < V_MACH1 - 50:
        mur_du_son_franchi = False

    altitude = -world_y
    
    # CLAMPING ET SECURITE
    vx = max(-150.0, min(150.0, vx))
    vy = max(-150.0, min(150.0, vy))
    if math.isnan(vx): vx = 0
    if math.isnan(vy): vy = 0
    
    vitesse_totale = math.sqrt(vx**2 + vy**2)
    vitesse_kph = int(vitesse_totale * 15)
    
    # Planeur / Décrochage (Plus permissif en mode facile)
    seuil_decrochage = V_DECROCHAGE - 10 
    if flaps_sortis: seuil_decrochage = 65 
    
    # Anti-Crash Sol
    if altitude < 100 and vitesse_kph > 50:
        en_decrochage = False
    elif vitesse_kph < seuil_decrochage:
        en_decrochage = True
    else:
        en_decrochage = False

    # --- PHYSIQUE DE VOL ---
    if pilote_auto_actif:
        vy = 0 
        vx *= FRICTION_AIR 
    else:
        vy += GRAVITE
        
        portance = 0
        friction_actuelle = FRICTION_AIR
        
        if flaps_sortis:
            friction_actuelle = 0.985  
            coeff_p = 0.0075           
        else:
            friction_actuelle = 0.992
            coeff_p = COEFF_PORTANCE

        if not en_decrochage:
            angle_incidence = angle + 2.0 
            
            lift_factor = angle_incidence * 0.1 
            if lift_factor < 0: lift_factor *= 0.1 
            
            densite_air = max(0.0, 1.0 - (altitude / 25000.0))

            portance_dynamique = (vitesse_totale**2) * coeff_p * lift_factor * 0.05 * densite_air
            
            # EFFET DE SOL (Ground Effect) - ADOUCI
            # Bonus de portance plus progressif (30m au lieu de 20m, max +15% au lieu de +25%)
            if altitude < 30:
                bonus_sol = 1.0 + (1.0 - (altitude / 30.0)) * 0.15 
                portance_dynamique *= bonus_sol
                
            portance = portance_dynamique

            trainee_induite = abs(portance) * 0.1
            friction_actuelle -= trainee_induite * 0.01

            vx *= friction_actuelle
            vy *= FRICTION_VERTICALE
            
            if abs(angle) < 5:
                vx *= 0.9995 
                vy *= 0.9995
        else:
            vx *= 0.99
            vy *= 0.99
            if angle > 10: angle -= 0.5 
        
        if angle < 0: vy += 0.02 

        vy -= portance

    world_x += vx
    world_y += vy
    
    # --- REBOND & IMMOBILISATION ---
    # --- REBOND & IMMOBILISATION ---
    if -world_y <= 0:
        world_y = 0
        altitude = 0
        
        # Friction au sol (Roulage plus fluide, plus d'inertie)
        friction_sol = 0.99 # Ça roule tout seul
        
        if freins_actifs:
            friction_sol = 0.92 # Freinage efficace mais pas "mur de briques"
            if vitesse_kph > 10:
                angle = 1.0 # Le nez plonge un peu moins
                
        vx *= friction_sol
        
        if abs(vx) < 0.1: 
            vx = 0
            vitesse_rotation_actuelle = 0
            
        # Rebond (Suspension plus môle)
        if vy > 2.0: # On ne rebondit que si le choc est significatif
             vy = -vy * 0.20 # Amortisseur efficace (absorbe 80% de l'énergie)
             world_y = 0.5 
        else:
            vy = 0
            en_decrochage = False
            
    altitude = -world_y

    # --- DESSIN ---
    fenetre.fill(obtenir_couleur_ciel(altitude))
    
    if vitesse_kph > 50:
        for p in particules:
            # Mouvement horizontal (existant)
            p[0] -= (vitesse_kph * 0.05 * p[2]) * zoom 
            
            # Mouvement vertical (NOUVEAU)
            # Si on monte (vy < 0), les particules descendent (+=)
            # On utilise vy pixels/frame. On applique le facteur zoom et un scalaire similaire à X
            p[1] -= (vy * 20.0 * p[2]) * zoom

            # Wrapping X
            if p[0] < -100:
                p[0] = L + random.randint(0, 100)
                p[1] = random.randint(0, H)
            
            # Wrapping Y (Si elles sortent en haut ou en bas)
            if p[1] < -100:
                p[1] = H + random.randint(0, 100)
            elif p[1] > H + 100:
                p[1] = -random.randint(0, 100)

            longueur = max(2, int(vitesse_kph / 50)) * zoom # Traits plus longs avec zoom
            
            # Orientation du trait selon le vecteur vitesse
            # Si vx=100, vy=0 -> trait horizontal
            # Si vx=100, vy=-10 (montée) -> trait légèrement incliné
            
            px = p[0]
            py = p[1]
            
            # Normalisation (approximative pour perf)
            # On veut un vecteur de taille 'longueur' opposé à la vitesse
            norme = math.sqrt(vx**2 + vy**2)
            if norme > 0.1:
                dx = (vx / norme) * longueur
                dy = (vy / norme) * longueur
            else:
                dx = longueur
                dy = 0
            
            px2 = px - dx
            py2 = py - dy
            
            # On ne dessine que si c'est dans l'écran (avec marge)
            if -100 < px < L+100 and -100 < py < H+100:
                pygame.draw.line(fenetre, (255, 255, 255), (px, py), (px2, py2), max(1, int(zoom)))

    pos_sol_y = (H // 2) + (altitude * zoom) 
    if pos_sol_y < H:
        pygame.draw.rect(fenetre, SOL_HERBE_BASE, (-100, pos_sol_y, L+200, H))
        largeur_motif = 2000 
        offset_herbe = int(world_x % largeur_motif)
        
        # Calcul du nombre de motifs nécessaires pour remplir l'écran
        largeur_motif_ecran = largeur_motif * zoom
        if largeur_motif_ecran < 1: largeur_motif_ecran = 1 # Sécurité
        
        nb_motifs_demi = int((L / 2) / largeur_motif_ecran) + 2
        
        for i in range(-nb_motifs_demi, nb_motifs_demi + 1):
            base_x = (i * largeur_motif * zoom) - (offset_herbe * zoom) + (L/2)
            if base_x + (largeur_motif*zoom) > 0 and base_x < L:
                for patch in decor_sol:
                    px = base_x + (patch[0] * zoom)
                    py = pos_sol_y + (patch[1] * zoom)
                    pw = patch[2] * zoom
                    ph = patch[3] * zoom
                    couleur_p = SOL_HERBE_FONCE if patch[4] == 0 else SOL_HERBE_CLAIR
                    pygame.draw.rect(fenetre, couleur_p, (px, py, pw, ph))
        
        debut_piste_ecran = (0 - world_x) * zoom + (L/2)
        longueur_piste_ecran = 5000 * zoom
        rect_piste = pygame.Rect(debut_piste_ecran, pos_sol_y, longueur_piste_ecran, H)
        
        if rect_piste.colliderect((0,0,L,H)):
            pygame.draw.rect(fenetre, SOL_PISTE, rect_piste)
            # Marquages piste
            pygame.draw.rect(fenetre, SOL_MARQUAGE, (debut_piste_ecran, pos_sol_y, longueur_piste_ecran, 4*zoom))
            nb_bandes = 50
            for i in range(nb_bandes):
                bx = debut_piste_ecran + (i * 100 * zoom)
                bw = 50 * zoom
                bh = 10 * zoom
                pygame.draw.rect(fenetre, SOL_MARQUAGE, (bx, pos_sol_y + 20*zoom, bw, bh))
            
    # --- DESSIN AVION ---
    # --- DESSIN AVION ---
    # Selection image
    img_base = img_avion_feu_base if (postcombustion and moteur_allume) else img_avion_normal_base
    
    # Redimensionnement (Zoom)
    # On limite la taille min pour qu'on voie toujours un point
    w_new = int(img_base.get_width() * zoom)
    h_new = int(img_base.get_height() * zoom)
    if w_new < 2: w_new = 2
    if h_new < 2: h_new = 2
    
    img_scaled = pygame.transform.scale(img_base, (w_new, h_new))
    
    # Rotation
    img_rot = pygame.transform.rotate(img_scaled, angle)
    rect_img = img_rot.get_rect(center=(L//2, H//2))
    
    # LANDING LIGHT (Phare)
    if lumiere_allume:
        # Création d'une surface pour le faisceau (transparente)
        # Scale du faisceau avec le zoom aussi sinon ça fait bizarre
        w_f = int(400 * zoom)
        h_f = int(100 * zoom)
        
        surf_light = pygame.Surface((w_f, h_f), pygame.SRCALPHA)
    
        p1 = (0, h_f // 2)
        p2 = (w_f, 0)
        p3 = (w_f, h_f)
        pygame.draw.polygon(surf_light, (255, 255, 200, 40), [p1, p2, p3]) 
        pygame.draw.polygon(surf_light, (255, 255, 220, 80), [p1, (w_f*0.7, 20*zoom), (w_f*0.7, h_f-(20*zoom))])

        faisceau_rot = pygame.transform.rotate(surf_light, angle)
        
        rad_a = math.radians(angle)
        offset_x = math.cos(rad_a) * 50 * zoom # Scale offset
        offset_y = -math.sin(rad_a) * 50 * zoom
        
        rect_light = faisceau_rot.get_rect(center=(L//2 + offset_x + math.cos(rad_a)*200*zoom, H//2 + offset_y - math.sin(rad_a)*200*zoom))
        fenetre.blit(faisceau_rot, rect_light)

    fenetre.blit(img_rot, rect_img)
    
    # --- DASHBOARD ---
    dessiner_dashboard(fenetre, vitesse_kph, altitude, moteur_allume, flaps_sortis, pilote_auto_actif, freins_actifs, lumiere_allume, niveau_poussee_reelle, heure_actuelle)
    
    # Message Alerte
    msg = ""
    c_msg = HUD_ROUGE
    if en_decrochage:
        msg = "!! DECROCHAGE !!"
    elif not moteur_allume and altitude > 10:
        msg = "!! MOTEUR COUPE !!"

    if msg:
        txt_msg = police_alarme.render(msg, True, c_msg)
        rect_msg = txt_msg.get_rect(center=(L//2, H//2 - 100))
        fenetre.blit(txt_msg, rect_msg)

    pygame.display.flip()

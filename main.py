import pygame
import math
import os
import random

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
pygame.display.set_caption("Simulateur - Cockpit Expert")

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
CIEL_HAUT = (10, 20, 40)      
CIEL_BAS  = (135, 206, 235)   
SOL_HERBE_BASE = (34, 100, 34)
SOL_HERBE_FONCE = (20, 60, 20)
SOL_HERBE_CLAIR = (50, 120, 50)
SOL_PISTE = (50, 50, 55)      
SOL_MARQUAGE = (240, 240, 240)

# COULEURS COCKPIT
DASH_BG = (30, 32, 36)         # Gris Cockpit
DASH_PANEL = (10, 10, 12)      # Fond des écrans (noir bleuté)
HUD_VERT = (0, 255, 100)       # Vert affichage
HUD_ROUGE = (255, 50, 50)
HUD_ORANGE = (255, 160, 0)
TXT_GRIS = (150, 150, 150)     # Libellés

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

moteur_allume = True
flaps_sortis = False

# DÉCOR
decor_sol = []
for _ in range(150):
    w = random.randint(20, 100)
    h = random.randint(4, 15)
    x_offset = random.randint(0, 2000)
    y_offset = random.randint(0, 800)
    couleur = SOL_HERBE_FONCE if random.random() > 0.5 else SOL_HERBE_CLAIR
    decor_sol.append([x_offset, y_offset, w, h, couleur])

particules = []
for _ in range(50): 
    particules.append([random.randint(0, L), random.randint(0, H), random.uniform(0.5, 2.0), random.randint(1, 3)])

# PHYSIQUE
V_DECOLLAGE = 220
V_DECROCHAGE = 160
V_VNE = 2500 
V_MACH1 = 1225 
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
    plafond = 20000 
    ratio = min(max(alt, 0), plafond) / plafond
    r = int(CIEL_BAS[0] * (1 - ratio) + CIEL_HAUT[0] * ratio)
    g = int(CIEL_BAS[1] * (1 - ratio) + CIEL_HAUT[1] * ratio)
    b = int(CIEL_BAS[2] * (1 - ratio) + CIEL_HAUT[2] * ratio)
    return (r, g, b)

# --- NOUVEAU DASHBOARD EXPERT ---
def dessiner_dashboard(surface, vitesse, alt, moteur, flaps, auto):
    # Dimensions
    h_dash = 140
    y_base = H - h_dash
    
    # Fond principal
    pygame.draw.rect(surface, DASH_BG, (0, y_base, L, h_dash))
    pygame.draw.line(surface, (100, 100, 100), (0, y_base), (L, y_base), 2)

    # --- 1. CADRAN VITESSE (ANEMOMETRE) ---
    # Échelle 0 à 7500
    x_spd = 120
    y_inst = y_base + 70
    rayon = 60
    
    pygame.draw.circle(surface, DASH_PANEL, (x_spd, y_inst), rayon)
    pygame.draw.circle(surface, (80, 80, 80), (x_spd, y_inst), rayon, 2)
    
    # Graduations
    max_speed = 7500
    for v in range(0, max_speed + 1, 1000):
        ang = 135 + (v / max_speed) * 270
        rad = math.radians(ang)
        # Gros trait
        x1 = x_spd + math.cos(rad) * (rayon - 10)
        y1 = y_inst + math.sin(rad) * (rayon - 10)
        x2 = x_spd + math.cos(rad) * rayon
        y2 = y_inst + math.sin(rad) * rayon
        pygame.draw.line(surface, TXT_GRIS, (x1, y1), (x2, y2), 2)
        
    # Aiguille
    val_aff = min(vitesse, max_speed)
    ang_aig = 135 + (val_aff / max_speed) * 270
    rad_aig = math.radians(ang_aig)
    xa = x_spd + math.cos(rad_aig) * (rayon - 5)
    ya = y_inst + math.sin(rad_aig) * (rayon - 5)
    pygame.draw.line(surface, HUD_ROUGE, (x_spd, y_inst), (xa, ya), 3)
    
    # Affichage numérique
    sf_spd = police_valeur.render(f"{int(vitesse)}", True, (255, 255, 255))
    surface.blit(sf_spd, sf_spd.get_rect(center=(x_spd, y_inst + 20)))
    surface.blit(police_label.render("KM/H", True, TXT_GRIS), (x_spd - 15, y_inst - 20))

    # --- 2. CADRAN ALTITUDE ---
    x_alt = 300
    pygame.draw.circle(surface, DASH_PANEL, (x_alt, y_inst), rayon)
    pygame.draw.circle(surface, (80, 80, 80), (x_alt, y_inst), rayon, 2)
    
    # Aiguille Alt (Max 10000)
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

    # --- 3. ECRAN CENTRAL (MACH & ETAT) ---
    x_ecran = 420
    w_ecran = 250
    h_ecran = 100
    y_ecran = y_base + 20
    
    pygame.draw.rect(surface, DASH_PANEL, (x_ecran, y_ecran, w_ecran, h_ecran))
    pygame.draw.rect(surface, (60, 60, 60), (x_ecran, y_ecran, w_ecran, h_ecran), 2)
    
    # Mach Number
    mach = vitesse / 1225.0
    c_mach = HUD_VERT
    if mach > 1.0: c_mach = HUD_ORANGE
    if mach > 2.0: c_mach = HUD_ROUGE
    
    lbl_mach = police_label.render("MACH NUMBER", True, TXT_GRIS)
    val_mach = police_valeur.render(f"{mach:.2f}", True, c_mach)
    surface.blit(lbl_mach, (x_ecran + 10, y_ecran + 10))
    surface.blit(val_mach, (x_ecran + 10, y_ecran + 30))
    
    # G-Force (Simulé)
    g_force = 1.0 + (abs(angle) * vitesse / 50000.0)
    lbl_g = police_label.render("G-FORCE", True, TXT_GRIS)
    val_g = police_valeur.render(f"{g_force:.1f} G", True, HUD_VERT)
    surface.blit(lbl_g, (x_ecran + 140, y_ecran + 10))
    surface.blit(val_g, (x_ecran + 140, y_ecran + 30))

    # --- 4. PANNEAU DE CONTROLE (DROITE) ---
    x_ctrl = L - 350
    y_ctrl = y_base + 20
    
    # Fonction pour dessiner un voyant
    def dessiner_voyant(label, etat, x, y, col_on=HUD_VERT, col_off=HUD_ROUGE):
        couleur = col_on if etat else col_off
        # Boite
        pygame.draw.rect(surface, (20, 20, 20), (x, y, 100, 30))
        pygame.draw.rect(surface, couleur, (x, y, 10, 30)) # Barre couleur
        # Texte
        txt_etat = "ON" if etat else "OFF"
        if label == "FLAPS": txt_etat = "EXT" if etat else "RET"
        
        lbl = police_label.render(label, True, TXT_GRIS)
        val = police_label.render(txt_etat, True, couleur)
        surface.blit(lbl, (x + 15, y + 2))
        surface.blit(val, (x + 15, y + 16))

    dessiner_voyant("MOTEUR (A)", moteur, x_ctrl, y_ctrl)
    dessiner_voyant("FLAPS (F)", flaps, x_ctrl + 110, y_ctrl, col_on=HUD_ORANGE, col_off=HUD_VERT)
    dessiner_voyant("AUTOPILOT", auto, x_ctrl + 220, y_ctrl, col_on=(0, 200, 255), col_off=(50, 50, 50))
    
    # Barre de poussée (Throttle)
    push = 0
    if moteur:
        push = 40 # Idle
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]: push = 100 # Full
    
    pygame.draw.rect(surface, (20, 20, 20), (x_ctrl, y_ctrl + 40, 320, 15))
    pygame.draw.rect(surface, HUD_VERT, (x_ctrl, y_ctrl + 40, 3.2 * push, 15))
    surface.blit(police_label.render("THRUST", True, TXT_GRIS), (x_ctrl, y_ctrl + 60))


while True:
    dt = horloge.tick(60) / 1000.0 

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEWHEEL:
            zoom_cible += event.y * 0.1 
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moteur_allume = not moteur_allume
            if event.key == pygame.K_f:
                flaps_sortis = not flaps_sortis

    touches = pygame.key.get_pressed()
    zoom_cible = max(0.5, min(2.0, zoom_cible))
    zoom += (zoom_cible - zoom) * 0.1

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
        if vitesse_kph > V_DECOLLAGE and not en_decrochage and moteur_allume:
            pilote_auto_actif = True
            angle_cible = vy * 1.5
            angle_cible = max(-10, min(10, angle_cible))
            angle += (angle_cible - angle) * 0.04
            
    angle += vitesse_rotation_actuelle

    # --- LOGIQUE SONORE ---
    if son_moteur:
        if moteur_allume:
            if son_moteur.get_num_channels() == 0:
                son_moteur.play(loops=-1)
            if touches[pygame.K_RIGHT]:
                son_moteur.set_volume(0.8)
            else:
                son_moteur.set_volume(0.4)
        else:
            son_moteur.stop()

    # --- PHYSIQUE ---
    postcombustion = False
    if moteur_allume and touches[pygame.K_RIGHT]:
        postcombustion = True
        rad = math.radians(angle)
        vx += math.cos(rad) * PUISSANCE_MOTEUR
        vy -= math.sin(rad) * PUISSANCE_MOTEUR

    # Alarme
    if en_decrochage:
        if not alarme_playing and son_alarme:
            son_alarme.play(loops=-1)
            alarme_playing = True
    else:
        if alarme_playing and son_alarme:
            son_alarme.stop()
            alarme_playing = False

    # Calculs Altitude/Vitesse
    altitude = -world_y 
    vitesse_totale = math.sqrt(vx**2 + vy**2)
    vitesse_kph = int(vitesse_totale * 15)
    
    # --- MODE PLANEUR ---
    seuil_decrochage = V_DECROCHAGE
    if flaps_sortis: seuil_decrochage = 100 
    
    if vitesse_kph < seuil_decrochage and altitude > 10:
        en_decrochage = True
    elif vitesse_kph > seuil_decrochage + 20:
        en_decrochage = False

    vy += GRAVITE

    portance = 0
    friction_actuelle = FRICTION_AIR
    
    if flaps_sortis:
        friction_actuelle = 0.995 
        coeff_p = 0.0050 
    else:
        coeff_p = COEFF_PORTANCE 

    if not en_decrochage:
        seuil_portance = 60 if flaps_sortis else 100
        if vitesse_kph > seuil_portance: 
            angle_attaque = abs(angle)
            if angle_attaque > 5:
                vx *= 0.999 
                vy *= 0.999
            
            if angle > -10: 
                base_lift = 0.05 if flaps_sortis else 0
                factor = (angle + 2) if flaps_sortis else angle
                if factor < 0: factor = 0
                portance = abs(vx) * (factor * coeff_p) + (abs(vx) * base_lift * 0.01)
            
            vx *= friction_actuelle
            vy *= FRICTION_VERTICALE
    else:
        vx *= 0.99
        vy *= 0.99
        if angle > 0: angle -= 0.4 

    vy -= portance
    world_x += vx
    world_y += vy
    
    # --- REBOND ---
    if -world_y <= 0:
        sur_piste = -500 < world_x < 5500
        seuil_rebond = 1.0 if sur_piste else 1.5 
        
        if vy > seuil_rebond: 
            coef = 0.5 if sur_piste else 0.3
            vy = -vy * coef 
            vx *= 0.95 
            world_y = 0.1 
            en_decrochage = False
        else:
            world_y = 0
            vy = 0
            vx *= 0.98 if sur_piste else 0.90 
            en_decrochage = False
            
    altitude = -world_y

    # --- DESSIN ---
    fenetre.fill(obtenir_couleur_ciel(altitude))
    
    # 1. Particules
    if vitesse_kph > 50:
        for p in particules:
            p[0] -= (vitesse_kph * 0.05 * p[2]) * zoom 
            if p[0] < 0:
                p[0] = L + random.randint(0, 100)
                p[1] = random.randint(0, H)
            longueur = max(2, int(vitesse_kph / 100))
            pygame.draw.line(fenetre, (255, 255, 255), (p[0], p[1]), (p[0]-longueur, p[1]), 1)

    # 2. SOL
    pos_sol_y = (H // 2) + (altitude * zoom) 
    
    if pos_sol_y < H:
        pygame.draw.rect(fenetre, SOL_HERBE_BASE, (-100, pos_sol_y, L+200, H))
        largeur_motif = 2000 
        offset_herbe = int(world_x % largeur_motif)
        for i in range(-1, 2):
            base_x = (i * largeur_motif * zoom) - (offset_herbe * zoom) + (L/2)
            if base_x + (largeur_motif*zoom) > 0 and base_x < L:
                for patch in decor_sol:
                    px = base_x + (patch[0] * zoom)
                    py = pos_sol_y + (patch[1] * zoom)
                    pw = patch[2] * zoom
                    ph = patch[3] * zoom
                    pygame.draw.rect(fenetre, patch[4], (px, py, pw, ph))

        debut_piste_ecran = (0 - world_x) * zoom + (L/2)
        longueur_piste_ecran = 5000 * zoom
        rect_piste = pygame.Rect(debut_piste_ecran, pos_sol_y, longueur_piste_ecran, H)
        
        if rect_piste.colliderect((0,0,L,H)):
            pygame.draw.rect(fenetre, SOL_PISTE, rect_piste)
            pygame.draw.rect(fenetre, SOL_MARQUAGE, (debut_piste_ecran, pos_sol_y, longueur_piste_ecran, 4*zoom))
            nb_bandes = 50
            for i in range(nb_bandes):
                bx = debut_piste_ecran + (i * 100 * zoom)
                bw = 50 * zoom
                bh = 10 * zoom
                pygame.draw.rect(fenetre, SOL_MARQUAGE, (bx, pos_sol_y + 20*zoom, bw, bh))
            for i in range(10):
                px = debut_piste_ecran + (10 * zoom)
                py = pos_sol_y + (i * 10 * zoom) + 10
                pygame.draw.rect(fenetre, SOL_MARQUAGE, (px, py, 40*zoom, 5*zoom))

    # 3. Avion
    if images_ok:
        img_actuelle = img_avion_feu_base if postcombustion else img_avion_normal_base
        new_w = max(10, int(90 * zoom))
        new_h = max(5, int(35 * zoom))
        img_scaled = pygame.transform.scale(img_actuelle, (new_w, new_h))
        avion_rot = pygame.transform.rotate(img_scaled, angle)
        rect_rot = avion_rot.get_rect(center=(L // 2, H // 2))
        fenetre.blit(avion_rot, rect_rot)
    else:
        pts = [(L//2+(30*zoom), H//2), (L//2-(10*zoom), H//2-(10*zoom)), (L//2-(10*zoom), H//2+(10*zoom))]
        pygame.draw.polygon(fenetre, (100, 100, 100), pts)

    # 4. DASHBOARD (Bas de l'écran)
    dessiner_dashboard(fenetre, vitesse_kph, altitude, moteur_allume, flaps_sortis, pilote_auto_actif)

    # Messages d'alerte (Au milieu)
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

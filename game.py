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
CIEL_HAUT = (10, 20, 40)      
CIEL_BAS  = (135, 206, 235)   
SOL_HERBE_BASE = (34, 100, 34)
SOL_HERBE_FONCE = (20, 60, 20)
SOL_HERBE_CLAIR = (50, 120, 50)
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

# GESTION POUSSEE
niveau_poussee_reelle = 0.0 
target_poussee = 0.0        

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

# --- PHYSIQUE TYPE CESSNA 172 ---
V_DECOLLAGE = 100          # Vitesse de rotation (~55 kts)
V_DECROCHAGE = 85          # Vitesse de décrochage (Stall speed)
V_VNE = 300                # Vitesse à ne jamais dépasser
V_MACH1 = 1225             # Mur du son (sécurité pour le code)
GRAVITE = 0.12             # Force de gravité
PUISSANCE_MOTEUR = 0.45    # Puissance du moteur Lycoming IO-360
FRICTION_AIR = 0.992       # Traînée aérodynamique globale
FRICTION_VERTICALE = 0.96  # Amortissement des mouvements verticaux (Celle qui manquait !)
ACCEL_ROTATION = 0.08      # Sensibilité du manche
MAX_ROTATION = 1.8         # Débattement maximum des gouvernes
COEFF_PORTANCE = 0.0035    # Portance de l'aile haute du Cessna
COEFF_TRAINEE_MONTEE = 0.004

horloge = pygame.time.Clock()

def obtenir_couleur_ciel(alt):
    plafond = 20000 
    ratio = min(max(alt, 0), plafond) / plafond
    r = int(CIEL_BAS[0] * (1 - ratio) + CIEL_HAUT[0] * ratio)
    g = int(CIEL_BAS[1] * (1 - ratio) + CIEL_HAUT[1] * ratio)
    b = int(CIEL_BAS[2] * (1 - ratio) + CIEL_HAUT[2] * ratio)
    return (r, g, b)

# --- DASHBOARD EXPERT ---
def dessiner_dashboard(surface, vitesse, alt, moteur, flaps, auto, freins, poussee_pct):
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

    # 4. PANNEAU DROITE
    x_ctrl = L - 460
    y_ctrl = y_base + 20
    def dessiner_voyant(label, etat, x, y, col_on=HUD_VERT, col_off=HUD_ROUGE):
        couleur = col_on if etat else col_off
        pygame.draw.rect(surface, (20, 20, 20), (x, y, 100, 30))
        pygame.draw.rect(surface, couleur, (x, y, 10, 30))
        txt_etat = "ON" if etat else "OFF"
        if label == "FLAPS": txt_etat = "EXT" if etat else "RET"
        lbl = police_label.render(label, True, TXT_GRIS)
        val = police_label.render(txt_etat, True, couleur)
        surface.blit(lbl, (x + 15, y + 2))
        surface.blit(val, (x + 15, y + 16))

    dessiner_voyant("MOTEUR (A)", moteur, x_ctrl, y_ctrl)
    dessiner_voyant("FLAPS (F)", flaps, x_ctrl + 110, y_ctrl, col_on=HUD_ORANGE, col_off=HUD_VERT)
    dessiner_voyant("AUTOPILOT", auto, x_ctrl + 220, y_ctrl, col_on=(0, 200, 255), col_off=(50, 50, 50))
    dessiner_voyant("FREINS (B)", freins, x_ctrl + 330, y_ctrl, col_on=HUD_ROUGE, col_off=(50, 50, 50))
    
    # Barre Thrust
    bar_x = x_ctrl
    bar_y = y_ctrl + 50
    bar_w = 320
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
            
            if moteur_allume:
                if event.key == pygame.K_RIGHT:
                    target_poussee += 5.0 
                if event.key == pygame.K_LEFT:
                    target_poussee -= 5.0 
                target_poussee = max(0.0, min(100.0, target_poussee))

    touches = pygame.key.get_pressed()
    zoom_cible = max(0.5, min(2.0, zoom_cible))
    zoom += (zoom_cible - zoom) * 0.1

    # --- CONTROLE STABILISÉ ---
    target_rotation = 0
    action_manche = False 
    pilote_auto_actif = False
    freins_actifs = False # Variable pour les freins

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
        # Rotation Active (plus douce)
        accel = ACCEL_ROTATION * 0.5 # On adoucit la réponse
        if target_rotation > vitesse_rotation_actuelle:
            vitesse_rotation_actuelle += accel
        elif target_rotation < vitesse_rotation_actuelle:
            vitesse_rotation_actuelle -= accel
    else:
        # --- STABILISATEUR (Retour à plat) ---
        vitesse_rotation_actuelle *= 0.90 # Amortissement rotation
        
        # Si on est en l'air, on ramène le nez à 0° mais beaucoup plus doucement
        if vitesse_kph > V_DECOLLAGE and not en_decrochage:
            # On ne force le retour à plat que si on est proche de l'horizon, sinon on laisse l'avion sur sa trajectoire
            if abs(angle) < 20:
                angle *= 0.995 # Retour TRES doux vers l'horizon (plus réaliste)
            
            # Si on est presque à plat, on verrouille
            if abs(angle) < 0.5 and abs(vitesse_rotation_actuelle) < 0.01:
                angle = 0
                pilote_auto_actif = True
        
    angle += vitesse_rotation_actuelle

    # --- LIMITATION ANGLE ---
    if angle > 60:  # Un peu plus de liberté de tangage
        angle = 60
        vitesse_rotation_actuelle = 0
    if angle < -60:
        angle = -60
        vitesse_rotation_actuelle = 0

    # --- MOTEUR & THRUST & SON ---
    if not moteur_allume:
        target_poussee = 0.0
        
    if niveau_poussee_reelle < target_poussee:
        niveau_poussee_reelle += 0.2  # Montée en régime lente
    elif niveau_poussee_reelle > target_poussee:
        niveau_poussee_reelle -= 0.4  # Décélération par friction de l'hélice 
        
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

    # Alarme
    if en_decrochage:
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
    vitesse_totale = math.sqrt(vx**2 + vy**2)
    vitesse_kph = int(vitesse_totale * 15)
    
    # Planeur
    seuil_decrochage = V_DECROCHAGE
    if flaps_sortis: seuil_decrochage = 75 # Plus permissif avec les volets
    
    if vitesse_kph < seuil_decrochage and altitude > 10:
        en_decrochage = True
    elif vitesse_kph > seuil_decrochage + 10:
        en_decrochage = False

    # --- PHYSIQUE DE VOL ET MAINTIEN ALTITUDE ---
    if pilote_auto_actif:
        # MODE STABILISÉ (VERROUILLAGE)
        vy = 0 # On force la vitesse verticale à 0 pour ne pas monter/descendre
        vx *= FRICTION_AIR # On garde juste le frottement de l'air
    else:
        # MODE MANUEL (PHYSIQUE NORMALE)
        vy += GRAVITE
        
        portance = 0
        friction_actuelle = FRICTION_AIR
        
        if flaps_sortis:
            friction_actuelle = 0.985  # Les volets créent beaucoup de traînée (freinage)
            coeff_p = 0.0075           # Portance massivement augmentée
        else:
            friction_actuelle = 0.992
            coeff_p = COEFF_PORTANCE

        if not en_decrochage:
            # Portance réaliste : proportionnelle au carré de la vitesse
            # Lift = Cl * 0.5 * rho * v^2 * S
            # Ici simplifié en : k * v^2 * angle_factor
            
            angle_incidence = angle + 2.0 # Angle d'attaque de l'aile par rapport au vent relatif
            
            # Facteur d'efficacité de l'aile selon l'angle
            lift_factor = angle_incidence * 0.1 
            if lift_factor < 0: lift_factor *= 0.1 # Portance négative faible

            # Calcul de la portance quadratique v^2
            # On divise par un grand nombre pour normaliser car v^2 augmente très vite
            portance_dynamique = (vitesse_totale**2) * coeff_p * lift_factor * 0.05
            
            # Application de la portance (perpendiculaire à la vitesse, ou simplifiée verticale ici)
            portance = portance_dynamique

            # Traînée induite (plus on porte, plus on freine)
            trainee_induite = abs(portance) * 0.1
            friction_actuelle -= trainee_induite * 0.01

            vx *= friction_actuelle
            vy *= FRICTION_VERTICALE
            
            # Amortissement naturel des oscillations
            if abs(angle) < 5:
                vx *= 0.9995 
                vy *= 0.9995
        else:
            # Décrochage = chute de pierre
            vx *= 0.99
            vy *= 0.99
            if angle > 10: angle -= 0.5 # Le nez tombe
        
        if angle < 0: vy += 0.02 # Piqué accélère la chute

        vy -= portance

    world_x += vx
    world_y += vy
    
    # --- REBOND & IMMOBILISATION ---
    if -world_y <= 0:
        # Au sol
        world_y = 0
        altitude = 0
        
        # Friction au sol (roulement des pneus)
        friction_sol = 0.96 # Friction naturelle du tarmac/herbe
        
        if freins_actifs:
            friction_sol = 0.85 # FREINAGE FORT
            
            # Effet visuel de piqué au freinage (suspension avant s'écrase)
            if vitesse_kph > 10:
                angle = 1.5 
                
        vx *= friction_sol
        
        if abs(vx) < 0.1: 
            vx = 0
            vitesse_rotation_actuelle = 0
            
        # Rebond simplifié
        if vy > 1.5: 
             vy = -vy * 0.3
             world_y = 0.5 # Petit saut
        else:
            vy = 0
            en_decrochage = False
            
    altitude = -world_y

    # --- DESSIN ---
    fenetre.fill(obtenir_couleur_ciel(altitude))
    
    if vitesse_kph > 50:
        for p in particules:
            p[0] -= (vitesse_kph * 0.05 * p[2]) * zoom 
            if p[0] < 0:
                p[0] = L + random.randint(0, 100)
                p[1] = random.randint(0, H)
            longueur = max(2, int(vitesse_kph / 100))
            pygame.draw.line(fenetre, (255, 255, 255), (p[0], p[1]), (p[0]-longueur, p[1]), 1)

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

    dessiner_dashboard(fenetre, vitesse_kph, altitude, moteur_allume, flaps_sortis, pilote_auto_actif, freins_actifs, niveau_poussee_reelle)

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

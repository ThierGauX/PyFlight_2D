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
pygame.display.set_caption("Simulateur - Herbe Detaillée & Image Nette")

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
            son_moteur.play(loops=-1)
            print(f"✅ Moteur chargé : {nom}")
            break
        except: pass

try:
    p_alarme = os.path.join(dossier, "alarme_decrochage.wav")
    if os.path.exists(p_alarme):
        son_alarme = pygame.mixer.Sound(p_alarme)
        son_alarme.set_volume(0.5)
except: pass


# --- PALETTE GRAPHIQUE ---
# Ciel
CIEL_HAUT = (10, 20, 40)      
CIEL_BAS  = (135, 206, 235)   

# Sol (Nouvelle palette herbe)
SOL_HERBE_BASE = (34, 100, 34)  # Vert moyen
SOL_HERBE_FONCE = (20, 60, 20)  # Touffes sombres
SOL_HERBE_CLAIR = (50, 120, 50) # Touffes claires

SOL_PISTE = (50, 50, 55)      
SOL_MARQUAGE = (240, 240, 240)

# HUD
HUD_VERT = (0, 255, 100)     
TXT_BLANC = (255, 255, 255)
ALERTE_ROUGE = (255, 50, 50)

# Polices
police = pygame.font.SysFont("consolas", 16, bold=True)
police_hud = pygame.font.SysFont("consolas", 20, bold=True)
police_grosse = pygame.font.SysFont("arial", 40, bold=True)

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
mur_du_son_franchi = False 
flash_timer = 0 

# GÉNÉRATION DU DÉCOR (HERBE)
# On crée des centaines de petits rectangles de "texture" qui vont défiler
decor_sol = []
for _ in range(150):
    w = random.randint(20, 100)       # Largeur de la touffe
    h = random.randint(4, 15)         # Hauteur
    x_offset = random.randint(0, 2000) # Position relative
    y_offset = random.randint(0, 800)  # Distance depuis l'horizon
    # Couleur aléatoire (sombre ou claire)
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

def dessiner_hud_cercle(surface, x, y, valeur, max_val, label):
    rayon = 60
    # Fond
    s = pygame.Surface((rayon*2, rayon*2), pygame.SRCALPHA)
    pygame.draw.circle(s, (0, 20, 0, 150), (rayon, rayon), rayon)
    surface.blit(s, (x-rayon, y-rayon))
    # Contour
    pygame.draw.circle(surface, HUD_VERT, (x, y), rayon, 2)
    # Aiguille
    angle_aig = 135 + (valeur / max_val) * 270
    rad = math.radians(angle_aig)
    x_fin = x + math.cos(rad) * (rayon - 10)
    y_fin = y + math.sin(rad) * (rayon - 10)
    pygame.draw.line(surface, ALERTE_ROUGE, (x, y), (x_fin, y_fin), 3)
    # Texte
    txt = police_hud.render(str(int(valeur)), True, TXT_BLANC)
    rect = txt.get_rect(center=(x, y + 20))
    surface.blit(txt, rect)
    # Label
    lbl = police.render(label, True, HUD_VERT)
    surface.blit(lbl, (x - 20, y - 30))

while True:
    dt = horloge.tick(60) / 1000.0 

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEWHEEL:
            zoom_cible += event.y * 0.1 

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
        if vitesse_kph > V_DECOLLAGE and not en_decrochage:
            pilote_auto_actif = True
            angle_cible = vy * 1.5
            angle_cible = max(-10, min(10, angle_cible))
            angle += (angle_cible - angle) * 0.04
            
    angle += vitesse_rotation_actuelle

    # --- LOGIQUE SONORE ---
    if son_moteur:
        if touches[pygame.K_RIGHT]:
            son_moteur.set_volume(0.8) # Fort
        else:
            son_moteur.set_volume(0.4) # Normal

    postcombustion = False
    if touches[pygame.K_RIGHT]:
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

    # Visuel Mur du son
    if vitesse_kph > V_MACH1:
        if not mur_du_son_franchi:
            flash_timer = 8 
            mur_du_son_franchi = True
    elif vitesse_kph < V_MACH1 - 50:
        mur_du_son_franchi = False

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
    
    # --- REBOND ---
    if -world_y <= 0:
        # Est-on sur la piste ? 
        sur_piste = -500 < world_x < 5500
        
        # Le sol est plus dur sur la piste
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
            vx *= 0.98 if sur_piste else 0.90 # Freine plus fort dans l'herbe
            en_decrochage = False
            
    altitude = -world_y

    # --- DESSIN ---
    fenetre.fill(obtenir_couleur_ciel(altitude))
    
    # 1. Particules (Ciel)
    if vitesse_kph > 50:
        for p in particules:
            p[0] -= (vitesse_kph * 0.05 * p[2]) * zoom 
            if p[0] < 0:
                p[0] = L + random.randint(0, 100)
                p[1] = random.randint(0, H)
            longueur = max(2, int(vitesse_kph / 100))
            pygame.draw.line(fenetre, (255, 255, 255), (p[0], p[1]), (p[0]-longueur, p[1]), 1)

    # 2. LE SOL (AMÉLIORÉ)
    pos_sol_y = (H // 2) + (altitude * zoom) 
    
    if pos_sol_y < H:
        # A. Fond herbe global
        pygame.draw.rect(fenetre, SOL_HERBE_BASE, (-100, pos_sol_y, L+200, H))
        
        # B. Texture herbe qui défile
        # Le "pattern" se répète tous les 2000 pixels
        largeur_motif = 2000 
        offset_herbe = int(world_x % largeur_motif)
        
        # On dessine 2 fois le motif pour couvrir l'écran si nécessaire
        for i in range(-1, 2):
            base_x = (i * largeur_motif * zoom) - (offset_herbe * zoom) + (L/2)
            
            # On n'affiche que si c'est visible
            if base_x + (largeur_motif*zoom) > 0 and base_x < L:
                for patch in decor_sol:
                    px = base_x + (patch[0] * zoom)
                    py = pos_sol_y + (patch[1] * zoom)
                    pw = patch[2] * zoom
                    ph = patch[3] * zoom
                    # Dessin du rectangle de texture
                    pygame.draw.rect(fenetre, patch[4], (px, py, pw, ph))

        # C. LA PISTE (Par dessus l'herbe)
        debut_piste_ecran = (0 - world_x) * zoom + (L/2)
        longueur_piste_ecran = 5000 * zoom
        rect_piste = pygame.Rect(debut_piste_ecran, pos_sol_y, longueur_piste_ecran, H)
        
        # On ne dessine la piste que si elle est à l'écran
        if rect_piste.colliderect((0,0,L,H)):
            pygame.draw.rect(fenetre, SOL_PISTE, rect_piste)
            
            # Marquages
            # Ligne blanche continue haut de piste
            pygame.draw.rect(fenetre, SOL_MARQUAGE, (debut_piste_ecran, pos_sol_y, longueur_piste_ecran, 4*zoom))
            
            # Bandes centrales
            nb_bandes = 50
            for i in range(nb_bandes):
                bx = debut_piste_ecran + (i * 100 * zoom)
                bw = 50 * zoom
                bh = 10 * zoom
                pygame.draw.rect(fenetre, SOL_MARQUAGE, (bx, pos_sol_y + 20*zoom, bw, bh))
                
            # Peigne seuil
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

    # 4. Flash Blanc (Passage mur du son)
    if flash_timer > 0:
        s_flash = pygame.Surface((L, H))
        s_flash.fill((255, 255, 255))
        alpha = int((flash_timer / 8) * 150) 
        s_flash.set_alpha(alpha)
        fenetre.blit(s_flash, (0, 0))
        flash_timer -= 1

    # 5. HUD
    dessiner_hud_cercle(fenetre, 100, H - 100, vitesse_kph, 3000, "KPH")
    dessiner_hud_cercle(fenetre, 250, H - 100, altitude, 5000, "ALT")
    
    infos = [
        f"MACH : {(vitesse_kph/1225):.2f}",
        f"AUTO : {'ON' if pilote_auto_actif else 'OFF'}",
    ]
    for i, ligne in enumerate(infos):
        c_txt = HUD_VERT
        if "AUTO" in ligne and pilote_auto_actif: c_txt = TXT_BLANC
        fenetre.blit(police.render(ligne, True, c_txt), (L - 150, H - 80 + i*20))

    # Messages
    msg = ""
    c_msg = HUD_VERT
    if en_decrochage:
        msg = "!! DECROCHAGE !!"
        c_msg = ALERTE_ROUGE
    elif vitesse_kph > V_MACH1:
         msg = "MACH 1 SUPERSONIC"
         c_msg = (255, 255, 0)
    elif pilote_auto_actif and abs(vy) < 1.0 and altitude > 50:
        msg = "PILOTE AUTO ACTIF"

    if msg:
        txt_msg = police_grosse.render(msg, True, c_msg)
        rect_msg = txt_msg.get_rect(center=(L//2, H//2 - 150))
        fenetre.blit(txt_msg, rect_msg)

    pygame.display.flip()

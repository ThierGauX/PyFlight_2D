import pygame
import math
import os
import random
import datetime # Pour l'heure réelle
import argparse
import sys

def resource_path(relative_path):
    import os, sys
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- ARGUMENTS (Lancement depuis le Menu) ---
parser = argparse.ArgumentParser()
parser.add_argument("--time", type=str, default="real", help="Heure de départ (real ou 0-24)")
parser.add_argument("--difficulty", type=str, default="easy", help="easy ou real")
parser.add_argument("--volume", type=float, default=0.5, help="Volume global (0.0-1.0)")

# On parse uniquement si on est lancé en tant que script principal
args = None
if __name__ == "__main__":
    args, unknown = parser.parse_known_args()
else:
    # Valeurs par défaut si importé (ou pas de main)
    args = argparse.Namespace(time="real", difficulty="easy", volume=0.5)


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
pygame.display.set_caption("Pyflight 2D")

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
            son_moteur.set_volume(args.volume)
            break
        except: pass

try:
    p_alarme = os.path.join(dossier, "alarme_decrochage.wav")
    if os.path.exists(p_alarme):
        son_alarme = pygame.mixer.Sound(p_alarme)
        son_alarme.set_volume(args.volume)
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
pilote_auto_actif = (args.difficulty == "easy")
zoom = 1.0          
zoom_cible = 1.0    

moteur_allume = False 
flaps_sortis = False
lumiere_allume = False # Landing Light

# CYCLE JOUR / NUIT (TEMPS RÉEL)
mode_temps_reel = (args.time == "real")
offset_temps = 0
if not mode_temps_reel:
    try:
        offset_temps = float(args.time)
    except:
        offset_temps = 12.0

heure_actuelle = offset_temps if not mode_temps_reel else 12.0 # Si temps réel, sera mis à jour dans la boucle

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
    # Type 0 = FONCE, Type 1 = CLAIR, Type 2 = ARBRE
    r = random.random()
    if r < 0.45: type_decor = 0
    elif r < 0.9: type_decor = 1
    else: type_decor = 2 # Arbre
    
    decor_sol.append([x_offset, y_offset, w, h, type_decor])

contrails = [] # Liste des traînées de condensation [x, y, life]

particules = []
for _ in range(50): 
    particules.append([random.randint(0, L), random.randint(0, H), random.uniform(0.5, 2.0), random.randint(1, 3)])

# --- CLOUDS & BIRDS & RUNWAYS ---
# --- CLOUDS & BIRDS & RUNWAYS ---
class Cloud:
    def __init__(self):
        self.reset(random_start=True)
        
    def reset(self, random_start=False):
        self.x = float(random.randint(-5000, 5000)) if random_start else 6000.0
        self.y = float(random.randint(-3000, -200)) # Plus haut
        self.depth = random.uniform(0.1, 0.9) 
        self.scale = random.uniform(1.0, 3.0) * self.depth
        
        # Generation Image Nuage (Pre-render)
        w_cloud = int(random.randint(150, 300) * self.scale)
        h_cloud = int(random.randint(80, 150) * self.scale)
        self.image = pygame.Surface((w_cloud, h_cloud), pygame.SRCALPHA)
        
        base_color = random.randint(240, 255)
        color = (base_color, base_color, base_color, 20 + int(40 * self.depth)) # Alpha tres faible pour douceur
        
        # Puffs
        num_puffs = random.randint(5, 10)
        for _ in range(num_puffs):
            cx = random.randint(w_cloud//4, 3*w_cloud//4)
            cy = random.randint(h_cloud//4, 3*h_cloud//4)
            rw = random.randint(w_cloud//4, w_cloud//2)
            rh = random.randint(h_cloud//4, h_cloud//2)
            pygame.draw.ellipse(self.image, color, (cx - rw//2, cy - rh//2, rw, rh))
            
    def update(self, cam_vx):
        # Parallax
        self.x -= (cam_vx * self.depth * 0.5) 
        self.x -= 0.5 * self.depth # Vent constant
        
        if self.x < -6000: self.reset()

    def draw(self, surface, cam_x, cam_y, zoom):
        eff_cam_x = cam_x * self.depth
        px = (self.x - eff_cam_x) * zoom + (L/2)
        py = (self.y - cam_y) * zoom + (H/2)
        
        # Optimisation
        if px < -500 or px > L + 500: return

        # Scale image selon zoom
        w_new = int(self.image.get_width() * zoom)
        h_new = int(self.image.get_height() * zoom)
        
        if w_new > 1 and h_new > 1:
            img_scaled = pygame.transform.scale(self.image, (w_new, h_new))
            if est_nuit:
                # Assombrir la surface grossierement (fill multiply)
                img_scaled.fill((100, 100, 120), special_flags=pygame.BLEND_MULT)
                
            surface.blit(img_scaled, (px, py))

clouds = [Cloud() for _ in range(40)] # Moins de nuages mais plus jolis

class Bird:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.flap_timer = 0.0
        self.reset()
        
    def reset(self):
        self.x = float(random.randint(-2000, 2000))
        self.y = float(random.randint(-1000, -50))
        self.vx = random.uniform(2, 5) * (1 if random.random() > 0.5 else -1)
        self.vy = random.uniform(-1, 1)
        self.flap_timer = 0.0
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.flap_timer += 0.2
        
        if self.x < -3000 or self.x > 3000:
            self.reset()
            
    def draw(self, surface, cam_x, cam_y, zoom):
        px = (self.x - cam_x) * zoom + (L/2)
        py = (self.y - cam_y) * zoom + (H/2)
        
        # V shape animation
        oscill = math.sin(self.flap_timer) * 5 * zoom
        wing_span = 8 * zoom
        
        if -50 < px < L+50:
            p1 = (px - wing_span, py - oscill)
            p2 = (px, py)
            p3 = (px + wing_span, py - oscill)
            pygame.draw.lines(surface, (20, 20, 20), False, [p1, p2, p3], max(1, int(1.5*zoom)))

birds = [Bird() for _ in range(20)]


# --- AIRPORT & RUNWAY ---
class Airport:
    def __init__(self, x_start, width):
        self.x_start = x_start
        self.width = width
        self.x_end = x_start + width
        self.altitude = 0 
        
    def draw(self, surface, cam_x, cam_y, zoom):
        # Sol Piste
        px = (self.x_start - cam_x) * zoom + (L/2)
        py = (0 - cam_y) * zoom + (H/2) # Sol est à y=0
        pw = self.width * zoom
        ph = 100 * zoom # Profondeur visuelle
        
        # Clipping simple
        if px + pw < 0 or px > L: return
        
        # Bitume
        pygame.draw.rect(surface, (40, 42, 45), (px, py, pw, H))
        
        # Bandes Seuils (Piano keys)
        nb_keys = 8
        kw = 40 * zoom
        kh = 6 * zoom
        # Seuil Début
        for k in range(nb_keys):
            pygame.draw.rect(surface, (220, 220, 220), (px + 10*zoom, py + 10*zoom + k*12*zoom, kw, kh))
        # Seuil Fin
        for k in range(nb_keys):
            pygame.draw.rect(surface, (220, 220, 220), (px + pw - 50*zoom, py + 10*zoom + k*12*zoom, kw, kh))

        # Ligne Médiane Discontinue
        dash_w = 60 * zoom
        gap_w = 40 * zoom
        current_x = px + 150 * zoom
        while current_x < px + pw - 150*zoom:
            pygame.draw.rect(surface, (220, 220, 220), (current_x, py + (H/2), dash_w, 4*zoom))
            current_x += dash_w + gap_w
            
        # Numéro Piste (09 / 27)
        # 09 à gauche
        # On triche et on dessine des rectangles pour les chiffres simplifiés pour éviter de charger une police à chaque frame
        # Ou on utilise la police existante
        lbl_09 = police_alarme.render("09", True, (200, 200, 200))
        surface.blit(lbl_09, (px + 80*zoom, py + 100))
        
        lbl_27 = police_alarme.render("27", True, (200, 200, 200))
        surface.blit(lbl_27, (px + pw - 140*zoom, py + 100))

MAIN_AIRPORT = Airport(0, 4000) # Piste de 4km partant de 0

RUNWAYS = [0] # Pour compatibilité dashboard (radar)

# --- SYSTEMES AVION (Carburant, Dégâts) ---
fuel = 100.0
max_fuel = 100.0
fuel_burn_rate = 0.005 # % par frame à pleins gaz
crashed = False
crash_reason = ""
game_over_timer = 0
shake_amount = 0.0

# --- METEO (Vent) ---
vent_x = random.uniform(-10, 10) # Vent de face ou dos
vent_y = random.uniform(-2, 2)   # Courants ascendants/descendants
turbulence_timer = 0




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

    return lerp_color(CIEL_BAS, CIEL_HAUT, ratio)

# --- DASHBOARD EXPERT (UPGRADE) ---
# --- DASHBOARD HUD MODERN (OVERLAY) ---
def dessiner_hud_overlay(surface, vitesse, alt, angle_pitch, vy):
    # Couleurs HUD
    C_TXT = (0, 255, 128)      # Vert HUD
    C_INFO = (0, 200, 255)     # Cyan Info
    C_BG = (0, 20, 10, 50)     # Fond TRES transparent

    # 1. GAUCHE: VITESSE (Speed Tape)
    x_spd = 80
    y_center = H // 2
    h_tape = 300
    w_tape = 70
    
    # Fond Tape Vitesse
    s_tape_spd = pygame.Surface((w_tape, h_tape), pygame.SRCALPHA)
    s_tape_spd.fill(C_BG)
    surface.blit(s_tape_spd, (x_spd - w_tape, y_center - h_tape//2))
    
    # Ligne centrale (repère)
    pygame.draw.line(surface, C_TXT, (x_spd - w_tape, y_center), (x_spd, y_center), 2)
    
    # Graduations Vitesse
    px_per_knot = 3
    start_v = int(vitesse - (h_tape // 2) / px_per_knot)
    end_v = int(vitesse + (h_tape // 2) / px_per_knot)
    
    for v in range((start_v // 10) * 10, end_v, 10):
        dy = (vitesse - v) * px_per_knot
        y_pos = y_center + dy
        if y_center - h_tape//2 < y_pos < y_center + h_tape//2:
            if v % 50 == 0:
                pygame.draw.line(surface, C_TXT, (x_spd, y_pos), (x_spd - 20, y_pos), 2)
                lbl = police_valeur.render(str(v), True, C_TXT)
                surface.blit(lbl, (x_spd - 55, y_pos - 10))
            else:
                pygame.draw.line(surface, C_TXT, (x_spd, y_pos), (x_spd - 10, y_pos), 1)

    # Valeur Vitesse Actuelle
    lbl_vagne = police_valeur.render(f"{int(vitesse)}", True, C_TXT)
    pygame.draw.rect(surface, (0, 0, 0), (x_spd + 15, y_center - 15, 50, 30))
    pygame.draw.rect(surface, C_TXT, (x_spd + 15, y_center - 15, 50, 30), 2)
    surface.blit(lbl_vagne, (x_spd + 22, y_center - 10))

    # 2. DROITE: ALTITUDE (Alt Tape)
    x_alt = L - 80
    
    s_tape_alt = pygame.Surface((w_tape, h_tape), pygame.SRCALPHA)
    s_tape_alt.fill(C_BG)
    surface.blit(s_tape_alt, (x_alt, y_center - h_tape//2))
    
    pygame.draw.line(surface, C_TXT, (x_alt, y_center), (x_alt + w_tape, y_center), 2)

    px_per_ft = 0.5 
    start_alt = int(alt - (h_tape // 2) / px_per_ft)
    end_alt = int(alt + (h_tape // 2) / px_per_ft)

    for a in range((start_alt // 100) * 100, end_alt, 100):
        dy = (alt - a) * px_per_ft
        y_pos = y_center + dy
        if y_center - h_tape//2 < y_pos < y_center + h_tape//2:
            if a % 500 == 0:
                pygame.draw.line(surface, C_TXT, (x_alt, y_pos), (x_alt + 20, y_pos), 2)
                lbl = police_valeur.render(str(a), True, C_TXT)
                surface.blit(lbl, (x_alt + 25, y_pos - 10))
            else:
                pygame.draw.line(surface, C_TXT, (x_alt, y_pos), (x_alt + 10, y_pos), 1)

    # Valeur Alt Actuelle
    lbl_a_act = police_valeur.render(f"{int(alt)}", True, C_TXT)
    pygame.draw.rect(surface, (0, 0, 0), (x_alt - 60, y_center - 15, 55, 30))
    pygame.draw.rect(surface, C_TXT, (x_alt - 60, y_center - 15, 55, 30), 2)
    surface.blit(lbl_a_act, (x_alt - 55, y_center - 10))

    # 3. CENTRE: PITCH LADDER
    pitch_px = angle_pitch * 5
    y_hor = y_center + pitch_px
    if 0 < y_hor < H:
        pygame.draw.line(surface, C_INFO, (L/2 - 50, y_hor), (L/2 + 50, y_hor), 1) 
    
    for p in range(-90, 90, 10):
        if p == 0: continue
        dy = (angle_pitch - p) * 5
        y_l = y_center + dy
        if y_center - 150 < y_l < y_center + 150:
            w_l = 40 if p % 20 == 0 else 20
            pygame.draw.line(surface, C_TXT, (L/2 - w_l, y_l), (L/2 + w_l, y_l), 1)
            if p % 20 == 0:
                txt_p = police_label.render(str(p), True, C_TXT)
                surface.blit(txt_p, (L/2 + w_l + 5, y_l - 5))

    # Maquette Avion
    cx, cy = L // 2, H // 2
    pygame.draw.circle(surface, (255, 0, 0), (cx, cy), 3, 1)

# --- DASHBOARD ANALOGIQUE (CLASSIC) ---
def dessiner_dashboard(surface, vitesse, alt, moteur, flaps, auto, freins, lumiere, poussee_pct, heure_dec, px_world, runways, vy, angle_pitch):
    h_dash = 140
    y_base = H - h_dash
    
    # Fond Carbone / Tableau de bord
    pygame.draw.rect(surface, (40, 40, 45), (0, y_base, L, h_dash))
    pygame.draw.line(surface, (80, 80, 90), (0, y_base), (L, y_base), 3)

    # 1. ANEMOMETRE (GAUCHE)
    x_spd = 120
    y_inst = y_base + 70
    rayon = 60
    
    # Cadran
    pygame.draw.circle(surface, (10, 10, 15), (x_spd, y_inst), rayon)
    pygame.draw.circle(surface, (200, 200, 200), (x_spd, y_inst), rayon, 2)
    
    # Graduations
    max_speed = 400
    for v in range(0, max_speed + 1, 50):
        ang = 135 + (v / max_speed) * 270
        rad = math.radians(ang)
        p1 = (x_spd + math.cos(rad) * (rayon - 8), y_inst + math.sin(rad) * (rayon - 8))
        p2 = (x_spd + math.cos(rad) * rayon, y_inst + math.sin(rad) * rayon)
        lc = (255, 255, 255) if v % 100 == 0 else (150, 150, 150)
        w = 2 if v % 100 == 0 else 1
        pygame.draw.line(surface, lc, p1, p2, w)
        
    val_aff = min(vitesse, max_speed)
    ang_aig = 135 + (val_aff / max_speed) * 270
    rad_aig = math.radians(ang_aig)
    pygame.draw.line(surface, HUD_ORANGE, (x_spd, y_inst), (x_spd + math.cos(rad_aig) * (rayon-5), y_inst + math.sin(rad_aig) * (rayon-5)), 3)
    
    sf_spd = police_valeur.render(f"{int(vitesse)}", True, (255, 255, 255))
    surface.blit(sf_spd, sf_spd.get_rect(center=(x_spd, y_inst + 25)))
    surface.blit(police_label.render("KTS", True, TXT_GRIS), (x_spd - 15, y_inst - 20))

    # 2. HORIZON ARTIFICIEL (CENTRE GAUCHE)
    x_hor = 280
    rayon_hor = 60
    
    pitch_pixel = angle_pitch * 3 # Sensibilité
    
    # Masque (Clip)
    s_hor = pygame.Surface((rayon_hor*2, rayon_hor*2))
    s_hor_rect = s_hor.get_rect()
    
    # Ciel / Sol sur surface temp
    pygame.draw.rect(s_hor, (40, 100, 200), s_hor_rect) # Ciel
    
    y_h_local = rayon_hor + pitch_pixel
    rect_sol_local = pygame.Rect(0, y_h_local, rayon_hor*2, rayon_hor*2)
    pygame.draw.rect(s_hor, (100, 60, 30), rect_sol_local) # Sol
    pygame.draw.line(s_hor, (255, 255, 255), (0, y_h_local), (rayon_hor*2, y_h_local), 2) # Ligne
    
    # Masque Circulaire
    mask = pygame.Surface((rayon_hor*2, rayon_hor*2), pygame.SRCALPHA)
    pygame.draw.circle(mask, (0,0,0,255), (rayon_hor, rayon_hor), rayon_hor)
    mask.set_colorkey((0,0,0))
    # On blit le mask sur s_hor pour "trout" (inverse) -> non, plus simple:
    # On crée une surface finale propre
    s_final_hor = pygame.Surface((rayon_hor*2, rayon_hor*2), pygame.SRCALPHA)
    pygame.draw.circle(s_final_hor, (255, 255, 255), (rayon_hor, rayon_hor), rayon_hor)
    # Mode de blend pour garder que le cercle... un peu complexe en pygame pur vite fait
    # Methode simple: on blit le carré s_hor et on redessine un cache par dessus (image png avec trou transparent ou 4 coins)
    # Ici on va juste afficher le carré clippé dans le cercle principal du dashboard qui a un bord épais
    
    # Pour faire simple et propre sans assets : On affiche le rect complet mais on dessine le contour par dessus
    surface.blit(s_hor, (x_hor - rayon_hor, y_inst - rayon_hor))
    
    # Repère Avion
    pygame.draw.line(surface, HUD_ORANGE, (x_hor - 40, y_inst), (x_hor - 10, y_inst), 3)
    pygame.draw.line(surface, HUD_ORANGE, (x_hor + 10, y_inst), (x_hor + 40, y_inst), 3)
    pygame.draw.circle(surface, HUD_ORANGE, (x_hor, y_inst), 3)
    
    # Contour cache misère (cercle épais autour)
    pygame.draw.circle(surface, (40, 40, 45), (x_hor, y_inst), rayon_hor + 10, 10) 
    pygame.draw.circle(surface, (50, 50, 60), (x_hor, y_inst), rayon_hor, 3)


    # 3. ALTIMETRE (CENTRE DROIT)
    x_alt = 440
    pygame.draw.circle(surface, (10, 10, 15), (x_alt, y_inst), rayon)
    pygame.draw.circle(surface, (200, 200, 200), (x_alt, y_inst), rayon, 2)
    
    # Aiguille 1000 ft
    val_1000 = (alt % 10000) / 10000.0
    ang_1000 = -90 + val_1000 * 360
    r1 = math.radians(ang_1000)
    pygame.draw.line(surface, (255, 255, 255), (x_alt, y_inst), (x_alt + math.cos(r1)*40, y_inst + math.sin(r1)*40), 4)

    # Aiguille 100 ft
    val_100 = (alt % 1000) / 1000.0
    ang_100 = -90 + val_100 * 360
    r2 = math.radians(ang_100)
    pygame.draw.line(surface, (255, 255, 255), (x_alt, y_inst), (x_alt + math.cos(r2)*55, y_inst + math.sin(r2)*55), 2)
    
    sf_alt = police_valeur.render(f"{int(alt)}", True, (200, 255, 200))
    surface.blit(sf_alt, sf_alt.get_rect(center=(x_alt, y_inst + 30)))
    surface.blit(police_label.render("ALT", True, TXT_GRIS), (x_alt - 10, y_inst - 20))

    # 4. VARIOMETRE (VSI)
    x_vsi = 600
    rayon_vsi = 50
    pygame.draw.circle(surface, (10, 10, 15), (x_vsi, y_inst), rayon_vsi)
    pygame.draw.circle(surface, (200, 200, 200), (x_vsi, y_inst), rayon_vsi, 2)
    
    v_montee = -vy
    val_climb = max(-20, min(20, v_montee * 2.0))
    ang_vsi = 180 + (val_climb * 6)
    rv = math.radians(ang_vsi)
    pygame.draw.line(surface, (255, 255, 100), (x_vsi, y_inst), (x_vsi + math.cos(rv)*(rayon_vsi-5), y_inst + math.sin(rv)*(rayon_vsi-5)), 3)
    surface.blit(police_label.render("V.S.", True, TXT_GRIS), (x_vsi - 10, y_inst + 10))
    
    # 5. FUEL (JAUGE) - INTEGRATION
    x_fuel = 720
    rayon_fuel = 40
    pygame.draw.circle(surface, (10, 10, 15), (x_fuel, y_inst), rayon_fuel)
    pygame.draw.circle(surface, (200, 200, 200), (x_fuel, y_inst), rayon_fuel, 2)
    
    # Aiguille Fuel (E -> F)
    # E = -135 deg, F = -45 deg (Arc de 90 deg en haut/gauche ?)
    # Faisons simple: E = 225 deg (bas gauche), F = 315 deg (bas droit) -> range 90
    # Ou classique: E = 180 (gauche), F = 0 (droite) -> range 180 (Haut)
    # Allons pour: E = 220, F = 320
    
    pct_fuel = fuel / 100.0
    ang_fuel = 220 + pct_fuel * 100
    rf = math.radians(ang_fuel)
    
    c_f_aig = (255, 255, 255)
    if fuel < 20: c_f_aig = (255, 50, 50)
    
    pygame.draw.line(surface, c_f_aig, (x_fuel, y_inst), (x_fuel + math.cos(rf)*(rayon_fuel-5), y_inst + math.sin(rf)*(rayon_fuel-5)), 2)
    
    lbl_f = police_label.render("FUEL", True, TXT_GRIS)
    surface.blit(lbl_f, (x_fuel - 15, y_inst + 10))
    lbl_e = police_label.render("E", True, (200, 50, 50))
    surface.blit(lbl_e, (x_fuel - 20, y_inst + 15))
    lbl_full = police_label.render("F", True, (200, 200, 200))
    surface.blit(lbl_full, (x_fuel + 15, y_inst + 15))


    # 6. RADAR / MAP
    x_map = 820
    y_map = y_base + 10
    w_map = 300
    h_map = 120
    
    pygame.draw.rect(surface, (10, 20, 10), (x_map, y_map, w_map, h_map))
    pygame.draw.rect(surface, (100, 100, 100), (x_map, y_map, w_map, h_map), 2)
    
    center_map_x = x_map + w_map // 2
    pygame.draw.line(surface, (0, 100, 0), (x_map, y_map+h_map-10), (x_map+w_map, y_map+h_map-10))
    
    h_rel = min(h_map - 20, alt * 0.02)
    pygame.draw.circle(surface, HUD_VERT, (center_map_x, y_map+h_map-10 - h_rel), 3)
    
    RANGE_MAP = 20000 
    px_per_m = w_map / (RANGE_MAP * 2)
    
    for rx in runways: 
        dist = rx - px_world
        if abs(dist) < RANGE_MAP:
             mx = center_map_x + (dist * px_per_m)
             pygame.draw.rect(surface, (180, 180, 180), (mx, y_map+h_map-12, 10, 4))
             
    # Infos Textes (THRUST)
    lbl_th = police_label.render(f"THR {int(poussee_pct)}%", True, HUD_ORANGE)
    surface.blit(lbl_th, (L - 80, y_map))
    
    # INDICATEURS CLASSIQUES (Lampes)
    # GEAR
    y_lamps = y_base + 60
    pygame.draw.circle(surface, (0, 200, 0), (L - 350, y_lamps), 6)
    surface.blit(police_label.render("GEAR", True, (200,200,200)), (L - 340, y_lamps - 8))
    
    # FLAPS
    c_flaps = (0, 200, 0) if flaps else (40, 40, 40)
    pygame.draw.circle(surface, c_flaps, (L - 250, y_lamps), 6)
    surface.blit(police_label.render("FLAPS", True, (200,200,200)), (L - 240, y_lamps - 8))
    
    # BRAKES
    c_brakes = (200, 0, 0) if freins else (40, 40, 40)
    pygame.draw.circle(surface, c_brakes, (L - 150, y_lamps), 6)
    surface.blit(police_label.render("BRAKE", True, (200,200,200)), (L - 140, y_lamps - 8))
    
    lbl_ti = police_valeur.render(f"{int(heure_dec):02d}:{int((heure_dec%1)*60):02d}", True, HUD_VERT)
    surface.blit(lbl_ti, (L - 80, y_map + 20))





while True:
    dt = horloge.tick(60) / 1000.0 
    
    if mode_temps_reel:
        now = datetime.datetime.now()
        heure_actuelle = now.hour + (now.minute / 60.0) + (now.second / 3600.0)
    else:
        # Mode Manuel
        heure_actuelle = offset_temps

    
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

    # --- MOTEUR & THRUST & FUEL ---
    if not moteur_allume or fuel <= 0:
        target_poussee = 0.0
        if fuel <= 0: moteur_allume = False
        
    if niveau_poussee_reelle < target_poussee:
        niveau_poussee_reelle += 1.0  
    elif niveau_poussee_reelle > target_poussee:
        niveau_poussee_reelle -= 1.0   
        
    # Consommation Fuel
    if moteur_allume:
        # Conso basale + conso poussée
        conso = 0.001 + (niveau_poussee_reelle / 100.0) * fuel_burn_rate
        fuel -= conso
        if fuel < 0: fuel = 0
    # Refuel au sol (Arrêté à la pompe... ou n'importe où sur la piste pour l'instant)
    elif altitude < 5 and abs(vitesse_kph) < 5 and (0 <= world_x <= MAIN_AIRPORT.width):
        fuel += 0.2 # Refuel rapide
        if fuel > max_fuel: fuel = max_fuel

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
    
    # --- VENT & TURBULENCE ---
    turbulence_timer += 1
    # Variation du vent (rafales)
    rafale_x = math.sin(turbulence_timer * 0.05) * 2.0
    rafale_y = math.cos(turbulence_timer * 0.13) * 1.5
    
    vent_actuel_x = vent_x + rafale_x
    vent_actuel_y = vent_y + rafale_y
    
    # Le vent affecte la vitesse AIR (et donc la portance), mais ici on simule l'effet sur le vecteur sol direct pour simplifier
    # On ajoute le vent aux forces
    # Mais attention, l'avion a de l'inertie.
    # On va dire que le vent pousse l'avion doucement
    vx += vent_actuel_x * 0.005 
    vy += vent_actuel_y * 0.005
    
    # Secousses Caméra
    # Secousses Caméra (REDUIT)
    shake_amount = (vitesse_kph / V_VNE) * 0.5 + (niveau_poussee_reelle/100.0) * 0.2
    if altitude < 20: shake_amount += 0.5 # Petite turbulence sol
    
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
    
    # --- CONTRAILS ---
    # ... (code existant inchangé, voir plus bas pour nettoyage si besoin)
    if moteur_allume and niveau_poussee_reelle > 80:
         # ... (Inchangé)
         pass

    # --- REBOND & CRASH ---
    if -world_y <= 0:
        impact_vitesse_vert = vy # Positive = Descente vers le sol
        world_y = 0
        altitude = 0
        
        # CRASH CHECK
        crash_limit = 8.0 # m/s (environ 1500 ft/min)
        if impact_vitesse_vert > crash_limit:
            crashed = True
            crash_reason = f"ATTERRISSAGE VIOLENT ({int(impact_vitesse_vert*200)} ft/min)"
            
        # PITCH CHECK AU SOL
        if abs(angle) > 20:
            crashed = True
            crash_reason = "CRASH NEZ/QUEUE (Angle trop fort)"
            
        if crashed and game_over_timer == 0:
            moteur_allume = False
            vx = 0
            vy = 0
            game_over_timer = 180 # 3 secondes à 60fps
            son_alarme.stop()
        
        if not crashed:
            # Friction Sol
            friction_sol = 0.99 
            if freins_actifs:
                friction_sol = 0.92 
                if vitesse_kph > 10: angle = 1.0 
                    
            vx *= friction_sol
            
            if abs(vx) < 0.1: 
                vx = 0
                vitesse_rotation_actuelle = 0
                
            # Rebond
            if impact_vitesse_vert > 2.0: 
                 vy = -impact_vitesse_vert * 0.20 
                 world_y = 0.5 
            else:
                vy = 0
                en_decrochage = False
            
    altitude = -world_y

    # --- RESET SI CRASH ---
    if crashed:
        game_over_timer -= 1
        if game_over_timer <= 0:
            # RESET COMPLET
            crashed = False
            world_x = 0
            world_y = 0
            vx, vy = 0, 0
            angle = 0
            fuel = 100.0
            moteur_allume = False
            niveau_poussee_reelle = 0
            
            # Respawn un peu avant la piste si on veut être gentil, ou à 0
            world_x = 100
            
            
    # --- DESSIN ---
    # Camera Shake
    offset_shake_x = random.uniform(-shake_amount, shake_amount)
    offset_shake_y = random.uniform(-shake_amount, shake_amount)
    
    # On applique le shake au contexte de rendu (pas aux coordonnées monde) - astuce simple: décaler tout le monde
    # Pour simplifier, on ajoute juste ça aux coords de dessin
    
    fenetre.fill(obtenir_couleur_ciel(altitude))
    
    # DESSIN NUAGES (ARRIÈRE PLAN)
    for c in clouds:
        c.update(vx)
        c.draw(fenetre, world_x, -altitude, zoom)
    
    # CONTIUE LE RESTE DU DESSIN (SOL, AVION)
    
    # DESSIN CONTRAILS (avant le sol pour être "dans" le ciel, mais bon le sol est en bas)
    # En fait on veut que ce soit derrière l'avion
    for c in contrails:
        px = (c[0] - world_x) * zoom + (L/2)
        py = (c[1] - world_y) * zoom + (H/2)
        
        if -50 < px < L+50 and -50 < py < H+50:
            radius = int(8 * zoom * c[2]) # Rétrécit avec la vie ? Ou grossit ?
            # Disons ça grossit un peu en se dissipant
            radius = int((5 + (1.0 - c[2]) * 10) * zoom)
            
            p_alpha = int(100 * c[2])
            surface_fumee = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(surface_fumee, (200, 200, 200, p_alpha), (radius, radius), radius)
            fenetre.blit(surface_fumee, (px - radius, py - radius))

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
            
            # --- MODIFICATION (Retour aux traits horizontaux blancs) ---
            # On garde le mouvement vertical (p[1] change), mais le trait reste horizontal
            px = p[0]
            py = p[1]
            px2 = px - longueur
            py2 = py # Pas d'inclinaison verticale
            
            # On ne dessine que si c'est dans l'écran (avec marge)
            if -100 < px < L+100 and -100 < py < H+100:
                pygame.draw.line(fenetre, (255, 255, 255), (px, py), (px2, py2), max(1, int(zoom)))

    # DESSIN OISEAUX
    for b in birds:
        b.update()
        b.draw(fenetre, world_x, -altitude, zoom)


    pos_sol_y = (H // 2) + (altitude * zoom) + offset_shake_y
    if pos_sol_y < H:
        # Optimisation & Haze de sol
        # Si on est très haut (zoom petit), on simplifie
        alpha_sol = 255
        if zoom < 0.3:
            # Fade out
            alpha_sol = int(255 * (zoom / 0.3))
        
        if alpha_sol > 10:
            # Sauf que Pygame draw rect gère pas alpha. On fait une surface.
            # Pour perf: on dessine normalement, et on dessine un rect bleu par dessus si haut
            pygame.draw.rect(fenetre, SOL_HERBE_BASE, (-100, pos_sol_y, L+200, H))
        
        # Patchs
        largeur_motif = 2000 
        offset_herbe = int(world_x % largeur_motif)
        largeur_motif_ecran = largeur_motif * zoom
        if largeur_motif_ecran < 1: largeur_motif_ecran = 1 
        nb_motifs_demi = int((L / 2) / largeur_motif_ecran) + 2
        
        if alpha_sol > 20: # Ne dessine les détails que si visibles
            for i in range(-nb_motifs_demi, nb_motifs_demi + 1):
                base_x = (i * largeur_motif * zoom) - (offset_herbe * zoom) + (L/2) + offset_shake_x
                if base_x + (largeur_motif*zoom) > 0 and base_x < L:
                    for patch in decor_sol:
                        px = base_x + (patch[0] * zoom)
                        py = pos_sol_y + (patch[1] * zoom)
                        pw = patch[2] * zoom
                        ph = patch[3] * zoom
                        # ... (Dessin patch)
                        couleur_p = SOL_HERBE_FONCE if patch[4] == 0 else SOL_HERBE_CLAIR
                        if patch[4] == 2: # ARBRE
                             if zoom > 0.2: # Arbres invisibles de très haut
                                tronc_w = 4 * zoom
                                tronc_h = 10 * zoom
                                pygame.draw.rect(fenetre, (100, 60, 20), (px + pw/2 - tronc_w/2, py, tronc_w, tronc_h))
                                p1 = (px + pw/2, py - 20*zoom)
                                p2 = (px + pw/2 - 15*zoom, py)
                                p3 = (px + pw/2 + 15*zoom, py)
                                pygame.draw.polygon(fenetre, (20, 100, 20), [p1, p2, p3])
                        else:
                            pygame.draw.rect(fenetre, couleur_p, (px, py, pw, ph))

    # ATMOSPHERE HAUTE ALTITUDE
    # Si zoom très faible (haute altitude), on rajoute du voile
    if zoom < 0.5:
        alpha_atmo = int((1.0 - (zoom / 0.5)) * 100) # Max 100 alpha (plus subtil)
        s_atmo = pygame.Surface((L, H), pygame.SRCALPHA)
        s_atmo.fill((*CIEL_BAS, alpha_atmo)) # Voile couleur ciel
        fenetre.blit(s_atmo, (0, 0))
        
        # Gestion Multi-Pistes
        for piste_x in RUNWAYS:
            debut_piste_ecran = (piste_x - world_x) * zoom + (L/2)
            longueur_piste_ecran = 5000 * zoom # 5km de piste
            rect_piste = pygame.Rect(debut_piste_ecran, pos_sol_y, longueur_piste_ecran, H)
            
            if rect_piste.colliderect((-500,0,L+1000,H)): # Large clipping
                pygame.draw.rect(fenetre, SOL_PISTE, rect_piste)
                # Marquages piste
                pygame.draw.rect(fenetre, SOL_MARQUAGE, (debut_piste_ecran, pos_sol_y, longueur_piste_ecran, 4*zoom))
                
                # Bandes (Optimisé)
                step_bandes = 100 * zoom
                if step_bandes < 1: step_bandes = 1
                nb_bandes = int(longueur_piste_ecran / step_bandes)
                
                # On ne dessine que ce qui est visible
                for i in range(nb_bandes):
                    bx = debut_piste_ecran + (i * step_bandes)
                    bw = 50 * zoom
                    bh = 10 * zoom
                    if -100 < bx < L+100:
                        pygame.draw.rect(fenetre, SOL_MARQUAGE, (bx, pos_sol_y + 20*zoom, bw, bh))
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
    # 1. Analogique (Bas)
    dessiner_dashboard(fenetre, vitesse_kph, altitude, moteur_allume, flaps_sortis, pilote_auto_actif, freins_actifs, lumiere_allume, niveau_poussee_reelle, heure_actuelle, world_x, RUNWAYS, vy, angle)
    
    # 2. HUD Overlay (Haut)
    dessiner_hud_overlay(fenetre, vitesse_kph, altitude, angle, vy)
    
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

    # Fin de boucle

    pygame.display.flip()

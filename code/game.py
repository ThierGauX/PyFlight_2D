import pygame
import math
import os
import random
import datetime # Pour l'heure réelle
import argparse
import sys
import time
import array # Pour generation son
import json # Pour sauvegarder les scores

def resource_path(relative_path):
    import os, sys
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def generer_son_vent():
    # Génération de bruit blanc simple (1 seconde)
    freq = 44100
    duration = 2.0 
    n_samples = int(freq * duration)
    # 16-bit signed (-32768 to 32767)
    # On génère des valeurs aléatoires
    # Stereo : L, R, L, R...
    
    # On va faire simple: un bytearray
    # Mais Sound attend un buffer compatible.
    # array 'h' = signed short (2 bytes)
    buf = array.array('h', [int(random.gauss(0, 5000)) for _ in range(n_samples * 2)])
    return pygame.mixer.Sound(buffer=buf)


# --- ARGUMENTS (Lancement depuis le Menu) ---
parser = argparse.ArgumentParser()
parser.add_argument("--time", type=str, default="real", help="Heure de départ (real ou 0-24)")
parser.add_argument("--difficulty", type=str, default="easy", help="easy ou real")
parser.add_argument("--volume", type=float, default=0.5, help="Volume global (0.0-1.0)")
parser.add_argument("--no-hud", action="store_true", help="Desactiver HUD")
parser.add_argument("--no-dash", action="store_true", help="Desactiver Dashboard Analogique")
parser.add_argument("--no-clouds", action="store_true", help="Desactiver Nuages")
parser.add_argument("--no-particles", action="store_true", help="Desactiver Particules")
parser.add_argument("--no-atmo", action="store_true", help="Desactiver Atmosphere")
parser.add_argument("--no-terrain", action="store_true", help="Desactiver Terrain Details")

# Nouveaux Args
parser.add_argument("--unlimited-fuel", action="store_true", help="Carburant illimité")
parser.add_argument("--god-mode", action="store_true", help="Invincible")
parser.add_argument("--no-stall", action="store_true", help="Desactiver le décrochage")
parser.add_argument("--no-gear-crash", action="store_true", help="Desactiver le crash train rentré")
parser.add_argument("--no-wind", action="store_true", help="Desactiver le vent et turbulences")
parser.add_argument("--auto-refuel", action="store_true", help="Ravitaillement auto sur piste")
parser.add_argument("--no-overheat", action="store_true", help="Désactiver la surchauffe Moteur")
parser.add_argument("--static-weight", action="store_true", help="Poids Statique (Ignorer le Fuel)")
parser.add_argument("--weather", type=str, default="clear", choices=["clear", "clouds", "fog"], help="Conditions météo")
parser.add_argument("--terrain-intensity", type=float, default=1.0, help="Multiplicateur de hauteur du relief")
parser.add_argument("--show-trail", action="store_true", help="Fumée acrobatique")
parser.add_argument("--trail-color", type=str, default="white", help="Couleur de la traînée")

parser.add_argument("--fullscreen", action="store_true", help="Plein Ecran")
parser.add_argument("--show-fps", action="store_true", help="Afficher FPS")
parser.add_argument("--season", type=str, default="summer", help="Saison: summer, rain, snow, wind")
parser.add_argument("--aircraft", type=str, default="cessna", help="Type d'avion: cessna, fighter, cargo, acro")
parser.add_argument("--fuel", type=float, default=100.0, help="Carburant initial (%)")
parser.add_argument("--missions", action="store_true", help="Activer le mode Missions (Confort passager, ATC, etc.)")
parser.add_argument("--mission-type", type=str, default="none", choices=["none", "rings", "landing", "cargo"], help="Lancer une mission spécifique au démarrage")
parser.add_argument("--num-birds", type=int, default=20, help="Nombre maximal d'oiseaux")
parser.add_argument("--num-planes", type=int, default=5, help="Nombre maximal d'avions IA")
parser.add_argument("--ui-sounds", action="store_true", help="Activer les sons d'interface (Clics)")

parser.add_argument("--multiplayer", action="store_true", help="Activer le multijoueur UDP")
parser.add_argument("--ip", type=str, default="127.0.0.1", help="IP du serveur")
parser.add_argument("--pseudo", type=str, default="Pilote_1", help="Pseudo du joueur")

# Upgrades Carrière
parser.add_argument("--upg-engine", type=int, default=0, help="Niveau d'amélioration moteur (0-5)")
parser.add_argument("--upg-finesse", type=int, default=0, help="Niveau d'amélioration finesse (0-5)")
parser.add_argument("--upg-fuel", type=int, default=0, help="Niveau d'amélioration carburant (0-5)")
parser.add_argument("--upg-weight", type=int, default=0, help="Niveau d'amélioration poids (0-5)")
parser.add_argument("--upg-gear", type=int, default=0, help="Niveau d'amélioration train d'atterrissage (0-5)")
parser.add_argument("--upg-cooling", type=int, default=0, help="Niveau d'amélioration refroidissement (0-5)")
parser.add_argument("--upg-brakes", type=int, default=0, help="Niveau d'amélioration freins (0-5)")

# On parse systématiquement pour que ça marche aussi quand importé par menu.py
args, unknown = parser.parse_known_args()

if args.multiplayer:
    args.num_planes = 0

# Valeurs par défaut de secours si jamais args est None (peu probable ici)
if args is None:
    args = argparse.Namespace(time="real", difficulty="easy", volume=0.5, 
                              no_hud=False, no_dash=False, no_clouds=False, 
                              no_particles=False, no_atmo=False, no_terrain=False,
                              unlimited_fuel=False, god_mode=False, fullscreen=False, show_fps=False,
                              season="summer", aircraft="cessna", fuel=100.0,
                              no_stall=False, no_gear_crash=False, no_wind=False, auto_refuel=False,
                              no_overheat=False, static_weight=False,
                              terrain_intensity=1.0, show_trail=False, trail_color="white", weather="clear", missions=False, mission_type="none",
                              num_birds=20, num_planes=5, ui_sounds=False)

# AIRCRAFT CONFIGS
AIRCRAFT_CONFIGS = {
    "cessna": {
        "mass": 1000.0,
        "thrust_max": 3000.0,
        "v_vne": 300,
        "drag_factor": 0.008,
        "lift_factor": 0.1,
        "fuel_rate": 0.005,
        "rot_speed": 2.0
    },
    "fighter": {
        "mass": 5000.0,
        "thrust_max": 7500.0,
        "v_vne": 1500,
        "drag_factor": 0.004,
        "lift_factor": 0.07,
        "fuel_rate": 0.020,
        "rot_speed": 3.0
    },
    "cargo": {
        "mass": 20000.0,
        "thrust_max": 6000.0,
        "v_vne": 500,
        "drag_factor": 0.020,
        "lift_factor": 0.25,
        "fuel_rate": 0.015,
        "rot_speed": 0.8
    },
    "acro": {
        "mass": 800.0,
        "thrust_max": 4000.0,
        "v_vne": 450,
        "drag_factor": 0.010,
        "lift_factor": 0.15,
        "fuel_rate": 0.010,
        "rot_speed": 4.5
    }
}

current_ac = AIRCRAFT_CONFIGS.get(args.aircraft, AIRCRAFT_CONFIGS["cessna"])


# --- INITIALISATION ---
pygame.init()
try:
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.mixer.init()
except: 
    print("Erreur initialisation module son")

# --- FENETRE ---
if args.fullscreen:
    # On récupère la résolution native du moniteur pour éviter la pixelisation
    info = pygame.display.Info()
    L, H = info.current_w, info.current_h
    flags = pygame.FULLSCREEN
else:
    L, H = 1200, 700
    flags = 0

# Facteur d'échelle pour l'UI (basé sur la hauteur originale de 700)
UI_SCALE = H / 700.0
def s(v): return int(v * UI_SCALE)

fenetre = pygame.display.set_mode((L, H), flags)
pygame.display.set_caption("Pyflight 2D")

# --- RESSOURCES ---
dossier = os.path.dirname(os.path.abspath(__file__))
dossier_parent = os.path.dirname(dossier)

if getattr(sys, 'frozen', False):
    dossier_img = os.path.join(sys._MEIPASS, "image")
    dossier_son = os.path.join(sys._MEIPASS, "son")
else:
    dossier_img = os.path.join(dossier_parent, "image")
    dossier_son = os.path.join(dossier_parent, "son")


images_ok = False
son_moteur = None
son_alarme = None

loaded_aircraft_images = {}
# 1. IMAGES
try:
    aircraft_image_files = {
        "cessna": "Avion_Cessna_172-removebg-preview.png",
        "acro": "Avion_acrobatique-removebg-preview.png",
        "cargo": "Avion_cargo-removebg-preview.png",
        "fighter": "Avion_de_chasse_sans_r-removebg-preview.png"
    }
    
    for ac_type, file_name in aircraft_image_files.items():
        p = os.path.join(dossier_img, file_name)
        if os.path.exists(p):
            loaded_aircraft_images[ac_type] = pygame.image.load(p).convert_alpha()
            
    # Fighter Gear Down
    path_fighter_gear = os.path.join(dossier_img, "Avion_de_chasse-removebg-preview.png")
    if os.path.exists(path_fighter_gear):
        loaded_aircraft_images["fighter_gear_down"] = pygame.image.load(path_fighter_gear).convert_alpha()
    else:
        loaded_aircraft_images["fighter_gear_down"] = loaded_aircraft_images.get("fighter")

    img_avion_normal_base = loaded_aircraft_images.get(args.aircraft, list(loaded_aircraft_images.values())[0] if loaded_aircraft_images else None)
    img_avion_feu_base = img_avion_normal_base

    path_aeroport = os.path.join(dossier_img, "aeroport.png")
    if os.path.exists(path_aeroport):
        img_aeroport_base = pygame.image.load(path_aeroport).convert_alpha()
    else:
        img_aeroport_base = None
        
    images_ok = len(loaded_aircraft_images) > 0
except Exception as e:
    img_aeroport_base = None
    print(f"Erreur Images: {e}")

# 2. SONS
chemins_moteur = ["moteur.mp3", "moteur.wav", "moteur_neuf.wav", "Moteur.ogg"]
for nom in chemins_moteur:
    p = os.path.join(dossier_son, nom)
    if os.path.exists(p):
        try:
            son_moteur = pygame.mixer.Sound(p)
            son_moteur.set_volume(args.volume)
            break
        except: pass

try:
    p_alarme = os.path.join(dossier_son, "alarme_decrochage.wav")
    if os.path.exists(p_alarme):
        son_alarme = pygame.mixer.Sound(p_alarme)
        son_alarme.set_volume(args.volume)
except: pass

son_clic = None
try:
    if args.ui_sounds:
        p_clic = os.path.join(dossier_son, "clique.mp3")
        if os.path.exists(p_clic):
            son_clic = pygame.mixer.Sound(p_clic)
            son_clic.set_volume(args.volume)
except: pass

son_tonnerre = None
try:
    p_ton = os.path.join(dossier_son, "tonnerre.mp3")
    if os.path.exists(p_ton):
        son_tonnerre = pygame.mixer.Sound(p_ton)
        son_tonnerre.set_volume(args.volume)
except: pass

# 3. GENERATION SON VENT
son_vent = None
try:
    son_vent = generer_son_vent()
    son_vent.set_volume(0.0)
except Exception as e:
    print(f"Erreur Vent: {e}")


# --- PALETTE GRAPHIQUE ---
# Couleurs de base (définitions)
C_CIEL_JOUR_BAS = (135, 206, 235)
C_CIEL_JOUR_HAUT = (10, 20, 40)
C_CIEL_NUIT_BAS = (20, 20, 40)
C_CIEL_NUIT_HAUT = (0, 0, 10)
C_SOL_JOUR_FONCE = (20, 60, 20)
C_SOL_JOUR_CLAIR = (50, 120, 50)
C_SOL_NUIT_FONCE = (5, 15, 5)
C_SOL_NUIT_CLAIR = (10, 30, 10)

C_CIEL_COUCHER_BAS = (255, 100, 50)
C_CIEL_COUCHER_HAUT = (50, 20, 40)
C_SOL_COUCHER_FONCE = (15, 30, 15)
C_SOL_COUCHER_CLAIR = (25, 60, 25)

# Variables globales de couleur (seront mises à jour)
CIEL_HAUT = C_CIEL_JOUR_HAUT      
CIEL_BAS  = C_CIEL_JOUR_BAS   
SOL_HERBE_BASE = (34, 100, 34) 
SOL_HERBE_FONCE = C_SOL_JOUR_FONCE
SOL_HERBE_CLAIR = C_SOL_JOUR_CLAIR
SOL_PISTE = (50, 50, 55)      
C_SOL_PISTE_JOUR = (50, 50, 55)
C_SOL_PISTE_NUIT = (10, 10, 15)
SOL_MARQUAGE = (240, 240, 240)
COLOR_TREE_LEAF = (20, 100, 20)
COLOR_TREE_TRUNK = (100, 60, 20)




# COULEURS COCKPIT
DASH_BG = (30, 32, 36)         
DASH_PANEL = (10, 10, 12)      
HUD_VERT = (0, 255, 100)       
HUD_ROUGE = (255, 50, 50)
HUD_ORANGE = (255, 160, 0)
TXT_GRIS = (150, 150, 150)     

# Polices
police_label = pygame.font.SysFont("arial", int(12 * UI_SCALE), bold=True)
police_valeur = pygame.font.SysFont("consolas", int(22 * UI_SCALE), bold=True)
police_alarme = pygame.font.SysFont("arial", int(28 * UI_SCALE), bold=True)

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

# HISTORIQUE POSITION (Map)
position_history = []
history_timer = 0
crash_sites = [] # Stocke la liste de tous les (world_x, altitude) de crash
explosions = [] # Stocke les particules d'explosion
ground_spray = []
eclair_timer = 0
tonnerre_timer = 0

pilote_auto_actif = (args.difficulty == "easy")
zoom = 1.0          
zoom_cible = 1.0    

moteur_allume = False 
flaps_sortis = False
gear_sorti = True
lumiere_allume = False # Landing Light

# CYCLE JOUR / NUIT (Heure et Cycle)
mode_temps_reel = (args.time == "real")
mode_temps_dynamique = (args.time == "dynamic")
offset_temps = 12.0
if not mode_temps_reel and not mode_temps_dynamique:
    try:
        offset_temps = float(args.time)
    except:
        offset_temps = 12.0

heure_actuelle = offset_temps if not mode_temps_reel else 12.0
if mode_temps_dynamique:
    heure_actuelle = 8.0 # On commence à 8h en dynamique par défaut

est_nuit = False

# GESTION POUSSEE
niveau_poussee_reelle = 0.0 
target_poussee = 0.0        


# DÉCOR
decor_sol = []
# On stocke juste la position et la taille, la couleur sera calculée dynamiquement
for _ in range(250): # Un peu plus de patches
    w = random.randint(20, 100)
    h = random.randint(4, 15)
    x_offset = random.randint(0, 4000) # Etalé sur 4km au lieu de 2km pour diversité
    y_offset = random.randint(0, 800)
    # Type 0 = FONCE, Type 1 = CLAIR, Type 2 = ARBRE
    r = random.random()
    if r < 0.45: type_decor = 0
    elif r < 0.90: type_decor = 1
    else: type_decor = 2 # Arbre
        
    decor_sol.append([x_offset, y_offset, w, h, type_decor])

# GENERATION AEROPORTS
# (Déplacé après la déclaration de la classe Airport)
airports = []
RUNWAYS = []

# Mapping des couleurs pour la fumée
TRAIL_COLORS = {
    "white": (240, 240, 240),
    "red": (255, 50, 50),
    "blue": (50, 100, 255),
    "green": (50, 255, 50),
    "yellow": (255, 255, 50)
}
current_trail_color = TRAIL_COLORS.get(args.trail_color, (240, 240, 240))

# Liste des traînées de condensation [x, y, life, size_multiplier]
contrails = [] 
particules = []
nb_particules = 1000 # Beaucoup plus de particules (Pluie/Neige)
if args.season in ["summer", "spring"] and not args.season == "wind":
    nb_particules = 50 # Peu de particules en été/printemps (juste un peu de pollen/vent ?)
if args.no_particles: nb_particules = 0

for _ in range(nb_particules): 
    # x, y, speed_factor, type/size
    particules.append([random.randint(0, L), random.randint(0, H), random.uniform(0.5, 2.0), random.randint(1, 3)])

# --- CLOUDS & BIRDS & RUNWAYS ---
# --- CLOUDS & BIRDS & RUNWAYS ---
class Cloud:
    def __init__(self):
        self.reset(random_start=True)
        
    def reset(self, random_start=False):
        # Rayon beaucoup plus large (15km) pour ne pas voir d'amas quand on dézoome
        self.x = float(random.randint(-15000, 15000)) if random_start else 16000.0
        self.y = float(random.randint(-3000, -200)) # Plus haut
        self.depth = random.uniform(0.1, 0.9) 
        
        # Scale: plus gros si plus haut
        base_scale_max = 3.0
        if self.y < -1500: base_scale_max = 6.0 # TRES GROS NUAGE HAUTE ALTITUDE
        
        self.scale = random.uniform(1.0, base_scale_max) * self.depth
        
        # Generation Image Nuage (Pre-render)
        mult = 3.0 if args.weather == "clouds" else 1.0
        w_cloud = int(random.randint(150, 300) * self.scale * mult)
        h_cloud = int(random.randint(80, 150) * self.scale * mult)
        self.image = pygame.Surface((w_cloud, h_cloud), pygame.SRCALPHA)
        
        base_color = random.randint(230, 255)
        # Plus opaque si météo nuageuse
        alpha_base = 60 if args.weather == "clouds" else 20
        color = (base_color, base_color, base_color, alpha_base + int(40 * self.depth))
        
        # Puffs
        num_puffs = random.randint(10, 20) if args.weather == "clouds" else random.randint(5, 10)
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
        
        if self.x < -16000: self.reset()

    def draw(self, surface, cam_x, cam_y, zoom):
        eff_cam_x = cam_x * self.depth
        px = (self.x - eff_cam_x) * zoom + (L/2)
        py = (self.y - cam_y) * zoom + (H/2)
        
        # Optimisation Sortie écran (Horizontale ET Verticale)
        if px < -1000 or px > L + 1000 or py < -500 or py > H + 500: return

        # Transparence dynamique selon le zoom (plus on dézoome, plus ils s'effacent)
        # On évite que des milliers de nuages satures l'écran de blanc au loin
        alpha_scale = 1.0
        if zoom < 0.2:
            alpha_scale = max(0.0, zoom / 0.2)
        if alpha_scale <= 0: return

        # Scale image selon zoom
        w_new = int(self.image.get_width() * zoom)
        h_new = int(self.image.get_height() * zoom)
        
        if w_new > 1 and h_new > 1:
            img_scaled = pygame.transform.scale(self.image, (w_new, h_new))
            
            # Application alpha dynamique
            if alpha_scale < 1.0:
                img_scaled.set_alpha(int(255 * alpha_scale))

            if est_nuit:
                # Assombrir la surface grossierement (fill multiply)
                img_scaled.fill((100, 100, 120), special_flags=pygame.BLEND_MULT)
                
            surface.blit(img_scaled, (px, py))

# Plus de nuages si météo nuageuse
num_clouds = 40 if args.weather != "clouds" else 80
clouds = [Cloud() for _ in range(num_clouds)]
ai_planes = []
bombs = []
missiles = []

class Bird:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
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

birds = [Bird() for _ in range(args.num_birds)]

def spawn_explosion(x, y, vx, vy):
    # Génère une explosion massive de particules (feu/fumée)
    print(f"DEBUG: spawning explosion at {x}, {y} with v=({vx}, {vy})")
    if args.no_particles: return
    for _ in range(300): # 300 particules pour une explosion énorme
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(20, 150) # Vitesse très rapide (immédiat)
        # Expansion sphérique beaucoup plus forte, plus la vélocité
        p_vx = math.cos(rad) * speed
        p_vy = math.sin(rad) * speed
        # Durée de vie plus longue pour profiter du spectacle
        life = random.uniform(1.0, 3.0) 
        # [x, y, vx, vy, vie, vie_initiale, couleur, taille]
        color = random.choice([(255,50,0), (255,100,0), (255,200,0), (200,30,0), (80,80,80), (40,40,40), (20,20,20)])
        explosions.append([x, y, p_vx, p_vy, life, life, color, 80])

# --- MISSIONS & CHALLENGES ---
class Ring:
    def __init__(self, x, y, radius=50):
        self.x = x
        self.y = y
        self.radius = radius
        self.passed = False
        
    def draw(self, surface, cam_x, cam_y, zoom):
        px = (self.x - cam_x) * zoom + (L/2)
        py = (self.y - cam_y) * zoom + (H/2)
        pr = self.radius * zoom
        
        if px < -pr or px > L+pr: return
        
        color = (255, 215, 0) # Gold
        if self.passed: color = (0, 255, 0) # Green
        
        pygame.draw.circle(surface, color, (px, py), pr, 2)
        # Inner glow
        if not self.passed:
            s = pygame.Surface((pr*2, pr*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 215, 0, 50), (pr, pr), pr)
            surface.blit(s, (px-pr, py-pr))

class CargoBox:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.active = True

    def update(self):
        if not self.active: return
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.12 # GRAVITE
        
        # friction aerodynamique simple
        self.vx *= 0.99
        self.vy *= 0.99
        
    def draw(self, surface, cam_x, cam_y, zoom):
        if not self.active: return
        px = (self.x - cam_x) * zoom + (L/2)
        py = (self.y - cam_y) * zoom + (H/2)
        pr = max(2, 5 * zoom)
        pygame.draw.rect(surface, (150, 100, 50), (px-pr, py-pr, pr*2, pr*2))

class AIPlane:
    def __init__(self, wx, airports_list):
        self.active = True
        self.mode = "cruise"
        self.aircraft = random.choice(["cessna", "cargo", "fighter", "acro"])
        
        closest_apt = min(airports_list, key=lambda a: abs(a.x_start - wx))
        
        if self.mode == "cruise":
            self.x = wx + random.choice([-20000, 20000]) # Spawns far away
            self.y = -random.randint(2000, 4500) # Maximum altitude 4500m (Y is negative)
            self.vx = random.uniform(150, 250) * (1 if self.x < wx else -1)
            self.vy = 0
            self.dir_x = 1 if self.vx > 0 else -1
            
        elif self.mode == "takeoff":
            apt = closest_apt if random.random() < 0.7 else random.choice(airports_list)
            self.dir_x = random.choice([1, -1])
            self.x = apt.x_start + (500 if self.dir_x == 1 else apt.width - 500)
            self.y = 0
            self.vx = 10 * self.dir_x
            self.target_vx = random.uniform(150, 200) * self.dir_x
            self.vy = 0
            
        elif self.mode == "landing":
            apt = closest_apt if random.random() < 0.7 else random.choice(airports_list)
            self.dir_x = random.choice([-1, 1])
            dist_app = 15000
            self.x = (apt.x_start + apt.width/2) - self.dir_x * dist_app
            self.y = -2000
            self.vx = 150 * self.dir_x
            self.vy = 2000 / (dist_app / 150) # Descente
        
    def update(self, wx, dt):
        if not self.active: return
        
        if self.mode == "cruise":
            self.x += self.vx * dt
            if abs(self.x - wx) > 30000:
                self.active = False
                
        elif self.mode == "takeoff":
            if abs(self.vx) < abs(self.target_vx):
                self.vx += 15 * dt * self.dir_x
            self.x += self.vx * dt
            
            if abs(self.vx) > 100:
                self.vy -= 15 * dt
                if self.vy < -40: self.vy = -40
            self.y += self.vy * dt
            
            if self.y < -4500:
                self.y = -4500
                self.mode = "cruise"
                self.vy = 0
            if abs(self.x - wx) > 30000:
                self.active = False
                
        elif self.mode == "landing":
            self.x += self.vx * dt
            self.y += self.vy * dt
            
            if self.y >= 0:
                self.y = 0
                self.vy = 0
                self.vx -= 15 * dt * self.dir_x
                if (self.dir_x == 1 and self.vx <= 0) or (self.dir_x == -1 and self.vx >= 0):
                    self.active = False
            
            if abs(self.x - wx) > 30000:
                self.active = False
            
    def draw(self, surface, cam_x, cam_y, zoom):
        if not self.active: return
        px = (self.x - cam_x) * zoom + (L/2)
        py = (self.y - cam_y) * zoom + (H/2)
        
        # Don't draw if outside screen
        if px < -200 or px > L+200 or py < -200 or py > H+200: return
        
        # Angle calc (avec valeur absolue sur vx pour gérer le flip séparément)
        vx_safe = abs(self.vx) if self.vx != 0 else 1
        angle = math.degrees(math.atan2(-self.vy, vx_safe))
        
        # Define baseline width for contrails and rendering
        scale_f = {"cessna": 1.0, "acro": 0.8, "fighter": 1.5, "cargo": 2.5}.get(self.aircraft, 1.0)
        pw = max(5, int(80 * scale_f * zoom))
        
        if images_ok:
            img_base = loaded_aircraft_images.get(self.aircraft, img_avion_normal_base)
            target_h = max(2, int(img_base.get_height() * (pw / img_base.get_width())))
            img_scaled = pygame.transform.scale(img_base, (pw, target_h))
            
            if self.dir_x == -1:
                img_scaled = pygame.transform.flip(img_scaled, True, False)
                
            s_plane_rot = pygame.transform.rotate(img_scaled, angle)
        else:
            # Draw a small shape (simple rect for distant plane) fallback
            pw = 40 * zoom # Plus grand pour être mieux vu
            ph = 12 * zoom
            s_plane = pygame.Surface((pw, ph), pygame.SRCALPHA)
            pygame.draw.rect(s_plane, (40, 40, 40), (0, 0, pw, ph)) # Plus sombre pour contraste
            s_plane_rot = pygame.transform.rotate(s_plane, angle if self.dir_x == 1 else -angle)

        r = s_plane_rot.get_rect(center=(px, py))
        surface.blit(s_plane_rot, r)

import socket
import json
import threading

network_players = {}
udp_socket = None
network_frame_count = 0

if args.multiplayer:
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setblocking(False)

class NetworkPlayer:
    def __init__(self, pseudo, aircraft):
        self.pseudo = pseudo
        self.x = 0
        self.y = 0
        self.angle = 0
        self.active = True
        self.aircraft = aircraft
        self.last_update = time.time()
        
    def draw(self, surface, cam_x, cam_y, zoom):
        px = (self.x - cam_x) * zoom + (L/2)
        py = (self.y - cam_y) * zoom + (H/2)
        
        if px < -200 or px > L+200 or py < -200 or py > H+200: return
        
        scale_f = {"cessna": 1.0, "acro": 0.8, "fighter": 1.5, "cargo": 2.5}.get(self.aircraft, 1.0)
        pw = max(5, int(80 * scale_f * zoom))
        
        if images_ok:
            img_base = loaded_aircraft_images.get(self.aircraft, img_avion_normal_base)
            target_h = max(2, int(img_base.get_height() * (pw / img_base.get_width())))
            img_scaled = pygame.transform.scale(img_base, (pw, target_h))
            s_plane_rot = pygame.transform.rotate(img_scaled, self.angle)
        else:
            ph = 12 * zoom
            s_plane = pygame.Surface((pw, ph), pygame.SRCALPHA)
            pygame.draw.rect(s_plane, (40, 40, 40), (0, 0, pw, ph))
            s_plane_rot = pygame.transform.rotate(s_plane, self.angle)

        r = s_plane_rot.get_rect(center=(px, py))
        surface.blit(s_plane_rot, r)
        
        # Draw Pseudo with Dark Background
        lbl = police_label.render(self.pseudo, True, (255, 255, 255))
        lbl_rect = lbl.get_rect(center=(px, py - s(30) - pw/2))
        
        # Background rect
        bg_rect = lbl_rect.inflate(s(10), s(6))
        pygame.draw.rect(surface, (20, 20, 30), bg_rect, border_radius=s(4))
        pygame.draw.rect(surface, (100, 150, 255), bg_rect, 1, border_radius=s(4))
        surface.blit(lbl, lbl_rect)

class Bomb:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.active = True

    def update(self):
        if not self.active: return
        self.x += self.vx
        self.y += self.vy
        self.vy += GRAVITE * 3.0 # Chute plus rapide (demande utilisateur)
        
        # Résistance de l'air légère
        self.vx *= 0.995
        self.vy *= 0.995
        
    def draw(self, surface, cam_x, cam_y, zoom):
        if not self.active: return
        px = (self.x - cam_x) * zoom + (L/2)
        py = (self.y - cam_y) * zoom + (H/2)
        
        # Angle de la bombe basé sur sa trajectoire
        angle_rad = math.atan2(-self.vy, self.vx)
        angle_deg = math.degrees(angle_rad)
        
        bw = 16 * zoom
        bh = 8 * zoom
        if -50 < px < L+50 and -50 < py < H+50:
            # Création d'une surface pour la bombe détaillée
            surf_bomb = pygame.Surface((bw * 2, bh * 2), pygame.SRCALPHA)
            
            # Corps de la bombe (Ellipse)
            pygame.draw.ellipse(surf_bomb, (50, 60, 50), (bw*0.5, bh*0.5, bw, bh))
            
            # Ailerons arrière
            pygame.draw.polygon(surf_bomb, (30, 40, 30), [
                (bw*0.5, bh*0.7), (bw*0.2, bh*0.3), (bw*0.2, bh*1.7), (bw*0.5, bh*1.3)
            ])
            
            # Rotation selon la trajectoire
            surf_rot = pygame.transform.rotate(surf_bomb, angle_deg)
            rect_rot = surf_rot.get_rect(center=(px, py))
            surface.blit(surf_rot, rect_rot)

class Missile:
    def __init__(self, x, y, vx, vy, angle):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.angle = angle
        self.active = True
        self.life = 200
        self.launch_timer = 30 # Environ 0.5s de chute libre
        self.engine_started = False
        
    def update(self):
        if not self.active: return
        
        if self.launch_timer > 0:
            self.launch_timer -= 1
            # Phase de chute : gravité uniquement
            self.vy += GRAVITE * 2.0
            # L'angle suit la trajectoire
            self.angle = math.degrees(math.atan2(-self.vy, self.vx))
        else:
            if not self.engine_started:
                self.engine_started = True
                # Boost initial à l'allumage
                rad = math.radians(self.angle)
                self.vx += math.cos(rad) * 40.0
                self.vy -= math.sin(rad) * 40.0
            
            self.life -= 1
            if self.life <= 0:
                self.active = False
                return
                
            # Propulsion continue
            thrust = 2.0
            rad = math.radians(self.angle)
            self.vx += math.cos(rad) * thrust
            self.vy -= math.sin(rad) * thrust
            
            # Traînée de fumée volumétrique et feu
            if not args.no_particles:
                rad_back = math.radians(self.angle + 180)
                # 1 particule de feu (rapide à mourir)
                explosions.append([self.x, self.y, 
                                   math.cos(rad_back)*2 + random.uniform(-1,1), 
                                   -math.sin(rad_back)*2 + random.uniform(-1,1), 
                                   0.2, 0.2, (255, random.randint(150, 200), 0), 10]) # Rayon feu: 10
                
                # 2-3 particules de fumée épaisse (plus longue durée)
                for _ in range(2):
                    explosions.append([self.x + random.uniform(-5,5), self.y + random.uniform(-5,5), 
                                       math.cos(rad_back)*1 + random.uniform(-0.5,0.5), 
                                       -math.sin(rad_back)*1 + random.uniform(-0.5,0.5), 
                                       random.uniform(0.3, 0.6), 0.6, (60, 60, 60), random.randint(15, 25)]) # Rayon fumée: ~20

        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.995
        self.vy *= 0.995

    def draw(self, surface, cam_x, cam_y, zoom):
        if not self.active: return
        px = (self.x - cam_x) * zoom + (L/2)
        py = (self.y - cam_y) * zoom + (H/2)
        
        if -100 < px < L+100 and -100 < py < H+100:
            bw = 16 * zoom
            bh = 6 * zoom # Plus fin qu'une bombe
            
            # Surface du missile (même base que la bombe)
            surf_m = pygame.Surface((bw * 2, bh * 3), pygame.SRCALPHA)
            
            # Corps (Ellipse grise)
            pygame.draw.ellipse(surf_m, (160, 160, 160), (bw*0.5, bh, bw, bh))
            
            # Nez (plus pointu)
            pygame.draw.polygon(surf_m, (100, 100, 100), [
                (bw*1.5, bh), (bw*1.5 + 5*zoom, bh*1.5), (bw*1.5, bh*2)
            ])
            
            # Ailerons arrière
            pygame.draw.polygon(surf_m, (80, 80, 80), [
                (bw*0.5, bh*1.2), (bw*0.2, bh*0.5), (bw*0.2, bh*2.5), (bw*0.5, bh*1.8)
            ])
            
            # Flamme moteur si allumé
            if self.engine_started and random.random() > 0.1:
                flame_len = random.uniform(8, 20) * zoom
                pygame.draw.polygon(surf_m, (255, 180, 50), [
                    (bw*0.5, bh*1.3), (bw*0.5 - flame_len, bh*1.5), (bw*0.5, bh*1.7)
                ])
            
            surf_rot = pygame.transform.rotate(surf_m, self.angle)
            rect_rot = surf_rot.get_rect(center=(px, py))
            surface.blit(surf_rot, rect_rot)

class MusicPlayer:
    def __init__(self, musique_dir):
        self.musique_dir = musique_dir
        self.playlist = []
        self.current_index = 0
        self.active = False
        self.volume = 0.5
        
        if os.path.exists(musique_dir):
            for f in os.listdir(musique_dir):
                if f.lower().endswith(('.mp3', '.wav', '.ogg')):
                    self.playlist.append(f)
        
        self.playlist.sort()
        
    def toggle(self):
        self.active = not self.active
        if self.active:
            if self.playlist:
                self.play_current()
        else:
            pygame.mixer.music.stop()
            
    def play_current(self):
        if not self.playlist: return
        try:
            p = os.path.join(self.musique_dir, self.playlist[self.current_index])
            pygame.mixer.music.load(p)
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Erreur Lecture Musique: {e}")
            
    def next(self):
        if not self.playlist: return
        self.current_index = (self.current_index + 1) % len(self.playlist)
        if self.active:
            self.play_current()
            
    def update(self):
        # Auto-next at end of song
        if self.active and not pygame.mixer.music.get_busy():
            self.next()
            
    def get_current_title(self):
        if not self.active or not self.playlist:
            return "RADIO: OFF"
        title = self.playlist[self.current_index]
        # On enlève l'extension et on tronque si trop long
        title = os.path.splitext(title)[0]
        if len(title) > 25: title = title[:22] + "..."
        return f"RADIO: {title.upper()}"

dossier_musique = os.path.join(dossier_son, "musique")
music_player = MusicPlayer(dossier_musique)
music_player.volume = args.volume
engine_sound_active = True

def save_session_coins():
    # 1 km = 1 pièce
    distance_km = int(distance_totale_session / 1000.0)
    if distance_km > 0:
        mission_manager.save_career_coins(distance_km)

def save_career_stats():
    # Chemin du fichier
    if getattr(sys, 'frozen', False):
        dossier_exe = os.path.dirname(sys.executable)
        path_career = os.path.join(dossier_exe, "career.json")
    else:
        dossier = os.path.dirname(os.path.abspath(__file__))
        path_career = os.path.join(dossier, "career.json")
        
    data = {"coins": 0, "upgrades": {}, "stats": {"max_speed": 0, "max_alt": 0, "total_dist": 0, "total_landings": 0, "total_crashes": 0}}
    if os.path.exists(path_career):
        try:
            with open(path_career, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                data.update(loaded)
                if "stats" not in data: data["stats"] = {"max_speed": 0, "max_alt": 0, "total_dist": 0, "total_landings": 0, "total_crashes": 0}
        except: pass
        
    # Mise à jour des records
    st = data["stats"]
    st["max_speed"] = max(st.get("max_speed", 0), max_vitesse_session)
    st["max_alt"] = max(st.get("max_alt", 0), max_alt_session)
    st["total_dist"] = st.get("total_dist", 0) + distance_totale_session
    st["total_landings"] = st.get("total_landings", 0) + session_landings
    st["total_crashes"] = st.get("total_crashes", 0) + session_crashes
    
    try:
        with open(path_career, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except: pass

class MenuBar:
    def __init__(self):
        self.height = s(24)
        self.visible = True
        self.active_menu = None
        self.font = pygame.font.SysFont("arial", s(11), bold=True)
        self.item_font = pygame.font.SysFont("arial", s(10))
        
        # Structure des menus
        self.menus = {
            "FICHIER": ["RECOMMENCER", "QUITTER"],
            "AUDIO": ["RADIO ON/OFF", "MOTEUR ON/OFF", "---", "VOLUME MUSIQUE", "MUSIQUE +", "MUSIQUE -", "---", "VOLUME MOTEUR", "BRUITAGES +", "BRUITAGES -"],
            "ENVIR": ["METEO: CLAIR", "METEO: NUAGES", "METEO: BROUILLARD", "TEMPS: MIDI", "TEMPS: NUIT", "TEMPS: DYNAMIQUE", "TEMPS: REEL", "SAISON: ETE", "SAISON: AUTOMNE", "SAISON: HIVER", "SAISON: PRINTEMPS", "SAISON: TEMPÊTE"],
            "AIDES": ["INVINCIBILITÉ", "FUEL ILLIMITÉ", "PAS DE DÉCROCHAGE", "SURCHAUFFE OFF", "POIDS STATIQUE", "PAS DE VENT", "PAS DE CRASH TRAIN"],
            "AFFICHAGE": ["HUD", "TABLEAU DE BORD", "NUAGES", "PARTICULES", "ATMOSPHÈRE", "TERRAIN", "FPS"],
            "APPAREIL": ["CESSNA", "CARGO", "FIGHTER", "ACRO", "RAVITAILLEMENT"],
            "SCORES": ["AFFICHER STATS"]
        }
        
        self.categories = list(self.menus.keys())
        self.cat_rects = []
        self.menu_rects = {} # category -> list of (item_rect, item_text)
        
        self.show_stats_window = False
        
        # Pré-calcul des positions
        x_start = s(10)
        for cat in self.categories:
            text_surf = self.font.render(cat, True, (255, 255, 255))
            w = text_surf.get_width() + s(30)
            self.cat_rects.append(pygame.Rect(x_start, 0, w, self.height))
            x_start += w
            
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            
            # Gestion de la fermeture de la fenêtre Stats
            if self.show_stats_window:
                w_pop, h_pop = s(400), s(300)
                x_pop, y_pop = (L - w_pop) // 2, (H - h_pop) // 2
                pop_rect = pygame.Rect(x_pop, y_pop, w_pop, h_pop)
                
                # Zone du bouton fermer (approximative en bas à droite)
                close_rect = pygame.Rect(x_pop + w_pop - s(120), y_pop + h_pop - s(50), s(110), s(40))
                
                if close_rect.collidepoint(mx, my) or not pop_rect.collidepoint(mx, my):
                    self.show_stats_window = False
                return True # Bloquer les clics si la fenêtre est ouverte
            
            # Clic sur une catégorie
            for i, rect in enumerate(self.cat_rects):
                if rect.collidepoint(mx, my):
                    if self.active_menu == self.categories[i]:
                        self.active_menu = None
                    else:
                        self.active_menu = self.categories[i]
                    return True
            
            # Clic sur un item de menu ouvert
            if self.active_menu:
                if self.active_menu in self.menu_rects:
                    for item_rect, item_text in self.menu_rects[self.active_menu]:
                        if item_rect.collidepoint(mx, my):
                            if item_text == "---": return True
                            self.execute_action(self.active_menu, item_text)
                            # Garder le menu ouvert pour les réglages de volume
                            if not ("+" in item_text or "-" in item_text):
                                self.active_menu = None
                            return True
            
            # Fermer le menu si on clique ailleurs
            self.active_menu = None
        return False

    def execute_action(self, cat, item):
        global args, fuel, autopilot_active, show_minimap, show_large_map, mtemp, sfx_volume, engine_sound_active
        global mode_temps_reel, mode_temps_dynamique, heure_actuelle, offset_temps, SOL_HERBE_BASE, SOL_HERBE_FONCE, SOL_HERBE_CLAIR, CIEL_BAS, CIEL_HAUT, SOL_PISTE, nb_particules, particules
        
        if cat == "FICHIER":
            if item == "RECOMMENCER": 
                save_session_coins()
                save_career_stats()
                if getattr(sys, 'frozen', False):
                    os.execl(sys.executable, sys.executable, *sys.argv)
                else:
                    os.execl(sys.executable, sys.executable, sys.argv[0], *sys.argv[1:])
            if item == "QUITTER": 
                save_session_coins()
                save_career_stats()
                pygame.quit(); sys.exit()
            
        elif cat == "AUDIO":
            if item == "RADIO ON/OFF": music_player.toggle()
            if item == "MOTEUR ON/OFF": 
                engine_sound_active = not engine_sound_active
                update_sfx_volume()
            if item == "MUSIQUE +": music_player.volume = min(1.0, music_player.volume + 0.1); pygame.mixer.music.set_volume(music_player.volume)
            if item == "MUSIQUE -": music_player.volume = max(0.0, music_player.volume - 0.1); pygame.mixer.music.set_volume(music_player.volume)
            if item == "BRUITAGES +": 
                args.volume = min(1.0, args.volume + 0.1)
                update_sfx_volume()
            if item == "BRUITAGES -": 
                args.volume = max(0.0, args.volume - 0.1)
                update_sfx_volume()
                
        elif cat == "ENVIR":
            if "METEO" in item:
                m_val = item.split(": ")[1]
                m_map = {"CLAIR": "clear", "NUAGES": "clouds", "BROUILLARD": "fog"}
                args.weather = m_map.get(m_val, "clear")
            elif "TEMPS" in item:
                t = item.split(": ")[1]
                mode_temps_reel = (t == "REEL")
                mode_temps_dynamique = (t == "DYNAMIQUE")
                if t == "MIDI": offset_temps = 12.0
                if t == "NUIT": offset_temps = 0.0
            elif "SAISON" in item:
                s_val = item.split(": ")[1]
                mapping = {"ETE": "summer", "AUTOMNE": "autumn", "HIVER": "snow", "PRINTEMPS": "spring", "TEMPÊTE": "wind"}
                args.season = mapping.get(s_val, "summer")
                # Appliquer les couleurs de saison
                update_season_visuals()

        elif cat == "AIDES":
            if item == "INVINCIBILITÉ": args.god_mode = not args.god_mode
            if item == "FUEL ILLIMITÉ": 
                args.unlimited_fuel = not args.unlimited_fuel
                if args.unlimited_fuel: fuel = 100.0
            if item == "PAS DE DÉCROCHAGE": args.no_stall = not args.no_stall
            if item == "SURCHAUFFE OFF": args.no_overheat = not args.no_overheat
            if item == "POIDS STATIQUE": args.static_weight = not args.static_weight
            if item == "PAS DE VENT": args.no_wind = not args.no_wind
            if item == "PAS DE CRASH TRAIN": args.no_gear_crash = not args.no_gear_crash

        elif cat == "AFFICHAGE":
            if item == "HUD": args.no_hud = not args.no_hud
            if item == "TABLEAU DE BORD": args.no_dash = not args.no_dash
            if item == "NUAGES": args.no_clouds = not args.no_clouds
            if item == "PARTICULES": args.no_particles = not args.no_particles; update_particles()
            if item == "ATMOSPHÈRE": args.no_atmo = not args.no_atmo
            if item == "TERRAIN": args.no_terrain = not args.no_terrain
            if item == "FPS": args.show_fps = not args.show_fps

        elif cat == "APPAREIL":
            if item == "RAVITAILLEMENT":
                if altitude < 5 and vitesse_kph < 10: fuel = 100.0
            else:
                switch_aircraft(item.lower())
            
        elif cat == "SCORES":
            if item == "AFFICHER STATS": self.show_stats_window = not self.show_stats_window

    def draw(self, surface):
        # Barre principale
        pygame.draw.rect(surface, (20, 20, 20, 200), (0, 0, L, self.height))
        pygame.draw.line(surface, (60, 60, 60), (0, self.height), (L, self.height), 1)
        
        mx, my = pygame.mouse.get_pos()
        
        for i, rect in enumerate(self.cat_rects):
            cat = self.categories[i]
            hover = rect.collidepoint(mx, my) or self.active_menu == cat
            
            if hover:
                pygame.draw.rect(surface, (60, 60, 70), rect)
            
            text_surf = self.font.render(cat, True, (255, 255, 255))
            surface.blit(text_surf, (rect.x + s(15), rect.y + (self.height - text_surf.get_height())//2))
            
            # Dessin du menu déroulant si actif
            if self.active_menu == cat:
                self.draw_dropdown(surface, cat, rect.x, self.height)

        # Fenêtre Stats si active
        if self.show_stats_window:
            self.draw_stats_popup(surface)

    def draw_dropdown(self, surface, cat, x, y):
        items = self.menus[cat]
        item_h = s(25)
        menu_w = s(180)
        menu_h = len(items) * item_h
        
        # Fond du menu
        pygame.draw.rect(surface, (30, 30, 35), (x, y, menu_w, menu_h))
        pygame.draw.rect(surface, (100, 100, 100), (x, y, menu_w, menu_h), 1)
        
        self.menu_rects[cat] = []
        mx, my = pygame.mouse.get_pos()
        
        for i, item in enumerate(items):
            item_rect = pygame.Rect(x, y + i * item_h, menu_w, item_h)
            
            if item == "---":
                pygame.draw.line(surface, (60, 60, 70), (x + s(10), y + i * item_h + item_h//2), (x + menu_w - s(10), y + i * item_h + item_h//2), 1)
                self.menu_rects[cat].append((item_rect, item))
                continue

            hover = item_rect.collidepoint(mx, my)
            if hover:
                pygame.draw.rect(surface, (50, 80, 150), item_rect)
            
            # Affichage spécial pour les volumes
            display_text = item
            if item == "VOLUME MUSIQUE":
                display_text = f"MUSIQUE: {int(music_player.volume * 100)}%"
            elif item == "VOLUME MOTEUR":
                display_text = f"MOTEUR: {int(args.volume * 100)}%"
            
            # Ajout d'une coche pour les toggles (approximation)
            prefix = ""
            if cat in ["AIDES", "AFFICHAGE", "ENVIR"] or item in ["RADIO ON/OFF", "MOTEUR ON/OFF"]:
                if self.is_option_active(item): prefix = "[x] "
                else: prefix = "[ ] "
                
            text_surf = self.item_font.render(prefix + display_text, True, (220, 220, 220))
            if "VOLUME" in item:
                text_surf = self.item_font.render(display_text, True, (150, 200, 255))
                
            surface.blit(text_surf, (item_rect.x + s(10), item_rect.y + (item_h - text_surf.get_height())//2))
            self.menu_rects[cat].append((item_rect, item))

    def is_option_active(self, item):
        if item == "RADIO ON/OFF": return music_player.active
        if item == "MOTEUR ON/OFF": return engine_sound_active
        if item == "INVINCIBILITÉ": return args.god_mode
        if item == "FUEL ILLIMITÉ": return args.unlimited_fuel
        if item == "PAS DE DÉCROCHAGE": return args.no_stall
        if item == "SURCHAUFFE OFF": return args.no_overheat
        if item == "POIDS STATIQUE": return args.static_weight
        if item == "PAS DE VENT": return args.no_wind
        if item == "PAS DE CRASH TRAIN": return args.no_gear_crash
        if item == "HUD": return not args.no_hud
        if item == "TABLEAU DE BORD": return not args.no_dash
        if item == "NUAGES": return not args.no_clouds
        if item == "PARTICULES": return not args.no_particles
        if item == "ATMOSPHÈRE": return not args.no_atmo
        if item == "TERRAIN": return not args.no_terrain
        if item == "FPS": return args.show_fps
        # Toggles Saison
        if "SAISON: " in item:
            s_map = {"ETE": "summer", "AUTOMNE": "autumn", "HIVER": "snow", "PRINTEMPS": "spring", "TEMPÊTE": "wind"}
            return args.season == s_map.get(item.split(": ")[1], "")
        # Toggles Temps
        if "TEMPS: " in item:
            t_val = item.split(": ")[1]
            if t_val == "REEL": return mode_temps_reel
            if t_val == "DYNAMIQUE": return mode_temps_dynamique
            if t_val == "MIDI": return not mode_temps_reel and not mode_temps_dynamique and offset_temps == 12.0
            if t_val == "NUIT": return not mode_temps_reel and not mode_temps_dynamique and offset_temps == 0.0
        # Toggles Meteo
        if "METEO: " in item:
            m_map = {"CLAIR": "clear", "NUAGES": "clouds", "BROUILLARD": "fog"}
            return args.weather == m_map.get(item.split(": ")[1], "")
        return False

    def draw_stats_popup(self, surface):
        w, h = s(400), s(300)
        x, y = (L-w)//2, (H-h)//2
        pygame.draw.rect(surface, (20, 25, 30), (x, y, w, h))
        pygame.draw.rect(surface, COL_PRIMARY_RGB, (x, y, w, h), 2)
        
        title = self.font.render("STATISTIQUES DE SESSION", True, (255, 255, 255))
        surface.blit(title, (x + s(20), y + s(20)))
        
        stats = [
            f"Vitesse Max: {int(max_vitesse_session)} KPH",
            f"Altitude Max: {int(max_alt_session)} FT",
            f"Distance Parcourue: {distance_totale_session/1000.0:.2f} KM",
            f"Temps de vol: {int(temps_vol_session)//60}m {int(temps_vol_session)%60}s",
            f"Consommation Est.: {int(distance_totale_session * current_ac['fuel_rate'] / 100)} L",
            f"Score Mission: {int(mission_manager.score)} PTS"
        ]
        
        for i, txt in enumerate(stats):
            s_txt = self.item_font.render(txt, True, (200, 200, 200))
            surface.blit(s_txt, (x + s(30), y + s(70) + i * s(30)))
            
        btn_close = self.item_font.render("[ FERMER ]", True, (100, 150, 255))
        surface.blit(btn_close, (x + w - s(100), y + h - s(40)))

# Helpers pour le menu
def update_sfx_volume():
    vol = args.volume if engine_sound_active else 0.0
    if son_moteur: son_moteur.set_volume(vol)
    if son_alarme: son_alarme.set_volume(vol)

def update_season_visuals():
    global SOL_HERBE_BASE, SOL_HERBE_FONCE, SOL_HERBE_CLAIR, SOL_PISTE, CIEL_BAS, CIEL_HAUT
    global C_SOL_JOUR_FONCE, C_SOL_JOUR_CLAIR, C_CIEL_JOUR_BAS, C_CIEL_JOUR_HAUT
    global C_SOL_NUIT_FONCE, C_SOL_NUIT_CLAIR, C_SOL_PISTE_JOUR, C_SOL_PISTE_NUIT
    global C_CIEL_NUIT_BAS, C_CIEL_NUIT_HAUT, C_CIEL_COUCHER_BAS, C_CIEL_COUCHER_HAUT
    global C_SOL_COUCHER_FONCE, C_SOL_COUCHER_CLAIR
    global COLOR_TREE_LEAF, COLOR_TREE_TRUNK
    
    if args.season == "snow":
        # AMBIANCE HIVER
        C_SOL_JOUR_FONCE = (150, 170, 160); C_SOL_JOUR_CLAIR = (230, 250, 240)
        C_SOL_NUIT_FONCE = (40, 50, 45); C_SOL_NUIT_CLAIR = (60, 70, 65)
        C_SOL_PISTE_JOUR = (140, 140, 150); C_SOL_PISTE_NUIT = (40, 40, 45)
        C_CIEL_JOUR_BAS = (190, 200, 210); C_CIEL_JOUR_HAUT = (100, 110, 130)
        C_CIEL_NUIT_BAS = (30, 35, 50); C_CIEL_NUIT_HAUT = (10, 15, 25)
        C_CIEL_COUCHER_BAS = (200, 150, 180); C_CIEL_COUCHER_HAUT = (60, 50, 80)
        C_SOL_COUCHER_FONCE = (80, 90, 100); C_SOL_COUCHER_CLAIR = (120, 130, 150)
        COLOR_TREE_LEAF = (200, 220, 210); COLOR_TREE_TRUNK = (60, 40, 20)
    elif args.season in ["rain", "autumn"]:
        # AMBIANCE AUTOMNE
        C_SOL_JOUR_FONCE = (101, 67, 33); C_SOL_JOUR_CLAIR = (205, 133, 63)
        C_SOL_NUIT_FONCE = (15, 10, 5); C_SOL_NUIT_CLAIR = (25, 20, 10)
        C_SOL_PISTE_JOUR = (60, 60, 65); C_SOL_PISTE_NUIT = (15, 15, 20)
        C_CIEL_JOUR_BAS = (80, 90, 100); C_CIEL_JOUR_HAUT = (30, 35, 45)
        C_CIEL_NUIT_BAS = (15, 15, 25); C_CIEL_NUIT_HAUT = (5, 5, 10)
        C_CIEL_COUCHER_BAS = (180, 80, 40); C_CIEL_COUCHER_HAUT = (40, 20, 20)
        C_SOL_COUCHER_FONCE = (40, 30, 15); C_SOL_COUCHER_CLAIR = (60, 45, 25)
        COLOR_TREE_LEAF = (139, 69, 19); COLOR_TREE_TRUNK = (80, 50, 20)
    elif args.season == "spring":
        # AMBIANCE PRINTEMPS
        C_SOL_JOUR_FONCE = (85, 107, 47); C_SOL_JOUR_CLAIR = (173, 255, 47)
        C_SOL_NUIT_FONCE = (10, 15, 5); C_SOL_NUIT_CLAIR = (20, 30, 10)
        C_SOL_PISTE_JOUR = (50, 50, 55); C_SOL_PISTE_NUIT = (10, 10, 15)
        C_CIEL_JOUR_BAS = (176, 224, 230); C_CIEL_JOUR_HAUT = (70, 130, 180)
        C_CIEL_NUIT_BAS = (15, 25, 30); C_CIEL_NUIT_HAUT = (5, 10, 15)
        C_CIEL_COUCHER_BAS = (255, 180, 100); C_CIEL_COUCHER_HAUT = (100, 80, 120)
        C_SOL_COUCHER_FONCE = (30, 40, 20); C_SOL_COUCHER_CLAIR = (50, 70, 30)
        COLOR_TREE_LEAF = (34, 139, 34); COLOR_TREE_TRUNK = (100, 60, 20)
    elif args.season == "wind":
        # AMBIANCE TEMPÊTE
        C_SOL_JOUR_FONCE = (40, 45, 40); C_SOL_JOUR_CLAIR = (60, 70, 60)
        C_SOL_NUIT_FONCE = (5, 8, 5); C_SOL_NUIT_CLAIR = (10, 15, 10)
        C_SOL_PISTE_JOUR = (40, 45, 50); C_SOL_PISTE_NUIT = (5, 5, 8)
        C_CIEL_JOUR_BAS = (100, 110, 120); C_CIEL_JOUR_HAUT = (40, 45, 50)
        C_CIEL_NUIT_BAS = (10, 10, 15); C_CIEL_NUIT_HAUT = (2, 2, 5)
        C_CIEL_COUCHER_BAS = (80, 70, 80); C_CIEL_COUCHER_HAUT = (20, 20, 25)
        C_SOL_COUCHER_FONCE = (15, 15, 15); C_SOL_COUCHER_CLAIR = (25, 25, 25)
        COLOR_TREE_LEAF = (60, 70, 60); COLOR_TREE_TRUNK = (50, 30, 10)
    else: # Summer
        C_SOL_JOUR_FONCE = (20, 60, 20); C_SOL_JOUR_CLAIR = (50, 120, 50)
        C_SOL_NUIT_FONCE = (5, 15, 5); C_SOL_NUIT_CLAIR = (10, 30, 10)
        C_SOL_PISTE_JOUR = (50, 50, 55); C_SOL_PISTE_NUIT = (10, 10, 15)
        C_CIEL_JOUR_BAS = (135, 206, 235); C_CIEL_JOUR_HAUT = (10, 20, 40)
        C_CIEL_NUIT_BAS = (20, 20, 40); C_CIEL_NUIT_HAUT = (0, 0, 10)
        C_CIEL_COUCHER_BAS = (255, 100, 50); C_CIEL_COUCHER_HAUT = (50, 20, 40)
        C_SOL_COUCHER_FONCE = (15, 30, 15); C_SOL_COUCHER_CLAIR = (25, 60, 25)
        COLOR_TREE_LEAF = (20, 100, 20); COLOR_TREE_TRUNK = (100, 60, 20)
    
    # Update immediate background colors
    SOL_HERBE_FONCE = C_SOL_JOUR_FONCE; SOL_HERBE_CLAIR = C_SOL_JOUR_CLAIR
    SOL_HERBE_BASE = lerp_color(SOL_HERBE_FONCE, SOL_HERBE_CLAIR, 0.5)
    SOL_PISTE = C_SOL_PISTE_JOUR
    CIEL_BAS = C_CIEL_JOUR_BAS; CIEL_HAUT = C_CIEL_JOUR_HAUT
    
    update_particles()

def update_particles():
    global nb_particules, particules
    # Beaucoup plus de particules pour la pluie et la neige (Intensité augmentée)
    nb_particules = 1000 if args.season in ["rain", "snow"] else 50
    if args.no_particles: nb_particules = 0
    particules = []
    for _ in range(nb_particules): 
        particules.append([random.randint(0, L), random.randint(0, H), random.uniform(0.5, 2.0), random.randint(1, 3)])

def switch_aircraft(name):
    global current_ac, PUISSANCE_MOTEUR, FRICTION_AIR, ACCEL_ROTATION, COEFF_PORTANCE, V_DECOLLAGE, V_DECROCHAGE, V_VNE, args, img_avion_normal_base, img_avion_feu_base, fuel_burn_rate
    global UPG_WEIGHT_REDUCTION, UPG_GEAR_CRASH_BONUS, UPG_COOLING_REDUCTION, UPG_BRAKES_POWER_BONUS
    if name in AIRCRAFT_CONFIGS:
        args.aircraft = name
        current_ac = AIRCRAFT_CONFIGS[name]
        
        # Mise a jour des images
        if images_ok:
            img_avion_normal_base = loaded_aircraft_images.get(args.aircraft, list(loaded_aircraft_images.values())[0] if loaded_aircraft_images else None)
            img_avion_feu_base = img_avion_normal_base
                
        # --- APPLICATION DES AMELIORATIONS DU GARAGE (50 Niveaux) ---
        upg_engine_mult = 1.0 + (args.upg_engine * 0.01) # +1% par niveau (+50% max)
        upg_finesse_mult = 1.0 + (args.upg_finesse * 0.005) # +0.5% portance par niveau (+25% max)
        upg_fuel_mult = 1.0 + (args.upg_fuel * 0.02) # +2% capacité par niveau (+100% max)
        
        # Nouveaux paramètres de carrière
        UPG_WEIGHT_REDUCTION = args.upg_weight * 0.01 # -1% par niveau
        UPG_GEAR_CRASH_BONUS = args.upg_gear * 0.02 # +2% par niveau
        UPG_COOLING_REDUCTION = args.upg_cooling * 0.02 # -2% par niveau
        UPG_BRAKES_POWER_BONUS = args.upg_brakes * 0.05 # Influence sur friction_sol
        
        # Re-calcul dynamique des constantes physiques
        PUISSANCE_MOTEUR = (current_ac["thrust_max"] / 8500.0) * upg_engine_mult
        
        drag_reduction = args.upg_finesse * 0.005 # -0.5% trainée par niveau
        drag = current_ac["drag_factor"] * (1.0 - drag_reduction)
        FRICTION_AIR = 1.0 - drag
        
        ACCEL_ROTATION = current_ac["rot_speed"] * 0.02
        COEFF_PORTANCE = (current_ac["lift_factor"] * 0.015) * upg_finesse_mult
        V_VNE = current_ac.get("v_vne", 300)
        
        # Le taux de conso diminue si la capacité augmente
        fuel_burn_rate = current_ac["fuel_rate"] / upg_fuel_mult
        
        # Ajustement des seuils de vitesse selon l'appareil
        if name == "fighter":
            V_DECOLLAGE, V_DECROCHAGE = 180, 150
        elif name == "cargo":
            V_DECOLLAGE, V_DECROCHAGE = 160, 130
        else: # Cessna / Acro
            V_DECOLLAGE, V_DECROCHAGE = 100, 85
            
        mission_manager.message = f"PASSAGE SUR : {name.upper()}"
        mission_manager.timer_message = 180

# Couleur primaire du thème pour le menu
COL_PRIMARY_RGB = (37, 99, 235)

# Variables de session pour les stats
max_vitesse_session = 0
max_alt_session = 0
distance_totale_session = 0
temps_vol_session = 0
session_landings = 0
session_crashes = 0
has_already_landed = False # Pour ne pas compter 50 atterrissages si on reste au sol
session_landings = 0
session_crashes = 0

# Facteurs d'upgrade (initialisés à 0, seront mis à jour par switch_aircraft)
UPG_WEIGHT_REDUCTION = 0.0
UPG_GEAR_CRASH_BONUS = 0.0
UPG_COOLING_REDUCTION = 0.0
UPG_BRAKES_POWER_BONUS = 0.0

menu_bar = MenuBar()

class MissionManager:
    def __init__(self):
        self.active_mission = None # "rings", "landing", None
        self.rings = []
        self.score = 0
        self.message = ""
        self.timer_message = 0
        self.target_landing_zone = None # (x_start, x_end)
        
        self.time_left = -1 # < 0 signifie pas de timer actif. > 0 est un compte à rebours en secondes.
        self.stopwatch_time = 0 # Temps écoulé pour les atterrissages.
        self.mission_over = False # True quand le temps est écoulé ou mission terminée
        self.final_message = ""
        
        # Cargo Missions
        self.cargos = []
        self.cargo_targets = []
        cx = 5000
        for i in range(20):
            self.cargo_targets.append({'x': cx, 'w': 800, 'active': True}) # Cibles plus larges (800)
            cx += random.randint(4000, 15000)
            
    def save_career_coins(self, amount):
        if amount <= 0: return
        # Chemin du fichier
        if getattr(sys, 'frozen', False):
            dossier_exe = os.path.dirname(sys.executable)
            path_career = os.path.join(dossier_exe, "career.json")
        else:
            dossier = os.path.dirname(os.path.abspath(__file__))
            path_career = os.path.join(dossier, "career.json")
            
        data = {"coins": 0, "upgrades": {}}
        if os.path.exists(path_career):
            try:
                with open(path_career, "r", encoding="utf-8") as f:
                    data.update(json.load(f))
            except: pass
            
        data["coins"] += amount
        
        try:
            with open(path_career, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except: pass

    def save_score(self):
        if not self.active_mission: return
        
        # Chemin du fichier
        if getattr(sys, 'frozen', False):
            dossier_exe = os.path.dirname(sys.executable)
            path_scores = os.path.join(dossier_exe, "scores.json")
        else:
            dossier = os.path.dirname(os.path.abspath(__file__))
            path_scores = os.path.join(dossier, "scores.json")
        
        scores_data = {"rings": [], "landing": [], "cargo": []}
        if os.path.exists(path_scores):
            try:
                with open(path_scores, "r", encoding="utf-8") as f:
                    scores_data.update(json.load(f))
            except Exception as e:
                print(f"Erreur de lecture scores : {e}")
                
        # Ajouter le score actuel
        if self.active_mission in scores_data:
            scores_data[self.active_mission].append(self.score)
            
        # Sauvegarder
        try:
            with open(path_scores, "w", encoding="utf-8") as f:
                json.dump(scores_data, f, indent=4)
        except Exception as e:
            print(f"Erreur d'écriture scores : {e}")
            
        # Récompense en pièces (Score direct)
        self.save_career_coins(self.score)
        
    def start_rings_challenge(self, current_x=0):
        self.active_mission = "rings"
        self.rings = []
        self.score = 0
        self.message = "MISSION: RINGS CHALLENGE START! (1 MIN 20)"
        self.timer_message = 180 # 3 sec
        self.time_left = 80.0
        self.mission_over = False
        
        # Trouver la piste la plus proche. La distance entre chaque aéroport est de 75000.
        # Si on est au début (x=0), l'aéroport est à x=0. La piste fait 6000m.
        # En divisant current_x par 75000, on trouve l'index de l'aéroport le plus proche.
        current_i = int(max(0, current_x) / 75000)
        x_start_piste = current_i * 75000
        
        # Commence environ 1 km après la fin de la piste actuelle
        cx = x_start_piste + 7000 
        cy = -500
        
        for i in range(15):
            # Ensure the ring is not spawning inside a mountain
            terrain_h = get_terrain_height(cx)
            # Y est négatif quand on monte. La surface du sol est à -terrain_h.
            # On veut être au-dessus du sol (donc avec un y ENCORE PLUS NEGATIF que la surface)
            min_y = -terrain_h - 150 # At least 150 units above the ground
            
            # Si cy est plus grand que min_y (ex: cy=0 et min_y=-200), le ring est "sous" terre
            if cy > min_y:
                cy = min_y
                
            self.rings.append(Ring(cx, cy, 60))
            cx += 1200 # Espacement doublé (au lieu de 600)
            cy += random.randint(-200, 200) # Un peu plus de variation verticale pour être proportionnel
            
    def start_landing_challenge(self, current_x=0):
        self.active_mission = "landing"
        self.score = 0
        self.message = "MISSION: PRECISION LANDING SUR AEROPORT! (CHRONOMETRÉ)"
        self.timer_message = 240
        self.time_left = -1 # Pas de compte à rebours, mais un chronomètre
        self.stopwatch_time = 0.0
        self.mission_over = False
        
        # Trouver la prochaine piste devant l'avion
        # Les pistes sont à i * 75000
        next_i = int((current_x + 8000) / 75000) + 1
        x_start_piste = next_i * 75000
        
        # On place la cible d'atterrissage sur la première moitié de la piste (la piste fait 6000m)
        self.target_landing_zone = (x_start_piste + 500, x_start_piste + 2500)
        
    def update(self, plane_x, plane_y, plane_vx, plane_vy, dt):
        if self.mission_over:
            return # Le jeu est figé, on ne met plus rien à jour
            
        # Chronomètres et Timers
        if self.active_mission == "landing":
            self.stopwatch_time += dt
        elif self.active_mission == "rings":
            if self.time_left > 0:
                self.time_left -= dt
                if self.time_left <= 0:
                    self.mission_over = True
                    self.final_message = f"TEMPS ÉCOULÉ ! SCORE FINAL : {self.score}"
                    self.save_score()
        elif self.active_mission == "cargo": # Le mode cargo a aussi 3 minutes si défini au lancement
            if self.time_left > 0:
                self.time_left -= dt
                if self.time_left <= 0:
                    self.mission_over = True
                    self.final_message = f"TEMPS ÉCOULÉ ! SCORE FINAL : {self.score}"
                    self.save_score()
                    
        if self.active_mission == "rings":
            for r in self.rings:
                if not r.passed:
                    # Check distance
                    dist = math.sqrt((plane_x - r.x)**2 + (plane_y - r.y)**2)
                    if dist < r.radius:
                        r.passed = True
                        self.score += 100
                        self.message = f"RING PASSED! (+100) [{self.score}]"
                        self.timer_message = 60
                        
        if self.active_mission == "landing" and self.target_landing_zone:
            x1, x2 = self.target_landing_zone
            if x1 <= plane_x <= x2:
                # Vérifier si l'avion est au sol (y proche de 0 sur piste) et quasiment à l'arrêt
                if plane_y >= -5 and abs(plane_vx) < 2 and abs(plane_vy) < 2:
                    # Conversion du temps (stopwatch_time) en score additionnel
                    # Base de 1000 points, -1 point par seconde (max 0)
                    time_bonus = max(0, 1000 - int(self.stopwatch_time) * 10) 
                    self.score += 500 + time_bonus
                    
                    self.mission_over = True
                    self.final_message = f"RÉUSSI EN {int(self.stopwatch_time)}s ! SCORE FINAL : {self.score}"
                    self.save_score()
                    self.timer_message = 300
                    self.target_landing_zone = None
                        
        # Update cargos
        for c in self.cargos:
            if not c.active: continue
            c.update()
            
            # Sol collision (y est négatif dans le jeu pour monter, donc y monte vers le sol = 0)
            terrain_h = get_terrain_height(c.x)
            terrain_z = -terrain_h
            if c.y >= terrain_z: # Hit ground
                c.active = False
                c.y = terrain_z
                
                # Check targets
                hit = False
                for t in self.cargo_targets:
                    if t['active'] and abs(c.x - t['x']) < t['w']/2:
                        hit = True
                        t['active'] = False
                        self.score += 500
                        self.message = f"CIBLE ATTEINTE ! (+500) [{self.score}]"
                        self.timer_message = 180
                        break
                
                if not hit:
                     self.message = "COLIS PERDU..."
                     self.timer_message = 120
                     
                # Check if all targets are inactive
                all_done = True
                for t in self.cargo_targets:
                    if t['active']:
                        all_done = False
                        break
                if all_done:
                    self.mission_over = True
                    self.final_message = f"TOUTES CIBLES ATTEINTES ! SCORE FINAL : {self.score}"
                    self.save_score()

        if self.timer_message > 0:
            self.timer_message -= 1

    def drop_cargo(self, cx, cy, vx, vy):
        self.cargos.append(CargoBox(cx, cy, vx, vy))
        self.message = "COLIS LARGUÉ !"
        self.timer_message = 120
            
    def draw(self, surface, cam_x, cam_y, zoom):
        if self.active_mission == "rings":
            for r in self.rings:
                r.draw(surface, cam_x, cam_y, zoom)
                
        if self.active_mission == "landing":
             if self.target_landing_zone:
                 x1, x2 = self.target_landing_zone
                 px1 = (x1 - cam_x) * zoom + (L/2)
                 px2 = (x2 - cam_x) * zoom + (L/2)
                 py = (0 - cam_y) * zoom + (H/2)
                 
                 if px2 > 0 and px1 < L:
                     s_mission = pygame.Surface(((x2-x1)*zoom, 20*zoom), pygame.SRCALPHA)
                     s_mission.fill((0, 255, 0, 100))
                     surface.blit(s_mission, (px1, py - 20*zoom))
                     l = police_label.render("LAND HERE", True, (0, 255, 0))
                     surface.blit(l, (px1, py - 40*zoom))

        if self.timer_message > 0:
             lbl = police_alarme.render(self.message, True, (255, 255, 0))
             # Centered
             r = lbl.get_rect(center=(L//2, H//4))
             surface.blit(lbl, r)
             
        # Draw cargo targets
        if self.active_mission == "cargo":
            for t in self.cargo_targets:
                if not t['active']: continue
                px = (t['x'] - cam_x) * zoom + (L/2)
                py = (-get_terrain_height(t['x']) - cam_y) * zoom + (H/2)
                pw = t['w'] * zoom
                if -pw < px < L+pw:
                    pygame.draw.rect(surface, (255, 50, 50), (px - pw/2, py - 5*zoom, pw, 10*zoom))
                    pygame.draw.line(surface, (255, 50, 50), (px, py), (px, py - 80*zoom), max(1, int(3*zoom)))
                    if zoom > 0.3:
                        lbl = police_label.render("DROP ZONE", True, (255, 50, 50))
                        surface.blit(lbl, (px - 40, py - 100*zoom))
                        
        # CCIP (Continuously Computed Impact Point) - Aide à la visée
        if self.active_mission == "cargo":
            sim_x = world_x
            sim_y = world_y
            sim_vx = vx
            sim_vy = vy
            for _ in range(400): # Simuler jusqu'à 400 frames
                sim_x += sim_vx
                sim_y += sim_vy
                sim_vy += 0.12
                sim_vx *= 0.99
                sim_vy *= 0.99
                terrain_h = get_terrain_height(sim_x)
                if sim_y >= -terrain_h:
                    sim_y = -terrain_h
                    break
            
            # Dessiner la croix de visée au sol
            px = (sim_x - cam_x) * zoom + (L/2)
            py = (sim_y - cam_y) * zoom + (H/2)
            
            # Ligne pointillée depuis l'avion jusqu'à la cible
            start_px = (world_x - cam_x) * zoom + (L/2)
            start_py = (world_y - cam_y) * zoom + (H/2)
            pygame.draw.aaline(surface, (0, 255, 0, 100), (start_px, start_py), (px, py))
            
            # Croix de ciblage
            csz = max(5, 10 * zoom)
            pygame.draw.line(surface, (0, 255, 0), (px - csz, py), (px + csz, py), max(1, int(2*zoom)))
            pygame.draw.line(surface, (0, 255, 0), (px, py - csz), (px, py + csz), max(1, int(2*zoom)))
            pygame.draw.circle(surface, (0, 255, 0), (px, py), csz, max(1, int(1*zoom)))

        # Draw score and time for Missions
        if self.score > 0 and args.missions:
            lbl_score = police_alarme.render(f"SCORE: {self.score}", True, (255, 215, 0))
            # Positionné sous la barre de menu
            surface.blit(lbl_score, lbl_score.get_rect(topright=(L - 20, s(35))))
            
        # Draw Timer
        if self.time_left > 0:
            m = int(self.time_left) // 60
            sec = int(self.time_left) % 60
            lbl_time = police_alarme.render(f"TEMPS RESTANT: {m:02d}:{sec:02d}", True, (255, 0, 0) if self.time_left < 30 else (255, 215, 0))
            surface.blit(lbl_time, lbl_time.get_rect(midtop=(L//2, s(35))))
        elif self.active_mission == "landing" and not self.mission_over:
            m = int(self.stopwatch_time) // 60
            sec = int(self.stopwatch_time) % 60
            lbl_time = police_alarme.render(f"CHRONO: {m:02d}:{sec:02d}", True, (255, 255, 255))
            surface.blit(lbl_time, lbl_time.get_rect(midtop=(L//2, s(35))))
            
        # Draw Game Over Text
        if self.mission_over:
            # Fond semi-transparent
            s_overlay = pygame.Surface((L, H), pygame.SRCALPHA)
            s_overlay.fill((0, 0, 0, 150))
            surface.blit(s_overlay, (0, 0))
            
            # Texte final
            lbl_end = police_alarme.render(self.final_message, True, (255, 255, 0))
            lbl_end2 = police_label.render("Appuyez sur ECHAP pour revenir au menu", True, (255, 255, 255))
            surface.blit(lbl_end, lbl_end.get_rect(center=(L//2, H//2 - 20)))
            surface.blit(lbl_end2, lbl_end2.get_rect(center=(L//2, H//2 + 30)))

        # Draw cargos
        for c in self.cargos:
            c.draw(surface, cam_x, cam_y, zoom)

mission_manager = MissionManager()


class Airport:
    def __init__(self, x_start, width):
        self.x_start = x_start
        self.width = width
        self.x_end = x_start + width
        self.altitude = 0 
        
    def draw(self, surface, cam_x, cam_y, zoom):
        # Position du sol
        px = (self.x_start - cam_x) * zoom + (L/2)
        py = (0 - cam_y) * zoom + (H/2) # Sol est à y=0
        pw = self.width * zoom
        ph = 150 * zoom # Profondeur visuelle augmentée
        
        # Clipping simple
        if px + pw < -500 or px > L + 500: return

        # 0. Dessin du Sprite Aéroport (Bâtiment)
        if img_aeroport_base:
            # On scale l'image de base selon le zoom
            # On imagine que le sprite représente un bâtiment d'environ 400m de large
            w_img = 400 * zoom
            h_img = (img_aeroport_base.get_height() / img_aeroport_base.get_width()) * w_img
            
            # Positionnement : On le met un peu en retrait de la piste
            # Au milieu de la longueur de la piste par exemple
            img_x = px + (pw / 2) - (w_img / 2)
            img_y = py - h_img + 5*zoom # Juste au dessus de la ligne du bitume
            
            if -w_img < img_x < L:
                img_scaled = pygame.transform.scale(img_aeroport_base, (int(w_img), int(h_img)))
                if est_nuit:
                    img_scaled.fill((100, 100, 120), special_flags=pygame.BLEND_MULT)
                surface.blit(img_scaled, (img_x, img_y))

        # 1. Bitume renforcé (bordures plus claires, centre foncé)
        pygame.draw.rect(surface, SOL_PISTE, (px, py, pw, ph)) # Piste
        pygame.draw.rect(surface, (150, 150, 150), (px, py, pw, ph), max(1, int(2*zoom))) # Contour béton
        
        # Bandes Seuils (Piano keys) - Plus réalistes
        nb_keys = 10
        kw = 60 * zoom
        kh = 8 * zoom
        espacement_y = 12 * zoom
        # Seuil Début (09)
        for k in range(nb_keys):
            pygame.draw.rect(surface, (240, 240, 240), (px + 20*zoom, py + 15*zoom + k*espacement_y, kw, kh))
        # Seuil Fin (27)
        for k in range(nb_keys):
            pygame.draw.rect(surface, (240, 240, 240), (px + pw - 80*zoom, py + 15*zoom + k*espacement_y, kw, kh))
            
        # Aiming Point / Touchdown Zone (Gros blocs de peinture)
        for dist in [300, 450, 600, 750]:
            if px + dist*zoom < L and px + dist*zoom > 0:
                 # Haut
                 pygame.draw.rect(surface, (240, 240, 240), (px + dist*zoom, py + 30*zoom, 80*zoom, 10*zoom))
                 # Bas
                 pygame.draw.rect(surface, (240, 240, 240), (px + dist*zoom, py + 110*zoom, 80*zoom, 10*zoom))

        # Ligne Médiane Discontinue (Bien centrée)
        dash_w = 80 * zoom
        gap_w = 60 * zoom
        current_x = px + 200 * zoom
        while current_x < px + pw - 200*zoom:
            if 0 < current_x < L: # Opti
                pygame.draw.rect(surface, (240, 240, 240), (current_x, py + (ph/2) - 2*zoom, dash_w, 4*zoom))
            current_x += dash_w + gap_w
            
        # Numéro Piste (09 / 27) plus grand et mieux placé
        if zoom > 0.3:
            lbl_09 = police_alarme.render("09", True, (240, 240, 240))
            lbl_09 = pygame.transform.scale(lbl_09, (int(40*zoom), int(60*zoom)))
            surface.blit(lbl_09, (px + 100*zoom, py + (ph/2) - 30*zoom))
            
            lbl_27 = police_alarme.render("27", True, (240, 240, 240))
            lbl_27 = pygame.transform.scale(lbl_27, (int(40*zoom), int(60*zoom)))
            surface.blit(lbl_27, (px + pw - 140*zoom, py + (ph/2) - 30*zoom))

        # Lumières de bord de piste (Edge lights) et PAPI
        if est_nuit or zoom > 0.1:
            step_light = 100 * zoom
            cx = px
            while cx < px + pw:
                if 0 < cx < L:
                    # Haut
                    pygame.draw.circle(surface, (255, 255, 200), (cx, py + 2*zoom), 2)
                    # Bas
                    pygame.draw.circle(surface, (255, 255, 200), (cx, py + ph - 2*zoom), 2)
                cx += step_light
                
            # PAPI Lights (4 lampes : 2 rouges, 2 blanches)
            papi_x = px + 250*zoom
            if 0 < papi_x < L:
                for idx, c in enumerate([(255,50,50), (255,50,50), (255,255,200), (255,255,200)]):
                    pygame.draw.circle(surface, c, (papi_x + idx*12*zoom, py - 6*zoom), max(1, int(3*zoom)))

            # ZONE RAVITAILLEMENT (REFUEL)
            rz_w = self.width
            px_rz = (self.x_start - cam_x) * zoom + (L/2)
            
            if px_rz + rz_w * zoom > 0 and px_rz < L:
                # Carré jaune transparent au sol sur toute la longueur
                s_zone = pygame.Surface((rz_w*zoom, 15*zoom), pygame.SRCALPHA)
                s_zone.fill((255, 200, 0, 60)) 
                surface.blit(s_zone, (px_rz, py - 10*zoom))
                
                # Texte "FUEL" répété tous les 2000m pour être sûr de le voir
                if zoom > 0.4:
                    for d in range(0, int(rz_w), 2000):
                        lbl_fuel = police_label.render("FUEL ZONE", True, (255, 200, 50))
                        surface.blit(lbl_fuel, (px_rz + d*zoom + 50*zoom, py - 30*zoom))

# (L'initialisation de MAIN_AIRPORT est remplacée par la boucle ci-dessous)
airports = [] # Re-initialiser la liste des aéroports
# Génération de quelques pistes
RUNWAYS = []
for i in range(-2, 3):
    airports.append(Airport(i * 75000, 6000)) # Ajouter l'aéroport à la liste
    RUNWAYS.append((i * 75000, 6000)) # Tuple: (début, longueur)

# ZONES MARITIMES (Ocean et Lacs)
OCEAN_ZONES = [
    (-450000, -350000), # Océan Ouest (poussé très loin)
    (100000, 150000)    # Océan Est
]

# --- SYSTEMES AVION (Carburant, Dégâts) ---
fuel = args.fuel
max_fuel = 100.0
fuel_burn_rate = current_ac["fuel_rate"] # % par frame à pleins gaz

# Moteur Température
moteur_temp = 0.0 # 0 à 100
moteur_endommage = False

crashed = False
crash_reason = ""
game_over_timer = 0
shake_amount = 0.0

# Missions
confort_passagers = 100.0
atc_message = ""
atc_timer = 0
atc_airport_triggered = set()

def get_terrain_height(x):
    # Utilisation de valeurs absolues pour éviter que le relief ne "stagne" à 0 (le plat)
    # Les fréquences sont augmentées pour plus de nervosité dans le relief
    h1 = abs(math.sin(x * 0.00025)) * 600
    h2 = abs(math.sin(x * 0.0008)) * 250
    h3 = abs(math.sin(x * 0.002)) * 80
    
    h = h1 + h2 + h3
    
    # Appliquer l'intensité demandée par l'utilisateur
    h *= args.terrain_intensity
    
    # Aplatir pour les Océans
    beach_factor = 1.0
    for (ox_start, ox_end) in OCEAN_ZONES:
        if ox_start <= x <= ox_end:
            return 0.0 # Parfaitement plat pour l'eau
            
        # Pente douce (plage) sur 4000m avant l'eau
        if x < ox_start:
            dist = ox_start - x
            if dist < 4000:
                f = dist / 4000.0
                beach_factor = min(beach_factor, f * f)
        elif x > ox_end:
            dist = x - ox_end
            if dist < 4000:
                f = dist / 4000.0
                beach_factor = min(beach_factor, f * f)
                
    h *= beach_factor

    # Aplatir uniquement pour la piste
    for piste_data in RUNWAYS:
        if isinstance(piste_data, tuple):
            rx = piste_data[0]
            rw = piste_data[1]
        else:
            rx = piste_data
            rw = 6000
            
        center = rx + rw/2
        dist = abs(x - center)
        # Zone de plat très réduite : juste la piste + 100m
        safe_zone = rw/2 + 100 
        
        if dist < safe_zone:
            return 0.0
        elif dist < safe_zone + 1500:
            # Transition beaucoup plus courte pour un relief escarpé
            factor = (dist - safe_zone) / 1500.0
            factor = factor * factor 
            h *= factor
            
    return h

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
PUISSANCE_MOTEUR = current_ac["thrust_max"] / 8500.0
FRICTION_AIR = 1.0 - current_ac["drag_factor"]
FRICTION_VERTICALE = 0.96  
ACCEL_ROTATION = current_ac["rot_speed"] * 0.02
MAX_ROTATION = 1.8         
COEFF_PORTANCE = current_ac["lift_factor"] * 0.015
COEFF_TRAINEE_MONTEE = 0.004

horloge = pygame.time.Clock()

# Appliquer les upgrades au démarrage
switch_aircraft(args.aircraft)

def lerp_color(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t)
    )

def mettre_a_jour_couleurs(heure):
    global CIEL_BAS, CIEL_HAUT, SOL_HERBE_FONCE, SOL_HERBE_CLAIR, SOL_HERBE_BASE, SOL_PISTE, est_nuit
    
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
        SOL_PISTE = lerp_color(C_SOL_PISTE_NUIT, C_SOL_PISTE_JOUR, ratio)
        
    elif 8 <= heure < 18: # PLEIN JOUR
        est_nuit = False
        CIEL_BAS = C_CIEL_JOUR_BAS
        CIEL_HAUT = C_CIEL_JOUR_HAUT
        SOL_HERBE_FONCE = C_SOL_JOUR_FONCE
        SOL_HERBE_CLAIR = C_SOL_JOUR_CLAIR
        SOL_PISTE = C_SOL_PISTE_JOUR
        
    elif 18 <= heure < 19: # CRÉPUSCULE (JOUR -> COUCHER)
        est_nuit = False
        ratio = (heure - 18)
        CIEL_BAS = lerp_color(C_CIEL_JOUR_BAS, C_CIEL_COUCHER_BAS, ratio)
        CIEL_HAUT = lerp_color(C_CIEL_JOUR_HAUT, C_CIEL_COUCHER_HAUT, ratio)
        SOL_HERBE_FONCE = lerp_color(C_SOL_JOUR_FONCE, C_SOL_COUCHER_FONCE, ratio)
        SOL_HERBE_CLAIR = lerp_color(C_SOL_JOUR_CLAIR, C_SOL_COUCHER_CLAIR, ratio)
        SOL_PISTE = lerp_color(C_SOL_PISTE_JOUR, C_SOL_PISTE_NUIT, ratio * 0.5)
        
    elif 19 <= heure < 20: # CRÉPUSCULE (COUCHER -> NUIT)
        est_nuit = False
        ratio = (heure - 19)
        CIEL_BAS = lerp_color(C_CIEL_COUCHER_BAS, C_CIEL_NUIT_BAS, ratio)
        CIEL_HAUT = lerp_color(C_CIEL_COUCHER_HAUT, C_CIEL_NUIT_HAUT, ratio)
        SOL_HERBE_FONCE = lerp_color(C_SOL_COUCHER_FONCE, C_SOL_NUIT_FONCE, ratio)
        SOL_HERBE_CLAIR = lerp_color(C_SOL_COUCHER_CLAIR, C_SOL_NUIT_CLAIR, ratio)
        SOL_PISTE = lerp_color(C_SOL_PISTE_JOUR, C_SOL_PISTE_NUIT, 0.5 + ratio * 0.5)
            
    else: # NUIT (20h-06h)
        est_nuit = True
        CIEL_BAS = C_CIEL_NUIT_BAS
        CIEL_HAUT = C_CIEL_NUIT_HAUT
        SOL_HERBE_FONCE = C_SOL_NUIT_FONCE
        SOL_HERBE_CLAIR = C_SOL_NUIT_CLAIR
        SOL_PISTE = C_SOL_PISTE_NUIT
        
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
    x_spd = s(80)
    y_center = H // 2
    h_tape = s(300)
    w_tape = s(70)
    
    # Fond Tape Vitesse
    s_tape_spd = pygame.Surface((w_tape, h_tape), pygame.SRCALPHA)
    s_tape_spd.fill(C_BG)
    surface.blit(s_tape_spd, (x_spd - w_tape, y_center - h_tape//2))
    
    # Ligne centrale (repère)
    pygame.draw.line(surface, C_TXT, (x_spd - w_tape, y_center), (x_spd, y_center), 2)
    
    # Graduations Vitesse
    px_per_knot = 3 * UI_SCALE
    start_v = int(vitesse - (h_tape // 2) / px_per_knot)
    end_v = int(vitesse + (h_tape // 2) / px_per_knot)
    
    for v in range((start_v // 10) * 10, end_v, 10):
        dy = (vitesse - v) * px_per_knot
        y_pos = y_center + dy
        if y_center - h_tape//2 < y_pos < y_center + h_tape//2:
            if v % 50 == 0:
                pygame.draw.line(surface, C_TXT, (x_spd, y_pos), (x_spd - s(20), y_pos), 2)
                lbl = police_valeur.render(str(v), True, C_TXT)
                surface.blit(lbl, (x_spd - s(55), y_pos - s(10)))
            else:
                pygame.draw.line(surface, C_TXT, (x_spd, y_pos), (x_spd - s(10), y_pos), 1)

    # Valeur Vitesse Actuelle
    lbl_vagne = police_valeur.render(f"{int(vitesse)}", True, C_TXT)
    pygame.draw.rect(surface, (0, 0, 0), (x_spd + s(15), y_center - s(15), s(50), s(30)))
    pygame.draw.rect(surface, C_TXT, (x_spd + s(15), y_center - s(15), s(50), s(30)), 2)
    surface.blit(lbl_vagne, (x_spd + s(22), y_center - s(10)))

    # 2. DROITE: ALTITUDE (Alt Tape)
    x_alt = L - s(80)
    
    s_tape_alt = pygame.Surface((w_tape, h_tape), pygame.SRCALPHA)
    s_tape_alt.fill(C_BG)
    surface.blit(s_tape_alt, (x_alt, y_center - h_tape//2))
    
    pygame.draw.line(surface, C_TXT, (x_alt, y_center), (x_alt + w_tape, y_center), 2)

    px_per_ft = 0.5 * UI_SCALE
    start_alt = int(alt - (h_tape // 2) / px_per_ft)
    end_alt = int(alt + (h_tape // 2) / px_per_ft)

    for a in range((start_alt // 100) * 100, end_alt, 100):
        dy = (alt - a) * px_per_ft
        y_pos = y_center + dy
        if y_center - h_tape//2 < y_pos < y_center + h_tape//2:
            if a % 500 == 0:
                pygame.draw.line(surface, C_TXT, (x_alt, y_pos), (x_alt + s(20), y_pos), 2)
                lbl = police_valeur.render(str(a), True, C_TXT)
                surface.blit(lbl, (x_alt + s(25), y_pos - s(10)))
            else:
                pygame.draw.line(surface, C_TXT, (x_alt, y_pos), (x_alt + s(10), y_pos), 1)

    # Valeur Alt Actuelle
    lbl_a_act = police_valeur.render(f"{int(alt)}", True, C_TXT)
    pygame.draw.rect(surface, (0, 0, 0), (x_alt - s(60), y_center - s(15), s(55), s(30)))
    pygame.draw.rect(surface, C_TXT, (x_alt - s(60), y_center - s(15), s(55), s(30)), 2)
    surface.blit(lbl_a_act, (x_alt - s(55), y_center - s(10)))

    # 3. CENTRE: PITCH LADDER
    pitch_spacing = s(5)
    pitch_px = angle_pitch * pitch_spacing
    y_hor = y_center + pitch_px
    if 0 < y_hor < H:
        pygame.draw.line(surface, C_INFO, (L/2 - s(50), y_hor), (L/2 + s(50), y_hor), 1) 
    
    for p in range(-90, 90, 10):
        if p == 0: continue
        dy = (angle_pitch - p) * pitch_spacing
        y_l = y_center + dy
        if y_center - s(150) < y_l < y_center + s(150):
            w_l = s(40) if p % 20 == 0 else s(20)
            pygame.draw.line(surface, C_TXT, (L/2 - w_l, y_l), (L/2 + w_l, y_l), 1)
            if p % 20 == 0:
                txt_p = police_label.render(str(p), True, C_TXT)
                surface.blit(txt_p, (L/2 + w_l + s(5), y_l - s(5)))

    # Maquette Avion
    cx, cy = L // 2, H // 2
    pygame.draw.circle(surface, (255, 0, 0), (cx, cy), s(3), 1)

def afficher_atc(msg, duree=300):
    global atc_message, atc_timer
    atc_message = msg
    atc_timer = duree

# --- DASHBOARD ANALOGIQUE (CLASSIC) ---
def dessiner_dashboard(surface, vitesse, alt, moteur, flaps, auto, freins, lumiere, poussee_pct, heure_dec, px_world, runways, portance, angle_pitch, gear, mtemp, show_large_map, flight_plan_waypoints):
    if show_large_map: return
    global fuel, atc_message, en_decrochage
    h_dash = s(140)
    y_base = H - h_dash
    gap = s(30)
    rayon = s(58)
    
    # 1. FOND DU TABLEAU DE BORD (Look Moderne)
    pygame.draw.rect(surface, (25, 28, 35), (0, y_base, L, h_dash))
    pygame.draw.line(surface, (60, 65, 75), (0, y_base), (L, y_base), s(2))

    # Utils pour effets
    def draw_glass_effect(x, y, r):
        s_glass = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.ellipse(s_glass, (255, 255, 255, 20), (s(5), s(5), r*1.5, r*0.8), 0)
        surface.blit(s_glass, (x - r, y - r))

    def draw_led(x, y, active, color_on, label):
        color = color_on if active else (40, 45, 50)
        if active:
            for radius in range(s(8), s(2), -1):
                alpha = int(100 * (1.0 - radius/s(8)))
                pygame.draw.circle(surface, (*color_on, alpha), (x, y), radius)
        pygame.draw.circle(surface, color, (x, y), s(4))
        pygame.draw.circle(surface, (100, 105, 115), (x, y), s(4), 1)
        lbl = police_label.render(label, True, (200, 200, 210) if active else (70, 75, 80))
        surface.blit(lbl, (x - lbl.get_width()//2, y + s(8)))

    def draw_v_bar(bx, val_pct, label, color):
        bw, bh = s(12), s(80)
        pygame.draw.rect(surface, (15, 15, 20), (bx, y_base + s(30), bw, bh))
        h_fill = int(bh * (max(0, min(100, val_pct)) / 100.0))
        pygame.draw.rect(surface, color, (bx, y_base + s(30) + bh - h_fill, bw, h_fill))
        surface.blit(police_label.render(label, True, TXT_GRIS), (bx - s(5), y_base + s(15)))
        # Valeur digitale sous la barre
        val_txt = police_label.render(f"{int(val_pct)}", True, (200, 200, 200))
        surface.blit(val_txt, (bx + bw//2 - val_txt.get_width()//2, y_base + s(115)))

    # 1. ANEMOMETRE (Vitesse)
    x_spd = gap + rayon
    y_inst = y_base + s(70)
    
    pygame.draw.circle(surface, (10, 12, 18), (x_spd, y_inst), rayon)
    pygame.draw.circle(surface, (80, 85, 95), (x_spd, y_inst), rayon, 2)
    
    max_speed = 400
    for v in range(0, max_speed + 1, 20):
        ang = 135 + (v / max_speed) * 270
        rad = math.radians(ang)
        l_size = s(10) if v % 100 == 0 else s(5)
        p1 = (x_spd + math.cos(rad) * (rayon - l_size), y_inst + math.sin(rad) * (rayon - l_size))
        p2 = (x_spd + math.cos(rad) * rayon, y_inst + math.sin(rad) * rayon)
        pygame.draw.line(surface, (200, 200, 210) if v % 100 == 0 else (100, 105, 115), p1, p2, 2 if v % 100 == 0 else 1)
        
    val_aff = min(vitesse, max_speed)
    ang_aig = 135 + (val_aff / max_speed) * 270
    rad_aig = math.radians(ang_aig)
    pygame.draw.line(surface, HUD_ORANGE, (x_spd, y_inst), (x_spd + math.cos(rad_aig) * (rayon-s(5)), y_inst + math.sin(rad_aig) * (rayon-s(5))), s(3))
    pygame.draw.circle(surface, (50, 55, 65), (x_spd, y_inst), s(6))
    draw_glass_effect(x_spd, y_inst, rayon)
    
    sf_spd = police_valeur.render(f"{int(vitesse)}", True, (255, 255, 255))
    surface.blit(sf_spd, sf_spd.get_rect(center=(x_spd, y_inst + s(25))))
    surface.blit(police_label.render("KNOTS", True, TXT_GRIS), (x_spd - s(20), y_inst - s(20)))

    # 2. HORIZON ARTIFICIEL
    x_hor = x_spd + rayon + gap + rayon
    rayon_hor = s(58)
    s_hor = pygame.Surface((rayon_hor*2, rayon_hor*2))
    pygame.draw.rect(s_hor, (45, 120, 220), (0, 0, rayon_hor*2, rayon_hor*2)) # Ciel
    y_h_local = rayon_hor + angle_pitch * s(2.5)
    pygame.draw.rect(s_hor, (120, 80, 40), (0, y_h_local, rayon_hor*2, rayon_hor*2)) # Terre
    pygame.draw.line(s_hor, (255, 255, 255), (0, y_h_local), (rayon_hor*2, y_h_local), s(2))
    
    # Clip circulaire
    mask = pygame.Surface((rayon_hor*2, rayon_hor*2), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255), (rayon_hor, rayon_hor), rayon_hor)
    s_hor.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
    surface.blit(s_hor, (x_hor - rayon_hor, y_inst - rayon_hor))
    
    # Repère fixe
    pygame.draw.line(surface, (255, 255, 0), (x_hor - s(35), y_inst), (x_hor - s(10), y_inst), s(3))
    pygame.draw.line(surface, (255, 255, 0), (x_hor + s(10), y_inst), (x_hor + s(35), y_inst), s(3))
    pygame.draw.circle(surface, (255, 255, 0), (x_hor, y_inst), s(3))
    pygame.draw.circle(surface, (80, 85, 95), (x_hor, y_inst), rayon_hor, s(3))
    draw_glass_effect(x_hor, y_inst, rayon_hor)

    # 3. ALTIMETRE
    x_alt = x_hor + rayon_hor + gap + rayon
    pygame.draw.circle(surface, (10, 12, 18), (x_alt, y_inst), rayon)
    pygame.draw.circle(surface, (80, 85, 95), (x_alt, y_inst), rayon, 2)
    # Aiguilles
    for unit, length, color, thickness in [(10000, 35, (200, 200, 200), 4), (1000, 50, (255, 255, 255), 2)]:
        ang = -90 + ((alt % unit) / unit) * 360
        r = math.radians(ang)
        pygame.draw.line(surface, color, (x_alt, y_inst), (x_alt + math.cos(r)*s(length), y_inst + math.sin(r)*s(length)), s(thickness))
    
    draw_glass_effect(x_alt, y_inst, rayon)
    sf_alt = police_valeur.render(f"{int(alt)}", True, (100, 255, 150))
    surface.blit(sf_alt, sf_alt.get_rect(center=(x_alt, y_inst + s(30))))

    # 4. JAUGE AOA (Angle of Attack) - SYNCHRONISATION TOTALE PHYSIQUE
    x_aoa = x_alt + rayon + gap + s(10)
    
    # On réutilise les mêmes seuils que la physique (Spécifique Acro)
    base_thr = 30.0 if args.aircraft == "acro" else 16.0
    stall_thr = base_thr + (args.upg_finesse * 0.1)
    if flaps: stall_thr += 4.0
    
    # Normalisation : 100% = Point de décrochage EXACT
    aoa_pct = max(0, min(100, (abs(real_aoa_phys) / stall_thr) * 100))
    
    # Sécurité base vitesse (Ignorée si Acro et gaz à fond)
    v_min = 65 if flaps else 85
    is_slow_risk = vitesse < v_min
    if args.aircraft == "acro" and poussee_pct > 80:
        is_slow_risk = False
        
    speed_danger = 0
    if is_slow_risk:
        speed_danger = max(0, min(100, (1.0 - (vitesse - v_min) / 20.0) * 100))
    
    # La jauge affiche le risque maximum
    final_aoa_display = max(aoa_pct, speed_danger)
    
    is_stalling = en_decrochage and (pygame.time.get_ticks() % 400 < 200)
    aoa_color = (255, 0, 0) if (final_aoa_display >= 98 or is_stalling) else (255, 160, 0) if final_aoa_display > 60 else (50, 255, 100)
    
    if final_aoa_display >= 98 or is_stalling:
        pygame.draw.rect(surface, (80, 0, 0), (x_aoa - s(15), y_base + s(10), s(40), s(120)), 0, 4)
    
    draw_v_bar(x_aoa, final_aoa_display, "AOA", aoa_color)

    # 5. BLOC MOTEUR (PWR, FUEL, TEMP)
    x_stats = x_aoa + s(20) + gap + s(10)
    draw_v_bar(x_stats, poussee_pct, "PWR", (50, 150, 255))
    draw_v_bar(x_stats + s(40), fuel, "FUEL", (50, 255, 100) if fuel > 20 else (255, 50, 50))
    draw_v_bar(x_stats + s(80), mtemp, "TEMP", (255, 0, 0) if mtemp > 80 else (100, 200, 255))

    # 6. VOYANTS LED (STATUS)
    x_leds = x_stats + s(80) + s(20) + gap + s(20)
    draw_led(x_leds, y_base + s(40), gear, (50, 255, 50), "GEAR")
    draw_led(x_leds + s(50), y_base + s(40), flaps, (50, 150, 255), "FLAPS")
    draw_led(x_leds, y_base + s(90), freins, (255, 50, 50), "BRAKE")
    draw_led(x_leds + s(50), y_base + s(90), auto, (255, 200, 50), "A/P")

    # 7. HORLOGE UTC (Boitier stylisé)
    x_clock = x_leds + s(100) + gap
    y_clock = y_base + s(45)
    h_int = int(heure_dec)
    m_int = int((heure_dec % 1) * 60)
    pygame.draw.rect(surface, (15, 18, 25), (x_clock, y_clock, s(110), s(50)), 0, 6)
    pygame.draw.rect(surface, (70, 75, 85), (x_clock, y_clock, s(110), s(50)), 2, 6)
    sf_h = police_valeur.render(f"{h_int:02d}:{m_int:02d}", True, (255, 200, 100))
    surface.blit(sf_h, (x_clock + s(10), y_clock + s(5)))
    surface.blit(police_label.render("UTC / ZULU", True, (150, 150, 160)), (x_clock + s(12), y_clock + s(30)))

    # 8. MINIMAP
    x_map = x_clock + s(110) + gap
    y_map = y_base + s(20)
    w_map = L - x_map - gap
    h_map = s(105)
    
    if show_minimap:
        pygame.draw.rect(surface, (10, 15, 20), (x_map, y_map, w_map, h_map))
        pygame.draw.rect(surface, (70, 75, 85), (x_map, y_map, w_map, h_map), 2)
        
        center_map_x = x_map + w_map // 2
        RANGE_MAP = 20000 
        px_per_m = w_map / (RANGE_MAP * 2)
        
        # Relief minimap
        points_map_relief = []
        points_map_relief.append((x_map, y_map+h_map-s(5)))
        for map_dx in range(0, w_map, s(5)):
            wx = (map_dx - w_map/2) / px_per_m + px_world
            ty = get_terrain_height(wx) 
            my = y_map+h_map-s(5) - (ty * (0.02 * UI_SCALE)) 
            my = max(y_map, min(y_map+h_map-s(5), my))
            points_map_relief.append((x_map + map_dx, my))
        points_map_relief.append((x_map + w_map, y_map+h_map-s(5)))
        pygame.draw.polygon(surface, (30, 60, 30), points_map_relief)
        
        # Aeroports
        for piste_data in runways: 
            rx = piste_data[0] if isinstance(piste_data, tuple) else piste_data
            rw = piste_data[1] if isinstance(piste_data, tuple) else 6000
            dist = rx - px_world
            if abs(dist) < RANGE_MAP:
                 mx = center_map_x + (dist * px_per_m)
                 pygame.draw.rect(surface, (200, 200, 200), (mx, y_map+h_map-s(7), max(2, rw*px_per_m), s(4)))

        # Trace de vol
        if len(position_history) > 1:
            points_trace = []
            for hx, halt in position_history[-200:]:
                 dist = hx - px_world
                 if abs(dist) < RANGE_MAP:
                     mx = center_map_x + (dist * px_per_m)
                     my = y_map + h_map - s(5) - (halt * 0.02 * UI_SCALE)
                     points_trace.append((mx, my))
            if len(points_trace) > 1:
                pygame.draw.lines(surface, (0, 255, 255), False, points_trace, 2)

        # AVIONS IA
        if args.missions:
            for aip in ai_planes:
                dist_obj = aip.x - px_world
                if abs(dist_obj) < 20000:
                    mx_c = center_map_x + (dist_obj * px_per_m)
                    hy_c = min(h_map - s(15), -aip.y * (0.02 * UI_SCALE))
                    my_c = y_map + h_map - s(10) - hy_c
                    sz = s(8) # Triangle plus grand sur la carte
                    pygame.draw.polygon(surface, (0, 0, 0), [(mx_c, my_c - sz), (mx_c - sz, my_c + sz), (mx_c + sz, my_c + sz)])
                    pygame.draw.polygon(surface, (255, 255, 255), [(mx_c, my_c - sz), (mx_c - sz, my_c + sz), (mx_c + sz, my_c + sz)], s(1))
    
        # DROP ZONES (Cibles Cargo)
        if mission_manager.active_mission == "cargo":
            for t in mission_manager.cargo_targets:
                if t['active']:
                    dist_obj = t['x'] - px_world
                    if abs(dist_obj) < 20000:
                        mx_c = center_map_x + (dist_obj * px_per_m)
                        hy_c = min(h_map - s(15), get_terrain_height(t['x']) * (0.02 * UI_SCALE))
                        my_c = y_map + h_map - s(10) - hy_c
                        sz = s(4) # Un poil plus grand pour être bien visible
                        pygame.draw.rect(surface, (255, 50, 50), (mx_c - sz, my_c - sz, sz*2, sz*2))
                        
        # ANNEAUX
        if mission_manager.active_mission == "rings":
            for r in mission_manager.rings:
                if not r.passed:
                    dist_obj = r.x - px_world
                    if abs(dist_obj) < 20000:
                        mx_c = center_map_x + (dist_obj * px_per_m)
                        hy_c = min(h_map - s(15), -r.y * (0.02 * UI_SCALE))
                        my_c = y_map + h_map - s(10) - hy_c
                        pygame.draw.circle(surface, (255, 215, 0), (int(mx_c), int(my_c)), s(3), s(1))
                        
        # ZONE D'ATTERRISSAGE
        if mission_manager.active_mission == "landing" and mission_manager.target_landing_zone:
            x1, x2 = mission_manager.target_landing_zone
            d1 = x1 - px_world
            d2 = x2 - px_world
            if abs(d1) < 20000 or abs(d2) < 20000:
                mx1 = center_map_x + (d1 * px_per_m)
                mx2 = center_map_x + (d2 * px_per_m)
                # Au sol (altitude 0)
                my_c = y_map + h_map - s(10)
                pygame.draw.line(surface, (0, 255, 0), (mx1, my_c), (mx2, my_c), s(4))
            
        # Position du joueur sur minimap
        if (pygame.time.get_ticks() // 200) % 2 == 0:
            h_rel = min(h_map - s(20), alt * (0.02 * UI_SCALE))
            p_center = (center_map_x, y_map+h_map-s(10) - h_rel)
            
            rad_a = math.radians(angle_pitch)
            t_size = s(6)
            p1_base = (t_size, 0) # Nez
            p2_base = (-t_size, -t_size + s(2)) # Aile gauche
            p3_base = (-t_size, t_size - s(2)) # Aile droite
            
            def rotate_point(p, r):
                rx = p[0] * math.cos(r) - p[1] * math.sin(r)
                ry = -(p[0] * math.sin(r) + p[1] * math.cos(r)) # Inversion Y
                return (p_center[0] + rx, p_center[1] + ry)

            pt1 = rotate_point(p1_base, rad_a)
            pt2 = rotate_point(p2_base, rad_a)
            pt3 = rotate_point(p3_base, rad_a)
            pygame.draw.polygon(surface, (255, 255, 0), [pt1, pt2, pt3])

        # DESSIN PLAN DE VOL MINIMAP
        if len(flight_plan_waypoints) > 0:
            surface.set_clip(pygame.Rect(x_map, y_map, w_map, h_map))
            pts_wp_minimap = []
            for wp_x, wp_alt in flight_plan_waypoints:
                dist = wp_x - px_world
                mx = center_map_x + (dist * px_per_m)
                hy_rel = min(h_map - s(15), wp_alt * (0.02 * UI_SCALE))
                my = y_map + h_map - s(10) - hy_rel
                pygame.draw.polygon(surface, (255, 100, 255), [(mx, my-s(3)), (mx+s(3), my), (mx, my+s(3)), (mx-s(3), my)])
                pts_wp_minimap.append((mx, my))
                
            if len(pts_wp_minimap) > 1:
                pygame.draw.lines(surface, (255, 100, 255), False, pts_wp_minimap, s(1))
            
            first_wp_x, first_wp_alt = flight_plan_waypoints[0]
            dist_first = first_wp_x - px_world
            mx_first = center_map_x + (dist_first * px_per_m)
            hy_rel_first = min(h_map - s(15), first_wp_alt * (0.02 * UI_SCALE))
            my_first = y_map + h_map - s(10) - hy_rel_first
            
            h_rel_player = min(h_map - s(20), alt * (0.02 * UI_SCALE))
            pygame.draw.line(surface, (200, 50, 200), (center_map_x, y_map+h_map-s(10) - h_rel_player), (mx_first, my_first), s(1))
            surface.set_clip(None)
            
            dist_to_wp = abs(dist_first)
            lbl_wp = police_valeur.render(f"WP1: {dist_to_wp/1000.0:.1f}KM", True, (255, 100, 255))
            surface.blit(lbl_wp, (x_map, y_map - s(25)))

    # ATC RADIOMESSAGE (Overlay)
    if args.missions and atc_message != "":
        lbl_atc = police_valeur.render(f"RADIO: {atc_message}", True, (150, 255, 150))
        surface.blit(lbl_atc, (s(20), y_base - s(40)))

    # RADIO DISPLAY
    lbl_radio = police_label.render(music_player.get_current_title(), True, (200, 200, 255))
    surface.blit(lbl_radio, (s(20), H - s(230)))
if args.mission_type == "rings":
    mission_manager.start_rings_challenge(world_x)
elif args.mission_type == "landing":
    mission_manager.start_landing_challenge(world_x)
elif args.mission_type == "cargo":
    mission_manager.message = "MISSION: LARGUEZ LES COLIS (2 MIN)"
    mission_manager.timer_message = 200
    mission_manager.active_mission = "cargo"
    mission_manager.time_left = 120.0
    mission_manager.mission_over = False

# Initialisation des variables de zoom et minimap
zoom = 0.5
zoom_cible = 0.5
show_minimap = True # Minimap toujours affichée
show_large_map = False # Idée 46: Toggle carte interactive avec M
flight_plan_waypoints = [] # Liste de points géographiques (x, y) pour le plan de vol

# Initialisation des couleurs selon la saison
update_season_visuals()

while True:
    dt = horloge.tick(60) / 1000.0 
    
    if args.multiplayer and udp_socket:
        # Reception des données serveur
        try:
            while True:
                data, _ = udp_socket.recvfrom(4096)
                others_data = json.loads(data.decode('utf-8'))
                
                # Mise a jour de la liste
                current_time = time.time()
                for pid, pdata in others_data.items():
                    if pid not in network_players:
                        network_players[pid] = NetworkPlayer(pdata.get("pseudo", "Inconnu"), pdata.get("aircraft", "cessna"))
                    
                    np = network_players[pid]
                    np.x = pdata.get("x", 0)
                    np.y = pdata.get("y", 0)
                    np.angle = pdata.get("angle", 0)
                    np.last_update = current_time
                    
                # Nettoyage
                to_remove = [k for k, p in network_players.items() if current_time - p.last_update > 5.0]
                for k in to_remove: del network_players[k]
        except (BlockingIOError, ConnectionRefusedError):
            pass # Rien a lire
        except Exception as e:
            print(f"Erreur reseau reception: {e}")
            
        # Envoi de nos donnees (1 frame sur 3 pour eviter de surcharger le reseau)
        if network_frame_count % 3 == 0:
            my_data = {
                "pseudo": args.pseudo,
                "x": world_x,
                "y": altitude,
                "angle": angle,
                "aircraft": args.aircraft
            }
            try:
                udp_socket.sendto(json.dumps(my_data).encode('utf-8'), (args.ip, 5555))
            except:
                pass
        network_frame_count += 1
    
    # --- GESTION DU TEMPS ---
    if mode_temps_reel:
        now = datetime.datetime.now()
        heure_actuelle = now.hour + (now.minute / 60.0) + (now.second / 3600.0)
    elif mode_temps_dynamique:
        # Avance du temps : 0.001 par frame = ~1h toutes les 1000 frames (~16s à 60fps)
        # Un cycle complet de 24h prend environ 6.5 minutes.
        heure_actuelle += 0.001
        if heure_actuelle >= 24: heure_actuelle -= 24
    else:
        heure_actuelle = offset_temps

    
    mettre_a_jour_couleurs(heure_actuelle) 

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if args.ui_sounds and son_clic:
                son_clic.play()
        if menu_bar.handle_event(event):
            continue
            
        if event.type == pygame.QUIT:
            save_session_coins()
            save_career_stats()
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEWHEEL:
            zoom_cible += event.y * 0.2 # Zoom plus rapide 
            # Clamp zoom to prevent negative sizes (crash) and excessive zoom
            if zoom_cible < 0.05: zoom_cible = 0.05
            if zoom_cible > 3.0: zoom_cible = 3.0
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if show_large_map:
                # Calcul de la position géographique du clic
                # La carte fait L-100 x H-100, ancrée en 50,50
                w_map = L - 100
                h_map = H - 100
                x_map = 50
                y_map = 50
                if x_map <= event.pos[0] <= x_map + w_map and y_map <= event.pos[1] <= y_map + h_map:
                    if event.button == 1: # Clic Gauche -> Ajouter Waypoint
                        # Echelle X : -150km à +150km
                        px_w = (event.pos[0] - x_map) / w_map * 300000 - 150000
                        # Echelle Y : 15000m à 0m (inversé)
                        py_alt = (1.0 - (event.pos[1] - y_map) / h_map) * 15000
                        flight_plan_waypoints.append((px_w, py_alt))
                    elif event.button == 3: # Clic Droit -> Retirer dernier Waypoint
                        if len(flight_plan_waypoints) > 0:
                            flight_plan_waypoints.pop()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moteur_allume = not moteur_allume
            if event.key == pygame.K_f:
                flaps_sortis = not flaps_sortis
            if event.key == pygame.K_g:
                gear_sorti = not gear_sorti
            if event.key == pygame.K_l: # LANDING LIGHT
                lumiere_allume = not lumiere_allume
            if event.key == pygame.K_m: # TOGGLE LARGE MAP (Idée 46)
                show_large_map = not show_large_map
            if event.key == pygame.K_k: # TOGGLE RADIO
                music_player.toggle()
            if event.key == pygame.K_n: # NEXT SONG
                music_player.next()
            if event.key == pygame.K_ESCAPE:
                save_session_coins()
                save_career_stats()
                pygame.quit()
                exit()
            
            # MISSIONS
            if event.key == pygame.K_F1:
                mission_manager.start_rings_challenge(world_x)
            if event.key == pygame.K_F2:
                mission_manager.start_landing_challenge(world_x)
            if event.key == pygame.K_c and mission_manager.active_mission == "cargo":
                mission_manager.drop_cargo(world_x, world_y, vx, vy)
                
            if args.aircraft == "fighter":
                if event.key == pygame.K_b:
                    bombs.append(Bomb(world_x, world_y, vx, vy))
                if event.key == pygame.K_v:
                    missiles.append(Missile(world_x, world_y, vx, vy, angle))

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
    zoom_cible = max(0.01, min(5.0, zoom_cible)) # Plage de zoom ÉNORME (0.01 permet de dézoomer de très loin)
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
            
        # L'inertie de rotation est aussi impactée par le poids
        facteur_poids_rot = 1.0
        if not args.static_weight:
            facteur_poids_rot = 1.0 + (fuel / 100.0) * 0.4
            
        accel = (ACCEL_ROTATION / facteur_poids_rot) * 0.5 * efficacite_vitesse * facteur_sol
        
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


    # --- LIMITATION ANGLE (Désactivée pour tous les appareils) ---
    # Tous les avions peuvent désormais faire des loopings à 360°
    # On garde l'angle entre -180 et 180 pour la logique de calcul
    if angle > 180: angle -= 360
    if angle < -180: angle += 360

    if args.missions:
        if atc_timer > 0:
            atc_timer -= 1

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
        # Conso basale + conso poussée exponentielle pour la postcombustion
        # Plus on pousse la manette, plus la consommation augmente de façon non linéaire
        facteur_poussee = (niveau_poussee_reelle / 100.0)
        # Quadrique pour simuler une consommation disproportionnée à haut régime
        # x2.5 burn rate if full throttle, only basal rate if idle
        conso = 0.001 + (facteur_poussee**2 * 2.5) * fuel_burn_rate
        
        if not args.unlimited_fuel:
            fuel -= conso
            if fuel < 0: fuel = 0
        else:
            fuel = 100.0 # Force le fuel à 100% si illimité
        
    # --- SURCHAUFFE MOTEUR ---
    if moteur_allume and not moteur_endommage and not args.no_overheat:
        # Chauffe augmente de façon exponentielle avec la poussée (Idée 4)
        facteur_poussee = (niveau_poussee_reelle / 100.0)
        chauffe_base = (facteur_poussee**2 * 0.08) * (1.0 - UPG_COOLING_REDUCTION)
        
        # Refroidissement lié à l'altitude (air plus froid) et la vitesse (flux d'air)
        # altitude est typiquement 0 à 15000+. Vitesse_kph de 0 à 300+
        refroidissement_alt = (max(0, altitude) / 10000.0) * 0.03 # De 0 à 0.045
        refroidissement_vit = (max(0, vitesse_kph) / V_VNE) * 0.05 # De 0 à 0.05
        refroidissement = 0.01 + refroidissement_alt + refroidissement_vit
        
        variation_temp = chauffe_base - refroidissement
        
        # Le cargo chauffe naturellement plus vite
        if current_ac["mass"] == 20000.0 and niveau_poussee_reelle > 85:
            variation_temp += 0.01
            
        moteur_temp += variation_temp
        
        if moteur_temp >= 100:
            moteur_temp = 100
            moteur_endommage = True
            moteur_allume = False
            son_moteur.stop()
            mission_manager.message = "MOTEUR EN FEU ! ATTERRISSEZ D'URGENCE !"
            mission_manager.timer_message = 300
            
    else:
        moteur_temp -= 0.1 # Refroidit si éteint ou si no_overheat
        
    # --- STATISTIQUES DE SESSION ---
    max_vitesse_session = max(max_vitesse_session, vitesse_kph)
    max_alt_session = max(max_alt_session, altitude)
    distance_totale_session += (vitesse_kph / 3.6) * dt
    temps_vol_session += dt
        
    if moteur_temp < 0: moteur_temp = 0

    # REFUELING MANUEL (Touche R sur n'importe quel aéroport)
    # L'avion doit être au sol (altitude < 5), presque arrêté, dans la zone d'un aéroport (0 à 2000m)
    can_refuel = False
    if altitude < 5 and abs(vitesse_kph) < 30: # Un peu plus tolérant sur la vitesse
        for piste_data in RUNWAYS:
            if isinstance(piste_data, tuple):
                piste_x = piste_data[0]
                piste_w = piste_data[1]
            else: 
                piste_x = piste_data
                piste_w = 6000
            # On peut recharger sur toute la longueur de la piste
            if piste_x - 300 <= world_x <= piste_x + piste_w + 300:
                can_refuel = True
                break
                
    if can_refuel:
        if args.auto_refuel or touches[pygame.K_r]:
            fuel += 1.0 # Remplissage rapide
            if fuel > max_fuel: fuel = max_fuel

    # SON CONTINU
    if son_moteur:
        if moteur_allume:
            if son_moteur.get_num_channels() == 0: 
                son_moteur.play(loops=-1)
            vol = 0.3 + (niveau_poussee_reelle / 100.0) * 0.7
            if not engine_sound_active:
                vol = 0.0
            else:
                vol *= args.volume
            son_moteur.set_volume(vol)
        else:
            son_moteur.stop()

    # SON VENT DYNAMIQUE
    if son_vent:
        if son_vent.get_num_channels() == 0: son_vent.play(loops=-1)
        # Volume prop à la vitesse (max 0.8)
        ratio_v = min(1.0, (vitesse_kph / 400.0)) # 400kph = max vent
        vol_wind = ratio_v * 0.5 # Max 50% volume
        if args.season == "wind": vol_wind *= 2.0 # Plus fort en tempête
        son_vent.set_volume(vol_wind * args.volume)

    postcombustion = (niveau_poussee_reelle > 90)
    
    # --- POIDS DYNAMIQUE (Idée 5) ---
    # Le fuel représente une part importante du poids (ex: 40% du poids max)
    # 0% fuel = facteur 1.0 (leger) | 100% fuel = facteur 1.4 (lourd)
    facteur_poids = 1.0
    if not args.static_weight:
        facteur_poids = 1.0 + (fuel / 100.0) * 0.4
    
    # APPLICATION UPGRADE POIDS (Allègement)
    facteur_poids *= (1.0 - UPG_WEIGHT_REDUCTION)
        
    # La puissance instantanée est divisée par le facteur de poids
    puissance_instantanee = ((niveau_poussee_reelle / 100.0) * PUISSANCE_MOTEUR) / facteur_poids
    rad = math.radians(angle)
    
    # --- VENT & TURBULENCE ---
    if not args.no_wind:
        turbulence_timer += 1
        # Variation du vent (rafales)
        rafale_x = math.sin(turbulence_timer * 0.05) * 2.0
        rafale_y = math.cos(turbulence_timer * 0.13) * 1.5
        
        vent_actuel_x = vent_x + rafale_x
        vent_actuel_y = vent_y + rafale_y
        
        vx += vent_actuel_x * 0.005 
        vy += vent_actuel_y * 0.005
    
    # Secousses Caméra
    # Secousses Caméra (REDUIT)
    shake_amount = 0
    if moteur_allume:
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

    terrain_y = get_terrain_height(world_x)
    altitude = -(world_y - terrain_y)
    
    # CLAMPING ET SECURITE
    vx = max(-150.0, min(150.0, vx))
    vy = max(-150.0, min(150.0, vy))
    if math.isnan(vx): vx = 0
    if math.isnan(vy): vy = 0
    
    vitesse_totale = math.sqrt(vx**2 + vy**2)
    vitesse_kph = int(vitesse_totale * 15)
    
    # --- TRACKING RECORDS SESSION ---
    max_vitesse_session = max(max_vitesse_session, vitesse_kph)
    max_alt_session = max(max_alt_session, altitude)
    distance_totale_session += abs(vx) # Approximation simple de la distance
    
    # Détection Atterrissage Réussi
    if not crashed and altitude < 5 and vitesse_kph < 10:
        if not has_already_landed:
            session_landings += 1
            has_already_landed = True
            # ATC message félicitations
            afficher_atc("BRAVO ! ATTERRISSAGE RÉUSSI.", 120)
    elif altitude > 20:
        has_already_landed = False # On redécolle
    
    # --- CALCUL AOA PHYSIQUE (UNIFIÉ & SPÉCIAL ACRO) ---
    rad_pitch = math.radians(angle)
    v_long = vx * math.cos(rad_pitch) + (-vy) * math.sin(rad_pitch)
    v_perp = -vx * math.sin(rad_pitch) + (-vy) * math.cos(rad_pitch)
    real_aoa_phys = math.degrees(math.atan2(v_perp, max(0.1, v_long)))
    
    # Seuil de décrochage dynamique
    # L'Acro est BEAUCOUP plus tolérant (30° au lieu de 16°)
    base_thr = 30.0 if args.aircraft == "acro" else 16.0
    stall_threshold_phys = base_thr + (args.upg_finesse * 0.1)
    if flaps_sortis: stall_threshold_phys += 4.0
    
    # Détection Décrochage
    # L'Acro ne décroche pas par manque de vitesse si le moteur compense (Prop-hanging)
    v_min_limit = 65 if flaps_sortis else 85
    is_slow = vitesse_kph < v_min_limit
    
    # Si Acro et moteur > 80%, on ignore le décrochage de vitesse (on tient sur l'hélice)
    if args.aircraft == "acro" and niveau_poussee_reelle > 80:
        is_slow = False

    if args.no_stall:
        en_decrochage = False
    elif altitude < 100 and vitesse_kph > 50:
        en_decrochage = False # Sécurité sol
    elif abs(real_aoa_phys) > stall_threshold_phys or is_slow:
        en_decrochage = True
    else:
        en_decrochage = False

    # --- PHYSIQUE DE VOL ---
    portance = 0
    if pilote_auto_actif:
        vy = 0 
        vx *= FRICTION_AIR 
    else:
        vy += GRAVITE
        
        friction_actuelle = FRICTION_AIR
        
        if flaps_sortis:
            friction_actuelle = 0.985  
            coeff_p = 0.0075           
        else:
            friction_actuelle = 0.992
            coeff_p = COEFF_PORTANCE
            
        if not gear_sorti:
            # Moins de traînée si le train est rentré (plus de vitesse)
            friction_actuelle += 0.002

        if not en_decrochage:
            # On plafonne l'angle effectif pour la portance (évite des valeurs immenses en looping)
            # L'angle d'attaque aérodynamique décroche au delà de ~20 degrés dans la réalité
            effective_angle = max(-15, min(25, angle))
            angle_incidence = effective_angle + 2.0 
            
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

        # La portance s'applique perpendiculairement aux ailes
        # (avant : vy -= portance, poussait toujours vers le ciel absolu)
        rad_portance = math.radians(angle)
        vx += -math.sin(rad_portance) * portance
        vy -= math.cos(rad_portance) * portance

    # --- COLLISION HORIZONTALE AVEC LA MONTAGNE ---
    # On regarde si l'avion va rentrer "dans" un mur devant lui
    if not args.god_mode:
        # Predict next height where the plane is going
        next_x = world_x + vx
        future_terrain_y = get_terrain_height(next_x)
        current_terrain_y = get_terrain_height(world_x)
        
        # Si on vole droit vers une pente raide qui est plus haute que notre altitude (en tenant compte de la chute prévue vy)
        altitude_future = -(world_y + vy - future_terrain_y)
        
        # Uniquement si on est près du sol
        if altitude_future < -10 and (future_terrain_y > current_terrain_y + 10) and abs(vx) > 10:
             # Le terrain monte brutalement devant nous et on va être EN DESSOUS (altitude_future négative importante)
             crashed = True
             crash_reason = f"CRASH: COLLISION RELIEF (Montagne)"

    # Freeze game physics if mission is over
    if args.missions and mission_manager.mission_over:
        vx = 0.0
        vy = 0.0
        target_poussee = 0.0

    # Blocage au sol pour éviter le glissement (vent/pente) à l'arrêt
    if not crashed and altitude < 1.0 and abs(vx) < 0.2 and niveau_poussee_reelle < 2.0:
        vx = 0.0

    world_x += vx
    world_y += vy
    
    # Update Weapons
    for b in bombs:
        if not b.active: continue
        b.update()
        terrain_h = get_terrain_height(b.x)
        if b.y >= -terrain_h:
            b.active = False
            spawn_explosion(b.x, b.y, b.vx, b.vy)
            
    for m in missiles:
        if not m.active: continue
        m.update()
        terrain_h = get_terrain_height(m.x)
        if m.y >= -terrain_h:
            m.active = False
            spawn_explosion(m.x, m.y, m.vx, m.vy)
            continue
            
        for aip in ai_planes:
            if aip.active:
                dist = math.hypot(m.x - aip.x, m.y - aip.y)
                if dist < 80:
                    aip.active = False
                    m.active = False
                    spawn_explosion(aip.x, aip.y, aip.vx, aip.vy)
                    break

    # Update Missions
    mission_manager.update(world_x, world_y, vx, vy, dt)
    
    # Update ATC Radios
    if args.missions:
        if altitude > 20 and vitesse_kph > 120 and "takeoff" not in atc_airport_triggered:
            afficher_atc("Tour : Décollage réussi. Bon vol PyFlight !")
            atc_airport_triggered.add("takeoff")
        
        for i, piste in enumerate(airports):
            dist = abs(world_x - (piste.x_start + piste.width/2))
            if dist < 6000 and i not in atc_airport_triggered and altitude > 100:
                afficher_atc(f"Tour : PyFlight, approche sur aéroport {i+1} claire.")
                atc_airport_triggered.add(i)
                
        # Messages ATC aléatoires en vol croisière
        if altitude > 1000 and random.random() < 0.0005: # Très rare
            msgs = [
                "Tour : PyFlight, maintenez votre altitude et cap actuel.",
                "Tour : PyFlight, trafic signalé à vos 12 heures, même altitude.",
                "Tour : PyFlight, signalez turbulences si rencontrées.",
                "Tour : PyFlight, contact radar perdu... Ah non c'est bon."
            ]
            afficher_atc(random.choice(msgs))
    
    # --- CONTRAILS ---
    if not crashed:
        # Trail permanent si option cochée
        if args.show_trail:
            rad_a = math.radians(angle)
            # On génère plusieurs particules par frame pour épaissir la fumée
            # et on les espace légèrement pour couvrir la distance parcourue (vx, vy)
            # Au lieu d'un nombre fixe (3), on calcule la distance parcourue.
            # L'avion parcourt sqrt(vx^2 + vy^2) pixels par frame.
            # Pour un jet, ça peut faire 30-50 pixels d'un coup, donc on laisse des trous.
            # Un espacement de 5 pixels entre les cercles est largement suffisant pour faire une ligne solide.
            dist_per_frame = math.sqrt(vx**2 + vy**2)
            steps = max(3, int(dist_per_frame / 5.0))
            
            for step in range(steps):
                # interp va de 0.0 (début de frame = position actuelle moins vx)
                # à 1.0 (fin de frame = position actuelle)
                interp = step / float(steps)
                
                # Le vecteur vitesse indique où on va. 
                # (world_x, world_y) est la NOUVELLE position finale (car on vient de faire += vx)
                # Donc la position de départ de cette frame était (world_x - vx, world_y - vy)
                spawn_x = (world_x - vx) + (vx * interp)
                spawn_y = (world_y - vy) + (vy * interp)
                
                # Offset pour placer la fumée à l'arrière de l'avion sur CETTE position précise
                offset_x = math.cos(rad_a) * (-35)
                offset_y = math.sin(rad_a) * (35) 
                # Léger jitter pour l'effet "cotonneux" naturel
                rx = random.uniform(-3, 3)
                ry = random.uniform(-3, 3)
                
                # Ajout d'une particule [x, y, life, size_multiplier]
                size_mult = random.uniform(0.7, 1.3)
                contrails.append([spawn_x + offset_x + rx, spawn_y + offset_y + ry, 1.0, size_mult])
            
    # --- GROUND SPRAY (Idee 15 - Améliorée) ---
    if not crashed and altitude < 5 and vitesse_kph > 60:
        if args.season in ["rain", "snow", "wind"]: # Also works in storm
            type_spray = 1 if args.season == "snow" else 0
            # Plus de particules pour un effet plus dense
            for _ in range(8):
                # On place les particules derrière l'avion
                rad_a = math.radians(angle)
                offset_back = -40
                gx = world_x + math.cos(rad_a) * offset_back + random.uniform(-15, 15)
                gy = world_y + random.uniform(-2, 2)
                ground_spray.append([gx, gy, 1.0, random.uniform(0.5, 2.0), type_spray])

    # Mise à jour et nettoyage des particules
    for c in contrails:
        # On réduit encore plus la vitesse de disparition (dure beaucoup plus longtemps)
        c[2] -= 0.003
    contrails = [c for c in contrails if c[2] > 0]
    
    for g in ground_spray:
        g[2] -= 0.03 # Disparait assez vite
        g[1] -= random.uniform(0.3, 0.8)  # Monte (soulevé par le vent relatif)
        # Dérive un peu vers l'arrière
        g[0] -= (vitesse_kph / 50.0)
    ground_spray = [g for g in ground_spray if g[2] > 0]

    # --- ORAGES (Idée 14 - Améliorée) ---
    if args.season == "wind":
        # Fréquence augmentée pour plus de spectacle (0.5% par frame au lieu de 0.2%)
        if random.random() < 0.005: 
            eclair_timer = random.randint(2, 4) # Durée variable du flash
            tonnerre_timer = random.randint(20, 100) # Délai tonnerre réduit
            
    if tonnerre_timer > 0:
        tonnerre_timer -= 1
        if tonnerre_timer == 0 and son_tonnerre:
            son_tonnerre.play()

    # --- REBOND & CRASH ---
    if -world_y <= terrain_y:
        impact_vitesse_vert = vy # Positive = Descente vers le sol
        world_y = -terrain_y
        altitude = 0
        
        # CRASH CHECK
        crash_limit = 8.0 * (1.0 + UPG_GEAR_CRASH_BONUS)
        if impact_vitesse_vert > crash_limit and not args.god_mode:
            crashed = True
            crash_reason = f"ATTERRISSAGE VIOLENT ({int(impact_vitesse_vert*200)} ft/min)"
        elif not gear_sorti and not args.god_mode and not args.no_gear_crash:
             crashed = True
             crash_reason = "CRASH: TRAIN D'ATTERRISSAGE RENTRÉ"
             
        # Collision Terrain en dehors de la piste
        elif terrain_y > 10 and not args.god_mode: 
             crashed = True
             crash_reason = f"CRASH: COLLISION TERRAIN ({int(terrain_y)}m)"
             
        # PITCH CHECK AU SOL
        if abs(angle) > 20:
            crashed = True
            crash_reason = "CRASH NEZ/QUEUE (Angle trop fort)"
            
        if crashed and game_over_timer == 0:
            session_crashes += 1
            # Enregistre le lieu du crash pour la map
            crash_sites.append((world_x, altitude))
            spawn_explosion(world_x, world_y, vx, vy)
            
            moteur_allume = False
            vx = 0
            vy = 0
            game_over_timer = 180 # 3 secondes à 60fps
            son_alarme.stop()
        
        if not crashed:
            # Friction Sol
            friction_sol = 0.99 
            if freins_actifs:
                # Les freins sont plus puissants avec l'upgrade
                friction_sol = max(0.5, 0.92 - UPG_BRAKES_POWER_BONUS)
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
            position_history = [] # Efface la trajectoire après le crash
            bombs.clear()
            missiles.clear()
            world_x = 0
            world_y = 0
            vx, vy = 0, 0
            angle = 0
            fuel = args.fuel
            moteur_allume = False
            moteur_temp = 0
            moteur_endommage = False
            gear_sorti = True
            flaps_sortis = False
            # Consommation carburant
            if not args.unlimited_fuel:
                fuel_flow = (niveau_poussee_reelle / 100.0) * 0.05
                fuel -= fuel_flow
                if fuel < 0: 
                    fuel = 0
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
    if not args.no_clouds:
        for c in clouds:
            c.update(vx)
            c.draw(fenetre, world_x, -altitude, zoom)
    
    # CONTIUE LE RESTE DU DESSIN (SOL, AVION)
    
    # DESSIN CONTRAILS
    # On la dessine derrière l'avion pour former un nuage lisse
    if contrails:
        # Pour des bulles lisses on peut tricher avec un surface globale par dessus si besoin
        # Mais pour les perfs, un draw circle sur des alphas pre-rendus est correct
        for c in contrails:
            px = (c[0] - world_x) * zoom + (L/2)
            py = (c[1] - world_y) * zoom + (H/2)
            
            if -100 < px < L+100 and -100 < py < H+100:
                life = c[2]
                s_mult = c[3] if len(c) > 3 else 1.0
                
                # Le rayon augmente avec le temps (la fumée s'étend)
                # Formule pour un nuage dense au début qui s'élargit
                radius = int((6 + (1.0 - life) * 30) * s_mult * zoom)
                
                # L'opacité chute non-linéairement (reste opaque puis disparaît)
                # alpha = life^2 pour disparaître plus doucement sur la fin
                p_alpha = int(150 * (life * life))
                
                if radius > 0 and p_alpha > 0:
                    surface_fumee = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                    
                    # Dessin avec contour doux (on dessine 2 cercles concentriques)
                    col = current_trail_color
                    pygame.draw.circle(surface_fumee, (*col, int(p_alpha*0.5)), (radius, radius), radius)
                    pygame.draw.circle(surface_fumee, (*col, p_alpha), (radius, radius), int(radius*0.6))
                    
                    fenetre.blit(surface_fumee, (px - radius, py - radius))
                    
    # DESSIN GROUND SPRAY
    if ground_spray:
        for g in ground_spray:
            px = (g[0] - world_x) * zoom + (L/2) + offset_shake_x
            py = (g[1] - world_y) * zoom + (H/2) + offset_shake_y
            if -50 < px < L+50 and -50 < py < H+50:
                life = g[2]
                s_mult = g[3]
                radius = int((3 + (1.0 - life) * 10) * s_mult * zoom)
                alpha = int(255 * (life ** 2))
                if radius > 0 and alpha > 0:
                    sg = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                    if g[4] == 1: # Snow
                        pygame.draw.circle(sg, (255, 255, 255, alpha), (radius, radius), radius)
                    else: # Rain/Water
                        pygame.draw.circle(sg, (150, 200, 220, alpha), (radius, radius), radius)
                    fenetre.blit(sg, (px - radius, py - radius))

    if not args.no_particles:
        for p in particules:
            # P[0]=x, p[1]=y, p[2]=speed_factor, p[3]=type(size)
            
            # Gestion Mouvement selon type (Wind, Rain, Snow)
            if args.season == "snow":
                p[1] += 2.0 * zoom # Tombe doucement
                p[0] -= (vitesse_kph * 0.05 + math.sin(p[1]*0.05)*2 - 2) * zoom # Flotte + vent léger
            elif args.season in ["rain", "autumn"]:
                p[1] += 15.0 * zoom # Tombe vite
                p[0] -= (vitesse_kph * 0.05 - 5) * zoom # Vent
            else:
                # Vent / Vitesse (Classique)
                # p[1] ne bouge pas VERTICALEMENT (fixé précédement)
                # sauf si on veut simuler des particules d'air
                pass 

            # Wrapping Vertical
            if p[1] > H + 50: p[1] = -50
            elif p[1] < -50: p[1] = H + 50
            
            # Vitesse horizontale relative avion
            p[0] -= (vitesse_kph * 0.05 * p[2]) * zoom 

            # Wrapping Horizontal (Amélioré pour gérer les deux sens)
            if p[0] < -100: p[0] = L + 100
            elif p[0] > L + 100: p[0] = -100
            
            # Dessin
            px = p[0]
            py = p[1]
            
            # On ne dessine que si dans l'écran
            if -50 < px < L+50 and -50 < py < H+50:
                if args.season == "snow":
                     pygame.draw.circle(fenetre, (255, 255, 255), (px, py), max(1, 2*zoom))
                elif args.season in ["rain", "autumn"]:
                     # Trait bleu penché
                     pygame.draw.line(fenetre, (100, 100, 150), (px, py), (px - 5*zoom, py + 10*zoom), 1)
                else:
                     # Trait blanc (vent)
                     if vitesse_kph > 50:
                         px2 = px - (20 * zoom * p[2])
                         pygame.draw.line(fenetre, (255, 255, 255), (px, py), (px2, py), max(1, int(zoom)))

    # DESSIN OISEAUX
    for b in birds:
        b.update()
        b.draw(fenetre, world_x, -altitude, zoom)
        
    # AI PLANES
    if args.missions:
        if random.random() < 0.005 and len(ai_planes) < args.num_planes:
            ai_planes.append(AIPlane(world_x, airports))
            
        for aip in ai_planes:
            aip.update(world_x, dt)
            aip.draw(fenetre, world_x, world_y, zoom)
            
    # ARMES DRAW
    for b in bombs:
        b.draw(fenetre, world_x, world_y, zoom)
    for m in missiles:
        m.draw(fenetre, world_x, world_y, zoom)
            
    # Gestion Waypoints (Navigation Automatique)
    # Si le joueur a un plan de vol et s'approche à moins de 2000 mètres du waypoint actuel
    if len(flight_plan_waypoints) > 0:
        wp_x, wp_alt = flight_plan_waypoints[0]
        # Distance en 2D (approximative)
        dist_wp = math.hypot(world_x - wp_x, altitude - wp_alt)
        if dist_wp < 2000.0:
            flight_plan_waypoints.pop(0) # Waypoint atteint, on passe au suivant
            
    # MISE A JOUR HISTORIQUE
    history_timer += 1
    if history_timer > 60: # Tous les 60 ticks (env 1 fois par seconde à 60fps)
        history_timer = 0
        position_history.append((world_x, altitude))
        if len(position_history) > 2000: # Garde les 2000 derniers points (~33 min)
            position_history.pop(0)


    pos_sol_y = (H // 2) + (altitude * zoom) + offset_shake_y
    # On autorise le dessin même si le sol sous l'avion "sort" de l'écran par le bas (pos_sol_y > H)
    # car une montagne devant l'avion peut tout à fait remonter dans l'écran !
    if pos_sol_y < H + 10000:
        # Optimisation & Haze de sol
        # Si on est très haut (zoom petit), on simplifie
        alpha_sol = 255
        if zoom < 0.3:
            # Fade out
            alpha_sol = int(255 * (zoom / 0.3))
        
        if alpha_sol > 10 or zoom <= 0.3:
            # Construction du polygone de relief
            points_relief = [(-100, H)] # Bas gauche
            
            step_x = 20 if zoom > 0.2 else 50
            for cx in range(-100, L + 200, step_x):
                wx = (cx - L/2 - offset_shake_x) / zoom + world_x
                ty = get_terrain_height(wx)
                cy = (-ty - world_y) * zoom + (H // 2) + offset_shake_y
                points_relief.append((cx, cy))
                
            # Pour fermer proprement la droite, on prend la dernière hauteur calculée
            last_cy = points_relief[-1][1]
            points_relief.append((L+200, last_cy)) 
            points_relief.append((L+200, H)) # Bas complet
            
            pygame.draw.polygon(fenetre, SOL_HERBE_BASE, points_relief)
            
            # --- DESSIN DES PLAGES (Transition Terre->Mer) ---
            C_SABLE = (220, 200, 140)
            for (ox_start, ox_end) in OCEAN_ZONES:
                # Plage côte Ouest
                beach1_start = ox_start - 4000
                beach1_end = ox_start + 100 # Un peu dans l'eau
                v1_s = (beach1_start - world_x) * zoom + L/2 + offset_shake_x
                v1_e = (beach1_end - world_x) * zoom + L/2 + offset_shake_x
                
                if v1_e > -100 and v1_s < L + 100:
                    pts_sable = [(max(-100, v1_s), H)]
                    for cx in range(int(max(-100, v1_s)), int(min(L + 200, v1_e)), step_x):
                        wx = (cx - L/2 - offset_shake_x) / zoom + world_x
                        ty = get_terrain_height(wx)
                        cy = (-ty - world_y) * zoom + (H // 2) + offset_shake_y
                        pts_sable.append((cx, cy))
                    pts_sable.append((min(L+200, v1_e), pts_sable[-1][1] if len(pts_sable)>1 else H))
                    pts_sable.append((min(L+200, v1_e), H))
                    if len(pts_sable) > 3:
                        pygame.draw.polygon(fenetre, C_SABLE, pts_sable)
                        
                # Plage côte Est
                beach2_start = ox_end - 100
                beach2_end = ox_end + 4000
                v2_s = (beach2_start - world_x) * zoom + L/2 + offset_shake_x
                v2_e = (beach2_end - world_x) * zoom + L/2 + offset_shake_x
                
                if v2_e > -100 and v2_s < L + 100:
                    pts_sable2 = [(max(-100, v2_s), H)]
                    for cx in range(int(max(-100, v2_s)), int(min(L + 200, v2_e)), step_x):
                        wx = (cx - L/2 - offset_shake_x) / zoom + world_x
                        ty = get_terrain_height(wx)
                        cy = (-ty - world_y) * zoom + (H // 2) + offset_shake_y
                        pts_sable2.append((cx, cy))
                    pts_sable2.append((min(L+200, v2_e), pts_sable2[-1][1] if len(pts_sable2)>1 else H))
                    pts_sable2.append((min(L+200, v2_e), H))
                    if len(pts_sable2) > 3:
                        pygame.draw.polygon(fenetre, C_SABLE, pts_sable2)
                        
            # --- DESSINS OCEANS DYNAMIQUES ---
            for (ox_start, ox_end) in OCEAN_ZONES:
                # Vérifier si l'océan est visible à l'écran
                vis_start = (ox_start - L/2 - offset_shake_x) / zoom + world_x
                vis_end = (ox_end + L/2 + offset_shake_x) / zoom + world_x
                
                # Coordonnées écran de l'océan
                screen_ox_start = (ox_start - world_x) * zoom + L/2 + offset_shake_x
                screen_ox_end = (ox_end - world_x) * zoom + L/2 + offset_shake_x
                
                # Si l'océan croise l'écran
                if screen_ox_end > -100 and screen_ox_start < L + 100:
                    pts_ocean_back = [(max(-100, screen_ox_start), H)]
                    pts_ocean_front = [(max(-100, screen_ox_start), H)]
                    
                    step_x = 20 if zoom > 0.2 else 50
                    for cx in range(int(max(-100, screen_ox_start)), int(min(L + 200, screen_ox_end)), step_x):
                        wx_vo = (cx - L/2 - offset_shake_x) / zoom + world_x
                        
                        # Vague arrière (plus foncée, décalée)
                        wave_bg = math.sin((wx_vo * 0.04) + time.time() * 2.5) * 6 * zoom + math.cos((wx_vo * 0.015) + time.time() * 1.0) * 4 * zoom
                        cy_bg = (wave_bg - world_y) * zoom + (H // 2) + offset_shake_y - (2 * zoom)
                        pts_ocean_back.append((cx, cy_bg))
                        
                        # Vague avant (plus claire, plus grande)
                        wave_fg = math.sin((wx_vo * 0.05) + time.time() * 2.0) * 5 * zoom + math.cos((wx_vo * 0.02) + time.time() * 1.5) * 8 * zoom
                        cy_fg = (wave_fg - world_y) * zoom + (H // 2) + offset_shake_y
                        pts_ocean_front.append((cx, cy_fg))
                        
                    # Finir les polygones proprement
                    last_bg_cy = pts_ocean_back[-1][1]
                    pts_ocean_back.append((min(L+200, screen_ox_end), last_bg_cy))
                    pts_ocean_back.append((min(L+200, screen_ox_end), H))
                    
                    last_fg_cy = pts_ocean_front[-1][1]
                    pts_ocean_front.append((min(L+200, screen_ox_end), last_fg_cy))
                    pts_ocean_front.append((min(L+200, screen_ox_end), H))
                    
                    if len(pts_ocean_back) > 3:
                        # Couleur fond (Bleu profond)
                        pygame.draw.polygon(fenetre, (15, 60, 130), pts_ocean_back)
                        
                        # Dessiner l'écume arrière
                        for i in range(1, len(pts_ocean_back)-2):
                            pygame.draw.line(fenetre, (40, 100, 170), pts_ocean_back[i], pts_ocean_back[i+1], max(1, int(s(2)*zoom)))
                            
                        # Couleur avant (Bleu cyan vibrant)
                        pygame.draw.polygon(fenetre, (25, 130, 190), pts_ocean_front)
                        
                        # Dessiner l'écume au sommet des vagues
                        for i in range(1, len(pts_ocean_front)-2):
                            pygame.draw.line(fenetre, (120, 200, 255), pts_ocean_front[i], pts_ocean_front[i+1], max(1, int(s(2)*zoom)))

    # --- RENDU MÉTÉO : BROUILLARD (FOG) ---
    if args.weather == "fog" and altitude < 2500:
        # Brouillard dense au sol, se dissipe avec l'altitude
        # Max densité à altitude=0 (alpha 200), dissipé à altitude 2500 (alpha 0)
        alpha_fog = int(210 * max(0.0, 1.0 - (altitude / 2500.0)))
        if alpha_fog > 0:
            surf_fog = pygame.Surface((L, H), pygame.SRCALPHA)
            # Couleur gris perle pour le brouillard
            surf_fog.fill((210, 215, 220, alpha_fog))
            fenetre.blit(surf_fog, (0, 0))

    # --- PHARE D'ATTERRISSAGE (NOCTURNE) ---
    if est_nuit and lumiere_allume and not crashed:
        # Dessin d'un cône de lumière devant l'avion
        rad_light = math.radians(angle)
        # On projette le cône vers l'avant
        dist_portee = 400 * zoom
        p_nose = (L/2, H/2) # Position centre écran = avion
        
        # Points du cône (triangle allongé)
        p1 = (p_nose[0] + math.cos(rad_light)*dist_portee, 
              p_nose[1] - math.sin(rad_light)*dist_portee)
        
        # Elargissement du cône
        rad_off = 0.3 # 20 degrés d'ouverture
        p2 = (p_nose[0] + math.cos(rad_light - rad_off)*dist_portee, 
              p_nose[1] - math.sin(rad_light - rad_off)*dist_portee)
        p3 = (p_nose[0] + math.cos(rad_light + rad_off)*dist_portee, 
              p_nose[1] - math.sin(rad_light + rad_off)*dist_portee)
        
        surf_light = pygame.Surface((L, H), pygame.SRCALPHA)
        pygame.draw.polygon(surf_light, (255, 255, 200, 100), [p_nose, p2, p1, p3])
        fenetre.blit(surf_light, (0, 0))

        
        # Patchs
        largeur_motif = 4000 # Elargi pour accomoder la ville
        offset_herbe = int(world_x % largeur_motif)
        largeur_motif_ecran = largeur_motif * zoom
        if largeur_motif_ecran < 1: largeur_motif_ecran = 1 
        nb_motifs_demi = int((L / 2) / largeur_motif_ecran) + 2
        
        if alpha_sol > 20 and not args.no_terrain: # Ne dessine les détails que si visibles
            for i in range(-nb_motifs_demi, nb_motifs_demi + 1):
                base_x = (i * largeur_motif * zoom) - (offset_herbe * zoom) + (L/2) + offset_shake_x
                if base_x + (largeur_motif*zoom) > 0 and base_x < L:
                    for patch in decor_sol:
                        # Calculer la hauteur du sol pour ce patch précis au lieu de pos_sol_y plat
                        p_wx = (base_x + (patch[0] * zoom) - L/2 - offset_shake_x) / zoom + world_x
                        p_ty = get_terrain_height(p_wx)
                        p_cy = (-p_ty - world_y) * zoom + (H // 2) + offset_shake_y
                        
                        px = base_x + (patch[0] * zoom)
                        py = p_cy + (patch[1] * zoom)
                        pw = patch[2] * zoom
                        ph = patch[3] * zoom
                        # ... (Dessin patch)
                        couleur_p = SOL_HERBE_FONCE if patch[4] == 0 else SOL_HERBE_CLAIR
                        
                        if patch[4] == 2: # ARBRE
                             if zoom > 0.2: # Arbres invisibles de très haut
                                tronc_w = 4 * zoom
                                tronc_h = 10 * zoom
                                pygame.draw.rect(fenetre, COLOR_TREE_TRUNK, (px + pw/2 - tronc_w/2, py, tronc_w, tronc_h))
                                p1 = (px + pw/2, py - 20*zoom)
                                p2 = (px + pw/2 - 15*zoom, py)
                                p3 = (px + pw/2 + 15*zoom, py)
                                pygame.draw.polygon(fenetre, COLOR_TREE_LEAF, [p1, p2, p3])
                        else:
                            pygame.draw.rect(fenetre, couleur_p, (px, py, pw, ph))

    # GESTION PISTES (RUNWAYS)
    for piste in airports:
        # Piste.draw utilise la largeur de l'Airport (ici config à 12000)
        piste.draw(fenetre, world_x, world_y, zoom)

    # MISSIONS DRAW
    mission_manager.draw(fenetre, world_x, world_y, zoom)

    # ATMOSPHERE HAUTE ALTITUDE
    # Si zoom très faible (haute altitude), on rajoute du voile
    if zoom < 0.5 and not args.no_atmo:
        alpha_atmo = int((1.0 - (zoom / 0.5)) * 100) # Max 100 alpha (plus subtil)
        s_atmo = pygame.Surface((L, H), pygame.SRCALPHA)
        s_atmo.fill((*CIEL_BAS, alpha_atmo)) # Voile couleur ciel
        fenetre.blit(s_atmo, (0, 0))


            
    # --- DESSIN AVION ---
    # --- DESSIN AVION ---
    if not crashed:
        # Selection image
        if args.aircraft == "fighter":
            img_base = loaded_aircraft_images.get("fighter_gear_down" if gear_sorti else "fighter", img_avion_normal_base)
        else:
            img_base = img_avion_feu_base if (postcombustion and moteur_allume) else img_avion_normal_base
        
        # Redimensionnement (Zoom basé sur une largeur fixe standard)
        scale_f = {"cessna": 1.0, "acro": 0.8, "fighter": 1.5, "cargo": 2.5}.get(args.aircraft, 1.0)
        pw = max(10, int(100 * scale_f * zoom))
        h_new = max(2, int(img_base.get_height() * (pw / max(1, img_base.get_width()))))
        w_new = pw
        
        img_scaled = pygame.transform.scale(img_base, (w_new, h_new))
        
        # Rotation
        img_rot = pygame.transform.rotate(img_scaled, angle)
        rect_img = img_rot.get_rect(center=(L//2, H//2))
        
        # LANDING LIGHT (Phare)
        if lumiere_allume:
            # Création d'une surface pour le faisceau (transparente)
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
        
        # --- Local Player Nametag (Multiplayer) ---
        if args.multiplayer:
            lbl_local = police_label.render(args.pseudo, True, (255, 255, 255))
            lbl_rect_local = lbl_local.get_rect(center=(L//2, H//2 - s(50)))
            bg_rect_local = lbl_rect_local.inflate(s(10), s(6))
            pygame.draw.rect(fenetre, (20, 20, 30), bg_rect_local, border_radius=s(4))
            pygame.draw.rect(fenetre, (100, 255, 100), bg_rect_local, 1, border_radius=s(4))
            fenetre.blit(lbl_local, lbl_rect_local)
    
    
    # --- DESSIN EXPLOSIONS ---
    # Update des particules
    for p in explosions:
        p[0] += p[2] * (1.0/60.0) # x += vx * dt
        p[1] += p[3] * (1.0/60.0)
        p[3] += GRAVITE * 2 # Gravité légère
        p[4] -= 0.02 # Life
        
        # Dessin
        if p[4] > 0:
            px = (p[0] - world_x) * zoom + L//2 + offset_shake_x
            py = (p[1] - world_y) * zoom + H//2 + offset_shake_y
            
            if px > -200 and px < L+200 and py > -200 and py < H+200:
                ratio_vie = p[4] / p[5]
                # Rayon dynamique (p[7] est le base_radius)
                radius = int(p[7] * (1 - ratio_vie) * zoom) + 2
                # Opaque au début, disparaît vers la fin
                alpha = int(255 * ratio_vie)
                
                # Surface transparente
                s_exp = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                
                # Couleur dynamique (commence clair feu, devient foncé fumée)
                col = p[6]
                if ratio_vie < 0.7: col = (40, 40, 40) # Devient fumée plus vite
                if ratio_vie < 0.3: col = (20, 20, 20)
                
                # Dessin du cercle pur, puis application de l'opacité globale à la surface
                pygame.draw.circle(s_exp, col, (radius, radius), radius)
                s_exp.set_alpha(alpha)
                
                fenetre.blit(s_exp, (px - radius, py - radius))
                
    # Nettoyage
    explosions = [p for p in explosions if p[4] > 0]
    
    # --- ECLAIR (FLASH SCREEN) ---
    if 'eclair_timer' in globals() and eclair_timer > 0:
        s_eclair = pygame.Surface((L, H), pygame.SRCALPHA)
        s_eclair.fill((255, 255, 255, 200))
        fenetre.blit(s_eclair, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        eclair_timer -= 1
        
    # --- DASHBOARD ---
    # 1. Analogique (Bas)
    if not args.no_dash:
        # On doit passer position_history à la fonction
        # Mais dessiner_dashboard n'a pas cet argument.
        # Soit on l'ajoute, soit on le dessine APRES.
        # Modifions dessiner_dashboard pour accepter *args ou utilisons une var globale si c'est plus simple ici ?
        # Non, on va modifier l'appel.
        # ATTENTION: dessiner_dashboard est défini plus haut, on doit update sa signature.
        # Pour faire simple et éviter de casser la signature partout si on a oublié,
        # je vais tricher légèrement : je dessine l'historique PAR DESSUS le dashboard ici, 
        # MAIS le dashboard est une surface opaque...
        # Donc je DOIS modifier dessiner_dashboard.
        
        # J'ai ajouté le code DANS dessiner_dashboard via le replace précédent, 
        # mais j'ai besoin que `position_history` soit accessible dedans.
        # Comme `position_history` est défini au niveau module (global), ça devrait marcher direcment 
        # sans le passer en argument si je ne l'ai pas masqué.
        # Python capture les globales.
        
        dessiner_dashboard(fenetre, vitesse_kph, altitude, moteur_allume, flaps_sortis, pilote_auto_actif, freins_actifs, lumiere_allume, niveau_poussee_reelle, heure_actuelle, world_x, RUNWAYS, portance, angle, gear_sorti, moteur_temp, show_large_map, flight_plan_waypoints)
    
    # --- DESSIN GRANDE CARTE INTERACTIVE ---
    if show_large_map:
        w_lmap = L - 100
        h_lmap = H - 100
        x_lmap = 50
        y_lmap = 50
        
        # Fond semi-transparent
        s_lmap = pygame.Surface((w_lmap, h_lmap), pygame.SRCALPHA)
        s_lmap.fill((10, 20, 10, 230))
        fenetre.blit(s_lmap, (x_lmap, y_lmap))
        pygame.draw.rect(fenetre, (150, 150, 150), (x_lmap, y_lmap, w_lmap, h_lmap), s(3))
        
        # Textes instructions
        lbl_inst = police_label.render("FLIGHT PLAN MAP: Left Click to Add Waypoint | Right Click to Remove | Press 'M' to Close", True, (200, 200, 200))
        fenetre.blit(lbl_inst, (x_lmap + s(10), y_lmap + s(10)))
        
        lbl_quit = police_label.render("Press ESCAPE to Return to Menu", True, (255, 100, 100))
        fenetre.blit(lbl_quit, (x_lmap + w_lmap - s(250), y_lmap + s(10)))
        
        # Echelles de la grande carte
        X_MIN = -150000
        X_MAX = 150000
        X_RANGE = X_MAX - X_MIN
        Y_MAX_ALT = 15000
        
        def map_x(world_x_coord):
            return x_lmap + ((world_x_coord - X_MIN) / X_RANGE) * w_lmap
            
        def map_y(world_alt_coord):
             return y_lmap + (1.0 - (world_alt_coord / Y_MAX_ALT)) * h_lmap
        
        # Ligne de sol de base (0m)
        pygame.draw.line(fenetre, (0, 100, 0), (x_lmap, map_y(0)), (x_lmap + w_lmap, map_y(0)))
        
        # Relief
        pts_relief = [(x_lmap, map_y(0))]
        for rx in range(X_MIN, X_MAX, 2000): # Echantillonnage tous les 2km
            rh = get_terrain_height(rx)
            pts_relief.append((map_x(rx), map_y(rh)))
        pts_relief.append((x_lmap + w_lmap, map_y(0)))
        pygame.draw.polygon(fenetre, (20, 50, 20), pts_relief)
            
        # Aéroports
        for piste_data in RUNWAYS: 
            if isinstance(piste_data, tuple):
                pt_x = piste_data[0]
                pt_w = piste_data[1]
            else:
                pt_x = piste_data
                pt_w = 6000
                
            pygame.draw.rect(fenetre, (180, 180, 180), (map_x(pt_x), map_y(0) - s(4), (pt_w / X_RANGE) * w_lmap, s(8)))
            
        # Plages et Océans Grande Carte
        for (ox_start, ox_end) in OCEAN_ZONES:
            # Plage Ouest
            b1_map = map_x(ox_start - 4000)
            b1_w = (4000) / X_RANGE * w_lmap
            pygame.draw.rect(fenetre, (220, 200, 140), (b1_map, map_y(0), b1_w, h_lmap - (map_y(0) - y_lmap)))
            
            # Océan
            ox_map = map_x(ox_start)
            ow_map = (ox_end - ox_start) / X_RANGE * w_lmap
            pygame.draw.rect(fenetre, (30, 130, 200), (ox_map, map_y(0), ow_map, h_lmap - (map_y(0) - y_lmap)))
            
            # Plage Est
            b2_map = map_x(ox_end)
            b2_w = (4000) / X_RANGE * w_lmap
            pygame.draw.rect(fenetre, (220, 200, 140), (b2_map, map_y(0), b2_w, h_lmap - (map_y(0) - y_lmap)))
            
        # Joueur
        px_map = map_x(world_x)
        py_map = map_y(altitude)
        pygame.draw.circle(fenetre, (255, 255, 0), (int(px_map), int(py_map)), s(5))
        pygame.draw.circle(fenetre, (0, 0, 0), (int(px_map), int(py_map)), s(5), 1)
        lbl_player = police_label.render("YOU", True, (255, 255, 0))
        fenetre.blit(lbl_player, (px_map - s(10), py_map - s(20)))
        
        # Waypoints
        pts_wp = []
        for i, (wp_x, wp_alt) in enumerate(flight_plan_waypoints):
            wpx_map = map_x(wp_x)
            wpy_map = map_y(wp_alt)
            
            # Losange violet
            pygame.draw.polygon(fenetre, (255, 100, 255), [(wpx_map, wpy_map-s(6)), (wpx_map+s(6), wpy_map), (wpx_map, wpy_map+s(6)), (wpx_map-s(6), wpy_map)])
            lbl_w = police_label.render(f"WP{i+1}", True, (255, 100, 255))
            fenetre.blit(lbl_w, (wpx_map + s(8), wpy_map - s(8)))
            
            pts_wp.append((wpx_map, wpy_map))
            
        # Connect waypoints on large map
        if len(pts_wp) > 1:
            pygame.draw.lines(fenetre, (255, 100, 255), False, pts_wp, s(2))
            
        # Ligne du joueur au WP1
        if len(pts_wp) > 0:
            pygame.draw.line(fenetre, (200, 50, 200), (px_map, py_map), pts_wp[0], s(2))

    # ---> Dessin des joueurs Multijoueur <---
    for np in network_players.values():
        if not show_large_map:
            np.draw(fenetre, world_x, altitude, zoom)
        else:
            # Simple point sur la minimap
            npm_x = map_x(np.x)
            npm_y = map_y(np.y)
            pygame.draw.circle(fenetre, (0, 255, 255), (int(npm_x), int(npm_y)), s(4))

    # 2. HUD Overlay (Haut)
    if not args.no_hud and not show_large_map:
        dessiner_hud_overlay(fenetre, vitesse_kph, altitude, angle, vy)
    
    # 3. FPS Counter (Coin Haut Gauche)
    if args.show_fps:
        fps = int(horloge.get_fps())
        lbl_fps = police_label.render(f"FPS: {fps}", True, (0, 255, 0))
        fenetre.blit(lbl_fps, (s(10), s(10)))

    # Message Alerte
    msg = ""
    c_msg = HUD_ROUGE
    if en_decrochage:
        msg = "!! DECROCHAGE !!"
    elif not moteur_allume and altitude > 10:
        msg = "!! MOTEUR COUPE !!"

    if msg:
        txt_msg = police_alarme.render(msg, True, c_msg)
        rect_msg = txt_msg.get_rect(center=(L//2, H//2 - s(100)))
        fenetre.blit(txt_msg, rect_msg)

    # 4. Refueling Message (MUST be drawn after screen fill)
    if can_refuel and not args.no_hud:
        # User requested to remove the persistent "MAINTENEZ 'R'" message.
        # We only show feedback when refueling is actively happening.
        if args.auto_refuel or touches[pygame.K_r]:
            msg_refuel = f"RECHARGE EN COURS... {int(fuel)}%"
            color_msg = (0, 255, 0)
            lbl_r = police_alarme.render(msg_refuel, True, color_msg)
            fenetre.blit(lbl_r, lbl_r.get_rect(center=(L//2, H//4)))

    # --- PLUIE SUR LE COCKPIT ---
    # Gouttes d'eau directement sur l'écran si saison de pluie
    if args.season == "rain" and vitesse_kph > 20: # Il faut avancer pour écraser les gouttes
        # Nombre de gouttes proportionnel à la vitesse
        # On utilise une technique très simple : dessin de petites gouttes semi-transparentes aléatoires
        nb_drops = int((vitesse_kph / V_VNE) * 5)
        for _ in range(nb_drops):
            dx = random.randint(0, L)
            dy = random.randint(0, H)
            # Trainées obliques
            p2_x = dx - random.randint(5, 20)
            p2_y = dy + random.randint(5, 20)
            
            s_drop = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.line(s_drop, (200, 220, 255, 60), (15, 0), (15 - (dx-p2_x), p2_y-dy), 2)
            fenetre.blit(s_drop, (dx-15, dy))

    # Fin de boucle

    # --- BARRE DE MENU (FlightGear Style) ---
    menu_bar.draw(fenetre)

    pygame.display.flip()
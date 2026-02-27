import pygame
import math
import os
import random
import datetime # Pour l'heure réelle
import argparse
import argparse
import sys
import array # Pour generation son

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

# On parse uniquement si on est lancé en tant que script principal
args = None
if __name__ == "__main__":
    args, unknown = parser.parse_known_args()
else:
    # Valeurs par défaut si importé (ou pas de main)
    args = argparse.Namespace(time="real", difficulty="easy", volume=0.5, 
                              no_hud=False, no_dash=False, no_clouds=False, 
                              no_particles=False, no_atmo=False, no_terrain=False,
                              unlimited_fuel=False, god_mode=False, fullscreen=False, show_fps=False,
                              season="summer", aircraft="cessna", fuel=100.0,
                              no_stall=False, no_gear_crash=False, no_wind=False, auto_refuel=False,
                              terrain_intensity=1.0, show_trail=False, trail_color="white", weather="clear", missions=False, mission_type="none")

# AIRCRAFT CONFIGS
AIRCRAFT_CONFIGS = {
    "cessna": {
        "mass": 1000.0,
        "thrust_max": 3000.0,
        "drag_factor": 0.008,      # Matches 0.992 friction
        "lift_factor": 0.1,        # Scaled x0.15 -> 0.0015
        "fuel_rate": 0.005,        # Matches 0.005 burn
        "rot_speed": 2.0           # Scaled x0.02 -> 0.04
    },
    "fighter": {
        "mass": 5000.0,
        "thrust_max": 7500.0,      # ~2.5x thrust
        "drag_factor": 0.004,      # Less drag (0.996)
        "lift_factor": 0.07,       # Less lift/mass
        "fuel_rate": 0.020,        # 4x fuel
        "rot_speed": 3.0           # Agility
    },
    "cargo": {
        "mass": 20000.0,
        "thrust_max": 6000.0,      # 2x thrust but heavy
        "drag_factor": 0.020,      # Draggy (0.98)
        "lift_factor": 0.25,       # High lift
        "fuel_rate": 0.015,        # 3x fuel
        "rot_speed": 0.8           # Heavy controls
    },
    "acro": {
        "mass": 800.0,             # Very light
        "thrust_max": 4000.0,      # Lots of power relative to mass
        "drag_factor": 0.010,      # Normal drag
        "lift_factor": 0.15,       # High lift for sharp turns
        "fuel_rate": 0.010,        # Moderate fuel
        "rot_speed": 4.5           # Extremely fast rotation
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
dossier_img = os.path.join(dossier_parent, "image")
dossier_son = os.path.join(dossier_parent, "son")

images_ok = False
son_moteur = None
son_alarme = None

# 1. IMAGES
try:
    path_arret = os.path.join(dossier_img, "avion_arret.png")
    path_marche = os.path.join(dossier_img, "avion_marche.png")
    
    img_avion_normal_base = pygame.image.load(path_arret).convert_alpha()
    img_avion_feu_base = pygame.image.load(path_marche).convert_alpha()
    
    path_aeroport = os.path.join(dossier_img, "aeroport.png")
    if os.path.exists(path_aeroport):
        img_aeroport_base = pygame.image.load(path_aeroport).convert_alpha()
    else:
        img_aeroport_base = None
        
    images_ok = True
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

# AJUSTEMENT SAISON
# AJUSTEMENT SAISON
# AJUSTEMENT SAISON
if args.season == "snow":
    # AMBIANCE HIVER (Neige avec un peu de vert)
    SOL_HERBE_BASE = (200, 220, 210)    # Blanc verdatre
    SOL_HERBE_FONCE = (150, 170, 160)   
    SOL_HERBE_CLAIR = (230, 250, 240)   
    SOL_PISTE = (140, 140, 150)         
    
    CIEL_BAS = (190, 200, 210)          
    CIEL_HAUT = (100, 110, 130)         

elif args.season in ["rain", "autumn"]:
    # AMBIANCE AUTOMNE (Feuilles mortes / Pluie)
    SOL_HERBE_BASE = (139, 69, 19)      # Saddle Brown
    SOL_HERBE_FONCE = (101, 67, 33)     # Dark Brown
    SOL_HERBE_CLAIR = (205, 133, 63)    # Peru (Orange/Brun)
    SOL_PISTE = (60, 60, 65)            
    
    CIEL_BAS = (80, 90, 100)             
    CIEL_HAUT = (30, 35, 45)            

elif args.season == "spring":
    # AMBIANCE PRINTEMPS (Jaune / Vert tendre)
    SOL_HERBE_BASE = (154, 205, 50)     # Yellow Green
    SOL_HERBE_FONCE = (85, 107, 47)     # Olive Drab
    SOL_HERBE_CLAIR = (173, 255, 47)    # Green Yellow
    
    # Ciel clair mais doux
    CIEL_BAS = (176, 224, 230)          
    CIEL_HAUT = (70, 130, 180)


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
police_alarme = pygame.font.SysFont("arial", int(40 * UI_SCALE), bold=True)

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
particules = []
nb_particules = 300 # Beaucoup plus de particules (Pluie/Neige)
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

birds = [Bird() for _ in range(20)]

def spawn_explosion(x, y, vx, vy):
    # Génère une explosion massive de particules (feu/fumée)
    print(f"DEBUG: spawning explosion at {x}, {y} with v=({vx}, {vy})")
    if args.no_particles: return
    for _ in range(300): # 300 particules pour une explosion énorme
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(20, 150) # Vitesse très rapide (immédiat)
        # Expansion sphérique beaucoup plus forte, plus la vélocité
        p_vx = math.cos(angle) * speed + (vx * 0.1)
        p_vy = math.sin(angle) * speed + (vy * 0.1)
        # Durée de vie plus longue pour profiter du spectacle
        life = random.uniform(1.0, 3.0) 
        # [x, y, vx, vy, vie, vie_initiale, couleur]
        color = random.choice([(255,50,0), (255,100,0), (255,200,0), (200,30,0), (80,80,80), (40,40,40), (20,20,20)])
        explosions.append([x, y, p_vx, p_vy, life, life, color])

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
        self.mode = random.choices(["cruise", "takeoff", "landing"], weights=[0.4, 0.3, 0.3])[0]
        
        closest_apt = min(airports_list, key=lambda a: abs(a.x_start - wx))
        
        if self.mode == "cruise":
            self.x = wx + random.choice([-20000, 20000]) # Spawns far away
            self.y = -random.randint(5000, 15000) # High altitude
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
            
            if self.y < -5000:
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
        
        # Angle calc
        angle = math.degrees(math.atan2(-self.vy, self.vx))
        if self.dir_x == -1 and self.vy != 0:
            angle = math.degrees(math.atan2(-self.vy, self.vx))
        
        # Draw a small shape (simple rect for distant plane)
        pw = 40 * zoom # Plus grand pour être mieux vu
        ph = 12 * zoom
        
        # We can just draw a rotated rect by making a small surface
        s_plane = pygame.Surface((pw, ph), pygame.SRCALPHA)
        pygame.draw.rect(s_plane, (40, 40, 40), (0, 0, pw, ph)) # Plus sombre pour contraste
        s_plane_rot = pygame.transform.rotate(s_plane, angle)
        
        r = s_plane_rot.get_rect(center=(px, py))
        surface.blit(s_plane_rot, r)
        
        # Draw a contrail behind it (only high alt)
        if self.y < -3000:
            tail_len = 150 * zoom
            # from back of plane
            back_x = px - math.cos(math.radians(angle)) * (pw/2)
            back_y = py + math.sin(math.radians(angle)) * (pw/2)
            end_x = back_x - math.cos(math.radians(angle)) * tail_len
            end_y = back_y + math.sin(math.radians(angle)) * tail_len
            pygame.draw.line(surface, (255, 255, 255, 100), (back_x, back_y), (end_x, end_y), max(1, int(2*zoom)))

class MissionManager:
    def __init__(self):
        self.active_mission = None # "rings", "landing", None
        self.rings = []
        self.score = 0
        self.message = ""
        self.timer_message = 0
        self.target_landing_zone = None # (x_start, x_end)
        
        # Cargo Missions
        self.cargos = []
        self.cargo_targets = []
        cx = 5000
        for i in range(20):
            self.cargo_targets.append({'x': cx, 'w': 800, 'active': True}) # Cibles plus larges (800)
            cx += random.randint(4000, 15000)
        
    def start_rings_challenge(self, current_x=0):
        self.active_mission = "rings"
        self.rings = []
        self.score = 0
        self.message = "MISSION: RINGS CHALLENGE START!"
        self.timer_message = 180 # 3 sec
        
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
        self.message = "MISSION: PRECISION LANDING SUR AEROPORT!"
        self.timer_message = 240
        
        # Trouver la prochaine piste devant l'avion
        # Les pistes sont à i * 75000
        next_i = int((current_x + 8000) / 75000) + 1
        x_start_piste = next_i * 75000
        
        # On place la cible d'atterrissage sur la première moitié de la piste (la piste fait 6000m)
        self.target_landing_zone = (x_start_piste + 500, x_start_piste + 2500)
        
    def update(self, plane_x, plane_y, plane_vx, plane_vy):
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
                    self.score += 500
                    self.message = f"ATTERRISSAGE REUSSI ! (+500) [{self.score}]"
                    self.timer_message = 300
                    self.target_landing_zone = None
                    self.active_mission = None
                        
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
        if args.missions and args.aircraft == "cargo":
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

        # Draw score for Missions
        if self.score > 0 and args.missions:
            lbl_score = police_alarme.render(f"SCORE: {self.score}", True, (255, 215, 0))
            # Alignement en haut à droite pour éviter de déborder
            surface.blit(lbl_score, lbl_score.get_rect(topright=(L - 20, 20)))

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
        pygame.draw.rect(surface, (60, 65, 70), (px, py, pw, ph)) # Piste
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
for i in range(10): 
    # Espacement de 75000 mètres, longueur divisée par 2 (12000 -> 6000 mètres)
    airports.append(Airport(i * 75000, 6000))
    RUNWAYS.append((i * 75000, 6000)) # Tuple: (début, longueur)

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
def dessiner_dashboard(surface, vitesse, alt, moteur, flaps, auto, freins, lumiere, poussee_pct, heure_dec, px_world, runways, portance, angle_pitch, gear, mtemp):
    global fuel
    h_dash = s(140)
    y_base = H - h_dash
    
    # Fond Carbone / Tableau de bord
    pygame.draw.rect(surface, (40, 40, 45), (0, y_base, L, h_dash))
    pygame.draw.line(surface, (80, 80, 90), (0, y_base), (L, y_base), s(3))

    # 1. ANEMOMETRE (GAUCHE)
    x_spd = s(120)
    y_inst = y_base + s(70)
    rayon = s(60)
    
    # Cadran
    pygame.draw.circle(surface, (10, 10, 15), (x_spd, y_inst), rayon)
    pygame.draw.circle(surface, (200, 200, 200), (x_spd, y_inst), rayon, 2)
    
    # Graduations
    max_speed = 400
    for v in range(0, max_speed + 1, 50):
        ang = 135 + (v / max_speed) * 270
        rad = math.radians(ang)
        p1 = (x_spd + math.cos(rad) * (rayon - s(8)), y_inst + math.sin(rad) * (rayon - s(8)))
        p2 = (x_spd + math.cos(rad) * rayon, y_inst + math.sin(rad) * rayon)
        lc = (255, 255, 255) if v % 100 == 0 else (150, 150, 150)
        w = 2 if v % 100 == 0 else 1
        pygame.draw.line(surface, lc, p1, p2, w)
        
    val_aff = min(vitesse, max_speed)
    ang_aig = 135 + (val_aff / max_speed) * 270
    rad_aig = math.radians(ang_aig)
    pygame.draw.line(surface, HUD_ORANGE, (x_spd, y_inst), (x_spd + math.cos(rad_aig) * (rayon-s(5)), y_inst + math.sin(rad_aig) * (rayon-s(5))), s(3))
    
    sf_spd = police_valeur.render(f"{int(vitesse)}", True, (255, 255, 255))
    surface.blit(sf_spd, sf_spd.get_rect(center=(x_spd, y_inst + s(25))))
    surface.blit(police_label.render("KTS", True, TXT_GRIS), (x_spd - s(15), y_inst - s(20)))

    # 2. HORIZON ARTIFICIEL (CENTRE GAUCHE)
    x_hor = s(280)
    rayon_hor = s(60)
    
    pitch_pixel = angle_pitch * (3 * UI_SCALE) # Sensibilité
    
    # Masque (Clip)
    s_hor = pygame.Surface((rayon_hor*2, rayon_hor*2))
    s_hor_rect = s_hor.get_rect()
    
    # Ciel / Sol sur surface temp
    pygame.draw.rect(s_hor, (40, 100, 200), s_hor_rect) # Ciel
    
    y_h_local = rayon_hor + pitch_pixel
    rect_sol_local = pygame.Rect(0, y_h_local, rayon_hor*2, rayon_hor*2)
    pygame.draw.rect(s_hor, (100, 60, 30), rect_sol_local) # Sol
    pygame.draw.line(s_hor, (255, 255, 255), (0, y_h_local), (rayon_hor*2, y_h_local), s(2)) # Ligne
    
    # Pour faire simple et propre sans assets : On affiche le rect complet mais on dessine le contour par dessus
    surface.blit(s_hor, (x_hor - rayon_hor, y_inst - rayon_hor))
    
    # Repère Avion
    pygame.draw.line(surface, HUD_ORANGE, (x_hor - s(40), y_inst), (x_hor - s(10), y_inst), s(3))
    pygame.draw.line(surface, HUD_ORANGE, (x_hor + s(10), y_inst), (x_hor + s(40), y_inst), s(3))
    pygame.draw.circle(surface, HUD_ORANGE, (x_hor, y_inst), s(3))
    
    # Contour cache misère (cercle épais autour)
    pygame.draw.circle(surface, (40, 40, 45), (x_hor, y_inst), rayon_hor + s(10), s(10)) 
    pygame.draw.circle(surface, (50, 50, 60), (x_hor, y_inst), rayon_hor, s(3))


    # 3. ALTIMETRE (CENTRE DROIT)
    x_alt = s(440)
    pygame.draw.circle(surface, (10, 10, 15), (x_alt, y_inst), rayon)
    pygame.draw.circle(surface, (200, 200, 200), (x_alt, y_inst), rayon, s(2))
    
    # Aiguille 1000 ft
    val_1000 = (alt % 10000) / 10000.0
    ang_1000 = -90 + val_1000 * 360
    r1 = math.radians(ang_1000)
    pygame.draw.line(surface, (255, 255, 255), (x_alt, y_inst), (x_alt + math.cos(r1)*s(40), y_inst + math.sin(r1)*s(40)), s(4))

    # Aiguille 100 ft
    val_100 = (alt % 1000) / 1000.0
    ang_100 = -90 + val_100 * 360
    r2 = math.radians(ang_100)
    pygame.draw.line(surface, (255, 255, 255), (x_alt, y_inst), (x_alt + math.cos(r2)*s(55), y_inst + math.sin(r2)*s(55)), s(2))

    # ATC RADIOMESSAGE
    if args.missions and atc_message != "":
        atc_bg = pygame.Surface((L, s(60)), pygame.SRCALPHA)
        atc_bg.fill((20, 25, 30, 200)) # Fond radio sombre
        surface.blit(atc_bg, (0, y_base - s(70)))
        lbl_atc = police_valeur.render(atc_message, True, (200, 255, 200))
        surface.blit(lbl_atc, lbl_atc.get_rect(center=(L//2, y_base - s(40))))
    
    sf_alt = police_valeur.render(f"{int(alt)}", True, (200, 255, 200))
    surface.blit(sf_alt, sf_alt.get_rect(center=(x_alt, y_inst + s(30))))
    surface.blit(police_label.render("ALT", True, TXT_GRIS), (x_alt - s(10), y_inst - s(20)))

    # 4. INDICATEUR DE PORTANCE (LIFT)
    x_vsi = s(600)
    rayon_vsi = s(50)
    pygame.draw.circle(surface, (10, 10, 15), (x_vsi, y_inst), rayon_vsi)
    pygame.draw.circle(surface, (200, 200, 200), (x_vsi, y_inst), rayon_vsi, s(2))
    
    val_lift = portance / 0.12 # 1G
    val_lift = max(0.0, min(2.0, val_lift))
    ang_vsi = 135 + (val_lift / 2.0) * 270
    rv = math.radians(ang_vsi)
    pygame.draw.line(surface, (255, 255, 100), (x_vsi, y_inst), (x_vsi + math.cos(rv)*(rayon_vsi-s(5)), y_inst + math.sin(rv)*(rayon_vsi-s(5))), s(3))
    surface.blit(police_label.render("LIFT", True, TXT_GRIS), (x_vsi - s(15), y_inst + s(10)))
    
    # 5. FUEL (JAUGE) - INTEGRATION
    x_fuel = s(720)
    rayon_fuel = s(40)
    
    # Fond et bordure
    pygame.draw.circle(surface, (10, 10, 15), (x_fuel, y_inst), rayon_fuel)
    pygame.draw.circle(surface, (150, 150, 160), (x_fuel, y_inst), rayon_fuel, s(2))
    
    # 5. FUEL (JAUGE) - INTEGRATION (TOP ARC 180 GRAD)
    x_fuel = s(720)
    rayon_fuel = s(40)
    
    # Fond et bordure
    pygame.draw.circle(surface, (10, 10, 15), (x_fuel, y_inst), rayon_fuel)
    pygame.draw.circle(surface, (150, 150, 160), (x_fuel, y_inst), rayon_fuel, s(2))
    
    # Arcs (Trig CCW: 0=East, 90=North, 180=West)
    arc_rect = pygame.Rect(x_fuel - rayon_fuel + s(2), y_inst - rayon_fuel + s(2), rayon_fuel * 2 - s(4), rayon_fuel * 2 - s(4))
    
    # Zone Verte (100% à 40%) -> 0 à 108 deg CCW
    pygame.draw.arc(surface, (50, 200, 50), arc_rect, math.radians(0), math.radians(108), s(5))
    # Zone Jaune (40% à 15%) -> 108 à 153 deg
    pygame.draw.arc(surface, (200, 200, 50), arc_rect, math.radians(108), math.radians(153), s(5))
    # Zone Rouge (15% à 0%) -> 153 à 180 deg
    pygame.draw.arc(surface, (200, 50, 50), arc_rect, math.radians(153), math.radians(180), s(5))
    
    # Texte central FUEL
    lbl_f = police_label.render("FUEL", True, TXT_GRIS)
    surface.blit(lbl_f, (x_fuel - s(15), y_inst + s(5)))
    
    # Aiguille Fuel (Math Screen: 180=W, 270=N, 360=E)
    pct_fuel = fuel / 100.0
    ang_fuel = 180 + (pct_fuel * 180)
    rf = math.radians(ang_fuel)
    
    c_f_aig = (255, 255, 255) if fuel >= 20 else (255, 50, 50)
    # Longueur presque totale pour bien voir qu'elle va au bout
    pygame.draw.line(surface, c_f_aig, (x_fuel, y_inst), 
                     (x_fuel + math.cos(rf)*(rayon_fuel-s(5)), y_inst + math.sin(rf)*(rayon_fuel-s(5))), s(3))
    
    # Cache central
    pygame.draw.circle(surface, (50, 50, 50), (x_fuel, y_inst), s(5))

    # Digital
    sf_f = police_label.render(f"{int(fuel)}%", True, c_f_aig)
    surface.blit(sf_f, sf_f.get_rect(center=(x_fuel, y_inst + s(25))))


    # 6. RADAR / MAP
    x_map = L - s(380)
    y_map = y_base + s(10)
    w_map = s(300)
    h_map = s(120)
    
    pygame.draw.rect(surface, (10, 20, 10), (x_map, y_map, w_map, h_map))
    pygame.draw.rect(surface, (100, 100, 100), (x_map, y_map, w_map, h_map), s(2))
    
    center_map_x = x_map + w_map // 2
    pygame.draw.line(surface, (0, 100, 0), (x_map, y_map+h_map-s(10)), (x_map+w_map, y_map+h_map-s(10)))
    
    # L'avion sera dessiné plus tard, par-dessus la trajectoire et le relief
    
    RANGE_MAP = 20000 
    px_per_m = w_map / (RANGE_MAP * 2)
    
    min_dist_airport = 999999
    
    for piste_data in runways: 
        if isinstance(piste_data, tuple):
            rx = piste_data[0]
            rw = piste_data[1]
        else:
            rx = piste_data
            rw = 6000
            
        dist = rx - px_world
        if abs(dist) < RANGE_MAP or abs(dist + rw) < RANGE_MAP:
             mx1 = center_map_x + (dist * px_per_m)
             mx2 = center_map_x + ((dist + rw) * px_per_m)
             # Limiter l'affichage aux bords de la map
             mx1 = max(x_map, min(x_map + w_map, mx1))
             mx2 = max(x_map, min(x_map + w_map, mx2))
             rect_w = max(2, mx2 - mx1) # Même si on est zoomé, toujours dessiner au moins 2 px
             
             pygame.draw.rect(surface, (180, 180, 180), (mx1, y_map+h_map-s(12), rect_w, s(4)))
             
             # Calcul Distance au plus près
             dist_closest = min(abs(dist), abs(dist + rw))
             if dist_closest < min_dist_airport:
                 min_dist_airport = dist_closest
                 
    # Affichage de la distance si < 20km
    if min_dist_airport < RANGE_MAP:
        dist_km = min_dist_airport / 1000.0
        lbl_dist = police_label.render(f"DIST: {dist_km:.1f}KM", True, (150, 200, 150))
        surface.blit(lbl_dist, (x_map + s(5), y_map + s(5)))
        
    # Dessin contour du Relief simplifié sur radar
    points_map_relief = []
    points_map_relief.append((x_map, y_map+h_map-s(10)))
    for map_dx in range(0, w_map, s(5)):
        wx = (map_dx - w_map/2) / px_per_m + px_world
        ty = get_terrain_height(wx)
        # On utilise la même échelle (0.02) que l'altitude de l'avion pour que ça corresponde
        my = y_map+h_map-s(10) - (ty * (0.02 * UI_SCALE)) 
        my = max(y_map, min(y_map+h_map-s(10), my))
        points_map_relief.append((x_map + map_dx, my))
    points_map_relief.append((x_map + w_map, y_map+h_map-s(10)))
    pygame.draw.polygon(surface, (20, 50, 20), points_map_relief)
    # DESSIN HISTORIQUE SUR MAP (Trajectoire)
    px_per_m = w_map / (20000 * 2) 
    if len(position_history) > 1:
        points_map = []
        for (hx, halt) in position_history[-300:]: # Ne garde que les 300 derniers pour éviter la surcharge (plus visible)
             dist = hx - px_world
             if abs(dist) < 20000: # RANGE_MAP
                 mx = center_map_x + (dist * px_per_m)
                 hy_rel = min(h_map - s(15), halt * (0.02 * UI_SCALE))
                 my = y_map + h_map - s(10) - hy_rel
                 points_map.append((mx, my))
        
        if len(points_map) > 1:
            pygame.draw.lines(surface, (50, 255, 255), False, points_map, s(2)) # Cyan plus épais pour la trainée
            
    # DESSIN DE TOUS LES CRASHS (CROIX ROUGES)
    for cx_w, calt in crash_sites:
        dist_crash = cx_w - px_world
        if abs(dist_crash) < 20000: # Même portée que le relief radar
            # Position sur la map
            mx_c = center_map_x + (dist_crash * px_per_m)
            hy_c = min(h_map - s(15), calt * (0.02 * UI_SCALE))
            my_c = y_map + h_map - s(10) - hy_c
            
            # Dessin de la croix
            sz = s(5)
            pygame.draw.line(surface, HUD_ROUGE, (mx_c - sz, my_c - sz), (mx_c + sz, my_c + sz), s(2))
            pygame.draw.line(surface, HUD_ROUGE, (mx_c + sz, my_c - sz), (mx_c - sz, my_c + sz), s(2))

    # OISEAUX
    for b in birds:
        dist_obj = b.x - px_world
        if abs(dist_obj) < 20000:
            mx_c = center_map_x + (dist_obj * px_per_m)
            hy_c = min(h_map - s(15), -b.y * (0.02 * UI_SCALE))
            my_c = y_map + h_map - s(10) - hy_c
            pygame.draw.circle(surface, (200, 200, 200), (int(mx_c), int(my_c)), s(1))

    # AVIONS IA (Triangles noirs)
    if args.missions:
        for aip in ai_planes:
            dist_obj = aip.x - px_world
            if abs(dist_obj) < 20000:
                mx_c = center_map_x + (dist_obj * px_per_m)
                hy_c = min(h_map - s(15), -aip.y * (0.02 * UI_SCALE))
                my_c = y_map + h_map - s(10) - hy_c
                sz = s(8) # Triangle plus grand sur la carte
                pygame.draw.polygon(surface, (0, 0, 0), [(mx_c, my_c - sz), (mx_c - sz, my_c + sz), (mx_c + sz, my_c + sz)])
                pygame.draw.polygon(surface, (255, 255, 255), [(mx_c, my_c - sz), (mx_c - sz, my_c + sz), (mx_c + sz, my_c + sz)], s(1)) # Contour blanc

    # DROP ZONES (Cibles Cargo)
    if args.missions and args.aircraft == "cargo":
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
            
    # DESSIN AVION SUR MAP (Marqueur)
    h_rel = min(h_map - s(20), alt * (0.02 * UI_SCALE))
    p_center = (center_map_x, y_map+h_map-s(10) - h_rel)
    
    # Calcul des points du triangle orienté selon l'angle (angle_pitch en degrés)
    rad_a = math.radians(angle_pitch)
    # Triangle de base pointant vers la droite (0 degrés)
    t_size = s(6)
    p1_base = (t_size, 0) # Nez
    p2_base = (-t_size, -t_size + s(2)) # Aile gauche
    p3_base = (-t_size, t_size - s(2)) # Aile droite
    
    def rotate_point(p, r):
        # Rotation trigo : x*cos - y*sin, x*sin + y*cos
        # Pygame Y est inversé, donc l'angle doit être adapté
        # angle_pitch > 0 signifie on monte (Nez vers le HAUT de l'écran, donc Y diminue)
        # Dans Pygame rotate usuel, un angle positif tourne dans le sens anti-horaire
        rx = p[0] * math.cos(r) - p[1] * math.sin(r)
        ry = -(p[0] * math.sin(r) + p[1] * math.cos(r)) # Inversion Y
        return (p_center[0] + rx, p_center[1] + ry)

    pt1 = rotate_point(p1_base, rad_a)
    pt2 = rotate_point(p2_base, rad_a)
    pt3 = rotate_point(p3_base, rad_a)
    
    pygame.draw.polygon(surface, (255, 255, 0), [pt1, pt2, pt3])

    # Infos Textes (THRUST & TEMP)
    x_panel = L - s(80)
    lbl_th = police_label.render("THR", True, HUD_ORANGE)
    surface.blit(lbl_th, (x_panel, y_map - s(20)))
    lbl_th_val = police_valeur.render(f"{int(poussee_pct)}%", True, (255, 255, 255))
    surface.blit(lbl_th_val, (x_panel, y_map))
    
    # TEMP JAUGE
    y_temp = y_map + s(40)
    lbl_temp = police_label.render("ENG TEMP", True, (200, 200, 200))
    surface.blit(lbl_temp, (x_panel, y_temp))
    
    c_temp = (50, 200, 50) # Vert
    if mtemp > 70: c_temp = (200, 200, 50) # Jaune
    if mtemp > 90: c_temp = (255, 50, 50)  # Rouge
    
    pygame.draw.rect(surface, (50, 50, 50), (x_panel, y_temp + s(20), s(60), s(10))) # Fond
    pygame.draw.rect(surface, c_temp, (x_panel, y_temp + s(20), int(s(60) * (mtemp/100.0)), s(10))) # Valeur
    pygame.draw.rect(surface, (200, 200, 200), (x_panel, y_temp + s(20), s(60), s(10)), 1) # Bord
    
    # Message Surchauffe (Clignotement)
    if mtemp > 95 and (pygame.time.get_ticks() % 500) < 250:
         lbl_warn = police_label.render("OVERHEAT", True, HUD_ROUGE)
         surface.blit(lbl_warn, (x_panel, y_temp + s(35)))

    # INDICATEURS REPOSITIONNES (AU-DESSUS DE RADAR/THR)
    y_ind = y_map - s(40)
    # GEAR
    c_gear = (0, 200, 0) if gear else (200, 50, 50)
    pygame.draw.circle(surface, c_gear, (L - s(260), y_ind), s(5))
    surface.blit(police_label.render("GEAR", True, (200, 200, 200)), (L - s(250), y_ind - s(7)))
    
    # FLAPS
    c_flaps = (0, 200, 0) if flaps else (50, 50, 50)
    pygame.draw.circle(surface, c_flaps, (L - s(180), y_ind), s(5))
    surface.blit(police_label.render("FLAPS", True, (200, 200, 200)), (L - s(170), y_ind - s(7)))

    # BRAKE
    c_brake = (200, 50, 50) if freins else (50, 50, 50)
    pygame.draw.circle(surface, c_brake, (L - s(100), y_ind), s(5))
    surface.blit(police_label.render("BRAKE", True, (200, 200, 200)), (L - s(90), y_ind - s(7)))
    # MANETTE DES GAZ
    x_thr = L - s(30)
    y_thr = y_map
    w_thr = s(15)
    h_thr = s(100)
    
    # Fond slot
    pygame.draw.rect(surface, (20, 20, 20), (x_thr, y_thr, w_thr, h_thr))
    pygame.draw.rect(surface, (100, 100, 100), (x_thr, y_thr, w_thr, h_thr), 1)
    
    # Curseur (Manette)
    pos_y_manette = y_thr + h_thr - (h_thr * (poussee_pct / 100.0))
    pygame.draw.rect(surface, (200, 200, 200), (x_thr - s(5), pos_y_manette - s(5), w_thr + s(10), s(10)))
    pygame.draw.line(surface, (50, 50, 50), (x_thr - s(5), pos_y_manette), (x_thr + w_thr + s(5), pos_y_manette), 1)

    lbl_ti = police_valeur.render(f"{int(heure_dec):02d}:{int((heure_dec%1)*60):02d}", True, HUD_VERT)
    surface.blit(lbl_ti, (L - s(80), y_map + s(20)))

# --- INITIALISATION MISSIONS SPECIFIQUES ---
if args.mission_type == "rings":
    mission_manager.start_rings_challenge(world_x)
elif args.mission_type == "landing":
    mission_manager.start_landing_challenge(world_x)
elif args.mission_type == "cargo":
    mission_manager.message = "MISSION: LARGUEZ LES COLIS (Touche C)"
    mission_manager.timer_message = 200

while True:
    dt = horloge.tick(60) / 1000.0 
    
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
            if event.key == pygame.K_g:
                gear_sorti = not gear_sorti
            if event.key == pygame.K_l: # LANDING LIGHT
                lumiere_allume = not lumiere_allume
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()
            
            # MISSIONS
            if event.key == pygame.K_F1:
                mission_manager.start_rings_challenge(world_x)
            if event.key == pygame.K_F2:
                mission_manager.start_landing_challenge(world_x)
            if event.key == pygame.K_c and args.missions and args.aircraft == "cargo":
                mission_manager.drop_cargo(world_x, world_y, vx, vy)

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


    # --- LIMITATION ANGLE ---
    if args.aircraft != "acro":
        LIMIT_ANGLE = 35
        if angle > LIMIT_ANGLE:  
            angle = LIMIT_ANGLE
            vitesse_rotation_actuelle = 0
        if angle < -LIMIT_ANGLE:
            angle = -LIMIT_ANGLE
            vitesse_rotation_actuelle = 0
    else:
        # Vol acrobatique : Rotation 360 continue
        # On garde l'angle entre -180 et 180 pour la logique (bien que Pygame gère au delà)
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
        
        fuel -= conso
        if fuel < 0: fuel = 0
        
    # --- SURCHAUFFE MOTEUR ---
    if moteur_allume and not moteur_endommage and not args.no_overheat:
        # Chauffe augmente de façon exponentielle avec la poussée (Idée 4)
        facteur_poussee = (niveau_poussee_reelle / 100.0)
        chauffe_base = facteur_poussee**2 * 0.08
        
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
    else:
        moteur_temp -= 0.1 # Refroidit si éteint ou si no_overheat
        
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
    
    # Planeur / Décrochage (Plus permissif en mode facile)
    seuil_decrochage = V_DECROCHAGE - 10 
    if flaps_sortis: seuil_decrochage = 65 
    
    # Anti-Crash Sol
    if args.no_stall:
        en_decrochage = False
    elif altitude < 100 and vitesse_kph > 50:
        en_decrochage = False
    elif vitesse_kph < seuil_decrochage:
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

    world_x += vx
    world_y += vy
    
    # Update Missions
    mission_manager.update(world_x, world_y, vx, vy)
    
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
            
    # Mise à jour et nettoyage des particules
    for c in contrails:
        # On réduit encore plus la vitesse de disparition (dure beaucoup plus longtemps)
        c[2] -= 0.003
    contrails = [c for c in contrails if c[2] > 0]

    # --- REBOND & CRASH ---
    if -world_y <= terrain_y:
        impact_vitesse_vert = vy # Positive = Descente vers le sol
        world_y = -terrain_y
        altitude = 0
        
        # CRASH CHECK
        crash_limit = 8.0 # m/s (environ 1500 ft/min)
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
            position_history = [] # Efface la trajectoire après le crash
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

            # Wrapping
            if p[1] > H: p[1] = -10
            
            # Vitesse horizontale relative avion
            p[0] -= (vitesse_kph * 0.05 * p[2]) * zoom 

            if p[0] < -100: p[0] = L + 100
            
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
        if random.random() < 0.005 and len(ai_planes) < 5:
            ai_planes.append(AIPlane(world_x, airports))
            
        for aip in ai_planes:
            aip.update(world_x, dt)
            aip.draw(fenetre, world_x, world_y, zoom)
            
        ai_planes = [p for p in ai_planes if p.active]
        
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
                                pygame.draw.rect(fenetre, (100, 60, 20), (px + pw/2 - tronc_w/2, py, tronc_w, tronc_h))
                                p1 = (px + pw/2, py - 20*zoom)
                                p2 = (px + pw/2 - 15*zoom, py)
                                p3 = (px + pw/2 + 15*zoom, py)
                                pygame.draw.polygon(fenetre, (20, 100, 20), [p1, p2, p3])
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
        img_base = img_avion_feu_base if (postcombustion and moteur_allume) else img_avion_normal_base
        
        # Redimensionnement (Zoom)
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
                # Rayon beaucoup plus grand pour une énorme explosion (rayon de base * 3)
                radius = int(80 * (1 - ratio_vie) * zoom) + 2
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
        
        dessiner_dashboard(fenetre, vitesse_kph, altitude, moteur_allume, flaps_sortis, pilote_auto_actif, freins_actifs, lumiere_allume, niveau_poussee_reelle, heure_actuelle, world_x, RUNWAYS, portance, angle, gear_sorti, moteur_temp)
    
    # 2. HUD Overlay (Haut)
    if not args.no_hud:
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

    pygame.display.flip()
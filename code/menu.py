import customtkinter as ctk
import sys
import os
import subprocess
import json
import statistics
from PIL import Image, ImageTk
import pygame

if "--run-game-internal" in sys.argv:
    # On retire l'argument de sys.argv pour ne pas perturber l'argparse de game.py
    sys.argv.remove("--run-game-internal")
    import game
    sys.exit(0)

def resource_path(relative_path):
    import os, sys
    try:
        base_path = sys._MEIPASS
    except Exception:
        # Utiliser le dossier parent du dossier 'code/' pour trouver 'son/' et 'image/'
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# --- CONFIGURATION DU DESIGN ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# Palette "Premium Aero"
COL_BG = "#0B0F19"         # Bleu nuit très profond 
COL_SIDEBAR = "#111827"    # Gris anthracite/bleu
COL_PANEL = "#1F2937"      # Gris bleuté pour les cartes
COL_PRIMARY = "#2563EB"    # Bleu éléctrique (Sélections)
COL_HOVER = "#1D4ED8"      # Bleu foncé (Hover)
COL_TEXT = "#F9FAFB"       # Blanc cassé
COL_TEXT_MUTED = "#9CA3AF" # Gris clair
COL_ACCENT = "#10B981"     # Vert Émeraude (Bouton Jouer)
COL_ACCENT_HOVER = "#059669" # Vert Émeraude foncé
COL_DANGER = "#EF4444"     # Rouge (Quitter)

class MenuPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Fenêtre
        self.title("Pyflight 2D - Launcher Premium")
        self.geometry("1150x850")
        self.resizable(False, False)
        self.configure(fg_color=COL_BG)

        # Initialisation Sonore pour le Menu
        try:
            pygame.mixer.init()
            self.click_sound = pygame.mixer.Sound(resource_path("son/clique.mp3"))
        except Exception as e:
            print(f"Erreur initialisation son menu: {e}")
            self.click_sound = None

        # Variables de base
        self.var_difficulte = ctk.StringVar(value="easy")
        self.var_temps = ctk.StringVar(value="real")
        self.var_heure_manuelle = ctk.DoubleVar(value=12.0)
        self.var_season = ctk.StringVar(value="summer")
        self.var_weather = ctk.StringVar(value="clear")
        self.var_volume = ctk.DoubleVar(value=0.5)
        self.var_ui_sounds = ctk.BooleanVar(value=True)

        # Variables Graphiques
        self.var_show_hud = ctk.BooleanVar(value=True)
        self.var_show_w_dashboard = ctk.BooleanVar(value=True)
        self.var_show_clouds = ctk.BooleanVar(value=True)
        self.var_show_particles = ctk.BooleanVar(value=True)
        self.var_show_atmo = ctk.BooleanVar(value=True)
        self.var_show_terrain = ctk.BooleanVar(value=True)
        self.var_show_trail = ctk.BooleanVar(value=False)
        self.var_trail_color = ctk.StringVar(value="white")
        self.var_terrain_intensity = ctk.DoubleVar(value=1.0)

        # Variables Système & Visualisation
        self.var_fullscreen = ctk.BooleanVar(value=False)
        self.var_show_fps = ctk.BooleanVar(value=False)

        # Variables Réalisme & Gameplay
        self.var_unlimited_fuel = ctk.BooleanVar(value=False)
        self.var_god_mode = ctk.BooleanVar(value=False)
        self.var_no_stall = ctk.BooleanVar(value=False)
        self.var_no_gear_crash = ctk.BooleanVar(value=False)
        self.var_no_wind = ctk.BooleanVar(value=False)
        self.var_auto_refuel = ctk.BooleanVar(value=False)
        self.var_no_overheat = ctk.BooleanVar(value=False)
        self.var_static_weight = ctk.BooleanVar(value=False)
        
        self.var_aircraft = ctk.StringVar(value="cessna")
        self.var_fuel_initial = ctk.DoubleVar(value=100.0)
        self.var_missions = ctk.BooleanVar(value=False)
        self.var_mission_type = ctk.StringVar(value="none")
        self.var_num_birds = ctk.IntVar(value=20)
        self.var_num_planes = ctk.IntVar(value=5)

        # Variables Réseau
        self.var_multiplayer = ctk.BooleanVar(value=False)
        self.var_pseudo = ctk.StringVar(value="Pilote_1")
        self.var_ip = ctk.StringVar(value="127.0.0.1")

        # MASTER TOGGLES (Nouveaux Toggles Globaux Expert)
        self.var_m_audio = ctk.BooleanVar(value=True)
        self.var_m_weather = ctk.BooleanVar(value=True)
        self.var_m_daynight = ctk.BooleanVar(value=True)
        self.var_m_birds = ctk.BooleanVar(value=True)
        self.var_m_planes = ctk.BooleanVar(value=True)
        self.var_m_stall = ctk.BooleanVar(value=True)  # Inverse de no_stall
        self.var_m_overheat = ctk.BooleanVar(value=True)
        self.var_m_gear_crash = ctk.BooleanVar(value=True)
        self.var_m_fuel_cons = ctk.BooleanVar(value=True)
        self.var_m_dyn_weight = ctk.BooleanVar(value=True)
        self.var_m_wind = ctk.BooleanVar(value=True)

        # TOOTH/CHEAT MODIFIERS (Expert)
        self.var_zero_gravity = ctk.BooleanVar(value=False)
        self.var_no_drag = ctk.BooleanVar(value=False)
        self.var_no_brakes = ctk.BooleanVar(value=False)
        self.var_no_collisions = ctk.BooleanVar(value=False)
        self.var_crazy_wind = ctk.BooleanVar(value=False)
        self.var_always_boost = ctk.BooleanVar(value=False)
        
        # Synchronisation init avec les vars inversées existantes
        self.var_m_stall.set(not self.var_no_stall.get())
        self.var_m_overheat.set(not self.var_no_overheat.get())
        self.var_m_gear_crash.set(not self.var_no_gear_crash.get())
        self.var_m_fuel_cons.set(not self.var_unlimited_fuel.get())
        self.var_m_dyn_weight.set(not self.var_static_weight.get())
        self.var_m_wind.set(not self.var_no_wind.get())

        # Layout Principal (2 Colonnes: Sidebar / Contenu)
        self.grid_columnconfigure(0, weight=0) # Sidebar width fixed
        self.grid_columnconfigure(1, weight=1) # Main View
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR (GAUCHE) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color=COL_SIDEBAR)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsw")
        self.sidebar_frame.grid_rowconfigure(11, weight=1) # Espaceur entre les menus et le bouton jouer
        
        # En-Tête Sidebar
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="PYFLIGHT 2D", font=("Arial", 36, "bold"), text_color=COL_TEXT)
        self.logo_label.grid(row=0, column=0, padx=20, pady=(40, 5))
        self.edition_label = ctk.CTkLabel(self.sidebar_frame, text="ULTIMATE EDITION", font=("Arial", 12, "bold"), text_color=COL_PRIMARY)
        self.edition_label.grid(row=1, column=0, padx=20, pady=(0, 40))

        # Onglets (Boutons Sidebar)
        self.tab_buttons = []
        
        self.btn_tab_accueil = self.create_sidebar_btn("Vue d'ensemble", 2)
        self.btn_tab_base = self.create_sidebar_btn("Appareil & Vol", 3)
        self.btn_tab_garage = self.create_sidebar_btn("Carrière & Garage", 4)
        self.btn_tab_env = self.create_sidebar_btn("Environnement", 5)
        self.btn_tab_realism = self.create_sidebar_btn("Réalisme & Aides", 6)
        self.btn_tab_gfx = self.create_sidebar_btn("Affichage & Rendu", 7)
        self.btn_tab_stats = self.create_sidebar_btn("Scores & Stats", 8)
        self.btn_tab_multi = self.create_sidebar_btn("Réseau & Multi", 9)
        self.btn_tab_expert = self.create_sidebar_btn("Tous les Modules", 10)
        
        # Spacer pour repousser les boutons vers le bas grace au weight=1
        ctk.CTkFrame(self.sidebar_frame, fg_color="transparent").grid(row=11, column=0, sticky="nsew")

        # Boutons Action (Bas de Sidebar)
        self.btn_jouer = ctk.CTkButton(self.sidebar_frame, text="LANCER LE VOL", command=self.lancer_jeu,
                                       font=("Arial", 18, "bold"), height=55, fg_color=COL_ACCENT, hover_color=COL_ACCENT_HOVER)
        self.btn_jouer.grid(row=12, column=0, padx=20, pady=(10, 10), sticky="ew")

        self.btn_quitter = ctk.CTkButton(self.sidebar_frame, text="QUITTER", command=self.quit,
                                         font=("Arial", 14, "bold"), height=40, fg_color="transparent", 
                                         border_width=2, border_color=COL_DANGER, text_color=COL_DANGER, hover_color="#451a1a")
        self.btn_quitter.grid(row=13, column=0, padx=20, pady=(0, 20), sticky="ew")

        # --- CONTENU (DROITE) ---
        self.main_frame = ctk.CTkFrame(self, fg_color=COL_BG, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=40, pady=40)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Career Data
        self.career_data = self.load_career_data()

        # Dictionnaires des frames "pages"
        self.pages = {}
        
        self.build_page_accueil()
        self.build_page_base()
        self.build_page_garage()
        self.build_page_env()
        self.build_page_realism()
        self.build_page_gfx()
        self.build_page_scores()
        self.build_page_multi()
        self.build_page_expert()

        # Binding du clic pour le son d'interface
        self.bind("<Button-1>", self.on_global_click)

        # Init par défaut
        self.select_tab("Vue d'ensemble")

    def create_sidebar_btn(self, texte, row_idx):
        btn = ctk.CTkButton(self.sidebar_frame, text=texte, corner_radius=8, height=45, border_spacing=10,
                            fg_color="transparent", text_color=COL_TEXT_MUTED, hover_color=COL_PANEL, anchor="w",
                            font=("Arial", 14), command=lambda t=texte: self.select_tab(t))
        btn.grid(row=row_idx, column=0, sticky="ew", padx=15, pady=5)
        self.tab_buttons.append((texte, btn))
        return btn

    def on_global_click(self, event):
        if self.var_ui_sounds.get() and self.click_sound:
            try:
                self.click_sound.play()
            except:
                pass

    def select_tab(self, nom_tab):
        # Update colors on sidebar
        for nom, btn in self.tab_buttons:
            if nom == nom_tab:
                btn.configure(fg_color=COL_PRIMARY, text_color=COL_TEXT)
            else:
                btn.configure(fg_color="transparent", text_color=COL_TEXT_MUTED)
                
        # Si c'est l'onglet des scores, on le reconstruit pour le mettre à jour
        if nom_tab == "Scores & Stats":
            self.build_page_scores()
            
        # Si c'est l'onglet Appareil & Vol, on s'assure qu'il est synchronisé avec le garage
        if nom_tab == "Appareil & Vol":
            self.build_page_base()
                
        # Afficher la bonne page
        for t, page_frame in self.pages.items():
            if t == nom_tab:
                page_frame.grid(row=0, column=0, sticky="nsew")
            else:
                page_frame.grid_forget()

    # --- PAGES BUILDERS ---
    
    def load_career_data(self):
        if getattr(sys, 'frozen', False):
            dossier_exe = os.path.dirname(sys.executable)
            path_career = os.path.join(dossier_exe, "career.json")
        else:
            dossier = os.path.dirname(os.path.abspath(__file__))
            path_career = os.path.join(dossier, "career.json")
            
        data = {
            "coins": 0, 
            "upgrades": {},
            "stats": {
                "max_speed": 0,
                "max_alt": 0,
                "total_dist": 0,
                "total_landings": 0,
                "total_crashes": 0
            }
        }
        if os.path.exists(path_career):
            try:
                with open(path_career, "r", encoding="utf-8") as f:
                    data.update(json.load(f))
            except:
                pass
        
        # S'assurer que la structure stats existe
        if "stats" not in data:
            data["stats"] = {"max_speed": 0, "max_alt": 0, "total_dist": 0, "total_landings": 0, "total_crashes": 0}
                
        # Initialize default upgrades structure for all planes
        planes = ["cessna", "fighter", "cargo", "acro"]
        for p in planes:
            if p not in data["upgrades"]:
                data["upgrades"][p] = {"engine": 0, "finesse": 0, "fuel": 0, "weight": 0, "gear": 0, "cooling": 0, "brakes": 0}
            else:
                # Ajout des nouveaux types si manquants
                for upg in ["weight", "gear", "cooling", "brakes"]:
                    if upg not in data["upgrades"][p]:
                        data["upgrades"][p][upg] = 0
        return data
        
    def save_career_data(self):
        if getattr(sys, 'frozen', False):
            dossier_exe = os.path.dirname(sys.executable)
            path_career = os.path.join(dossier_exe, "career.json")
        else:
            dossier = os.path.dirname(os.path.abspath(__file__))
            path_career = os.path.join(dossier, "career.json")
            
        try:
            with open(path_career, "w", encoding="utf-8") as f:
                json.dump(self.career_data, f, indent=4)
        except:
            pass

    def build_page_garage(self):
        page_name = "Carrière & Garage"
        if page_name in self.pages:
            self.pages[page_name].destroy()
            
        page = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.pages[page_name] = page
        self.title_label(page, "Garage & Améliorations")
        
        # Reload data to ensure it's up to date
        self.career_data = self.load_career_data()
        coins = self.career_data.get("coins", 0)
        stats = self.career_data.get("stats", {})
        current_ac_name = self.var_aircraft.get()

        # --- BLOC CARRIÈRE ---
        c_stats = self.card_frame(page, "VOTRE CARRIÈRE (RECORDS)")
        f_st = ctk.CTkFrame(c_stats, fg_color="transparent")
        f_st.pack(fill="x", padx=15, pady=5)
        f_st.grid_columnconfigure((0,1,2,3,4), weight=1)

        def create_stat_mini(parent, title, value, col, unit=""):
            b = ctk.CTkFrame(parent, fg_color=COL_BG, corner_radius=8)
            b.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")
            ctk.CTkLabel(b, text=title, font=("Arial", 10, "bold"), text_color=COL_TEXT_MUTED).pack(pady=(10,2))
            ctk.CTkLabel(b, text=f"{value}{unit}", font=("Arial", 16, "bold"), text_color=COL_TEXT).pack(pady=(2,10))

        create_stat_mini(f_st, "Vitesse Max", int(stats.get("max_speed", 0)), 0, " km/h")
        create_stat_mini(f_st, "Alt Max", int(stats.get("max_alt", 0)), 1, " ft")
        create_stat_mini(f_st, "Dist Totale", int(stats.get("total_dist", 0)), 2, " km")
        create_stat_mini(f_st, "Atterrissages", stats.get("total_landings", 0), 3)
        create_stat_mini(f_st, "Crashs", stats.get("total_crashes", 0), 4)
        
        c_bank = self.card_frame(page, "VOTRE COMPTE")
        lbl_coins = ctk.CTkLabel(c_bank, text=f"💰 Pièces disponibles : {int(coins)}", font=("Arial", 24, "bold"), text_color="#F59E0B")
        lbl_coins.pack(pady=10)
        
        # --- VISUEL DE L'AVION ---
        # Menu de sélection de l'avion à améliorer
        f_select = ctk.CTkFrame(page, fg_color="transparent")
        f_select.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(f_select, text="Choisir l'avion à améliorer :", font=("Arial", 14)).pack(side="left", padx=10)
        
        def on_change_ac_garage(new_val):
            # On change la variable globale de l'avion sélectionné pour que le garage se mette à jour
            self.var_aircraft.set(new_val)
            self.build_page_garage()
            self.pages[page_name].grid(row=0, column=0, sticky="nsew")

        opt_ac = ctk.CTkOptionMenu(f_select, values=["cessna", "fighter", "cargo", "acro"], 
                                   command=on_change_ac_garage)
        opt_ac.set(current_ac_name)
        opt_ac.pack(side="left", padx=10)

        c_visual = self.card_frame(page, f"APPAREIL : {current_ac_name.upper()}")
        
        # Mapping images
        img_files = {
            "cessna": "Avion_Cessna_172-removebg-preview.png",
            "fighter": "Avion_de_chasse_sans_r-removebg-preview.png",
            "cargo": "Avion_cargo-removebg-preview.png",
            "acro": "Avion_acrobatique-removebg-preview.png"
        }
        
        try:
            img_path = resource_path(os.path.join("image", img_files.get(current_ac_name, "")))
            if os.path.exists(img_path):
                pil_img = Image.open(img_path)
                # Resize for menu
                ratio = pil_img.width / pil_img.height
                new_w = 300
                new_h = int(new_w / ratio)
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(new_w, new_h))
                lbl_img = ctk.CTkLabel(c_visual, image=ctk_img, text="")
                lbl_img.pack(pady=10)
        except Exception as e:
            print(f"Erreur chargement image garage: {e}")

        c_upg = self.card_frame(page, "AMÉLIORER LES SYSTÈMES (50 Niveaux)")
        
        current_ac = self.var_aircraft.get()
        upgrades = self.career_data["upgrades"].get(current_ac, {"engine": 0, "finesse": 0, "fuel": 0, "weight": 0, "gear": 0, "cooling": 0, "brakes": 0})
        
        def buy_upgrade(upg_type):
            lvl = self.career_data["upgrades"][current_ac][upg_type]
            if lvl >= 50: return
            
            # Prix réduit : 100 de base + 50 par niveau
            cost = 100 + (lvl * 50)
            
            if self.career_data["coins"] >= cost:
                self.career_data["coins"] -= cost
                self.career_data["upgrades"][current_ac][upg_type] += 1
                self.save_career_data()
                self.build_page_garage() # Refresh
                self.pages[page_name].grid(row=0, column=0, sticky="nsew")

        def create_upgrade_row(parent, title, upg_type, desc):
            f_row = ctk.CTkFrame(parent, fg_color=COL_BG, corner_radius=8)
            f_row.pack(fill="x", padx=15, pady=10, ipady=5)
            
            lvl = upgrades.get(upg_type, 0)
            
            f_info = ctk.CTkFrame(f_row, fg_color="transparent")
            f_info.pack(side="left", padx=15, fill="x", expand=True)
            ctk.CTkLabel(f_info, text=f"{title} (Niv. {lvl}/50)", font=("Arial", 16, "bold")).pack(anchor="w")
            ctk.CTkLabel(f_info, text=desc, font=("Arial", 12), text_color=COL_TEXT_MUTED).pack(anchor="w")
            
            # Progress bar visual (Plus compacte pour 50 niveaux)
            f_bars = ctk.CTkFrame(f_info, fg_color=COL_PANEL, height=10, width=250)
            f_bars.pack(anchor="w", pady=5)
            f_fill = ctk.CTkFrame(f_bars, height=10, width=int(250 * (lvl/50.0)), fg_color=COL_ACCENT)
            f_fill.place(x=0, y=0)
                
            if lvl < 50:
                cost = 100 + (lvl * 50)
                btn_buy = ctk.CTkButton(f_row, text=f"AMÉLIORER ({cost} 💰)", width=150, 
                                        command=lambda t=upg_type: buy_upgrade(t))
                if coins < cost:
                    btn_buy.configure(state="disabled", fg_color=COL_PANEL)
                btn_buy.pack(side="right", padx=15)
            else:
                ctk.CTkLabel(f_row, text="MAXIMUM", font=("Arial", 14, "bold"), text_color=COL_ACCENT).pack(side="right", padx=30)

        create_upgrade_row(c_upg, "Moteur & Poussée", "engine", "+1% puissance par niveau.")
        create_upgrade_row(c_upg, "Finesse Aérodynamique", "finesse", "+0.5% portance, -0.5% traînée par niveau.")
        create_upgrade_row(c_upg, "Réservoir Supplémentaire", "fuel", "+2% capacité fuel par niveau.")
        create_upgrade_row(c_upg, "Allègement Structurel", "weight", "-0.5% poids par niveau.")
        create_upgrade_row(c_upg, "Résistance du Train", "gear", "+1% tolérance vitesse/impact au sol.")
        create_upgrade_row(c_upg, "Refroidissement", "cooling", "-1% taux de surchauffe par niveau.")
        create_upgrade_row(c_upg, "Freins Haute Performance", "brakes", "+2% puissance de freinage par niveau.")


    def title_label(self, parent, text):
        lbl = ctk.CTkLabel(parent, text=text, font=("Arial", 28, "bold"), text_color=COL_TEXT)
        lbl.pack(anchor="w", pady=(0, 30))
        return lbl
        
    def card_frame(self, parent, title):
        card = ctk.CTkFrame(parent, fg_color=COL_PANEL, corner_radius=12)
        card.pack(fill="x", pady=10, ipady=10, ipadx=10)
        ctk.CTkLabel(card, text=title, font=("Arial", 14, "bold"), text_color=COL_PRIMARY).pack(anchor="w", padx=15, pady=(10, 15))
        return card

    def build_page_accueil(self):
        page_name = "Vue d'ensemble"
        if page_name in self.pages:
            self.pages[page_name].destroy()
            
        page = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.pages[page_name] = page
        
        self.title_label(page, "Bienvenue Commandant.")
        
        infos = """
PyFlight 2D vous offre une simulation aéronautique exigeante :

• Physique de vol avancée (Décrochage, Inertie, Traînée)
• Poids Dynamique & Surchauffe Moteur Réalistes
• Nouvelles Missions (Anneaux, Cargo, Atterrissage)
• Cibles au sol, Chronomètres et Statistiques de vol
• Trafic IA ambiant et Tour de Contrôle (ATC)
• Cycle Jour/Nuit, Météo Volumétrique & Océans Dynamiques
• Cockpit Interactif (HUD / Instruments Analogiques)
• Plan de Vol Interactif GPS (Touche 'M')
• Combat & Missions : Bombes (B), Missiles (V), Cargo (C). 
• Challenges : F1/F2 pour lancer des défis instantanés.
• Commandes Avancées : 'A' pour le Moteur, SHIFT/CTRL pour les gaz.
• Radio & Musique : K pour On/Off, N pour Suivant.
• Replay & Pause : P pour Pauser, R (maintenir) pour Rewind.

Configurez votre appareil via les onglets à gauche, 
puis cliquez sur LANCER LE VOL.
"""
        card = ctk.CTkFrame(page, fg_color="transparent")
        card.pack(fill="both", expand=True, pady=10)
        
        lbl_infos = ctk.CTkLabel(card, text=infos, font=("Consolas", 14), text_color=COL_TEXT_MUTED, justify="left")
        lbl_infos.pack(anchor="nw", padx=10, pady=10)
        
        # Image de fond ou illustration (Optionnel)
        # ctk.CTkLabel(page, text="[Illustration / Astuces]", font=("Arial", 16), text_color=COL_PANEL).pack(expand=True)

    def build_page_base(self):
        page_name = "Appareil & Vol"
        if page_name in self.pages:
            self.pages[page_name].destroy()
            
        page = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.pages[page_name] = page
        self.title_label(page, "Configuration de l'Appareil")

        # Avion
        c_avion = self.card_frame(page, "CHOIX DE L'APPAREIL")
        def set_aircraft(val):
            map_a = {"Cessna (Standard)": "cessna", "Chasseur (Armé)": "fighter",  "Gros Porteur (Lourd)": "cargo", "Acrobatique (Voltige)": "acro"}
            self.var_aircraft.set(map_a.get(val, "cessna"))
            
        opt_avion = ctk.CTkOptionMenu(c_avion, values=["Cessna (Standard)", "Chasseur (Armé)", "Gros Porteur (Lourd)", "Acrobatique (Voltige)"], 
                                      command=set_aircraft, width=300, height=40)
        opt_avion.pack(anchor="w", padx=15, pady=5)
        
        # Synchronisation inverse : map du code vers le texte du menu
        inv_map = {"cessna": "Cessna (Standard)", "fighter": "Chasseur (Armé)", "cargo": "Gros Porteur (Lourd)", "acro": "Acrobatique (Voltige)"}
        opt_avion.set(inv_map.get(self.var_aircraft.get(), "Cessna (Standard)"))

        c_mode = self.card_frame(page, "MODE DE JEU")
        
        # Frame pour contenir le segment et le dropdown (pour un layout propre)
        f_mode = ctk.CTkFrame(c_mode, fg_color="transparent")
        f_mode.pack(fill="x", padx=15, pady=(0, 10))
        
        opt_mission = ctk.CTkOptionMenu(c_mode, values=["Aucune (Trafic & ATC Seuls)", "Parcours d'Anneaux", "Atterrissage de Précision", "Largage Cargo (Requis: Avion Cargo)"], width=300, height=40)
        
        def set_mission_type(val):
            map_m = {
                "Aucune (Trafic & ATC Seuls)": "none",
                "Parcours d'Anneaux": "rings",
                "Atterrissage de Précision": "landing",
                "Largage Cargo (Requis: Avion Cargo)": "cargo"
            }
            self.var_mission_type.set(map_m.get(val, "none"))
            
        opt_mission.configure(command=set_mission_type)
        opt_mission.pack(anchor="w", padx=15, pady=(0, 10))
        opt_mission.set("Aucune (Trafic & ATC Seuls)")
        
        def set_gamemode(val):
            is_mission = (val == "CARRIÈRE & MISSIONS")
            self.var_missions.set(is_mission)
            if is_mission:
                opt_mission.configure(state="normal")
            else:
                opt_mission.configure(state="disabled")
            
        seg_mode = ctk.CTkSegmentedButton(f_mode, values=["VOL LIBRE", "CARRIÈRE & MISSIONS"], command=set_gamemode, height=35)
        seg_mode.pack(anchor="w", fill="x")
        seg_mode.set("CARRIÈRE & MISSIONS" if self.var_missions.get() else "VOL LIBRE")
        opt_mission.configure(state="normal" if self.var_missions.get() else "disabled")

        # Difficulté
        c_diff = self.card_frame(page, "MODE DE PILOTAGE")
        def set_diff(val):
            self.var_difficulte.set("easy" if "FACILE" in val else "real")
        seg_diff = ctk.CTkSegmentedButton(c_diff, values=["FACILE (Assisté)", "RÉALISTE"], command=set_diff, height=35)
        seg_diff.pack(anchor="w", padx=15, fill="x")
        seg_diff.set("FACILE (Assisté)" if self.var_difficulte.get()=="easy" else "RÉALISTE")
        
        # Heure de Vol
        c_time = self.card_frame(page, "HEURE & HORLOGE")
        def set_time_mode(val):
            if val == "DYNAMIQUE":
                self.var_temps.set("dynamic")
                self.slider_heure.configure(state="disabled")
            elif val == "RÉEL (FR)":
                self.var_temps.set("real")
                self.slider_heure.configure(state="disabled")
            else:
                self.var_temps.set("manual")
                self.slider_heure.configure(state="normal")
                
        seg_time = ctk.CTkSegmentedButton(c_time, values=["MANUEL", "RÉEL (FR)", "DYNAMIQUE"], command=set_time_mode, height=35)
        seg_time.pack(anchor="w", padx=15, fill="x", pady=(0, 15))
        seg_time.set("RÉEL (FR)")

        f_slid = ctk.CTkFrame(c_time, fg_color="transparent")
        f_slid.pack(fill="x", padx=15)
        self.lbl_heure_val = ctk.CTkLabel(f_slid, text=f"{int(self.var_heure_manuelle.get())}H", font=("Arial", 16, "bold"))
        self.lbl_heure_val.pack(side="right", padx=10)
        
        def update_lbl(val): self.lbl_heure_val.configure(text=f"{int(val)}H")
        self.slider_heure = ctk.CTkSlider(f_slid, from_=0, to=23, number_of_steps=24, variable=self.var_heure_manuelle, command=update_lbl)
        self.slider_heure.pack(fill="x", side="left", expand=True)
        self.slider_heure.configure(state="disabled")

    def build_page_env(self):
        page_name = "Environnement"
        if page_name in self.pages:
            self.pages[page_name].destroy()
            
        page = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.pages[page_name] = page
        self.title_label(page, "Environnement & Monde")

        c_meteo = self.card_frame(page, "CONDITIONS MÉTÉOROLOGIQUES")
        def set_weather_opt(val):
            map_w = {"CIEL CLAIR": "clear", "NUAGES VOLUMÉTRIQUES": "clouds", "BROUILLARD ÉPAIS": "fog"}
            self.var_weather.set(map_w.get(val, "clear"))
        opt_w = ctk.CTkOptionMenu(c_meteo, values=["CIEL CLAIR", "NUAGES VOLUMÉTRIQUES", "BROUILLARD ÉPAIS"], command=set_weather_opt, width=300, height=40)
        opt_w.pack(anchor="w", padx=15, pady=5)
        
        c_season = self.card_frame(page, "PALETTE SAISONNIÈRE")
        def set_season(val):
            map_s = {"PRINTEMPS (Fleurs)": "spring", "ÉTÉ (Vert)": "summer", "AUTOMNE (Roux)": "autumn", "HIVER (Neige)": "snow", "TEMPÊTE (Gris)": "wind"}
            self.var_season.set(map_s.get(val, "summer"))
        opt_s = ctk.CTkOptionMenu(c_season, values=["PRINTEMPS (Fleurs)", "ÉTÉ (Vert)", "AUTOMNE (Roux)", "HIVER (Neige)", "TEMPÊTE (Gris)"], command=set_season, width=300, height=40)
        opt_s.pack(anchor="w", padx=15, pady=5)
        opt_s.set("ÉTÉ (Vert)")
        
        c_terrain = self.card_frame(page, "GÉNÉRATION DU RELIEF")
        self.lbl_terrain = ctk.CTkLabel(c_terrain, text=f"Multiplicateur des Alpes : {self.var_terrain_intensity.get():.1f}x", text_color=COL_TEXT_MUTED)
        self.lbl_terrain.pack(anchor="w", padx=15)
        def update_terrain_lbl(val): self.lbl_terrain.configure(text=f"Multiplicateur des Alpes : {val:.1f}x")
        ctk.CTkSlider(c_terrain, from_=0.0, to=5.0, number_of_steps=50, variable=self.var_terrain_intensity, command=update_terrain_lbl).pack(fill="x", padx=15, pady=(5, 10))

        c_sound = self.card_frame(page, "VOLUME SONORE MOTEUR")
        ctk.CTkSlider(c_sound, from_=0.0, to=1.0, variable=self.var_volume).pack(fill="x", padx=15, pady=(10, 15))
        
        ctk.CTkCheckBox(c_sound, text="Activer les sons d'interface (Clics)", variable=self.var_ui_sounds).pack(anchor="w", padx=15, pady=(0, 10))

        c_traffic = self.card_frame(page, "DENSITÉ DU TRAFIC & FAUNE")
        self.lbl_birds = ctk.CTkLabel(c_traffic, text=f"Nombre maximum d'oiseaux : {self.var_num_birds.get()}", text_color=COL_TEXT_MUTED)
        self.lbl_birds.pack(anchor="w", padx=15)
        def update_birds_lbl(val): self.lbl_birds.configure(text=f"Nombre maximum d'oiseaux : {int(val)}")
        ctk.CTkSlider(c_traffic, from_=0, to=100, number_of_steps=100, variable=self.var_num_birds, command=update_birds_lbl).pack(fill="x", padx=15, pady=(5, 10))
        
        self.lbl_planes = ctk.CTkLabel(c_traffic, text=f"Nombre maximum d'avions IA : {self.var_num_planes.get()}", text_color=COL_TEXT_MUTED)
        self.lbl_planes.pack(anchor="w", padx=15)
        def update_planes_lbl(val): self.lbl_planes.configure(text=f"Nombre maximum d'avions IA : {int(val)}")
        ctk.CTkSlider(c_traffic, from_=0, to=20, number_of_steps=20, variable=self.var_num_planes, command=update_planes_lbl).pack(fill="x", padx=15, pady=(5, 15))


    def build_page_realism(self):
        page_name = "Réalisme & Aides"
        if page_name in self.pages:
            self.pages[page_name].destroy()
            
        page = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.pages[page_name] = page
        self.title_label(page, "Ajustement du Réalisme")
        
        c_poids = self.card_frame(page, "GESTION CARBURANT & POIDS (Idée 5)")
        self.lbl_fuel = ctk.CTkLabel(c_poids, text=f"Carburant Embarqué : {int(self.var_fuel_initial.get())}%", text_color=COL_TEXT_MUTED)
        self.lbl_fuel.pack(anchor="w", padx=15, pady=(0, 5))
        def update_fuel_lbl(val): self.lbl_fuel.configure(text=f"Carburant Embarqué : {int(val)}%")
        ctk.CTkSlider(c_poids, from_=10.0, to=100.0, variable=self.var_fuel_initial, command=update_fuel_lbl).pack(fill="x", padx=15, pady=(0, 20))
        
        # Grid layout for checkboxes
        chk_frame1 = ctk.CTkFrame(c_poids, fg_color="transparent")
        chk_frame1.pack(fill="x", padx=15)
        ctk.CTkCheckBox(chk_frame1, text="Carburant Illimité", variable=self.var_unlimited_fuel).pack(side="left", padx=(0, 20), pady=10)
        ctk.CTkCheckBox(chk_frame1, text="Poids Statique (Ignorer le Fuel)", variable=self.var_static_weight).pack(side="left", padx=20, pady=10)
        ctk.CTkCheckBox(chk_frame1, text="Ravitaillement Auto", variable=self.var_auto_refuel).pack(side="left", padx=20, pady=10)
        
        c_meca = self.card_frame(page, "MÉCANIQUES DE VOL")
        chk_frame2 = ctk.CTkFrame(c_meca, fg_color="transparent")
        chk_frame2.pack(fill="x", padx=15)
        
        left_col = ctk.CTkFrame(chk_frame2, fg_color="transparent")
        left_col.pack(side="left", fill="y", expand=True)
        right_col = ctk.CTkFrame(chk_frame2, fg_color="transparent")
        right_col.pack(side="left", fill="y", expand=True)

        ctk.CTkCheckBox(left_col, text="Désactiver Surchauffe (Idée 4)", variable=self.var_no_overheat).pack(anchor="w", pady=10)
        ctk.CTkCheckBox(left_col, text="Désactiver le Décrochage", variable=self.var_no_stall).pack(anchor="w", pady=10)
        ctk.CTkCheckBox(left_col, text="God Mode (Invincible)", variable=self.var_god_mode).pack(anchor="w", pady=10)
        
        ctk.CTkCheckBox(right_col, text="Pas de vent ni turbulences", variable=self.var_no_wind).pack(anchor="w", pady=10)
        ctk.CTkCheckBox(right_col, text="Atterrissage ventre sécurisé", variable=self.var_no_gear_crash).pack(anchor="w", pady=10)


    def build_page_gfx(self):
        page_name = "Affichage & Rendu"
        if page_name in self.pages:
            self.pages[page_name].destroy()
            
        page = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.pages[page_name] = page
        self.title_label(page, "Options Graphiques")

        c_ui = self.card_frame(page, "INTERFACE COCKPIT")
        f_ui = ctk.CTkFrame(c_ui, fg_color="transparent")
        f_ui.pack(fill="x", padx=15, pady=5)
        ctk.CTkCheckBox(f_ui, text="Afficher HUD (Affichage Tête Haute)", variable=self.var_show_hud).pack(side="left", padx=(0, 20))
        ctk.CTkCheckBox(f_ui, text="Afficher Tableau de Bord (Analogique)", variable=self.var_show_w_dashboard).pack(side="left", padx=20)

        c_fx = self.card_frame(page, "EFFETS VISUELS")
        f_fx = ctk.CTkFrame(c_fx, fg_color="transparent")
        f_fx.pack(fill="x", padx=15, pady=5)
        
        l_fx = ctk.CTkFrame(f_fx, fg_color="transparent")
        l_fx.pack(side="left", fill="y", expand=True)
        r_fx = ctk.CTkFrame(f_fx, fg_color="transparent")
        r_fx.pack(side="left", fill="y", expand=True)
        
        ctk.CTkCheckBox(l_fx, text="Nuages 2D", variable=self.var_show_clouds).pack(anchor="w", pady=10)
        ctk.CTkCheckBox(l_fx, text="Particules Cinétiques", variable=self.var_show_particles).pack(anchor="w", pady=10)
        ctk.CTkCheckBox(l_fx, text="Dégradé Atmosphérique", variable=self.var_show_atmo).pack(anchor="w", pady=10)
        
        ctk.CTkCheckBox(r_fx, text="Détails Terrain (Arbres, etc)", variable=self.var_show_terrain).pack(anchor="w", pady=10)
        
        f_trail = ctk.CTkFrame(r_fx, fg_color="transparent")
        f_trail.pack(anchor="w", pady=10)
        ctk.CTkCheckBox(f_trail, text="Fumée Acrobatique ", variable=self.var_show_trail).pack(side="left", padx=(0, 10))
        ctk.CTkOptionMenu(f_trail, values=["white", "red", "blue", "green", "yellow"], variable=self.var_trail_color, width=100, height=28).pack(side="left")

        c_sys = self.card_frame(page, "MOTEUR DE JEU")
        f_sys = ctk.CTkFrame(c_sys, fg_color="transparent")
        f_sys.pack(fill="x", padx=15, pady=5)
        ctk.CTkCheckBox(f_sys, text="Mode Plein Écran Natif", variable=self.var_fullscreen).pack(side="left", padx=(0, 20))
        ctk.CTkCheckBox(f_sys, text="Afficher Compteur FPS", variable=self.var_show_fps).pack(side="left", padx=20)

    def build_page_scores(self):
        page_name = "Scores & Stats"
        # On recrée l'onglet si besoin (actualisation)
        if page_name in self.pages:
            self.pages[page_name].destroy()
            
        page = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.pages[page_name] = page
        
        self.title_label(page, "Vos Statistiques et Performances")
        
        # Lecture du json. On le garde à côté de l'exécutable pour qu'il soit persistant
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
                pass
                
        mission_labels = {
            "rings": "Parcours d'Anneaux",
            "landing": "Atterrissage de Précision",
            "cargo": "Largage Cargo"
        }
        
        for key, name in mission_labels.items():
            card = self.card_frame(page, name.upper())
            s_list = scores_data.get(key, [])
            
            if not s_list:
                ctk.CTkLabel(card, text="Aucune donnée (Jouez une partie pour afficher les scores)", text_color=COL_TEXT_MUTED).pack(pady=10)
            else:
                best = max(s_list)
                mean = int(statistics.mean(s_list))
                median = int(statistics.median(s_list))
                
                f_stats = ctk.CTkFrame(card, fg_color="transparent")
                f_stats.pack(fill="x", padx=15, pady=5)
                f_stats.grid_columnconfigure((0,1,2), weight=1)
                
                # Bloc Meilleur
                b1 = ctk.CTkFrame(f_stats, fg_color=COL_BG, corner_radius=8)
                b1.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
                ctk.CTkLabel(b1, text="MEILLEUR SCORE", font=("Arial", 12, "bold"), text_color=COL_TEXT_MUTED).pack(pady=(15,5))
                ctk.CTkLabel(b1, text=f"{best}", font=("Arial", 36, "bold"), text_color=COL_ACCENT).pack(pady=(5,15))
                
                # Bloc Moyenne
                b2 = ctk.CTkFrame(f_stats, fg_color=COL_BG, corner_radius=8)
                b2.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
                ctk.CTkLabel(b2, text="MOYENNE", font=("Arial", 12, "bold"), text_color=COL_TEXT_MUTED).pack(pady=(15,5))
                ctk.CTkLabel(b2, text=f"{mean}", font=("Arial", 36, "bold"), text_color=COL_PRIMARY).pack(pady=(5,15))
                
                # Bloc Médiane
                b3 = ctk.CTkFrame(f_stats, fg_color=COL_BG, corner_radius=8)
                b3.grid(row=0, column=2, padx=10, pady=5, sticky="nsew")
                ctk.CTkLabel(b3, text="MÉDIANE", font=("Arial", 12, "bold"), text_color=COL_TEXT_MUTED).pack(pady=(15,5))
                ctk.CTkLabel(b3, text=f"{median}", font=("Arial", 36, "bold"), text_color="#A3B8CC").pack(pady=(5,15))
                
                ctk.CTkLabel(card, text=f"Parties jouées : {len(s_list)}", text_color=COL_TEXT_MUTED, font=("Arial", 12, "italic")).pack(pady=(5,0))


    def build_page_multi(self):
        page_name = "Réseau & Multi"
        if page_name in self.pages:
            self.pages[page_name].destroy()
            
        page = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.pages[page_name] = page
        self.title_label(page, "Multijoueur en Ligne")
        
        c_conn = self.card_frame(page, "CONNEXION AU SERVEUR")
        ctk.CTkCheckBox(c_conn, text="Activer le mode Multijoueur", variable=self.var_multiplayer).pack(anchor="w", padx=15, pady=10)
        
        f_pseudo = ctk.CTkFrame(c_conn, fg_color="transparent")
        f_pseudo.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(f_pseudo, text="Votre Pseudo :", width=120, anchor="w").pack(side="left")
        ctk.CTkEntry(f_pseudo, textvariable=self.var_pseudo, width=200).pack(side="left", padx=10)
        
        f_ip = ctk.CTkFrame(c_conn, fg_color="transparent")
        f_ip.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(f_ip, text="IP du Serveur :", width=120, anchor="w").pack(side="left")
        ctk.CTkEntry(f_ip, textvariable=self.var_ip, width=200).pack(side="left", padx=10)
        
        ctk.CTkLabel(c_conn, text="(Laissez 127.0.0.1 pour jouer sur votre propre PC)", text_color=COL_TEXT_MUTED, font=("Arial", 11, "italic")).pack(anchor="w", padx=15, pady=(0, 10))

        c_host = self.card_frame(page, "HÉBERGER UNE PARTIE")
        lbl_host = ctk.CTkLabel(c_host, text="Vous pouvez héberger le serveur sur cette machine.\nAssurez-vous d'avoir ouvert le port UDP 5555 sur votre routeur.", justify="left", text_color=COL_TEXT_MUTED)
        lbl_host.pack(anchor="w", padx=15, pady=5)
        
        def start_server_bg():
            import subprocess, os
            subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "server.py")])
            btn_host.configure(text="Serveur Lancé !", state="disabled", fg_color=COL_PRIMARY)
            
        btn_host = ctk.CTkButton(c_host, text="Démarrer le Serveur Local", command=start_server_bg, fg_color=COL_ACCENT)
        btn_host.pack(anchor="w", padx=15, pady=10)

    def build_page_expert(self):
        page_name = "Tous les Modules"
        if page_name in self.pages:
            self.pages[page_name].destroy()
            
        page = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.pages[page_name] = page
        self.title_label(page, "Mode Expert : Tous les Modules")
        
        lbl_info = ctk.CTkLabel(page, text="Activez ou désactivez intégralement chaque système du jeu.\nCeci supplante certains réglages des autres onglets.", justify="left", text_color=COL_PRIMARY)
        lbl_info.pack(anchor="w", padx=15, pady=(0, 15))
        
        # Colonnes pour organiser les checkboxes
        f_cols = ctk.CTkFrame(page, fg_color="transparent")
        f_cols.pack(fill="x", padx=15)
        col1 = ctk.CTkFrame(f_cols, fg_color="transparent")
        col1.pack(side="left", fill="y", expand=True)
        col2 = ctk.CTkFrame(f_cols, fg_color="transparent")
        col2.pack(side="right", fill="y", expand=True, padx=(20, 0))

        def create_toggle(parent, text, var, command_sync=None):
            cb = ctk.CTkCheckBox(parent, text=text, variable=var, command=command_sync, font=("Arial", 13, "bold"), text_color=COL_TEXT)
            cb.pack(anchor="w", pady=8)
            
        def sync_inverted(master_var, inverted_var):
            inverted_var.set(not master_var.get())
            
        # --- COLONNE 1 ---
        ctk.CTkLabel(col1, text="✈️ MÉCANIQUES DE VOL", text_color=COL_TEXT_MUTED, font=("Arial", 14, "bold")).pack(anchor="w", pady=(10, 5))
        create_toggle(col1, "Décrochage Aérodynamique", self.var_m_stall, lambda: sync_inverted(self.var_m_stall, self.var_no_stall))
        create_toggle(col1, "Surchauffe Moteur", self.var_m_overheat, lambda: sync_inverted(self.var_m_overheat, self.var_no_overheat))
        create_toggle(col1, "Dégâts Train d'Atterrissage", self.var_m_gear_crash, lambda: sync_inverted(self.var_m_gear_crash, self.var_no_gear_crash))
        create_toggle(col1, "Consommation de Carburant", self.var_m_fuel_cons, lambda: sync_inverted(self.var_m_fuel_cons, self.var_unlimited_fuel))
        create_toggle(col1, "Poids Statique (Ignorer Fuel)", self.var_static_weight) # Attention: on garde le nom "Poids Statique" donc inversé visuellement
        
        ctk.CTkLabel(col1, text="⛅ ENVIRONNEMENT", text_color=COL_TEXT_MUTED, font=("Arial", 14, "bold")).pack(anchor="w", pady=(20, 5))
        create_toggle(col1, "Cycle Jour/Nuit Automatique", self.var_m_daynight)
        create_toggle(col1, "Système Météorologique (Nuages/Brouillard)", self.var_m_weather)
        create_toggle(col1, "Générateur de Vent & Turbulences", self.var_m_wind, lambda: sync_inverted(self.var_m_wind, self.var_no_wind))
        create_toggle(col1, "Relief Terrestre Détaillé", self.var_show_terrain)

        ctk.CTkLabel(col1, text="🦅 TRAFIC & ENTITÉS", text_color=COL_TEXT_MUTED, font=("Arial", 14, "bold")).pack(anchor="w", pady=(20, 5))
        create_toggle(col1, "Avions IA (Trafic Aérien)", self.var_m_planes)
        create_toggle(col1, "Faune (Oiseaux, Mouettes)", self.var_m_birds)
        create_toggle(col1, "Missions Interactives", self.var_missions)

        # --- COLONNE 2 ---
        ctk.CTkLabel(col2, text="🎨 RENDU VISUEL & EFFETS", text_color=COL_TEXT_MUTED, font=("Arial", 14, "bold")).pack(anchor="w", pady=(10, 5))
        create_toggle(col2, "Nuages 2D Volumétriques", self.var_show_clouds)
        create_toggle(col2, "Particules (Pluie/Neige/Explosions)", self.var_show_particles)
        create_toggle(col2, "Dégradé Atmosphérique Ciel", self.var_show_atmo)
        create_toggle(col2, "Traînées de Condensation / Fumée", self.var_show_trail)

        ctk.CTkLabel(col2, text="🎛️ INTERFACE & AUDIO", text_color=COL_TEXT_MUTED, font=("Arial", 14, "bold")).pack(anchor="w", pady=(20, 5))
        create_toggle(col2, "HUD (Affichage Tête Haute)", self.var_show_hud)
        create_toggle(col2, "Tableau de Bord Analogique", self.var_show_w_dashboard)
        create_toggle(col2, "Compteur de Performances FPS", self.var_show_fps)
        create_toggle(col2, "Tous les effets Audio & Moteur", self.var_m_audio)
        create_toggle(col2, "Sons d'interface UI", self.var_ui_sounds)
        
        ctk.CTkLabel(col2, text="⚙️ SYSTÈME & AIDES", text_color=COL_TEXT_MUTED, font=("Arial", 14, "bold")).pack(anchor="w", pady=(20, 5))
        create_toggle(col2, "Plein Écran Natif", self.var_fullscreen)
        create_toggle(col2, "Mode Invincible (God Mode)", self.var_god_mode)
        create_toggle(col2, "Ravitaillement Auto sur Piste", self.var_auto_refuel)
        
        ctk.CTkLabel(col2, text="🔥 MODIFICATEURS EXTRÊMES", text_color=COL_TEXT_MUTED, font=("Arial", 14, "bold")).pack(anchor="w", pady=(20, 5))
        create_toggle(col2, "Apesanteur (Zéro Gravité)", self.var_zero_gravity)
        create_toggle(col2, "Zéro Traînée Aérodynamique", self.var_no_drag)
        create_toggle(col2, "Freins Inopérants", self.var_no_brakes)
        create_toggle(col2, "Pas de Collisions (Passe-murailles)", self.var_no_collisions)
        create_toggle(col2, "Vent Tempétueux (Aléatoire)", self.var_crazy_wind)
        create_toggle(col2, "Boost Moteur x3 Constant", self.var_always_boost)

    def lancer_jeu(self):
        # On cache le menu au lieu de le détruire
        self.withdraw()
        
        if getattr(sys, 'frozen', False):
            cmd = [sys.executable, "--run-game-internal"]
        else:
            cmd = [sys.executable, sys.argv[0], "--run-game-internal"]
        
        # Mapping base
        cmd.extend(["--difficulty", self.var_difficulte.get()])
        # Surcharge des variables selon les toggles Expert
        if not self.var_m_audio.get():
            self.var_volume.set(0.0)
            
        if not self.var_m_daynight.get():
            self.var_temps.set("manual")
            self.var_heure_manuelle.set(12.0)
            
        if not self.var_m_weather.get():
            self.var_weather.set("clear")
            
        # Remplacement "Master" des arguments au lancement
        cmd.extend(["--volume", str(self.var_volume.get())])
        if self.var_ui_sounds.get(): cmd.append("--ui-sounds")
        cmd.extend(["--aircraft", self.var_aircraft.get()])
        
        if self.var_temps.get() == "real": cmd.extend(["--time", "real"])
        elif self.var_temps.get() == "dynamic": cmd.extend(["--time", "dynamic"])
        else: cmd.extend(["--time", str(self.var_heure_manuelle.get())])
            
        cmd.extend(["--weather", self.var_weather.get()])
            
        # Graphiques
        if not self.var_show_hud.get(): cmd.append("--no-hud")
        if not self.var_show_w_dashboard.get(): cmd.append("--no-dash")
        if not self.var_show_clouds.get(): cmd.append("--no-clouds")
        if not self.var_show_particles.get(): cmd.append("--no-particles")
        if not self.var_show_atmo.get(): cmd.append("--no-atmo")
        if not self.var_show_terrain.get(): cmd.append("--no-terrain")
        if self.var_show_trail.get(): 
            cmd.append("--show-trail")
            cmd.extend(["--trail-color", self.var_trail_color.get()])
        cmd.extend(["--terrain-intensity", str(self.var_terrain_intensity.get())])
        
        # Gameplay
        if self.var_missions.get(): 
            cmd.append("--missions")
            if self.var_mission_type.get() != "none":
                cmd.extend(["--mission-type", self.var_mission_type.get()])
        if not self.var_m_fuel_cons.get(): cmd.append("--unlimited-fuel")
        if self.var_god_mode.get(): cmd.append("--god-mode")
        if self.var_fullscreen.get(): cmd.append("--fullscreen")
        if self.var_show_fps.get(): cmd.append("--show-fps")
        cmd.extend(["--fuel", str(self.var_fuel_initial.get())])
        
        # Objets Extreme
        if getattr(self, "var_zero_gravity", ctk.BooleanVar(value=False)).get(): cmd.append("--no-gravity")
        if getattr(self, "var_no_drag", ctk.BooleanVar(value=False)).get(): cmd.append("--no-drag")
        if getattr(self, "var_no_brakes", ctk.BooleanVar(value=False)).get(): cmd.append("--no-brakes")
        if getattr(self, "var_no_collisions", ctk.BooleanVar(value=False)).get(): cmd.append("--no-collisions")
        if getattr(self, "var_crazy_wind", ctk.BooleanVar(value=False)).get(): cmd.append("--crazy-wind")
        if getattr(self, "var_always_boost", ctk.BooleanVar(value=False)).get(): cmd.append("--always-boost")
        
        # Réalisme
        if not self.var_m_stall.get(): cmd.append("--no-stall")
        if not self.var_m_gear_crash.get(): cmd.append("--no-gear-crash")
        if not self.var_m_overheat.get(): cmd.append("--no-overheat")
        if self.var_static_weight.get(): cmd.append("--static-weight")
        if not self.var_m_wind.get(): cmd.append("--no-wind")
        if self.var_auto_refuel.get(): cmd.append("--auto-refuel")

        # Saison
        cmd.extend(["--season", self.var_season.get()])
        
        # Trafic (Surcharge Expert)
        if self.var_m_birds.get():
            cmd.extend(["--num-birds", str(int(self.var_num_birds.get()))])
        else:
            cmd.extend(["--num-birds", "0"])
            
        if self.var_m_planes.get():
            cmd.extend(["--num-planes", str(int(self.var_num_planes.get()))])
        else:
            cmd.extend(["--num-planes", "0"])
        
        # Multiplayer
        if self.var_multiplayer.get():
            cmd.append("--multiplayer")
            cmd.extend(["--ip", self.var_ip.get()])
            cmd.extend(["--pseudo", self.var_pseudo.get()])
            
        # Upgrades (Carrière)
        # Rafraichit pour avoir les dernières infos
        self.career_data = self.load_career_data() 
        current_ac = self.var_aircraft.get()
        upgs = self.career_data.get("upgrades", {}).get(current_ac, {"engine":0, "finesse":0, "fuel":0, "weight":0, "gear":0, "cooling":0, "brakes":0})
        cmd.extend(["--upg-engine", str(upgs.get("engine", 0))])
        cmd.extend(["--upg-finesse", str(upgs.get("finesse", 0))])
        cmd.extend(["--upg-fuel", str(upgs.get("fuel", 0))])
        cmd.extend(["--upg-weight", str(upgs.get("weight", 0))])
        cmd.extend(["--upg-gear", str(upgs.get("gear", 0))])
        cmd.extend(["--upg-cooling", str(upgs.get("cooling", 0))])
        cmd.extend(["--upg-brakes", str(upgs.get("brakes", 0))])
        
        print(f"Lancement de : {cmd}")
        subprocess.run(cmd)
        
        # --- RETOUR AU MENU ---
        # Le jeu a été quitté (ex: touche Echap), on réaffiche le menu
        # On reconstruit TOUTES les pages pour garantir la stabilité de l'interface
        self.build_page_accueil()
        self.build_page_base()
        self.build_page_garage()
        self.build_page_scores()
        self.build_page_multi()
        self.build_page_expert()
        
        # On retourne sur l'onglet d'accueil par défaut
        self.select_tab("Vue d'ensemble")
        self.deiconify()

if __name__ == "__main__":
    app = MenuPrincipal()
    app.mainloop()
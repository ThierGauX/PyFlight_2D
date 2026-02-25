import customtkinter as ctk
import sys
import os
import subprocess
from PIL import Image, ImageTk

def resource_path(relative_path):
    import os, sys
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
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
        self.geometry("1100x750")
        self.resizable(False, False)
        self.configure(fg_color=COL_BG)

        # Variables de base
        self.var_difficulte = ctk.StringVar(value="easy")
        self.var_temps = ctk.StringVar(value="real")
        self.var_heure_manuelle = ctk.DoubleVar(value=12.0)
        self.var_season = ctk.StringVar(value="summer")
        self.var_weather = ctk.StringVar(value="clear")
        self.var_volume = ctk.DoubleVar(value=0.5)

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

        # Layout Principal (2 Colonnes: Sidebar / Contenu)
        self.grid_columnconfigure(0, weight=0) # Sidebar width fixed
        self.grid_columnconfigure(1, weight=1) # Main View
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR (GAUCHE) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color=COL_SIDEBAR)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsw")
        self.sidebar_frame.grid_rowconfigure(5, weight=1) # Espaceur entre les menus et le bouton jouer
        
        # En-Tête Sidebar
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="PYFLIGHT 2D", font=("Impact", 36), text_color=COL_TEXT)
        self.logo_label.grid(row=0, column=0, padx=20, pady=(40, 5))
        self.edition_label = ctk.CTkLabel(self.sidebar_frame, text="ULTIMATE EDITION", font=("Arial", 12, "bold"), text_color=COL_PRIMARY)
        self.edition_label.grid(row=1, column=0, padx=20, pady=(0, 40))

        # Onglets (Boutons Sidebar)
        self.tab_buttons = []
        
        self.btn_tab_accueil = self.create_sidebar_btn("🏠  Vue d'ensemble", 2)
        self.btn_tab_base = self.create_sidebar_btn("✈️  Appareil & Vol", 3)
        self.btn_tab_env = self.create_sidebar_btn("⛅  Environnement", 4)
        self.btn_tab_realism = self.create_sidebar_btn("⚙️  Réalisme & Aides", 5)
        self.btn_tab_gfx = self.create_sidebar_btn("📺  Affichage & Rendu", 6)
        
        # Spacer
        ctk.CTkFrame(self.sidebar_frame, fg_color="transparent").grid(row=7, column=0, sticky="ns", pady=20)

        # Boutons Action (Bas de Sidebar)
        self.btn_jouer = ctk.CTkButton(self.sidebar_frame, text="LANCER LE VOL", command=self.lancer_jeu,
                                       font=("Arial", 18, "bold"), height=55, fg_color=COL_ACCENT, hover_color=COL_ACCENT_HOVER)
        self.btn_jouer.grid(row=8, column=0, padx=20, pady=(0, 15), sticky="ew")

        self.btn_quitter = ctk.CTkButton(self.sidebar_frame, text="QUITTER", command=self.quit,
                                         font=("Arial", 14, "bold"), height=40, fg_color="transparent", 
                                         border_width=2, border_color=COL_DANGER, text_color=COL_DANGER, hover_color="#451a1a")
        self.btn_quitter.grid(row=9, column=0, padx=20, pady=(0, 30), sticky="ew")

        # --- CONTENU (DROITE) ---
        self.main_frame = ctk.CTkFrame(self, fg_color=COL_BG, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=40, pady=40)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Dictionnaires des frames "pages"
        self.pages = {}
        
        self.build_page_accueil()
        self.build_page_base()
        self.build_page_env()
        self.build_page_realism()
        self.build_page_gfx()

        # Init par défaut
        self.select_tab("🏠  Vue d'ensemble")

    def create_sidebar_btn(self, texte, row_idx):
        btn = ctk.CTkButton(self.sidebar_frame, text=texte, corner_radius=8, height=45, border_spacing=10,
                            fg_color="transparent", text_color=COL_TEXT_MUTED, hover_color=COL_PANEL, anchor="w",
                            font=("Arial", 14), command=lambda t=texte: self.select_tab(t))
        btn.grid(row=row_idx, column=0, sticky="ew", padx=15, pady=5)
        self.tab_buttons.append((texte, btn))
        return btn

    def select_tab(self, nom_tab):
        # Update colors on sidebar
        for nom, btn in self.tab_buttons:
            if nom == nom_tab:
                btn.configure(fg_color=COL_PRIMARY, text_color=COL_TEXT)
            else:
                btn.configure(fg_color="transparent", text_color=COL_TEXT_MUTED)
                
        # Afficher la bonne page
        for t, page_frame in self.pages.items():
            if t == nom_tab:
                page_frame.grid(row=0, column=0, sticky="nsew")
            else:
                page_frame.grid_forget()

    # --- PAGES BUILDERS ---
    
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
        page = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.pages["🏠  Vue d'ensemble"] = page
        
        self.title_label(page, "Bienvenue Commandant.")
        
        infos = """
PyFlight 2D vous offre une simulation aéronautique exigeante :

• Physique de vol avancée (Décrochage, Inertie, Traînée)
• Poids Dynamique & Surchauffe Moteur Réalistes
• Cycle Jour/Nuit & Météo Volumétrique 
• Cockpit Interactif (HUD / Instruments Analogiques)

Configurez votre appareil via les onglets à gauche, 
puis cliquez sur LANCER LE VOL.
"""
        card = ctk.CTkFrame(page, fg_color="transparent")
        card.pack(fill="both", expand=True, pady=10)
        
        lbl_infos = ctk.CTkLabel(card, text=infos, font=("Consolas", 16), text_color=COL_TEXT_MUTED, justify="left")
        lbl_infos.pack(anchor="nw", pady=20)
        
        # Image de fond ou illustration (Optionnel)
        # ctk.CTkLabel(page, text="[Illustration / Astuces]", font=("Arial", 16), text_color=COL_PANEL).pack(expand=True)

    def build_page_base(self):
        page = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.pages["✈️  Appareil & Vol"] = page
        self.title_label(page, "Configuration de l'Appareil")

        # Avion
        c_avion = self.card_frame(page, "CHOIX DE L'APPAREIL")
        def set_aircraft(val):
            map_a = {"Cessna (Standard)": "cessna", "Chasseur (Rapide)": "fighter",  "Gros Porteur (Lourd)": "cargo", "Acrobatique (Voltige)": "acro"}
            self.var_aircraft.set(map_a.get(val, "cessna"))
            
        opt_avion = ctk.CTkOptionMenu(c_avion, values=["Cessna (Standard)", "Chasseur (Rapide)", "Gros Porteur (Lourd)", "Acrobatique (Voltige)"], 
                                      command=set_aircraft, width=300, height=40)
        opt_avion.pack(anchor="w", padx=15, pady=5)
        opt_avion.set("Cessna (Standard)")

        c_mode = self.card_frame(page, "MODE DE JEU")
        def set_gamemode(val):
            self.var_missions.set(val == "CARRIÈRE & MISSIONS")
        seg_mode = ctk.CTkSegmentedButton(c_mode, values=["VOL LIBRE", "CARRIÈRE & MISSIONS"], command=set_gamemode, height=35)
        seg_mode.pack(anchor="w", padx=15, fill="x")
        seg_mode.set("CARRIÈRE & MISSIONS" if self.var_missions.get() else "VOL LIBRE")

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
        page = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.pages["⛅  Environnement"] = page
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


    def build_page_realism(self):
        page = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.pages["⚙️  Réalisme & Aides"] = page
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
        page = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.pages["📺  Affichage & Rendu"] = page
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


    def lancer_jeu(self):
        self.destroy() 
        
        dossier = os.path.dirname(os.path.abspath(__file__))
        path_game = os.path.join(dossier, "game.py")
        cmd = [sys.executable, path_game]
        
        # Mapping base
        cmd.extend(["--difficulty", self.var_difficulte.get()])
        cmd.extend(["--volume", str(self.var_volume.get())])
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
        if self.var_missions.get(): cmd.append("--missions")
        if self.var_unlimited_fuel.get(): cmd.append("--unlimited-fuel")
        if self.var_god_mode.get(): cmd.append("--god-mode")
        if self.var_fullscreen.get(): cmd.append("--fullscreen")
        if self.var_show_fps.get(): cmd.append("--show-fps")
        cmd.extend(["--fuel", str(self.var_fuel_initial.get())])
        
        # Réalisme
        if self.var_no_stall.get(): cmd.append("--no-stall")
        if self.var_no_gear_crash.get(): cmd.append("--no-gear-crash")
        if self.var_no_overheat.get(): cmd.append("--no-overheat")
        if self.var_static_weight.get(): cmd.append("--static-weight")
        if self.var_no_wind.get(): cmd.append("--no-wind")
        if self.var_auto_refuel.get(): cmd.append("--auto-refuel")

        # Saison
        cmd.extend(["--season", self.var_season.get()])
        
        print(f"Lancement de : {cmd}")
        subprocess.run(cmd)

if __name__ == "__main__":
    app = MenuPrincipal()
    app.mainloop()
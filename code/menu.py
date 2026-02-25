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

# Palette "Aero"
COL_BG = "#0f172a"        # Bleu Nuit Profond
COL_PANEL = "#1e293b"     # Gris Bleu
COL_PRIMARY = "#3b82f6"   # Bleu Electrique
COL_HOVER = "#2563eb"     # Bleu plus sombre
COL_TEXT = "#f8fafc"      # Blanc
COL_ACCENT = "#ef4444"    # Rouge (Quitter)

class MenuPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Fenêtre
        self.title("Pyflight 2D - Launcher")
        self.geometry("1000x700")
        self.resizable(False, False)
        self.configure(fg_color=COL_BG)

        # Variables Paramètres
        self.var_difficulte = ctk.StringVar(value="easy")
        self.var_temps = ctk.StringVar(value="real")
        self.var_heure_manuelle = ctk.DoubleVar(value=12.0)
        self.var_season = ctk.StringVar(value="summer") # sun/summer default
        self.var_weather = ctk.StringVar(value="clear") # clear/clouds/fog
        self.var_volume = ctk.DoubleVar(value=0.5)

        # Variables Graphiques
        self.var_show_hud = ctk.BooleanVar(value=True)
        self.var_show_w_dashboard = ctk.BooleanVar(value=True) # Analog
        self.var_show_clouds = ctk.BooleanVar(value=True)
        self.var_show_particles = ctk.BooleanVar(value=True)
        self.var_show_atmo = ctk.BooleanVar(value=True)
        self.var_show_terrain = ctk.BooleanVar(value=True)

        # Variables Gameplay (Cheat / Fun)
        self.var_unlimited_fuel = ctk.BooleanVar(value=False)
        self.var_god_mode = ctk.BooleanVar(value=False)
        self.var_aircraft = ctk.StringVar(value="cessna") # Default Aircraft
        self.var_fuel_initial = ctk.DoubleVar(value=100.0)

        # Variables Système
        self.var_fullscreen = ctk.BooleanVar(value=False)
        self.var_show_fps = ctk.BooleanVar(value=False)
        
        # Nouvelles Variables Réalisme
        self.var_no_stall = ctk.BooleanVar(value=False)
        self.var_no_gear_crash = ctk.BooleanVar(value=False)
        self.var_no_wind = ctk.BooleanVar(value=False)
        self.var_auto_refuel = ctk.BooleanVar(value=False)
        self.var_no_overheat = ctk.BooleanVar(value=False)
        self.var_static_weight = ctk.BooleanVar(value=False)
        
        # Variable Relief (Intensité)
        self.var_terrain_intensity = ctk.DoubleVar(value=1.0)
        
        # Variable Traînée Acrobatique
        self.var_show_trail = ctk.BooleanVar(value=False)
        self.var_trail_color = ctk.StringVar(value="white")

        # Layout Principal (2 Colonnes)
        self.grid_columnconfigure(0, weight=1) # Gauche (Visuel/Titre)
        self.grid_columnconfigure(1, weight=0) # Droite (Menu)
        self.grid_rowconfigure(0, weight=1)

        # --- GAUCHE : VISUEL ---
        self.frame_visuel = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_visuel.grid(row=0, column=0, sticky="nswe", padx=40, pady=40)
        
        # Titre (Grand)
        self.lbl_titre = ctk.CTkLabel(self.frame_visuel, text="Pyflight 2D", 
                                      font=("Impact", 80), text_color=COL_TEXT, justify="left")
        self.lbl_titre.pack(anchor="w", pady=(50, 0))
        
        self.lbl_subtitle = ctk.CTkLabel(self.frame_visuel, text="ULTIMATE EDITION", 
                                         font=("Arial", 20, "bold"), text_color=COL_PRIMARY, justify="left")
        self.lbl_subtitle.pack(anchor="w", pady=(0, 20))

        # Infos Rapides
        infos = "• Physique de vol avancée\n• Cycle Jour/Nuit Dynamique\n• Météo Temps Réel\n• Cockpit Interactif\n• Consultez idees amelioration.txt (50 idées)"
        self.lbl_infos = ctk.CTkLabel(self.frame_visuel, text=infos,
                                      font=("Consolas", 16), text_color="gray", justify="left")
        self.lbl_infos.pack(anchor="w", pady=40)

        # --- DROITE : MENU ---
        self.frame_menu = ctk.CTkFrame(self, width=350, fg_color=COL_PANEL, corner_radius=0)
        self.frame_menu.grid(row=0, column=1, sticky="nswe")
        
        # Initialisation du menu
        self.creer_menu_principal()

    def creer_menu_principal(self):
        # Nettoyage
        for widget in self.frame_menu.winfo_children():
            widget.destroy()

        # En-tête Menu
        ctk.CTkLabel(self.frame_menu, text="MENU PRINCIPAL", font=("Arial", 20, "bold"), text_color="gray").pack(pady=(50, 30))

        # Boutons
        self.btn_jouer = ctk.CTkButton(self.frame_menu, text="VOL LIBRE", command=self.lancer_jeu, 
                                       font=("Arial", 16, "bold"), height=50, width=280,
                                       fg_color=COL_PRIMARY, hover_color=COL_HOVER)
        self.btn_jouer.pack(pady=15)

        self.btn_params = ctk.CTkButton(self.frame_menu, text="PARAMÈTRES DE VOL", command=self.afficher_parametres,
                                       font=("Arial", 16, "bold"), height=50, width=280,
                                       fg_color=COL_PANEL, border_width=2, border_color="gray", hover_color="#334155")
        self.btn_params.pack(pady=15)

        self.btn_quitter = ctk.CTkButton(self.frame_menu, text="QUITTER", command=self.quit,
                                        font=("Arial", 16, "bold"), height=50, width=280,
                                        fg_color="transparent", border_width=2, border_color=COL_ACCENT, 
                                        text_color=COL_ACCENT, hover_color="#334155")
        self.btn_quitter.pack(pady=30, side="bottom")

    def afficher_parametres(self):
        # Nettoyage
        for widget in self.frame_menu.winfo_children():
            widget.destroy()
            
        # En-tête Fixe
        ctk.CTkLabel(self.frame_menu, text="CONFIGURATION", font=("Arial", 20, "bold"), text_color="gray").pack(pady=(30, 10))

        # Zone Défilante pour les options
        scroll_frame = ctk.CTkScrollableFrame(self.frame_menu, fg_color="transparent", width=320)
        scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # 1. DIFFICULTÉ
        f_diff = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        f_diff.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(f_diff, text="MODE DE PILOTAGE", font=("Arial", 12, "bold"), text_color="gray").pack(anchor="w")
        
        def set_diff(val):
            self.var_difficulte.set("easy" if "FACILE" in val else "real")

        seg_diff = ctk.CTkSegmentedButton(f_diff, values=["FACILE (Assisté)", "RÉALISTE"], command=set_diff)
        seg_diff.pack(fill="x", pady=5)
        seg_diff.set("FACILE (Assisté)" if self.var_difficulte.get()=="easy" else "RÉALISTE")
        
        # 2. TEMPS / HEURE
        f_time = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        f_time.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(f_time, text="HEURE DU VOL", font=("Arial", 12, "bold"), text_color="gray").pack(anchor="w")

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

        seg_time = ctk.CTkSegmentedButton(f_time, values=["MANUEL", "RÉEL (FR)", "DYNAMIQUE"], command=set_time_mode)
        seg_time.pack(fill="x", pady=5)
        
        initial_time_mode = "MANUEL"
        if self.var_temps.get() == "real": initial_time_mode = "RÉEL (FR)"
        elif self.var_temps.get() == "dynamic": initial_time_mode = "DYNAMIQUE"
        seg_time.set(initial_time_mode)

        # Slider Heure
        self.lbl_heure_val = ctk.CTkLabel(f_time, text=f"{int(self.var_heure_manuelle.get())}H")
        self.lbl_heure_val.pack(anchor="e")
        
        def update_lbl(val):
            self.lbl_heure_val.configure(text=f"{int(val)}H")

        self.slider_heure = ctk.CTkSlider(f_time, from_=0, to=23, number_of_steps=24, variable=self.var_heure_manuelle, command=update_lbl)
        self.slider_heure.pack(fill="x", pady=5)
        if self.var_temps.get() == "real":
            self.slider_heure.configure(state="disabled")

        # 3. MOYEN DE TRANSPORT (AVION)
        f_avion = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        f_avion.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(f_avion, text="TYPE D'AVION", font=("Arial", 12, "bold"), text_color="gray").pack(anchor="w")

        def set_aircraft(val):
            map_a = {
                "Cessna (Standard)": "cessna",
                "Chasseur (Rapide)": "fighter", 
                "Gros Porteur (Lourd)": "cargo",
                "Acrobatique (Voltige)": "acro"
            }
            self.var_aircraft.set(map_a.get(val, "cessna"))

        seg_avion = ctk.CTkOptionMenu(f_avion, values=["Cessna (Standard)", "Chasseur (Rapide)", "Gros Porteur (Lourd)", "Acrobatique (Voltige)"], command=set_aircraft)
        seg_avion.pack(fill="x", pady=5)
        seg_avion.set("Cessna (Standard)")


        # 4. MÉTÉO / SAISONS
        f_season = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        f_season.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(f_season, text="MÉTÉO & SAISON", font=("Arial", 12, "bold"), text_color="gray").pack(anchor="w")

        def set_season(val):
            # Mapping nom -> value
            map_s = {
                "PRINTEMPS (Fleurs)": "spring",
                "ÉTÉ (Vert)": "summer", 
                "AUTOMNE (Feuilles)": "autumn", 
                "HIVER (Neige)": "snow", 
                "TEMPÊTE (Vent)": "wind"
            }
            self.var_season.set(map_s.get(val, "summer"))

        # Inverse mapping for display
        val_display = "ÉTÉ (Vert)"
        if self.var_season.get() == "spring": val_display = "PRINTEMPS (Fleurs)"
        elif self.var_season.get() == "autumn": val_display = "AUTOMNE (Feuilles)"
        elif self.var_season.get() == "rain": val_display = "AUTOMNE (Feuilles)" # Legacy
        elif self.var_season.get() == "snow": val_display = "HIVER (Neige)"
        elif self.var_season.get() == "wind": val_display = "TEMPÊTE (Vent)"

        seg_season = ctk.CTkOptionMenu(f_season, values=["PRINTEMPS (Fleurs)", "ÉTÉ (Vert)", "AUTOMNE (Feuilles)", "HIVER (Neige)", "TEMPÊTE (Vent)"], command=set_season)
        seg_season.pack(fill="x", pady=5)
        seg_season.set(val_display)

        # 4.5 MÉTÉO (FOG / CLOUDS)
        f_weather = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        f_weather.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(f_weather, text="CONDITIONS MÉTÉO", font=("Arial", 12, "bold"), text_color="gray").pack(anchor="w")

        def set_weather_opt(val):
            map_w = {"CIEL CLAIR": "clear", "NUAGES VOLUMETRIQUES": "clouds", "BROUILLARD ÉPAIS": "fog"}
            self.var_weather.set(map_w.get(val, "clear"))

        seg_weather = ctk.CTkOptionMenu(f_weather, values=["CIEL CLAIR", "NUAGES VOLUMETRIQUES", "BROUILLARD ÉPAIS"], command=set_weather_opt)
        seg_weather.pack(fill="x", pady=5)
        
        w_display = "CIEL CLAIR"
        if self.var_weather.get() == "clouds": w_display = "NUAGES VOLUMETRIQUES"
        elif self.var_weather.get() == "fog": w_display = "BROUILLARD ÉPAIS"
        seg_weather.set(w_display)


        # 4. VOLUME
        f_vol = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        f_vol.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(f_vol, text="VOLUME MOTEUR", font=("Arial", 12, "bold"), text_color="gray").pack(anchor="w")
        ctk.CTkSlider(f_vol, from_=0.0, to=1.0, variable=self.var_volume).pack(fill="x", pady=5)

        # 5. GAMEPLAY & RÉALISME
        f_game = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        f_game.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(f_game, text="RÉALISME & AIDES (Triche)", font=("Arial", 12, "bold"), text_color="gray").pack(anchor="w")
        
        ctk.CTkCheckBox(f_game, text="Carburant Illimité", variable=self.var_unlimited_fuel).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(f_game, text="Invincibilité (God Mode)", variable=self.var_god_mode).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(f_game, text="Désactiver le Décrochage (Anti-Stall)", variable=self.var_no_stall).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(f_game, text="Atterrissage ventre sécurisé (No Gear Crash)", variable=self.var_no_gear_crash).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(f_game, text="Désactiver la Surchauffe Moteur", variable=self.var_no_overheat).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(f_game, text="Poids Statique (Ignorer le Fuel)", variable=self.var_static_weight).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(f_game, text="Pas de Vent ni Turbulences", variable=self.var_no_wind).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(f_game, text="Ravitaillement Automatique (Sur piste)", variable=self.var_auto_refuel).pack(anchor="w", pady=2)

        # Slider Carburant Initial
        self.lbl_fuel = ctk.CTkLabel(f_game, text=f"Carburant Initial: {int(self.var_fuel_initial.get())}%", text_color="gray")
        self.lbl_fuel.pack(anchor="w", pady=(10, 0))
        def update_fuel_lbl(val):
            self.lbl_fuel.configure(text=f"Carburant Initial: {int(val)}%")
        ctk.CTkSlider(f_game, from_=10.0, to=100.0, variable=self.var_fuel_initial, command=update_fuel_lbl).pack(fill="x", pady=5)

        # 6. SYSTÈME
        f_sys = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        f_sys.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(f_sys, text="SYSTÈME", font=("Arial", 12, "bold"), text_color="gray").pack(anchor="w")
        ctk.CTkSwitch(f_sys, text="Plein Écran", variable=self.var_fullscreen).pack(anchor="w", pady=2)
        ctk.CTkSwitch(f_sys, text="Afficher FPS", variable=self.var_show_fps).pack(anchor="w", pady=2)

        # 7. GRAPHIQUES
        f_gfx = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        f_gfx.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(f_gfx, text="AFFICHAGE & DETAILS", font=("Arial", 12, "bold"), text_color="gray").pack(anchor="w")
        
        ctk.CTkCheckBox(f_gfx, text="HUD (Haut)", variable=self.var_show_hud).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(f_gfx, text="Tableau Bord (Bas)", variable=self.var_show_w_dashboard).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(f_gfx, text="Nuages", variable=self.var_show_clouds).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(f_gfx, text="Particules Vitesse", variable=self.var_show_particles).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(f_gfx, text="Atmosphere", variable=self.var_show_atmo).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(f_gfx, text="Details Terrain", variable=self.var_show_terrain).pack(anchor="w", pady=2)
        
        f_trail = ctk.CTkFrame(f_gfx, fg_color="transparent")
        f_trail.pack(fill="x", pady=2)
        ctk.CTkCheckBox(f_trail, text="Fumée Acrobatique", variable=self.var_show_trail).pack(side="left")
        ctk.CTkOptionMenu(f_trail, values=["white", "red", "blue", "green", "yellow"], variable=self.var_trail_color, width=100).pack(side="right")
        
        # Slider Intensité du Relief
        self.lbl_terrain = ctk.CTkLabel(f_gfx, text=f"Intensité du Relief: {self.var_terrain_intensity.get():.1f}x", text_color="gray")
        self.lbl_terrain.pack(anchor="w", pady=(10, 0))
        def update_terrain_lbl(val):
            self.lbl_terrain.configure(text=f"Intensité du Relief: {val:.1f}x")
        ctk.CTkSlider(f_gfx, from_=0.0, to=5.0, number_of_steps=50, variable=self.var_terrain_intensity, command=update_terrain_lbl).pack(fill="x", pady=5)

        # BOUTON RETOUR (HORS du ScrollFrame pour rester visible)
        ctk.CTkButton(self.frame_menu, text="RETOUR", command=self.creer_menu_principal,
                      font=("Arial", 14, "bold"), height=40, width=280,
                      fg_color="transparent", border_width=1, border_color="gray", hover_color="#334155").pack(side="bottom", pady=20)


    def lancer_jeu(self):
        self.destroy() 
        
        # Chemin absolu de game.py
        dossier = os.path.dirname(os.path.abspath(__file__))
        path_game = os.path.join(dossier, "game.py")
        
        # Construction commande
        cmd = [sys.executable, path_game]
        
        # Args
        cmd.extend(["--difficulty", self.var_difficulte.get()])
        cmd.extend(["--volume", str(self.var_volume.get())])
        cmd.extend(["--aircraft", self.var_aircraft.get()])
        
        if self.var_temps.get() == "real":
            cmd.extend(["--time", "real"])
        elif self.var_temps.get() == "dynamic":
            cmd.extend(["--time", "dynamic"])
        else:
            cmd.extend(["--time", str(self.var_heure_manuelle.get())])
            
        cmd.extend(["--weather", self.var_weather.get()])
            
        # Args Graphiques
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
        
        # Args Gameplay / Systeme
        if self.var_unlimited_fuel.get(): cmd.append("--unlimited-fuel")
        if self.var_god_mode.get(): cmd.append("--god-mode")
        if self.var_fullscreen.get(): cmd.append("--fullscreen")
        if self.var_show_fps.get(): cmd.append("--show-fps")
        cmd.extend(["--fuel", str(self.var_fuel_initial.get())])
        
        # Args Réalisme
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
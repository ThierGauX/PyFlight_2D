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

        # Variables Système
        self.var_fullscreen = ctk.BooleanVar(value=False)
        self.var_show_fps = ctk.BooleanVar(value=False)

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
        infos = "• Physique de vol avancée\n• Cycle Jour/Nuit Dynamique\n• Météo Temps Réel\n• Cockpit Interactif"
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

        def toggle_time():
            if self.var_temps.get() == "real":
                self.slider_heure.configure(state="disabled")
            else:
                self.slider_heure.configure(state="normal")

        switch_real = ctk.CTkSwitch(f_time, text="Temps Réel (France)", command=toggle_time,
                                    onvalue="real", offvalue="manual", variable=self.var_temps)
        switch_real.pack(anchor="w", pady=5)

        # Slider Heure
        self.lbl_heure_val = ctk.CTkLabel(f_time, text=f"{int(self.var_heure_manuelle.get())}H")
        self.lbl_heure_val.pack(anchor="e")
        
        def update_lbl(val):
            self.lbl_heure_val.configure(text=f"{int(val)}H")

        self.slider_heure = ctk.CTkSlider(f_time, from_=0, to=24, number_of_steps=24, command=update_lbl,
                                          variable=self.var_heure_manuelle)
        self.slider_heure.pack(fill="x", pady=5)
        if self.var_temps.get() == "real":
            self.slider_heure.configure(state="disabled")

        # 3. VOLUME
        f_vol = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        f_vol.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(f_vol, text="VOLUME MOTEUR", font=("Arial", 12, "bold"), text_color="gray").pack(anchor="w")
        ctk.CTkSlider(f_vol, from_=0.0, to=1.0, variable=self.var_volume).pack(fill="x", pady=5)

        # 4. GAMEPLAY (Nouveau)
        f_game = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        f_game.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(f_game, text="GAMEPLAY & CHEATS", font=("Arial", 12, "bold"), text_color="gray").pack(anchor="w")
        ctk.CTkCheckBox(f_game, text="Carburant Illimité", variable=self.var_unlimited_fuel).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(f_game, text="Invincibilité (God Mode)", variable=self.var_god_mode).pack(anchor="w", pady=2)

        # 5. SYSTÈME (Nouveau)
        f_sys = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        f_sys.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(f_sys, text="SYSTÈME", font=("Arial", 12, "bold"), text_color="gray").pack(anchor="w")
        ctk.CTkSwitch(f_sys, text="Plein Écran", variable=self.var_fullscreen).pack(anchor="w", pady=2)
        ctk.CTkSwitch(f_sys, text="Afficher FPS", variable=self.var_show_fps).pack(anchor="w", pady=2)

        # 6. GRAPHIQUES (Toggle)
        f_gfx = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        f_gfx.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(f_gfx, text="AFFICHAGE", font=("Arial", 12, "bold"), text_color="gray").pack(anchor="w")
        
        ctk.CTkCheckBox(f_gfx, text="HUD (Haut)", variable=self.var_show_hud).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(f_gfx, text="Tableau Bord (Bas)", variable=self.var_show_w_dashboard).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(f_gfx, text="Nuages", variable=self.var_show_clouds).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(f_gfx, text="Particules Vitesse", variable=self.var_show_particles).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(f_gfx, text="Atmosphere", variable=self.var_show_atmo).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(f_gfx, text="Details Terrain", variable=self.var_show_terrain).pack(anchor="w", pady=2)

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
        
        if self.var_temps.get() == "real":
            cmd.extend(["--time", "real"])
        else:
            cmd.extend(["--time", str(self.var_heure_manuelle.get())])
            
        # Args Graphiques
        if not self.var_show_hud.get(): cmd.append("--no-hud")
        if not self.var_show_w_dashboard.get(): cmd.append("--no-dash")
        if not self.var_show_clouds.get(): cmd.append("--no-clouds")
        if not self.var_show_particles.get(): cmd.append("--no-particles")
        if self.var_show_atmo.get() is False: cmd.append("--no-atmo")
        if self.var_show_terrain.get() is False: cmd.append("--no-terrain")
        
        # Args Gameplay / Systeme
        if self.var_unlimited_fuel.get(): cmd.append("--unlimited-fuel")
        if self.var_god_mode.get(): cmd.append("--god-mode")
        if self.var_fullscreen.get(): cmd.append("--fullscreen")
        if self.var_show_fps.get(): cmd.append("--show-fps")
            
        print(f"Lancement de : {cmd}")
        subprocess.run(cmd)

if __name__ == "__main__":
    app = MenuPrincipal()
    app.mainloop()

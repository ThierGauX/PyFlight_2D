import customtkinter as ctk
import sys
import os
import subprocess
from PIL import Image

# --- CONFIGURATION DU DESIGN ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# Palette de couleurs "PyFlight"
COL_FOND = "#1a1a2e"       # Bleu nuit très sombre
COL_SIDEBAR = "#16213e"    # Bleu marine
COL_BOUTON = "#0f3460"     # Bleu royal
COL_ACCENT = "#e94560"     # Rouge/Rose (pour Quitter)
COL_VERTE = "#228B22"      # Vert (pour Jouer)
COL_TEXTE = "#eaeaea"      # Blanc cassé

class MenuPyFlight(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuration Fenêtre
        self.title("Launcher - PyFlight")
        self.geometry("900x600")
        self.resizable(False, False)
        
        # Configuration Grille (1 ligne, 2 colonnes)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- GAUCHE : SIDEBAR (TITRE & INFO) ---
        self.frame_left = ctk.CTkFrame(self, width=300, corner_radius=0, fg_color=COL_SIDEBAR)
        self.frame_left.grid(row=0, column=0, sticky="nswe")
        
        # Logo / Titre (Modifié : Plus de 2D)
        self.lbl_titre = ctk.CTkLabel(self.frame_left, text="PyFlight", 
                                      font=ctk.CTkFont(family="Impact", size=64),
                                      text_color=COL_TEXTE)
        self.lbl_titre.place(relx=0.5, rely=0.2, anchor="center")

        self.lbl_sous_titre = ctk.CTkLabel(self.frame_left, text="SIMULATEUR DE VOL", 
                                           font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
                                           text_color="#536878")
        self.lbl_sous_titre.place(relx=0.5, rely=0.32, anchor="center")

        # Ligne de décoration
        self.ligne = ctk.CTkFrame(self.frame_left, height=2, width=150, fg_color=COL_ACCENT)
        self.ligne.place(relx=0.5, rely=0.36, anchor="center")

        # Statut du système (Décoration)
        self.lbl_status = ctk.CTkLabel(self.frame_left, text="SYSTEME: ONLINE\nMOTEUR: PRET\nMETEO: CLAIR",
                                       font=ctk.CTkFont(family="Consolas", size=12),
                                       text_color="gray", justify="left")
        self.lbl_status.place(relx=0.5, rely=0.85, anchor="center")

        # --- DROITE : BOUTONS D'ACTION ---
        self.frame_right = ctk.CTkFrame(self, corner_radius=0, fg_color=COL_FOND)
        self.frame_right.grid(row=0, column=1, sticky="nswe")
        
        # Centrage vertical des boutons
        self.frame_buttons = ctk.CTkFrame(self.frame_right, fg_color="transparent")
        self.frame_buttons.place(relx=0.5, rely=0.5, anchor="center")

        # 1. BOUTON JOUER (Gros et Vert)
        self.btn_play = ctk.CTkButton(self.frame_buttons, text="DÉCOLLER", 
                                      font=ctk.CTkFont(size=24, weight="bold"),
                                      height=70, width=350,
                                      corner_radius=35, # Bords très ronds
                                      fg_color=COL_VERTE, hover_color="#2ecc71",
                                      command=self.lancer_jeu)
        self.btn_play.pack(pady=20)

        # 2. BOUTON INFOS (Classique)
        self.btn_info = ctk.CTkButton(self.frame_buttons, text="MANUEL DE PILOTAGE", 
                                      font=ctk.CTkFont(size=18),
                                      height=50, width=350,
                                      corner_radius=25,
                                      fg_color=COL_BOUTON, hover_color="#16213e",
                                      command=self.ouvrir_info)
        self.btn_info.pack(pady=10)

        # 3. BOUTON QUITTER (Rouge discret)
        self.btn_quit = ctk.CTkButton(self.frame_buttons, text="QUITTER", 
                                      font=ctk.CTkFont(size=18),
                                      height=50, width=350,
                                      corner_radius=25,
                                      fg_color="transparent", border_width=2, border_color=COL_ACCENT,
                                      text_color=COL_ACCENT, hover_color=COL_ACCENT,
                                      command=self.quitter)
        self.btn_quit.pack(pady=30)

    # --- FONCTIONS ---

    def lancer_jeu(self):
        self.destroy() # Ferme le menu
        # Cherche game.py dans le même dossier
        dossier_courant = os.path.dirname(os.path.abspath(__file__))
        chemin_jeu = os.path.join(dossier_courant, "game.py")
        
        try:
            subprocess.run([sys.executable, chemin_jeu])
        except Exception as e:
            print(f"Erreur : Impossible de lancer game.py. {e}")
        sys.exit()

    def ouvrir_info(self):
        # Création d'une fenêtre Pop-up stylée
        info = ctk.CTkToplevel(self)
        info.title("Manuel de Vol")
        info.geometry("450x450")
        info.resizable(False, False)
        info.attributes("-topmost", True)
        info.configure(fg_color=COL_FOND)

        ctk.CTkLabel(info, text="COMMANDES DE VOL", font=("Impact", 25), text_color=COL_TEXTE).pack(pady=20)

        # Liste des commandes
        commandes = [
            ("FLÈCHES HAUT/BAS", "Contrôle du manche (Tangage)"),
            ("FLÈCHES GAUCHE/DROITE", "Contrôle des gaz (Puissance)"),
            ("TOUCHE [ A ]", "Démarrer / Couper Moteur"),
            ("TOUCHE [ F ]", "Sortir / Rentrer Volets"),
            ("TOUCHE [ ECHAP ]", "Quitter la simulation")
        ]

        for touche, desc in commandes:
            f = ctk.CTkFrame(info, fg_color="transparent")
            f.pack(fill="x", padx=30, pady=8)
            ctk.CTkLabel(f, text=touche, font=("Arial", 12, "bold"), text_color="#4CC9F0", width=180, anchor="w").pack(side="left")
            ctk.CTkLabel(f, text=desc, font=("Arial", 12), text_color="white", anchor="w").pack(side="left")

        ctk.CTkButton(info, text="COMPRIS", fg_color=COL_BOUTON, command=info.destroy).pack(pady=30)

    def quitter(self):
        self.destroy()
        sys.exit()

if __name__ == "__main__":
    app = MenuPyFlight()
    app.mainloop()
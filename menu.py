import pygame
import sys
import os
import random
import subprocess 

# --- INITIALISATION ---
pygame.init()
L, H = 1200, 700
fenetre = pygame.display.set_mode((L, H))
pygame.display.set_caption("AERO ACE - Launcher")

# --- COULEURS ---
BLEU_NUIT = (10, 20, 40)
BLEU_CIEL = (100, 180, 220)
BLANC = (255, 255, 255)
ORANGE = (255, 140, 0)
GRIS_BOUTON = (40, 50, 60)
GRIS_HOVER = (60, 70, 80)

# --- POLICES ---
try:
    font_titre = pygame.font.SysFont("impact", 100)
    font_sous_titre = pygame.font.SysFont("arial", 30, bold=True)
    font_bouton = pygame.font.SysFont("arial", 40, bold=True)
except:
    font_titre = pygame.font.SysFont(None, 100)
    font_sous_titre = pygame.font.SysFont(None, 30)
    font_bouton = pygame.font.SysFont(None, 40)

# --- EFFET DE FOND ---
nuages = []
for _ in range(20):
    nuages.append([random.randint(0, L), random.randint(0, H), random.uniform(0.5, 2.0), random.randint(50, 150)])

def dessiner_fond_anime():
    # Dégradé de ciel
    for y in range(H):
        r = int(BLEU_NUIT[0] * (1 - y/H) + BLEU_CIEL[0] * (y/H))
        g = int(BLEU_NUIT[1] * (1 - y/H) + BLEU_CIEL[1] * (y/H))
        b = int(BLEU_NUIT[2] * (1 - y/H) + BLEU_CIEL[2] * (y/H))
        pygame.draw.line(fenetre, (r, g, b), (0, y), (L, y))

    # Nuages
    for n in nuages:
        n[0] -= n[2]
        if n[0] < -150:
            n[0] = L + 50
            n[1] = random.randint(0, H)
        
        alpha_s = pygame.Surface((n[3]*2, n[3]), pygame.SRCALPHA)
        pygame.draw.ellipse(alpha_s, (255, 255, 255, 50), (0, 0, n[3]*2, n[3]))
        fenetre.blit(alpha_s, (n[0], n[1]))

# --- CLASSE BOUTON ---
class Bouton:
    def __init__(self, text, x, y, w, h, action_cmd=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action_cmd = action_cmd
        self.is_hovered = False

    def draw(self, surface):
        pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(pos)

        color = GRIS_HOVER if self.is_hovered else GRIS_BOUTON
        border_col = ORANGE if self.is_hovered else BLANC

        pygame.draw.rect(surface, (0, 0, 0, 100), (self.rect.x + 5, self.rect.y + 5, self.rect.w, self.rect.h), border_radius=15)
        pygame.draw.rect(surface, color, self.rect, border_radius=15)
        pygame.draw.rect(surface, border_col, self.rect, 3, border_radius=15)

        txt_surf = font_bouton.render(self.text, True, BLANC)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def check_click(self):
        if self.is_hovered:
            return True
        return False

# --- CONFIGURATION ---
bouton_jouer = Bouton("DÉCOLLER", L//2 - 125, 300, 250, 80, "game.py")
bouton_quitter = Bouton("QUITTER", L//2 - 125, 420, 250, 80)

clock = pygame.time.Clock()

# --- BOUCLE PRINCIPALE ---
running = True
while running:
    dt = clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if bouton_jouer.check_click():
                    print("Lancement du simulateur...")
                    pygame.quit()
                    
                    # --- CORRECTION DU CHEMIN ---
                    # On cherche game.py exactement dans le même dossier que ce fichier menu.py
                    dossier_courant = os.path.dirname(os.path.abspath(__file__))
                    chemin_jeu = os.path.join(dossier_courant, "game.py")
                    
                    try:
                        subprocess.run([sys.executable, chemin_jeu]) 
                    except Exception as e:
                        print(f"Erreur lors du lancement : {e}")
                    sys.exit() 

                if bouton_quitter.check_click():
                    running = False

    dessiner_fond_anime() 

    titre = font_titre.render("AERO ACE", True, BLANC)
    ombre = font_titre.render("AERO ACE", True, (0,0,0))
    fenetre.blit(ombre, (L//2 - titre.get_width()//2 + 5, 85))
    fenetre.blit(titre, (L//2 - titre.get_width()//2, 80))

    sous_titre = font_sous_titre.render("ULTIMATE FLIGHT SIMULATOR", True, ORANGE)
    fenetre.blit(sous_titre, (L//2 - sous_titre.get_width()//2, 180))

    bouton_jouer.draw(fenetre)
    bouton_quitter.draw(fenetre)

    pygame.display.flip()

pygame.quit()
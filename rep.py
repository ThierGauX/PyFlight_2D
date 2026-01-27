import wave
import random
import os

# Ce script va fabriquer un fichier son valide (bruit blanc type réacteur)
nom_fichier = "moteur_neuf.wav"
dossier = os.path.dirname(os.path.abspath(__file__))
chemin_complet = os.path.join(dossier, nom_fichier)

print(f"Création du fichier son dans : {chemin_complet}")

# Paramètres du son (Qualité CD)
framerate = 44100
duree_secondes = 2 # Son court lu en boucle

# Génération de bruit blanc (SSSSSHHHHHH)
bruit = bytearray()
for i in range(int(framerate * duree_secondes)):
    # On génère des octets aléatoires pour faire du bruit
    byte = random.randint(0, 255)
    bruit.append(byte)

try:
    with wave.open(chemin_complet, 'wb') as f:
        f.setnchannels(1)      # Mono
        f.setsampwidth(1)      # 8 bits (son rétro compatible)
        f.setframerate(framerate)
        f.writeframes(bruit)
    print("✅ SUCCÈS : Fichier 'moteur_neuf.wav' créé avec succès !")
    print("Maintenant, lancez main.py")
except Exception as e:
    print(f"❌ ERREUR : Impossible de créer le fichier : {e}")
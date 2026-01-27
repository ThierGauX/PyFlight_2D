# PyFlight 2D - Simulateur de Vol 

Bienvenue dans **PyFlight 2D**, un simulateur de vol développé en Python avec la bibliothèque Pygame et CustomTkinter pour l'interface.

* **Gauthier :** Architecture logicielle, Physique de vol & Développement du Launcher (Menu).
* **Jules :** Direction Artistique, Design de l'avion & Assets graphiques.

##  Fonctionnalités Nouvelles & Principales

###  Physique & Pilotage
* **Inertie Réaliste :** Les commandes sont "lourdes". L'avion ne tourne pas instantanément, simulant la masse d'un véritable appareil.
* **Système SAS (Stabilisateur) :** Un co-pilote virtuel stabilise automatiquement l'appareil à l'horizon lorsque vous lâchez le manche.
* **Gestion Moteur & Volets :** Démarrage/Arrêt manuel de la turbine et déploiement mécanique des volets (Flaps) pour la portance.
* **Modèle de Vol "Chasseur" :**
    * Vitesse de décollage : **~200 km/h**
    * Vitesse maximale (VNE) : **2500 km/h** (Mach 2.0+)
    * Décrochage (Stall) avec alarme sonore.

###  Immersion Visuelle & Interface
* **Launcher Moderne :** Menu de démarrage "Flat Design" avec accès aux réglages et informations.
* **Caméra Dynamique (ZOOM) :** Possibilité de zoomer/dézoomer fluide avec la souris.
* **HUD Militaire :** Affichage tête haute du Mach, des G-Force, de l'Altitude et de la Poussée (Thrust).
* **Environnement :** Ciel dynamique changeant de couleur avec l'altitude et effets de particules.

##  Commandes de Vol

Le simulateur se joue au Clavier et à la Souris.

| Touche / Action | Fonction | Effet Physique |
| :--- | :--- | :--- |
| **Flèche HAUT** | **Piquer** | Le nez descend pour prendre de la vitesse ou descendre. |
| **Flèche BAS** | **Cabrer** | Le nez monte. Attention à la perte de vitesse ! |
| **Flèche DROITE** | **Augmenter Gaz** | Augmente la puissance moteur par paliers. |
| **Flèche GAUCHE** | **Réduire Gaz** | Diminue la puissance moteur. |
| **Touche [ A ]** | **Moteur** | Démarrer ou Couper la turbine (Start/Stop). |
| **Touche [ F ]** | **Volets (Flaps)** | Sortir (Décollage/Atterro) ou Rentrer (Croisière). |
| **Touche [ ECHAP ]** | **Menu** | Quitter la simulation et revenir au lanceur. |
| *(Aucune touche)* | **Auto-Pilot** | Activation automatique du mode **STABLE** (Maintien d'altitude à plat). |

##  Guide Rapide

1.  **Mise en route :** Appuyez sur **[ A ]** pour allumer le moteur.
2.  **Configuration :** Appuyez sur **[ F ]** pour sortir les volets (indispensable au sol).
3.  **Décollage :** Maintenez **Flèche DROITE** (100%). À **200 km/h**, appuyez doucement sur **BAS**.
4.  **En vol :** Rentrez les volets (**[ F ]**) et relâchez le manche pour laisser le stabilisateur équilibrer l'avion.
5.  **Atterrissage :** Réduisez les gaz, sortez les volets et levez le nez pour toucher le sol doucement.

##  Installation

### Prérequis
* Python 3.10 ou supérieur installé.
* Bibliothèques `pygame`, `customtkinter` et `pillow`.

### Installation
1.  Assurez-vous d'avoir les fichiers suivants dans le même dossier :
    * `menu.py` (Lanceur)
    * `game.py` (Moteur de jeu)
    * `avion_marche.png` / `avion_arret.png`
    * `moteur.wav` / `alarme_decrochage.wav` (Optionnels)

2.  Installez les dépendances via le terminal :
    ```bash
    pip install pygame customtkinter pillow
    ```

### Lancement
Exécutez le script du menu pour démarrer :
```bash
python menu.py

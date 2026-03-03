# PyFlight 2D

Bienvenue dans **PyFlight 2D**, un simulateur de vol 2D ultra-complet développé en Python. Alliant physique aérodynamique avancée, rendu haute résolution et systèmes météo dynamiques, il offre une expérience de pilotage immersive et entièrement personnalisable via son Launcher Premium.

---

## Les Appareils (Aircrafts)

Chaque avion possède son propre modèle physique (masse, poussée, traînée, inertie) :

*   **Cessna 172 (Standard)** : L'équilibre parfait. Idéal pour l'apprentissage et la navigation.
*   **Chasseur Mirage (Armé)** : Vitesse extrême (VNE 1500 km/h). Équipé d'un système d'armement (Bombes & Missiles).
*   **Gros Porteur (Lourd)** : Une masse imposante de 20 tonnes. Lent à la réaction, il demande une grande anticipation pour les atterrissages et les missions de fret.
*   **Acrobatique (Acro)** : Conçu pour les loopings à 360° et les figures extrêmes. Rotation ultra-rapide et fumées colorées.

---

## Modes de Jeu & Missions

### 1. Vol Libre
Explorez un monde de 600km de large sans contrainte. Le trafic aérien IA et la tour de contrôle (ATC) sont actifs pour rendre le ciel vivant.

### 2. Carrière & Missions
Activez ce mode pour accéder aux défis spécifiques et au système de scoring :
*   **Parcours d'Anneaux** : Testez votre agilité en traversant une série d'anneaux disposés dans le ciel.
*   **Atterrissage de Précision** : Posez-vous le plus près possible de la cible sur la piste pour maximiser vos points.
*   **Largage Cargo** : (Exclusif au Gros Porteur) Larguez des caisses de ravitaillement sur des zones cibles au sol. Utilisez le viseur prédictif vert (CCIP) pour viser.

---

## Environnement & Météo Dynamique

Le simulateur simule un monde riche et évolutif :

*   **Saisons** : 
    *   *Été* : Ciel clair, conditions optimales.
    *   *Pluie* : Gouttes d'eau sur le cockpit, ciel gris et visibilité réduite.
    *   *Neige* : Particules de neige et ambiance hivernale.
    *   *Tempête* : Turbulences fortes et vents violents.
*   **Conditions Météo** : 
    *   *Nuages* : Couche nuageuse massive au-delà de 1500m.
    *   *Brouillard* : Visibilité au sol réduite selon l'intensité.
*   **Cycle Temporel** : 
    *   *Réel* : Synchronisé sur l'heure de votre ordinateur.
    *   *Dynamique* : Le temps défile (Aube, Jour, Crépuscule, Nuit).
    *   *Manuel* : Fixez l'heure de votre choix.

---

## Paramètres de Réalisme (Customisation Totale)

Vous pouvez ajuster le simulateur selon votre niveau :

*   **Mode de Pilotage** : 
    *   *Facile* : L'avion se stabilise automatiquement et la physique est simplifiée.
    *   *Réaliste* : Gestion complexe de la portance, de l'angle d'attaque et de l'inertie.
*   **Systèmes Avancés** (Activables/Désactivables) :
    *   **Température Moteur** : Risque de surchauffe en cas de gaz excessifs à basse altitude.
    *   **Poids Dynamique** : Le poids de l'avion diminue à mesure que vous consommez du carburant.
    *   **Décrochage (Stall)** : Perte de portance si la vitesse est trop faible ou l'angle trop élevé.
    *   **Vent & Turbulences** : Secousses aléatoires et dérive liée au vent.
    *   **Gestion du Train** : Risque de crash en cas d'atterrissage train rentré.

---

## Interface & Cockpit (HUD/IFR)

*   **HUD de Chasse** : Échelles de vitesse (gauche), altitude (droite), échelle de tangage et vecteur de trajectoire.
*   **Dashboard Analogique** : 
    *   *Horizon Artificiel* : Inclinaison et assiette.
    *   *Altimètre & Tachymètre* (Vitesse).
    *   *Indicateur de Portance (LIFT)* : Crucial pour éviter le décrochage.
*   **Radar Interactif (Touche M)** : 
    *   Carte GPS plein écran ou mini-map.
    *   Profil altimétrique du terrain en temps réel.
    *   Historique de trajectoire et marquage des zones de crash.

---

## Commandes de Vol

| Touche | Action | Note |
| :--- | :--- | :--- |
| **Flèches HAUT/BAS** | **Profondeur** | Piquer ou cabrer le nez de l'avion. |
| **Flèches GAUCHE/DROITE** | **Gaz (Throttle)** | Augmenter ou réduire la puissance moteur. |
| **ESPACE / B** | **Freins** | Freins de roue pour le roulage au sol. |
| **F** | **Volets (Flaps)** | Sortir les volets pour plus de portance au décollage/atterrissage. |
| **G** | **Train (Gear)** | Entrer/Sortir le train d'atterrissage. |
| **L** | **Phares** | Activer les feux d'atterrissage. |
| **B / V** | **Armement** | Larguer des bombes (B) ou tirer des missiles (V) - Mirage uniquement. |
| **C** | **Cargo** | Larguer du fret - Gros Porteur uniquement. |
| **R** | **Ravitaillement** | Maintenir à l'arrêt sur une piste pour faire le plein. |
| **K / N** | **Radio** | **K** pour On/Off, **N** pour changer de piste (Lo-Fi Radio). |
| **Molette** | **Zoom** | Zoomer ou dézoomer la vue caméra. |
| **ECHAP** | **Menu/Quitter** | Quitter le vol en cours. |

---

## Installation & Lancement

### Lancement via Python
1.  Prérequis : Python 3.x.
2.  Installation : `pip install pygame customtkinter pillow`
3.  Lancement : `python code/menu.py`

### Version Exécutable (.exe)
*   **Windows** : Double-cliquez sur `build_windows.bat` pour générer votre propre `.exe` dans le dossier `dist`.
*   **Linux** : Lancez `./dist/menu` (si déjà compilé).

---

## Améliorations Futures
N'hésitez pas à consulter le fichier `idees amelioration.txt` pour voir la feuille de route du projet (+50 idées d'évolution !).

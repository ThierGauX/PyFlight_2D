# PyFlight 2D

Bienvenue dans **PyFlight 2D**, un simulateur de vol 2D ultra-complet développé en Python. Alliant physique aérodynamique avancée, rendu haute résolution et systèmes météo dynamiques, il offre une expérience de pilotage immersive et entièrement personnalisable via son Launcher Premium.

---

## 🏆 Mode Carrière & Garage (Nouveau)

Le projet intègre désormais un système de progression complet. Gagnez des **pièces (💰)** en volant et en accomplissant des missions pour améliorer vos appareils.

### 💰 Économie de vol
*   **Distance** : Gagnez 1 pièce pour chaque kilomètre parcouru.
*   **Missions** : Votre score de mission est directement converti en pièces.
*   **Sauvegarde** : Vos pièces et améliorations sont conservées localement dans `career.json` (exclu du dépôt pour protéger votre progression).

### 🛠️ Le Garage (50 Niveaux d'amélioration)
Améliorez chaque avion indépendamment sur 7 axes techniques :
1.  **Moteur** : Augmente la poussée brute (+1% par niveau).
2.  **Aérodynamisme** : Améliore la finesse, augmente la portance et réduit la traînée.
3.  **Réservoir** : Augmente la capacité en carburant (+2% par niveau).
4.  **Allègement** : Réduit la masse totale de l'appareil pour plus d'agilité.
5.  **Train d'Atterrissage** : Augmente la tolérance aux chocs verticaux.
6.  **Refroidissement** : Réduit la vitesse de surchauffe moteur.
7.  **Freins** : Augmente la puissance de freinage au sol.

### 📊 Suivi des Records
Consultez vos records personnels dans l'onglet Carrière : **Vitesse Max**, **Altitude Record**, **Distance Totale**, **Nombre d'Atterrissages** et **Crashs**.

---

## Les Appareils (Aircrafts)

Chaque avion possède son propre modèle physique (masse, poussée, traînée, inertie) :

*   **Cessna 172 (Standard)** : L'équilibre parfait. Idéal pour l'apprentissage et la navigation.
*   **Chasseur Mirage (Armé)** : Vitesse extrême (VNE 1500 km/h). Équipé d'un système d'armement.
*   **Gros Porteur (Lourd)** : Une masse imposante. Demande une grande anticipation.
*   **Acrobatique (Acro)** : Conçu pour les figures extrêmes. Supporte des Angles d'Attaque (AOA) jusqu'à 30° et permet le "prop-hanging" (maintien sur l'hélice).

---

## Interface & Cockpit Professionnel

Le tableau de bord a été entièrement repensé pour offrir une clarté maximale sans aucune superposition :

*   **Jauge AOA (Angle of Attack)** : Instrument de précision mesurant l'angle entre le nez de l'avion et sa trajectoire réelle. Calibré à 16° (Aviation civile) et 30° (Acro). Elle atteint 100% pile au moment du décrochage.
*   **Instruments Analogiques** : Tachymètre (Knots), Horizon Artificiel fluide et Altimètre (Feet) avec effets de verre et de reflets.
*   **Bloc Moteur Digital** : Jauges verticales pour la Puissance (PWR), le Fuel et la Température (TEMP).
*   **Horloge UTC / ZULU** : Boitier numérique dédié affichant l'heure au format aéronautique standard.
*   **Voyants LED** : Indicateurs d'état avec halo lumineux pour le Train (GEAR), les Volets (FLAPS), les Freins (BRAKE) et le Pilote Auto (A/P).

---

## Environnement & Météo Avancée

*   **Météo Haute Densité** : Pluie et Neige simulées par 1000 particules actives avec gestion de la dérive et du bouclage infini.
*   **Effets Storm** : Éclairs aléatoires illuminant le ciel et flashs blancs en mode Tempête.
*   **Ground Spray** : Soulèvement de particules d'eau ou de neige derrière les roues lors des décollages à haute vitesse.

---

## Commandes de Vol

| Touche | Action | Note |
| :--- | :--- | :--- |
| **Flèches HAUT/BAS** | **Profondeur** | Piquer ou cabrer le nez de l'avion. |
| **Flèches GAUCHE/DROITE** | **Gaz (Throttle)** | Ajuster finement la puissance (+/- 10%). |
| **LSHIFT / LCTRL** | **Gaz Rapides** | Plein Gaz (SHIFT) ou Couper les Gaz (CTRL). |
| **A** | **Moteur** | Allumer ou éteindre le moteur (Toggle). |
| **ESPACE / B** | **Freins** | Freins de roue pour le roulage au sol. |
| **F** | **Volets (Flaps)** | Sortir les volets pour plus de portance (Vmax réduite). |
| **G** | **Train (Gear)** | Entrer/Sortir le train d'atterrissage. |
| **L** | **Phares** | Activer les feux d'atterrissage. |
| **M** | **Carte GPS** | Afficher/Masquer la grande carte interactive. |
| **ECHAP** | **Menu/Quitter** | Quitter le vol en cours (Sauvegarde auto carrière). |

---

## Installation & Lancement

1.  Prérequis : Python 3.x.
2.  Installation : `pip install -r requirements.txt`
3.  Lancement : `python code/menu.py`

---

## Améliorations Futures
Consultez [docs/idees amelioration.txt](docs/idees%20amelioration.txt) pour voir la feuille de route (+50 idées d'évolution !).

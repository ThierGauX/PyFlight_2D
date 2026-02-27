# PyFlight 2D - Simulateur de Vol Pro

Bienvenue dans PyFlight 2D, un simulateur de vol 2D ultra-complet développé en Python. Alliant physique aérodynamique, rendu haute résolution et systèmes météo dynamiques, il offre une expérience de pilotage immersive et personnalisable.

---

## Fonctionnalités Majeures

### Expérience de Vol & Voltige
*   Physique Avancée : Simulation de la portance, traînée, inertie et décrochage (Stall).
*   **Poids Dynamique** : La charge en carburant modifie de manière réaliste le poids et la maniabilité de l'avion en plein vol. (Désactivable)
*   Mode Voltige : Pilotez l'avion d'acrobatie pour réaliser des loopings à 360° sans aucune limite d'angle.
*   Portance Vectorisée : Un modèle physique précis où la portance suit l'inclinaison de vos ailes.
*   Effet de Sol : Ressentez le coussin d'air lors des atterrissages et décollages.

### Gestion Réaliste des Systèmes
*   **Température Moteur** : Risque de surchauffe dynamique ! Refroidissez votre moteur en prenant de l'altitude ou augmentez votre vitesse de croisière. (Désactivable)
*   **Consommation Carburant** : Surveillez votre jauge et ravitaillez sur l'un des nombreux aéroports (espacés de 75km).

### Monde Dynamique & Météo
*   Cycle Jour/Nuit : Transition fluide en temps réel (Aube, Jour, Crépuscule, Nuit).
*   Météo Volumétrique (Nuages 2D, brouillard, éclairage selon l'heure)
*   **Mode Missions** : Largage de cargo, parcours d'anneaux, atterrissage de précision.
*   **Statistiques et Scores** : Suivi des meilleures performances, moyennes et médianes pour chaque mission.
    *   Nuages Géants : Couche nuageuse massive au-delà de 1500m.
    *   Brouillard au sol : Visibilité réduite selon l'altitude.
    *   Saisons : Printemps, Été, Automne (pluie), Hiver (tempêtes de neige).
*   Relief Alpin : Génération procédurale de montagnes majestueuses avec détection de collision.

### Interface & Graphismes "Pro"
*   **Launcher Premium "Dashboard"** : Menu de configuration sous forme d'onglets (Vol, Environnement, Réalisme, Affichage) avec un design sombre et minimaliste ("Aero Dark").
*   Haute Résolution Native : Support du plein écran avec mise à l'échelle dynamique (UI Scaling) pour une netteté parfaite sur tous les moniteurs.
*   Cockpit Hybride :
    *   HUD de Chasse : Speed & Alt tapes, Pitch ladder et vecteur de vitesse.
    *   Dashboard Analogique : Horizon artificiel, Altimètre, Tachymètre et Jauge de portance (LIFT).
    *   Radar Multifonction : Profil altimétrique du terrain, trajectoire historique et navigation vers les pistes.
*   Suivi des Crashs et Explosions : Le radar garde une trace de chaque accident avec des croix rouges persistantes. Les crashs déclenchent également un effet de particules d'explosion.
*   Effets Visuels : Phares d'atterrissage, gouttes de pluie sur le cockpit, et traînées de fumée colorées personnalisables.

### Missions & Défis (Nouveau !)
En activant le mode **CARRIÈRE & MISSIONS** depuis le menu de configuration, vous accédez à :
*   **Trafic IA** : Avions de ligne sillonnant le ciel générés procéduralement.
*   **Contrôle Aérien (ATC)** : La tour de contrôle vous contacte par messages radio lors du décollage et des approches. Elle communique aussi aléatoirement en vol de croisière.
*   **Missions Ciblées** : Depuis le menu "MODE DE JEU", vous pouvez choisir explicitement :
    *   **Aucune** : Juste le trafic IA et l'ATC pour une ambiance ralaxante.
    *   **Parcours d'Anneaux** : Testez votre agilité (Anciennement F1).
    *   **Atterrissage de Précision** : Posez-vous en douceur sur la cible (Anciennement F2).
    *   **Largage Cargo** : À bord du Gros Porteur, volez à basse altitude pour larguer des colis (Touche C) avec précision sur des zones cibles. Un viseur prédictif (CCIP) vert s'affiche au sol pour vous aider à viser !
-   `L` : Allumer/Éteindre les phares
-   `M` : Afficher/Masquer la Mini-Map GPS (Radar)
-   `C` : Larguer des caisses (Uniquement si Avion Cargo & Mission Cargo)
-   `R` : Allumer/Éteindre la Radio de bord Lo-Fi

---

## Commandes de Vol

| Touche | Action | Note |
| :--- | :--- | :--- |
| **Flèche HAUT** | **Piquer (Nez Bas)** | Pousse le manche. |
| **Flèche BAS** | **Cabrer (Nez Haut)** | Tire le manche. |
| **Flèches G/D** | **Gaz (Throttle)** | Contrôle la puissance moteur. |
| **ESPACE / B** | **Freins de roues** | Utile lors du roulage. |
| **F** | **Volets (Flaps)** | Augmente la portance à basse vitesse. |
| **G** | **Train d'Atterrissage** | À rentrer pour la vitesse, sortir pour la pose. |
| **L** | **Lumières (Landing lights)** | Essentiel pour la navigation nocturne. |
| **C** | **Largage Cargo** | Disponible uniquement avec l'avion Cargo en mode Missions. |
| **R** | **Ravitaillement** | Maintenir à l'arrêt sur une piste. |
| **Molette** | **Zoom Caméra** | Vue d'ensemble ou cockpit serré. |
| **ECHAP** | **Quitter** | Ferme le jeu instantanément. |

---

## Installation & Lancement

1.  Prérequis : Python 3.x installé.
2.  Installation des dépendances :
    ```bash
    pip install pygame customtkinter pillow
    ```
3.  Lancement :
    ```bash
    python menu.py
    ```

---

## Améliorations Futures
Consultez le fichier `idees amelioration.txt` pour découvrir 50 idées d'évolution (physique, gameplay, IA, etc.) !

---

## Développeurs

**Gauthier** : Architecture logicielle, simulation physique avancée (portance vectorisée, traînée, décrochage), développement des systèmes de bord (HUD haute résolution, radar, instruments analogiques) et moteur météo procédural.

**Jules** : Design visuel et direction artistique, création des sprites haute résolution (avions, décors), conception de l'interface utilisateur (UI/UX) et intégration des effets visuels dynamiques (particules de fumée, reflets, animations météo).


## Licence
Ce projet est sous licence MIT.

# PyFlight 2D - Simulateur de Vol Pro

Bienvenue dans PyFlight 2D, un simulateur de vol 2D ultra-complet développé en Python. Alliant physique aérodynamique, rendu haute résolution et systèmes météo dynamiques, il offre une expérience de pilotage immersive et personnalisable.

---

## Fonctionnalités Majeures

### Expérience de Vol & Voltige
*   Physique Avancée : Simulation de la portance, traînée, inertie et décrochage (Stall).
*   Mode Voltige : Pilotez l'avion d'acrobatie pour réaliser des loopings à 360° sans aucune limite d'angle.
*   Portance Vectorisée : Un modèle physique précis où la portance suit l'inclinaison de vos ailes.
*   Effet de Sol : Ressentez le coussin d'air lors des atterrissages et décollages.

### Monde Dynamique & Météo
*   Cycle Jour/Nuit : Transition fluide en temps réel (Aube, Jour, Crépuscule, Nuit).
*   Météo Volumétrique :
    *   Nuages Géants : Couche nuageuse massive au-delà de 1500m.
    *   Brouillard au sol : Visibilité réduite selon l'altitude.
    *   Saisons : Printemps, Été, Automne (pluie), Hiver (tempêtes de neige).
*   Relief Alpin : Génération procédurale de montagnes majestueuses avec détection de collision.

### Interface & Graphismes "Pro"
*   Haute Résolution Native : Support du plein écran avec mise à l'échelle dynamique (UI Scaling) pour une netteté parfaite sur tous les moniteurs.
*   Cockpit Hybride :
    *   HUD de Chasse : Speed & Alt tapes, Pitch ladder et vecteur de vitesse.
    *   Dashboard Analogique : Horizon artificiel, Altimètre, Tachymètre et Jauge de portance (LIFT).
    *   Radar Multifonction : Profil altimétrique du terrain, trajectoire historique et navigation vers les pistes.
*   Suivi des Crashs et Explosions : Le radar garde une trace de chaque accident avec des croix rouges persistantes. Les crashs déclenchent également un effet de particules d'explosion.
*   Effets Visuels : Phares d'atterrissage, gouttes de pluie sur le cockpit, et traînées de fumée colorées personnalisables.

### Missions & Défis
*   Anneaux de Navigation : Suivez un parcours complexe à travers les montagnes (F1).
*   Précision d'Atterrissage : Atterrissez sur une zone cible spécifique pour valider votre mission (F2).
*   Gestion du Carburant : Surveillez votre jauge (désormais 100% précise) et ravitaillez sur l'un des nombreux aéroports (espacés de 75km).

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

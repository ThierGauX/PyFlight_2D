# PyFlight 2D


Gauthier: menu de jeu

Jules: avion

Bienvenue dans PyFlight 2D, un simulateur de vol développé en Python avec la bibliothèque Pygame.Contrairement aux jeux d'arcade classiques, ce projet se concentre sur une simulation aérodynamique réaliste.
L'avion ne se déplace pas simplement sur l'écran : il vole grâce à la portance générée par la vitesse et l'angle d'attaque des ailes.🌟 Fonctionnalités PrincipalesPhysique de Vol Avancée : Gestion de la gravité, de la traînée (drag), de la poussée (thrust) et de la portance (lift).Modèle de Vol Précis :Vitesse de décollage : 79 km/hVitesse de décrochage : 89 km/h (en vol)

**Gestion des Incidents** 
: Simulation du décrochage avec perte de contrôle et alarmes de survitesse.
Environnement Dynamique :HUD (Heads-Up Display) complet : Altitude, Vitesse, Variomètre, Angle.
Atmosphère visuelle : La couleur du ciel change avec l'altitude (dégradé bleu vers l'espace).Défilement infini du terrain.


**Commandes de Vol**

| Touche | Action | Effet Physique |
| :--- | :--- | :--- |
| **➡️ Flèche DROITE** | **Moteur / Gaz** | Accélère l'avion (Maintenir pour décoller). |
| **⬇️ Flèche BAS** | **Tirer le manche** | Le nez monte (**Cabrer**) pour prendre de l'altitude. 🛫 |
| **⬆️ Flèche HAUT** | **Pousser le manche** | Le nez descend (**Piquer**) pour plonger ou prendre de la vitesse. 🛬 |
| *(Aucune touche)* | **Planer** | L'avion plane et ralentit progressivement (Frottement de l'air). |


**Installation et Lancement Prérequis.**

-Python 3.x installé sur votre machine.
-La bibliothèque pygame.
-InstallationClonez ce dépôt ou téléchargez les fichiers.
-Installez les dépendances via le terminal :Bashpip install pygame
-LancementExécutez simplement le script principal :Bashpython avion.py

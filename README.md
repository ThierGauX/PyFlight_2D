# PyFlight 2D - Simulateur de Vol

Bienvenue dans **PyFlight 2D**, un simulateur de vol avancé développé en Python avec **Pygame** et **CustomTkinter**.
Ce projet propose une expérience de vol immersive mêlant physique réaliste, graphismes soignés et interface moderne.

- **Gauthier :** Développement & Interface (Menu "Ultimate").
- **Jules :** Design & Identité Visuelle.

##  Fonctionnalités Principales

###  Physique & Réalisme
* **Modèle de Vol Avancé :** Inertie, portance, traînée et décrochage simulés.
* **Effet de Sol :** Décollage plus réaliste avec une "bulle d'air" près du sol.
* **Roulage Fluide :** Système de freinage progressif et suspensions actives pour des atterrissages doux.
* **Météo Temps Réel :** Synchronisation avec l'heure réelle (France) pour des cycles jour/nuit dynamiques.

###  Menu "Ultimate"
* **Interface Pro :** Launcher moderne style "Aero" (Bleu nuit/Glass).
* **Paramètres Complets :**
    * **Difficulté :** Facile (Assisté) ou Réaliste.
    * **Temps :** Réel (Horloge Système) ou Manuel (Curseur 0h-24h).
    * **Volume :** Réglage précis du moteur.
* **Lancement Direct :** Le jeu démarre instantanément avec vos préférences.

###  Immersion Visuelle
* **Monde Infini :** Génération procédurale du terrain (herbe, piste) à l'infini.
* **Zoom Dynamique :** Molette de souris pour passer d'une vue cockpit à une vue satellite (x0.1 à x5.0).
* **Particules de Vitesse :** Traits blancs dynamiques qui suivent vos mouvements verticaux.
* **Lumière d'Atterrissage :** Projecteur orientable pour les vols de nuit.

##  Commandes de Vol

| Touche / Action | Fonction | Détails |
| :--- | :--- | :--- |
| **Flèche GAUCHE / DROITE** | **Gaz (Puissance)** | Gère la poussée du moteur. |
| **SHIFT (Maj)** | **Plein Gaz** | Poussée maximale immédiate (Décollage d'urgence). |
| **CTRL** | **Couper Gaz** | Arrêt moteur immédiat (Approche finale). |
| **Flèche HAUT** | **Piquer (Descendre)** | Pousse le manche vers l'avant. |
| **Flèche BAS** | **Cabrer (Monter)** | Tire le manche vers l'arrière. |
| **ESPACE / B** | **Freins de Roue** | Ralentir au sol après l'atterrissage. |
| **L** | **Lumière** | Allumer/Éteindre le phare d'atterrissage. |
| **Molette SOURIS** | **Zoom Caméra** | Zoom avant/arrière fluide. |

##  Guide de Démarrage

### Prérequis
* Python 3.x installé.
* Bibliothèques nécessaires :
    ```bash
    pip install pygame customtkinter pillow
    ```

### Lancement
Pour profiter de toutes les fonctionnalités (paramètres, météo...), lancez toujours le **Launcher** :

```bash
python menu.py
```

*Bon vol Commandant !*

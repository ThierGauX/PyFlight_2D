# PyFlight 2D - Simulateur de Vol

Bienvenue dans **PyFlight 2D**, un simulateur de vol avancé développé en Python avec **Pygame** et **CustomTkinter**.
Ce projet propose une expérience de vol immersive mêlant physique réaliste, graphismes soignés et interface moderne.

- **Gauthier :** Développement & Interface (Menu "Ultimate").
- **Jules :** Design & Identité Visuelle.

## Nouveautes (Mise a jour Saisons)

### Saisons & Meteo Dynamique
Le monde change selon vos envies grace au nouveau selecteur de saison :
*   **PRINTEMPS (Fleurs) :** Herbe vert tendre, ciel bleu doux, ambiance calme.
*   **ETE (Vert) :** Couleurs vibrantes, ciel degage, chaleur.
*   **AUTOMNE (Feuilles) :** Sol orange/brun, ciel orageux sombre, pluie battante.
*   **HIVER (Neige) :** Sol blanc/gele, ciel froid gris-bleu, tempete de neige massive.
*   **TEMPETE (Vent) :** Effets de vent violent pour tester votre pilotage.

### Dashboard Hybride
Un nouveau tableau de bord repense pour la clarte et le style :
*   **Overlay HUD :** Bandes de vitesse et d'altitude transparentes style "Chasseur".
*   **Instruments Analogiques :** Cadrans classiques pour l'horizon artificiel et le variometre.
*   **Indicateurs Regroupes :** GEAR, FLAPS et BRAKES sont maintenant clairement visibles au-dessus du radar.

### Options & Cheats
Nouveau menu "Gameplay" pour le fun :
*   **Carburant Illimite :** Volez eternellement sans ravitailler.
*   **Invincibilite (God Mode) :** Rebondissez sur le sol sans crash !

---

## Fonctionnalites Principales

### Physique & Realisme
*   **Modele de Vol Avance :** Inertie, portance, trainee et decrochage simules.
*   **Effet de Sol :** Decollage plus realiste avec une "bulle d'air" pres du sol.
*   **Roulage Fluide :** Systeme de freinage progressif et suspensions actives.

### Menu "Ultimate"
*   **Interface Pro :** Launcher moderne style "Aero" (Bleu nuit/Glass).
*   **Parametres Complets :** Difficulte, Heure (Reelle/Manuelle), Volume.
*   **Lancement Direct :** Configuration instantanee.

### Immersion Visuelle
*   **Monde Infini :** Generation procedurale du terrain.
*   **Nuages Volumetriques :** Les nuages deviennent enormes a haute altitude (>1500m).
*   **Particules Meteo :** Pluie, Neige et Vent reagissent a la vitesse de l'avion.

---

## Commandes de Vol

| Touche / Action | Fonction | Details |
| :--- | :--- | :--- |
| **Fleche HAUT** | **Piquer (Descendre)** | Pousse le manche vers l'avant. |
| **Fleche BAS** | **Cabrer (Monter)** | Tire le manche vers l'arriere. |
| **Fleche GAUCHE / DROITE** | **Gaz (Puissance)** | Gere la poussee du moteur. |
| **ESPACE** | **Freins** | Ralentir au sol. |
| **F** | **Volets (Flaps)** | Sortir/Rentrer les volets pour la portance. |
| **G** | **Train d'Atterrissage** | Rentrer/Sortir le train (Gear). |
| **L** | **Lumiere** | Allumer/Eteindre le phare. |
| **Molette SOURIS** | **Zoom Camera** | Zoom avant/arriere fluide. |
| **ECHAP** | **Quitter** | Retour au bureau. |

---

## Installation & Lancement

### Prerequis
*   Python 3.x installe.
*   Bibliotheques necessaires :
    ```bash
    pip install pygame customtkinter pillow
    ```

### Lancement
Pour profiter de toutes les fonctionnalites (parametres, meteo...), lancez toujours le **Launcher** :

```bash
python menu.py
```

*Bon vol Commandant !*


## Nouveautés Récentes
- Variomètre remplacé par un indicateur de Portance (LIFT)
- Ajout d'un paramètre de contrôle du Carburant Initial dans le launcher
- Consommation dynamique de carburant basée de façon quadratique sur l'utilisation de la manette des gaz
- Refonte graphique de la jauge de carburant analogique du tableau de bord (suppression des indicateurs E et F pour plus de clarté)
- Implémentation du train d'atterrissage rétractable (Touche G) avec impact sur la physique (vitesse) et gestion des crashs (atterrissage sur le ventre)
- Création d'une liste détaillée des variations de sprites et d'effets sonores nécessaires pour chaque appareil (liste de choses a faire Jules.txt)
- Ajout d'améliorations visuelles (gouttes de pluie dynamiques sur l'écran, suppression des villes)
- Refonte du système de ravitaillement : aéroports espacés tous les 75km, piste de 6km affichée entièrement sur le radar, et obligation de s'arrêter pour refuel (touche R)
- Amélioration majeure du réalisme visuel des aéroports (ajout de PAPI lights, lumières de bord de piste, zones de toucher de roues, signalisation 09/27 agrandie)
- Ajout d'options de réalisme dans le menu des paramètres (désactivation du décrochage, du vent, des crashs de train d'atterrissage, et ravitaillement automatique)
- Génération de relief dynamique (montagnes/collines) avec collisions et radar profil altimétrique
- Aide à la navigation sur la mini-carte avec la distance exacte jusqu'à la piste la plus proche
- Surchauffe moteur avec jauge de température (panne moteur en cas de sur-régime prolongé)
- Ajout d'un réglage d'intensité du relief dans les options pour des paysages plus plats ou plus montagneux
- Refonte de la trajectoire sur le radar (ligne cyan plus épaisse) et ajout d'un marqueur d'avion triangulaire jaune
- Génération de montagnes immenses (Multiplicateur de relief jusqu'à x5.0 dans les options)
- Collision horizontale avec le relief (Crash direct contre les pentes abruptes)
- Montagnes élargies pour des massifs beaucoup plus imposants au milieu de la map
- Limite de zoom étendue pour permettre une vue beaucoup plus lointaine (molette souris)
- Échelle du relief sur le radar corrigée pour correspondre parfaitement à la taille des montagnes
- Orientation dynamique de l'avion sur le radar en fonction du tangage
- Correction de la disparition du sol lors d'un dézoom extrême
- Ajout d'une option "Fumée Acrobatique (Traînée)" dans les paramètres pour afficher la trajectoire de l'avion en plein ciel
- Option de personnalisation de la couleur de la traînée (Blanc, Rouge, Bleu, Vert, Jaune)
- Amélioration visuelle très forte du rendu volumétrique de la traînée (fondu et cercles concentriques alpha)
- Amélioration de la traînée de fumée : Dure 4x plus longtemps dans le ciel et part bien de la queue de l'avion
- Correction de la traînée en pointillés : Génération dynamique des particules d'air basée sur la vitesse réelle pour un nuage continu parfait
- Nouvel avion 'Acrobatique (Voltige)' : Très maniable, débloque la limite d'angle de tangage pour permettre des loopings complets (360°)
- Correction de la physique de looping : La portance est désormais vectorisée (perpendiculaire aux ailes) et l'angle d'attaque est plafonné pour empêcher les sauts d'altitude irréalistes sur le dos.
- Correction de l'affichage du terrain : Les montagnes restent visibles même avec un zoom très proche (correction de l'optimisation de rendu).
- Correction de la case à cocher 'Fumée' : La fumée ne s'active désormais plus de force quand le moteur est à pleine puissance si l'option est décochée.
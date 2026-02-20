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
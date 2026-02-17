# PyFlight 2D - Simulateur de Vol

Bienvenue dans **PyFlight 2D**, un simulateur de vol avancé développé en Python avec **Pygame** et **CustomTkinter**.
Ce projet propose une expérience de vol immersive mêlant physique réaliste, graphismes soignés et interface moderne.

- **Gauthier :** Développement & Interface (Menu "Ultimate").
- **Jules :** Design & Identité Visuelle.

##  Nouveautés (Mise à jour Saisons)

###  Saisons & Météo Dynamique
Le monde change selon vos envies grâce au nouveau sélecteur de saison :
*   **PRINTEMPS (Fleurs) :** Herbe vert tendre, ciel bleu doux, ambiance calme.
*   **ÉTÉ (Vert) :** Couleurs vibrantes, ciel dégagé, chaleur.
*   **AUTOMNE (Feuilles) :** Sol orange/brun, ciel orageux sombre, pluie battante.
*   **HIVER (Neige) :** Sol blanc/gelé, ciel froid gris-bleu, tempête de neige massive.
*   **TEMPÊTE (Vent) :** Effets de vent violent pour tester votre pilotage.

###  Dashboard Hybride
Un nouveau tableau de bord repensé pour la clarté et le style :
*   **Overlay HUD :** Bandes de vitesse et d'altitude transparentes style "Chasseur".
*   **Instruments Analogiques :** Cadrans classiques pour l'horizon artificiel et le variomètre.
*   **Indicateurs Regroupés :** GEAR, FLAPS et BRAKES sont maintenant clairement visibles au-dessus du radar.

###  Options & Cheats
Nouveau menu "Gameplay" pour le fun :
*   **Carburant Illimité :** Volez éternellement sans ravitailler.
*   **Invincibilité (God Mode) :** Rebondissez sur le sol sans crash !

---

##  Fonctionnalités Principales

### Physique & Réalisme
*   **Modèle de Vol Avancé :** Inertie, portance, traînée et décrochage simulés.
*   **Effet de Sol :** Décollage plus réaliste avec une "bulle d'air" près du sol.
*   **Roulage Fluide :** Système de freinage progressif et suspensions actives.

### Menu "Ultimate"
*   **Interface Pro :** Launcher moderne style "Aero" (Bleu nuit/Glass).
*   **Paramètres Complets :** Difficulté, Heure (Réelle/Manuelle), Volume.
*   **Lancement Direct :** Configuration instantanée.

### Immersion Visuelle
*   **Monde Infini :** Génération procédurale du terrain.
*   **Nuages Volumétriques :** Les nuages deviennent énormes à haute altitude (>1500m).
*   **Particules Météo :** Pluie, Neige et Vent réagissent à la vitesse de l'avion.

---

##  Commandes de Vol

| Touche / Action | Fonction | Détails |
| :--- | :--- | :--- |
| **Flèche HAUT** | **Piquer (Descendre)** | Pousse le manche vers l'avant. |
| **Flèche BAS** | **Cabrer (Monter)** | Tire le manche vers l'arrière. |
| **Flèche GAUCHE / DROITE** | **Gaz (Puissance)** | Gère la poussée du moteur. |
| **ESPACE** | **Freins** | Ralentir au sol. |
| **F** | **Volets (Flaps)** | Sortir/Rentrer les volets pour la portance. |
| **G** | **Train d'Atterrissage** | Rentrer/Sortir le train (Gear). |
| **L** | **Lumière** | Allumer/Éteindre le phare. |
| **Molette SOURIS** | **Zoom Caméra** | Zoom avant/arrière fluide. |
| **ECHAP** | **Quitter** | Retour au bureau. |

---

##  Installation & Lancement

### Prérequis
*   Python 3.x installé.
*   Bibliothèques nécessaires :
    ```bash
    pip install pygame customtkinter pillow
    ```

### Lancement
Pour profiter de toutes les fonctionnalités (paramètres, météo...), lancez toujours le **Launcher** :

```bash
python menu.py
```

*Bon vol Commandant !*

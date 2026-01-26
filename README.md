# PyFlight 2D - Simulateur de Vol 

Bienvenue dans **PyFlight 2D**, un simulateur de vol développé en Python avec la bibliothèque Pygame.


* **Gauthier :** Développement du Menu du jeu.
* **Jules :** style de l'avion.

##  Fonctionnalités Nouvelles & Principales

###  Physique & Pilotage
* **Inertie Réaliste :** Les commandes sont "lourdes". L'avion ne tourne pas instantanément, simulant la masse d'un véritable appareil.
* **Modèle de Vol "Chasseur" :**
    * Vitesse de décollage : **~220 km/h**
    * Vitesse maximale (VNE) : **2500 km/h** (Mach 2.0+)
    * Simulation de la traînée induite (perte de vitesse en virage serré).

###  Immersion Visuelle
* **Caméra Dynamique (ZOOM) :** Possibilité de zoomer/dézoomer fluide avec la souris pour observer les détails ou le terrain.
* **Cockpit Analogique :** Anémomètre à aiguille fonctionnel en temps réel.
* **Effets de Particules :** Système de poussières atmosphériques pour ressentir la vitesse.
* **HUD Militaire :** Affichage tête haute du Mach, des G-Force et du Variomètre.

## 🎮 Commandes de Vol

Le simulateur se joue au Clavier et à la Souris.

| Touche / Action | Fonction | Effet Physique |
| :--- | :--- | :--- |
| **➡️ Flèche DROITE** | **Postcombustion** | Accélère l'avion (Maintenir pour décoller). |
| **⬇️ Flèche BAS** | **Tirer le manche** | Le nez monte (**Cabrer**). Attention à la perte de vitesse ! 🛫 |
| **⬆️ Flèche HAUT** | **Pousser le manche** | Le nez descend (**Piquer**) pour prendre de la vitesse. 🛬 |
| **🖱️ Molette SOURIS** | **Zoom Caméra** | **Haut :** Zoom Avant (Détails) <br> **Bas :** Zoom Arrière (Vue large). |
| *(Aucune touche)* | **Auto-Pilot** | Activation automatique du mode **STABLE** (Maintien d'altitude). |

##  Guide Rapide

1.  **Au sol :** Maintenez la **Flèche DROITE**.
2.  **Décollage :** Attendez **220 km/h**, puis appuyez doucement sur **BAS**. Ne tirez pas trop fort pour éviter de décrocher.
3.  **En vol :** Utilisez la **Molette** de la souris pour ajuster la vue.
4.  **Atterrissage :** Coupez les gaz, levez le nez pour freiner avec l'air (Aérofreinage) et touchez le sol doucement (< 5 m/s).

##  Installation

### Prérequis
* Python 3.x installé.
* Bibliothèque `pygame`.

### Installation
1.  Clonez ce dépôt ou téléchargez les fichiers `avion.py`, `avion_arret.png` et `avion_marche.png`.
2.  Installez les dépendances via le terminal :
    ```bash
    pip install pygame
    ```

### Lancement
Exécutez le script principal :
```bash
python avion.py

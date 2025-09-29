# Script de remplissage des données PvM

Ce script permet de remplir la base de données avec toutes les capacités et terrains PvM (Player vs Monster) en français.

## Utilisation

### Méthode 1: Via Django runscript (recommandée)
```bash
python manage.py runscript populate_pvm_data
```

### Méthode 2: Exécution directe
```bash
python scripts/populate_pvm_data.py
```

## Fonctionnalités

- **Sécurisé**: Le script peut être exécuté plusieurs fois sans créer de doublons
- **Bilingue**: Toutes les données sont en français comme requis
- **Complet**: Inclut toutes les capacités et terrains définis dans le code
- **Informatif**: Affiche un rapport détaillé de l'exécution

## Données ajoutées

### Capacités PvM (20 au total)

#### Capacités d'équipe (8):
1. **Dernier souffle** - Récupération de PV quand un allié meurt
2. **Sprint préhistorique** - Bonus de vitesse temporaire au début
3. **Esprit de meute** - Bonus d'attaque conditionnel
4. **Bouclier collectif** - Partage des dégâts
5. **Instinct protecteur** - Bonus de défense après coup critique
6. **Pression croissante** - Augmentation progressive d'attaque
7. **Seul contre tous** - Bonus de défense pour le dernier survivant
8. **Terreur collective** - Bonus d'attaque permanent après élimination

#### Capacités individuelles (12):
1. **Mort-vivant** - Attaques posthumes
2. **Frénésie** - Vitesse d'attaque accrue à bas PV
3. **Bourreau** - Exécution instantanée
4. **Peau dure** - Réduction de dégâts à haut PV
5. **Inspiration héroïque** - Bonus d'équipe après coup critique
6. **Vol de vie** - Récupération de PV par attaque
7. **Provocation** - Attraction des attaques ennemies
8. **Agilitée accrue** - Esquive d'attaques
9. **Regard pétrifiant** - Ralentissement d'ennemi
10. **Régénération** - Récupération périodique de PV
11. **Chasseur nocturne** - Bonus critique conditionnel
12. **Carapace robuste** - Résistance dégressive aux dégâts

### Terrains PvM (7 au total)

1. **Distorsion** - Mélange aléatoire des statistiques
2. **Lac Putréfié** - Perte de PV continue
3. **Brouillard Épais** - Réduction de précision
4. **Jungle Perfide** - Cooldown réduit pour supports
5. **Ère Glaciaire** - Vitesse uniforme
6. **Montagne Rocheuse** - Bonus défense Tank, malus attaque DPS
7. **Éruption Volcanique** - Bonus attaque DPS, malus défense Tank

## Structure de la base de données

Le script remplit deux tables:
- `DWPvmAbility` (capacités) avec les champs `name`, `description`, `to_dino`
- `DWPvmTerrain` (terrains) avec les champs `name`, `description`

## Exemple de sortie

```
🚀 Début du remplissage de la base de données PvM...
============================================================
=== Ajout des capacités PvM ===
✅ Créée: Dernier souffle (Équipe)
✅ Créée: Sprint préhistorique (Équipe)
[...]

📊 Résumé des capacités:
   - Nouvelles capacités créées: 20
   - Capacités déjà existantes: 0
   - Total: 20 capacités dans la base de données

=== Ajout des terrains PvM ===
✅ Créé: Distorsion
✅ Créé: Lac Putréfié
[...]

📊 Résumé des terrains:
   - Nouveaux terrains créés: 7
   - Terrains déjà existants: 0
   - Total: 7 terrains dans la base de données

============================================================
✅ Remplissage terminé avec succès!
📋 Total final:
   - Capacités: 20
   - Terrains: 7
```
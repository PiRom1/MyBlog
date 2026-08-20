# DiploPark — Équilibrage consolidé

**Version :** 1.0 — décisions validées le 20 août 2026  
**Source :** réponse joueur `diplopark-equilibrage-valide.md`  
**Statut :** normatif pour l’implémentation ; seules les calibrations statistiques signalées restent variables

## Progression cible

| Jalon | Cible moyenne |
|---|---:|
| Deuxième enclos | 5 MAJ |
| Sixième enclos | 30 MAJ |
| Habitat privilégié largement rempli | 200 MAJ |
| Parc presque complet | 500 MAJ |

## Démarrage

- 400 000 ParkCoins ;
- 15 MAJ bonus initiales, puis 5 supplémentaires à la fin du tutoriel ;
- aucun enclos, animal ou membre du personnel offert ;
- billet à 5 et 5 visiteurs de base ;
- dégâts désactivés pendant les 10 premières MAJ ;
- aide débutant dégressive pendant 50 MAJ.

Courbe candidate à simuler : `bonus(i) = 100 000 - 2 000 × i`, pour `i = 0..49`, donc de 100 000 à 2 000. La pente finale sera choisie par une simulation de 2 000 parcours afin de respecter les quatre jalons.

## Enclos

| Élément | Valeur |
|---|---:|
| Construction nue | 2 500 |
| Capacité niveau 1 | 40 points de gabarit |
| Niveau 2 | 75 000 ; capacité 70 |
| Niveau 3 | 180 000 ; capacité 100 |
| Luxe | 20 000 ; capacité 100 ; +5 % visiteurs ; 20 paysagistes |
| Population maximale | 100 individus |

## Installations

| Installation | Niveaux | Coût du palier `n` | Revenu total au niveau `n` |
|---|---:|---:|---:|
| Hôtel | 5 | `100 000 × n` | `10 000 × n` par MAJ |
| Train | 10 | `50 000 × n` | `5 000 × n` par MAJ |

Coûts initiaux des boutiques : Souvenirs 80 000, restauration 100 000, boissons 120 000, glaces 150 000.

## Cycle de vie et reproduction

- maturité : 5 MAJ ;
- longévité standard : 50 MAJ ;
- 45 occasions reproductives pour un couple formé dès la maturité ;
- santé du parc strictement supérieure à 25 % ;
- au-delà de 15 couples de la même espèce dans un enclos, taux réduit de moitié pour chaque couple excédentaire.

| Rareté | Descendants moyens ciblés par couple | Taux initial par couple et par MAJ |
|---|---:|---:|
| Commune | 4 | 8,89 % |
| Peu commune | 3,5 | 7,78 % |
| Rare | 3 | 6,67 % |
| Exceptionnelle | 2,5 | 5,56 % |
| Secrète | 2 | 4,44 % |

Ces taux sont les points de départ mathématiques `espérance / 45`. La simulation peut les corriger légèrement pour compenser les décès anticipés et formations tardives, sans changer les espérances cibles.

Albinos : jamais achetable ; prestige ×5. Probabilités à la naissance : 5 % avec deux parents normaux, 20 % avec un parent albinos, 50 % avec deux parents albinos, 70 % sous potion.

## Météo

| État | Poids | Visiteurs | Naissances |
|---|---:|---:|---:|
| Grand soleil | 22 % | +20 % | ×1,10 |
| Beau temps | 30 % | +10 % | ×1,00 |
| Couvert | 22 % | 0 % | ×1,00 |
| Pluie | 16 % | −20 % | ×1,00 |
| Neige | 8 % | −50 % | ×0,90 |
| Météorite | 2 % | −75 % | ×1,00 |

Une météorite verse 20 000 ParkCoins. Chaque enclos construit subit un tirage indépendant de dégâts à 30 %, avec au plus 10 enclos endommagés par MAJ et immunité pendant les 10 premières MAJ du parc.

## Apparitions spontanées

- tirage pour chaque enclos éligible : 0,5 % par MAJ ;
- aucune hausse pendant les 20 premiers échecs ;
- ensuite +0,05 point de pourcentage par échec ;
- succès garanti au 50e tirage éligible consécutif ;
- compteur anti-malchance unique au parc, incrémenté après chaque tirage d’enclos échoué dans un ordre stable ;
- remise à zéro du compteur du parc après tout succès ;
- une apparition au maximum par enclos et par MAJ ; plusieurs enclos peuvent réussir au même cycle.

## Marché

Mise à jour à chaque distribution biquotidienne des MAJ :

```text
pression = clamp(achats - ventes, -10, +10)
variation_volume = pression × 1 %
retour_base = clamp((prix_base - prix_actuel) / (2 × prix_base), -5 %, +5 %)
variation_totale = clamp(variation_volume + retour_base, -10 %, +10 %)
nouveau_prix = clamp(prix_actuel × (1 + variation_totale), 50 % × prix_base, 200 % × prix_base)
```

Les volumes ne sont consommés qu’une fois par créneau. Sans mouvement, seul le retour à la base agit. Les albinos ne sont pas achetables.

## Espèces

| Rareté | Prix de base | Prestige | Poids de rotation |
|---|---:|---:|---:|
| Commune | 5 000–30 000 | 1 | 100 |
| Peu commune | 30 000–80 000 | 2 | 60 |
| Rare | 80 000–180 000 | 4 | 25 |
| Exceptionnelle | 180 000–400 000 | 7 | 8 |
| Secrète | 250 000–600 000 | 10 | 0 avant déblocage |

Générer et valider 92 fiches d’espèces et 29 variantes albinos.

## Missions périodiques

Trois missions sont actives, portant le total du catalogue à **652 objectifs** : 605 missions de naissance, 44 avancées et 3 périodiques.

| Mission | Cadence | Objectifs | Récompenses |
|---|---|---|---|
| Semaine jurassique | Hebdomadaire | Une naissance naturelle de chaque espèce vedette ; MAJ bonus exclues | 1 stock exceptionnel |
| Espèce du mois | Mensuelle | Commune 20/25/30 ; peu commune 15/20/25 ; rare 10/15/20 ; exceptionnelle 5/10/15 ; secrète exclue | 1/2/3 MAJ bonus |
| Contrebandier | Hebdomadaire | Ventes : commune 4/6/8 ; peu commune 3/5/7 ; rare 2/4/6 ; exceptionnelle 1/3/5 ; secrète exclue | 1/2/3 MAJ bonus |

Supprimées : Inestimable, Gardien fidèle et Une méthode à suivre. Chaîne alimentaire est remplacée par Contrebandier.

## Événements et boutique

Le moteur sait gérer, mais laisse inactifs au lancement : rotations du 1er et du 15 pendant sept jours, migration temporaire, espèce du mois, promotion de marché et fenêtre de naissance conditionnelle.

La boutique en Diplodocoins est visible mais fermée. Les récompenses quotidiennes restent : 50 au premier, 25 au deuxième et 10 à chaque joueur actif la veille, cumulables.

## Portes de validation technique

Avant activation des fixtures :

1. simuler au moins 2 000 parcours avec graines reproductibles ;
2. mesurer médiane, P10 et P90 des quatre jalons ;
3. vérifier l’absence de faillite structurelle ;
4. calibrer uniquement la pente de l’aide débutant et, si nécessaire, les taux reproductifs autour des valeurs initiales ;
5. vérifier sur au moins 100 000 tirages la distribution météo et les apparitions ;
6. enregistrer toutes les valeurs finales dans un ruleset versionné.

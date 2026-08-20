# Livret de spécifications — DiploPark

> Nom de projet provisoire. Document vivant destiné à être enrichi et corrigé au fil des décisions.

| Information | Valeur |
| --- | --- |
| Version | 1.1.0 |
| Date de création | 19 août 2026 |
| Statut | Décisions et équilibrage consolidés ; calibrations statistiques requises |
| Application cible | Site Django existant |
| Inspiration fonctionnelle | Jeu de gestion de parc en semi-temps réel |

### Convention de preuve

Les règles issues de l'audit sont accompagnées d'un niveau de certitude :

| Marqueur | Signification |
| --- | --- |
| **Observé** | Comportement ou valeur affiché dans l'interface du compte avancé le 19 août 2026 |
| **Documenté** | Règle indiquée dans le règlement ou le tutoriel interne |
| **Déduit** | Formule reconstruite à partir de plusieurs valeurs affichées |
| **DinoPark** | Choix de conception propre à cette adaptation, non présenté comme une règle du jeu de référence |

Une règle contradictoire entre l'interface actuelle et une ancienne page de règles est conservée comme point ouvert ; l'interface actuelle est prioritaire pour reproduire le comportement visible.

### État de couverture des mécaniques fondamentales

| Mécanique | État après audit | Sections | Dernière incertitude |
| --- | --- | --- | --- |
| Individus, sexes, couples et reproduction | **Documenté** | 13 et 15 | Taux aléatoire exact d'une naissance |
| Personnel par enclos | **Documenté et vérifié** | 14.1 | Aucune sur les formules de PA |
| Nourriture et santé | **Documenté et vérifié** | 14.2 et 16.2 | Récupération naturelle éventuelle de santé |
| Enclos de luxe et dégâts | **Documenté** | 14.3 | Bonus chiffré exact de visiteurs d'un enclos luxe |
| Hôtel, train et boutiques | **Documenté et retenu** | 16.3.1 et 16.3.2 | Barème initial à valider |
| Bourse dynamique | **Documenté et vérifié** | 15.2 et 16.1.1 | Algorithme exact de génération du prochain cours |
| Météo | **Documenté et vérifié** | 15.2 et 16.4 | Pondération des tirages et coefficients biologiques exacts |
| Missions | **Documenté et adapté** | 16.5 | Équilibrage final des récompenses et des espèces vedettes |
| Classements et comparaison | **Documenté et vérifié** | 16.6 | Barème économique final des récompenses DinoPark |
| Potions et monnaie du site | **Documenté et adapté** | 16.8 et 16.9 | Prix de boutique à valider avant ouverture |

## 1. Vision

DinoPark est un jeu web privé de gestion d'un parc préhistorique. Le joueur construit des habitats, acquiert des dinosaures, affecte du personnel, entretient ses installations et fait progresser son parc au fil de mises à jour régulières.

Le jeu doit rester léger : rendu côté serveur, règles pilotées par les données et absence de dépendances d'infrastructure inutiles. La profondeur vient du nombre d'espèces, des interactions entre les règles et de la progression sur la durée.

Les habitats indiqués dans ce document sont des catégories de gameplay. Ils ne prétendent pas reconstituer exactement les paléoenvironnements de chaque genre.

## 2. Décisions confirmées

- Il n'existe pas d'île aux dinos séparée.
- Il n'existe pas de laboratoire, d'œufs ni de système d'incubation.
- Il n'existe pas de musée.
- Il n'existe pas d'explorateur, d'espionnage ni de rubrique « Top Secret ».
- Il n'existe pas d'équipe, de cagnotte collective, de tournoi inter-équipe ni de bagarre.
- Aucun paiement en argent réel n'est intégré : les anciennes offres payantes utilisent exclusivement la monnaie virtuelle déjà commune au site Django.
- Tous les dinosaures utilisent le même système d'habitats, d'individus, de personnel, de santé, de reproduction et de marché.
- Le jeu démarre avec plusieurs types d'habitats et un catalogue important d'espèces.
- Le parc contient quatre habitats principaux disposant chacun de plusieurs enclos constructibles.
- L'insectarium et le vivarium sont deux habitats spéciaux limités à un enclos unique chacun.
- Deux espèces partageant un habitat ne sont pas nécessairement compatibles dans le même enclos.
- Les espèces et leurs paramètres sont des données configurables, jamais des branches de code spécifiques.
- La rareté d'une espèce, la variante albinos et le mode d'obtention sont trois notions indépendantes.
- Les actions de gestion ont un effet immédiat ; les évolutions biologiques et économiques sont résolues pendant les mises à jour.
- Le nom définitif du jeu est **DiploPark**.
- La monnaie interne du parc est le **ParkCoin** ; la monnaie transversale existante reste le **Diplodocoin**.
- La persistance DiploPark utilise un fichier SQLite séparé `dinopark.db`. Les utilisateurs restent dans la base SQLite existante du site.
- Une visite quotidienne réelle entretient la fidélité, mais ne fait pas avancer le temps du parc. Les mises à jour de parc constituent un mécanisme distinct et volontaire.
- Il n'existe qu'une fenêtre de fidélité par jour civil, en `Europe/Paris`. Une journée manquée casse la série et ne se rattrape pas.
- Le VIP, les espèces VIP, les sponsors, la Botanica, les zones de spectacle, le compagnon et le parrainage sont supprimés.
- La V1 ne contient ni port, ni aires de repos, ni grande roue.
- Les tournois sont reportés après le lancement.
- La boutique en Diplodocoins est implémentée et visible, mais fermée au lancement.
- Le front repose sur les templates Django et du JavaScript natif, sans HTMX, React ni Vue.

## 3. Hors périmètre actuel

- Musée et collections d'objets.
- Île spéciale, laboratoire et incubation.
- Explorateur, expéditions, espionnage et vol d'animaux.
- Paiements en argent réel.
- Forum externe.
- Application mobile native.
- Moteur 3D ou carte librement déplaçable.

Ces exclusions ne suppriment pas les futures extensions, mais aucun modèle ou écran spécifique ne doit être créé pour elles à ce stade.

## 4. Boucle de jeu principale

1. Le joueur construit ou améliore un habitat.
2. Il achète, débloque ou accueille des espèces compatibles.
3. Il affecte le personnel requis et constitue des couples adultes.
4. Il achète les stocks nécessaires.
5. Une mise à jour résout revenus, dépenses, santé, âge, décès et naissances.
6. Les naissances peuvent produire un albinos ou déclencher une règle spéciale.
7. Des espèces peuvent apparaître spontanément dans les habitats éligibles.
8. Les événements alimentent les missions, le prestige et les notifications.
9. Le joueur réinvestit ses gains dans de nouveaux habitats et de nouvelles espèces.

## 5. Structure initiale du parc

La première version contient quatre habitats principaux et deux habitats spéciaux.

Un habitat principal est une famille d'enclos : plusieurs emplacements de la carte partagent le même type d'habitat, mais chaque emplacement devient un enclos indépendant. La proposition initiale est de six emplacements par habitat principal, soit 24 enclos possibles. Cette valeur reste configurable.

Un habitat spécial correspond à une construction unique et à un seul enclos. Toutes les espèces de son catalogue doivent donc pouvoir y cohabiter pour des raisons de gameplay.

| Code | Habitat | Structure | Orientation de gameplay | Espèces initiales |
| --- | --- | --- | --- | ---: |
| `plains` | Grandes plaines | 6 enclos | Troupeaux, grands herbivores et sauropodes | 18 |
| `forest` | Forêt primitive | 6 enclos | Petites espèces, dinosaures à plumes et prédateurs | 18 |
| `wetlands` | Marais et rivières | 6 enclos | Espèces semi-aquatiques et météo exigeante | 12 |
| `badlands` | Reliefs arides | 6 enclos | Déserts, hautes terres et espèces cuirassées | 24 |
| `insectarium` | Insectarium préhistorique | 1 enclos unique | Insectes fossiles et griffinflies | 10 |
| `vivarium` | Vivarium préhistorique | 1 enclos unique | Reptiles préhistoriques non dinosaures | 10 |

Total initial : **72 dinosaures et 20 espèces spéciales**, soit 92 entrées de catalogue.

### Écart d'échelle assumé

**Observé.** La carte actuelle du jeu de référence comporte 15 enclos de savane, 16 de forêt, 15 de terre/eau et 11 de bassin, soit 57 emplacements principaux. Sur le compte audité, chaque emplacement principal encore libre affiche un coût de construction de 107 500 unités, auquel s'ajoute le premier animal.

**DinoPark.** La première version reste volontairement limitée à six emplacements par habitat principal. Le schéma doit toutefois accepter un nombre configurable afin de pouvoir atteindre ultérieurement une échelle comparable sans migration de données.

## 6. Rareté

La rareté est une catégorie de présentation et un ensemble de valeurs par défaut. Les paramètres finaux restent définis par espèce.

| Code | Libellé | Disponibilité indicative | Rôle |
| --- | --- | --- | --- |
| `common` | Commune | Permanente | Base du parc et reproduction fréquente |
| `uncommon` | Peu commune | Permanente après déblocage | Progression intermédiaire |
| `rare` | Rare | Marché moins fréquent ou condition de prestige | Objectif de moyen terme |
| `exceptional` | Exceptionnelle | Fenêtres temporaires et prix élevé | Objectif de long terme |
| `secret` | Secrète | Apparition, naissance ou mission spéciale | Découverte et collection |

La rareté peut fournir des valeurs par défaut pour le prix, le prestige et la fréquence de marché, mais elle ne doit pas imposer une formule universelle. Deux espèces rares peuvent avoir des fertilités et des prix très différents.

**Observation de référence.** Hors extension ignorée, l'interface ne présente pas une étiquette de rareté universelle. La rareté ressentie provient de la combinaison du prix, du mode de déblocage et de la disponibilité : achat permanent, rang de prestige, fidélité, mission, stock de récompense, jour particulier ou rotation temporaire. La table ci-dessus est donc une couche de présentation propre à DinoPark ; les règles d'accès demeurent la source fonctionnelle de vérité.

## 7. Catalogue initial des espèces

### 7.1 Grandes plaines

| Espèce | Rareté | Obtention initiale | Albinos |
| --- | --- | --- | --- |
| Gallimimus | Commune | Marché permanent | Non |
| Dryosaurus | Commune | Marché permanent | Non |
| Camptosaurus | Commune | Marché permanent | Oui |
| Edmontosaurus | Commune | Marché permanent | Non |
| Struthiomimus | Commune | Marché permanent | Non |
| Parasaurolophus | Peu commune | Marché après déblocage | Oui |
| Maiasaura | Peu commune | Marché après déblocage | Non |
| Corythosaurus | Peu commune | Marché après déblocage | Non |
| Triceratops | Rare | Marché rare | Oui |
| Styracosaurus | Rare | Marché rare | Non |
| Shantungosaurus | Exceptionnelle | Marché temporaire | Oui |
| Einiosaurus | Secrète | Apparition spontanée | Non |
| Camarasaurus | Commune | Marché permanent | Non |
| Diplodocus | Commune | Marché permanent | Oui |
| Apatosaurus | Peu commune | Marché après déblocage | Non |
| Giraffatitan | Peu commune | Marché après déblocage | Non |
| Argentinosaurus | Rare | Marché rare | Non |
| Patagotitan | Secrète | Mission et naissance conditionnelle | Non |

### 7.2 Forêt primitive

| Espèce | Rareté | Obtention initiale | Albinos |
| --- | --- | --- | --- |
| Compsognathus | Commune | Marché permanent | Non |
| Hypsilophodon | Commune | Marché permanent | Non |
| Sinosauropteryx | Commune | Marché permanent | Non |
| Scutellosaurus | Commune | Marché permanent | Non |
| Lesothosaurus | Commune | Marché permanent | Non |
| Iguanodon | Peu commune | Marché après déblocage | Oui |
| Caudipteryx | Peu commune | Marché après déblocage | Non |
| Microraptor | Peu commune | Marché après déblocage | Oui |
| Deinonychus | Rare | Marché rare | Oui |
| Dilophosaurus | Rare | Marché rare | Oui |
| Therizinosaurus | Exceptionnelle | Marché temporaire | Non |
| Pyroraptor | Secrète | Naissance conditionnelle | Oui |
| Allosaurus | Commune | Marché permanent | Oui |
| Carnotaurus | Peu commune | Marché après déblocage | Oui |
| Acrocanthosaurus | Peu commune | Marché après déblocage | Non |
| Carcharodontosaurus | Rare | Marché rare | Non |
| Giganotosaurus | Exceptionnelle | Marché temporaire | Oui |
| Tyrannosaurus | Secrète | Mission et marché événementiel | Oui |

### 7.3 Marais et rivières

| Espèce | Rareté | Obtention initiale | Albinos |
| --- | --- | --- | --- |
| Ouranosaurus | Commune | Marché permanent | Non |
| Lurdusaurus | Commune | Marché permanent | Non |
| Nigersaurus | Commune | Marché permanent | Non |
| Tenontosaurus | Commune | Marché permanent | Non |
| Muttaburrasaurus | Commune | Marché permanent | Non |
| Saurolophus | Peu commune | Marché après déblocage | Non |
| Baryonyx | Peu commune | Marché après déblocage | Oui |
| Suchomimus | Peu commune | Marché après déblocage | Oui |
| Deinocheirus | Rare | Marché rare | Non |
| Irritator | Rare | Marché rare | Non |
| Spinosaurus | Exceptionnelle | Marché temporaire | Oui |
| Pelecanimimus | Secrète | Apparition spontanée | Non |

### 7.4 Reliefs arides

| Espèce | Rareté | Obtention initiale | Albinos |
| --- | --- | --- | --- |
| Protoceratops | Commune | Marché permanent | Oui |
| Archaeoceratops | Commune | Marché permanent | Non |
| Oviraptor | Commune | Marché permanent | Non |
| Mononykus | Commune | Marché permanent | Non |
| Shuvuuia | Commune | Marché permanent | Non |
| Citipati | Peu commune | Marché après déblocage | Non |
| Pinacosaurus | Peu commune | Marché après déblocage | Non |
| Saichania | Peu commune | Marché après déblocage | Oui |
| Velociraptor | Rare | Marché rare | Oui |
| Tarchia | Rare | Marché rare | Non |
| Tarbosaurus | Exceptionnelle | Marché temporaire | Oui |
| Gigantoraptor | Secrète | Naissance conditionnelle | Non |
| Stegosaurus | Commune | Marché permanent | Oui |
| Chungkingosaurus | Commune | Marché permanent | Non |
| Tuojiangosaurus | Commune | Marché permanent | Non |
| Scelidosaurus | Commune | Marché permanent | Non |
| Edmontonia | Commune | Marché permanent | Non |
| Euoplocephalus | Peu commune | Marché après déblocage | Oui |
| Gastonia | Peu commune | Marché après déblocage | Non |
| Pachycephalosaurus | Peu commune | Marché après déblocage | Non |
| Ankylosaurus | Rare | Marché rare | Oui |
| Amargasaurus | Rare | Marché rare | Non |
| Cryolophosaurus | Exceptionnelle | Marché temporaire | Oui |
| Yutyrannus | Secrète | Apparition par temps froid | Oui |

### 7.5 Insectarium préhistorique

| Espèce | Rareté | Obtention initiale | Albinos |
| --- | --- | --- | --- |
| Kalligramma | Commune | Marché permanent | Non |
| Juracimbrophlebia | Commune | Marché permanent | Non |
| Pseudopulex | Commune | Marché permanent | Non |
| Arctotypus | Commune | Marché permanent | Non |
| Meganeurites | Peu commune | Marché après déblocage | Non |
| Titanomyrma | Peu commune | Marché après déblocage | Non |
| Bojophlebia | Peu commune | Marché après déblocage | Non |
| Meganeura | Rare | Marché rare | Non |
| Mazothairos | Rare | Apparition spontanée | Non |
| Meganeuropsis | Exceptionnelle | Mission ou événement | Non |

L'insectarium utilise le mot « insectes » au sens de collection de gameplay. Les fiches devront préciser le groupe taxonomique exact et éviter de présenter les autres arthropodes comme des insectes si le catalogue est étendu plus tard.

### 7.6 Vivarium préhistorique

| Espèce | Rareté | Obtention initiale | Albinos |
| --- | --- | --- | --- |
| Gobiderma | Commune | Marché permanent | Oui |
| Agriodontosaurus | Commune | Marché permanent | Non |
| Coelurosauravus | Commune | Marché permanent | Non |
| Longisquama | Commune | Marché permanent | Non |
| Proterosuchus | Peu commune | Marché après déblocage | Non |
| Euparkeria | Peu commune | Marché après déblocage | Oui |
| Tanystropheus | Peu commune | Marché après déblocage | Non |
| Scutosaurus | Rare | Marché rare | Non |
| Postosuchus | Rare | Marché rare | Oui |
| Redondasaurus | Exceptionnelle | Mission ou événement | Non |

Le vivarium regroupe des reptiles et des archosaures non dinosaures. Les grands reptiles marins ne sont pas inclus, car un enclos de vivarium unique ne serait pas cohérent avec leur gabarit.

### 7.7 Règles du catalogue

- Les noms représentent actuellement des genres afin de garder des libellés lisibles.
- La répartition par habitat est thématique et peut être ajustée pour le gameplay.
- Une espèce peut changer de rareté sans migration technique.
- Le catalogue doit pouvoir être importé depuis une fixture JSON ou YAML.
- L'ajout d'une espèce ne doit nécessiter aucune migration Django tant que le schéma de données ne change pas.
- Les espèces de l'insectarium sont toutes compatibles entre elles dans la première version.
- Les espèces du vivarium sont toutes compatibles entre elles dans la première version.
- Les valeurs économiques, gabarits, longévités et taux de reproduction seront ajoutés dans une version ultérieure du livret.

Sources de nomenclature consultées : répertoire du Natural History Museum, notamment les index [A](https://www.nhm.ac.uk/discover/dino-directory/name/a/gallery.html), [C](https://www.nhm.ac.uk/discover/dino-directory/name/c/gallery.html), [D](https://www.nhm.ac.uk/discover/dino-directory/name/d/gallery.html), [P](https://www.nhm.ac.uk/discover/dino-directory/name/p/gallery.html) et [S](https://www.nhm.ac.uk/discover/dino-directory/name/s/gallery.html), son article sur les [griffinflies](https://www.nhm.ac.uk/discover/giant-dragonflies.html), sa présentation des [reptiles qui ne sont pas des dinosaures](https://www.nhm.ac.uk/discover/what-are-dinosaurs.html) et sa fiche sur [Agriodontosaurus](https://www.nhm.ac.uk/discover/news/2025/september/newly-found-fossils-lizard-like-animal-oldest-ever-discovered.html). Le vivarium s'appuie aussi sur les fiches de l'American Museum of Natural History consacrées à [Gobiderma](https://www.amnh.org/explore/ology/ology-cards/039-gobiderma-pulchrum) et [Redondasaurus](https://www.amnh.org/explore/ology/ology-cards/267-redondasaurus).

## 8. Compatibilité des espèces

Partager un type d'habitat autorise une espèce à être placée dans l'un de ses enclos, mais ne garantit pas sa compatibilité avec les espèces déjà présentes.

Une tentative d'achat, de déplacement ou d'accueil doit être refusée si l'une des conditions suivantes n'est pas satisfaite :

1. l'espèce accepte le type d'habitat de l'enclos ;
2. la capacité restante couvre le gabarit de l'individu ;
3. les familles de compatibilité peuvent cohabiter ;
4. aucune interdiction propre aux deux espèces n'existe ;
5. les contraintes particulières de l'espèce sont respectées.

### 8.1 Groupes de compatibilité

**Observé.** Le jeu de référence emploie un mécanisme très léger :

- une espèce marquée « groupe : oui » peut rejoindre les autres espèces groupables du même habitat ;
- une espèce marquée « groupe : non » ne voit à l'achat qu'une petite famille autorisée ; par exemple, deux variantes de panthère peuvent cohabiter et plusieurs types de loups partagent un enclos ;
- le premier animal choisi lors de la construction fixe donc la famille de compatibilité de l'enclos ;
- une apparition spontanée peut s'ajouter hors de la liste d'achat normale ; un écureuil a ainsi été observé dans un enclos de panthères.

**DinoPark.** Pour rester léger, la première implémentation utilisera trois champs configurables :

```text
Species.is_groupable
Species.compatibility_family
Species.compatibility_exceptions
```

Les espèces groupables d'un même habitat sont compatibles par défaut. Les espèces non groupables exigent la même `compatibility_family`, sauf exception explicite. Une matrice de groupes plus complexe ne sera ajoutée que si le catalogue réel la rend nécessaire.

### 8.2 Exceptions par espèce

Exemples provisoires :

- Tyrannosaurus et Giganotosaurus sont incompatibles avec toutes les autres espèces et occupent chacun un enclos dédié ;
- Triceratops et Styracosaurus peuvent cohabiter ;
- Diplodocus et Apatosaurus peuvent cohabiter si la capacité de l'enclos le permet ;
- Velociraptor ne peut pas être placé avec Protoceratops ;
- Baryonyx et Suchomimus peuvent cohabiter dans un grand enclos de marais ;
- toutes les entrées de l'insectarium sont compatibles entre elles ;
- toutes les entrées du vivarium sont compatibles entre elles dans la première version.

### 8.3 Représentation technique

Le système recommandé combine :

```text
Species.is_groupable
Species.compatibility_family
SpeciesCompatibilityOverride(species_a, species_b, allowed, reason)
```

La paire d'espèces d'une exception est non ordonnée : une seule ligne représente la relation dans les deux sens. L'interface d'achat ne montre que les espèces compatibles avec l'enclos sélectionné, comme dans le jeu de référence.

## 9. Modes d'obtention

Le mode d'obtention est indépendant de la rareté.

| Code | Description |
| --- | --- |
| `market_permanent` | Espèce disponible en permanence après son déblocage |
| `market_rotation` | Espèce proposée pendant une fenêtre limitée |
| `spontaneous` | Individu rencontré aléatoirement dans un habitat éligible |
| `conditional_birth` | Individu ou déblocage obtenu à la suite d'une naissance spéciale |
| `mission_reward` | Espèce débloquée par une mission |
| `event_reward` | Espèce attribuée par un événement temporaire |
| `prestige_tier` | Espèce achetable à partir d'un rang de prestige |
| `fidelity_streak` | Espèce débloquée après une série de fenêtres de connexion réussies |
| `reward_stock` | Achat autorisé uniquement en consommant un stock propre à l'espèce |
| `calendar_window` | Espèce achetable pendant une fenêtre calendaire déterminée |

Une espèce secrète peut devenir achetable après sa première découverte. Ce comportement sera configurable par espèce.

**Observé.** Les espèces à stock affichent une réserve propre, plafonnée à 10. Certaines rotations exceptionnelles commencent le 1er et le 15 du mois et rendent une espèce achetable pendant sept jours. Les rangs de prestige ouvrent également des espèces à 35 %, 50 %, 65 % et 80 %, tandis que la fidélité en ouvre après 10, 20, 35, 50 et 60 mises à jour classiques consécutives.

## 10. Variantes albinos

L'albinisme est une variante d'individu. Il ne doit pas être représenté par une seconde espèce en base de données.

Un animal albinos :

- conserve l'habitat et le gabarit de son espèce ;
- possède une apparence distincte ;
- peut avoir une valeur marchande et un prestige supérieurs ;
- peut compter séparément dans certaines missions ;
- peut transmettre un bonus de probabilité à sa descendance si cette règle est activée.

**Observé.** Dans le jeu de référence, une naissance issue de parents normaux appartenant à une espèce éligible a 12,5 % de chances de produire la variante albinos. **DiploPark retient un taux différent** : 5 % avec deux parents normaux, 20 % avec exactement un parent albinos et 50 % avec deux parents albinos. Une potion temporaire porte la chance finale à 70 % pour la prochaine mise à jour. Les albinos possèdent un prix de base et un cours distincts et comptent comme une entrée séparée dans certaines missions.

Paramètres prévus par espèce :

```text
albino_enabled
albino_base_rate
albino_parent_bonus
albino_value_multiplier
albino_prestige_bonus
albino_asset_key
```

Valeurs de compatibilité retenues pour le premier équilibrage :

```text
albino_base_rate = 0.05
albino_one_parent_rate = 0.20
albino_two_parents_rate = 0.50
albino_boosted_rate = 0.70
albino_boost_duration_ticks = 1
```

**DiploPark.** L'albinos reste une variante d'individu en base. Chaque espèce possède une variante `normal`; les espèces éligibles possèdent aussi `albino`, avec prix, cours, illustration et compteurs de mission distincts. Les trois taux ci-dessus constituent la règle officielle DiploPark.

## 11. Apparitions spontanées

Une apparition spontanée est évaluée pendant une mise à jour, après les naissances normales.

Conditions génériques possibles :

- habitat construit et en bon état ;
- place disponible ;
- aucun déficit de personnel ;
- santé minimale ;
- météo compatible ;
- prestige minimal ;
- espèce pas encore découverte ou stock maximal non atteint.

Règles initiales proposées :

| Espèce | Conditions provisoires |
| --- | --- |
| Einiosaurus | Grandes plaines, santé ≥ 80 %, au moins trois espèces différentes |
| Pelecanimimus | Marais, pluie ou temps couvert, stocks suffisants |
| Yutyrannus | Hautes terres, neige ou événement de froid |

Chaque enclos éligible effectue son propre tirage à chaque mise à jour : 0,5 % initialement, sans hausse pendant les 20 premiers échecs, puis +0,05 point de pourcentage par échec. Le compteur anti-malchance est unique au parc et s'incrémente après chaque tirage d'enclos éligible échoué, dans l'ordre stable des enclos. Le 50e tirage éligible consécutif sans succès est garanti et tout succès remet le compteur du parc à zéro. Une apparition au maximum peut survenir dans un même enclos pendant une mise à jour, mais plusieurs enclos peuvent réussir lors du même cycle ; après un succès, les enclos suivants repartent du taux initial.

**Observé.** Le compte audité contient plusieurs espèces bonus absentes de la liste d'achat normale dans les enclos concernés. L'écureuil peut notamment apparaître dans plusieurs enclos de forêt, y compris un enclos non groupable. Une mission décrit aussi une « migration » de taupes se terminant à un moment déterminé. La présence de suricates, rainettes et étoiles de mer dans plusieurs habitats confirme le besoin d'un canal d'arrivée distinct, mais leur déclencheur exact n'est pas encore établi.

Les apparitions doivent donc accepter les modes suivants :

- tirage à chaque mise à jour ;
- vague ou migration sur une fenêtre calendaire ;
- apparition dans chaque enclos admissible plutôt qu'une seule fois dans le parc ;
- capture limitée dans le temps ;
- ajout malgré une famille de compatibilité fermée, lorsque la règle le prévoit.

Le compteur anti-malchance est un choix **DiploPark** destiné à éviter des séries trop frustrantes ; il n'a pas été observé dans la référence.

## 12. Naissances conditionnelles

Une naissance spéciale ne doit pas être codée directement dans le modèle `Species`. Elle est évaluée par une règle nommée recevant un contexte de mise à jour.

Le contexte peut contenir :

- espèces et parents concernés ;
- nombre de couples adultes ;
- santé de l'enclos et du parc ;
- météo actuelle et précédente ;
- niveau de l'habitat ;
- nombre de naissances simultanées ;
- présence d'autres espèces ;
- missions actives ;
- séries de connexions ou de mises à jour ;
- variantes des parents.

Résultats possibles :

- création d'un nouveau-né normal ;
- création d'un albinos ;
- apparition d'une espèce différente ;
- déblocage permanent d'une espèce ;
- récompense économique ;
- message ou événement temporaire.

Premières règles candidates :

| Identifiant | Condition provisoire | Résultat |
| --- | --- | --- |
| `pyroraptor_after_storm` | Naissance de Deinonychus dans la mise à jour suivant un orage | Déblocage ou naissance d'un Pyroraptor |
| `gigantoraptor_large_brood` | Au moins quatre naissances d'Oviraptor dans une même mise à jour | Déblocage du Gigantoraptor |
| `patagotitan_giant_lineage` | Naissances simultanées de Diplodocus et d'Argentinosaurus avec une santé parfaite | Déblocage du Patagotitan |

Ces règles sont volontairement configurées comme des objectifs de jeu, pas comme des affirmations paléontologiques.

### 12.1 Familles de conditions à supporter

**Observé.** Les missions avancées combinent les mêmes briques de règles de nombreuses façons. Le moteur DinoPark doit pouvoir exprimer sans code spécifique :

- une ou plusieurs espèces nées pendant la même mise à jour ;
- un nombre exact ou minimal de nouveau-nés et des portées doubles, triples ou quintuples ;
- un couple de nouveau-nés de sexes opposés ;
- une naissance dans chacun des enclos d'un habitat ;
- une naissance sous une météo donnée ou pendant la mise à jour suivant cette météo ;
- une naissance pendant plusieurs mises à jour consécutives ;
- un total cumulé pendant une mission, un jour, une semaine ou un mois ;
- la naissance d'une espèce normale et de sa variante albinos pendant la même mise à jour ;
- une chaîne de déblocages où l'espèce A ouvre B, puis les naissances de B ouvrent C ;
- une condition de décès naturel ou de prédation ;
- une règle temporaire modifiant la simulation pendant que la mission est active ;
- une collection presque complète, avec récompense dégressive selon le nombre de manquants.

Les règles doivent recevoir les événements de la mise à jour et non relire uniquement l'état final : sans journal d'événements, il est impossible de prouver la simultanéité, l'ordre des météos, le sexe des naissances ou la cause d'un décès.

## 13. Individus et reproduction

Chaque animal préhistorique est initialement enregistré individuellement.

Champs fonctionnels prévus :

```text
species
enclosure
sex
variant
born_at_tick
acquired_at_tick
age_ticks
remaining_life
health
is_adult
is_alive
origin
```

Principes retenus :

- un mâle adulte et une femelle adulte compatibles forment un couple reproducteur ;
- un individu devient adulte après 5 mises à jour ;
- la longévité de référence DiploPark est de 50 unités ; l'âge augmente et la longévité restante diminue d'une unité par mise à jour ;
- la reproduction exige une santé moyenne calculée du parc strictement supérieure à 25 % ;
- un couple formé dès la maturité produit en moyenne 4 descendants communs, 3,5 peu communs, 3 rares, 2,5 exceptionnels ou 2 secrets pendant ses 45 mises à jour reproductives ;
- à partir du seizième couple adulte d'une même espèce dans un enclos, la probabilité marginale de naissance diminue légèrement ;
- la santé et le personnel influencent la reproduction ;
- les naissances produisent un sexe aléatoire ;
- le tirage albinos intervient après la validation d'une naissance normale : 5 % avec deux parents normaux, 20 % avec exactement un parent albinos et 50 % avec deux parents albinos ;
- les pénalités de nourriture et de personnel sont appliquées avant la reproduction et peuvent donc la bloquer en faisant tomber la santé globale à 25 % ou moins.

**Observé sur MonZoo et adapté.** L'achat de référence est limité à 10 animaux par jour. DiploPark conserve la formule proportionnelle mais remplace le dénominateur 100 par la longévité configurée de l'espèce :

```text
prix_revente = round(cours_actuel × 0,60 × remaining_life / lifespan_ticks)
```

Un jeune affichant 95 de longévité restante et coté 71 905 est proposé à 40 986, soit 57 % du cours. Un adulte affichant 40 et coté 17 099 est proposé à 4 104, soit 24 %. La page de vente individuelle demande une confirmation, tandis que la vente de masse accepte plusieurs identifiants d'individus.

Une potion d'équilibre active pendant trois mises à jour choisit en priorité le sexe sous-représenté dans l'espèce concernée. Exemple fonctionnel : si un enclos compte davantage de mâles que de femelles, le prochain bébé de cette espèce devient une femelle.

### 13.1 Représentation dans l'interface et calcul des couples

**Observé.** Chaque individu possède sa propre entrée et affiche au minimum : espèce, sexe, stade bébé ou adulte, longévité restante, variante éventuelle et action de vente. L'intendance agrège ensuite ces individus par espèce et par enclos avec les compteurs suivants :

- mâles et femelles ;
- adultes et bébés ;
- animaux mourants ;
- couples en âge de se reproduire ;
- valeur du cheptel au cours actuel.

Un couple n'est pas une relation persistante entre deux identifiants d'animaux. Pour une espèce donnée dans un enclos, il est recalculé par :

```text
couples_reproducteurs = min(males_adultes, femelles_adultes)
```

Cette formule est confirmée par plusieurs troupeaux. Un enclos de six rhinocéros affiche trois mâles, trois femelles, mais seulement deux couples : l'un des six individus possède encore 99 unités de longévité et porte l'icône bébé. À l'inverse, un troupeau de neuf mâles et sept femelles affiche sept couples lorsque le jeune observé appartient au sexe excédentaire.

**Décidé.** Un individu devient adulte après cinq mises à jour suivant son achat ou sa naissance. La reproduction est automatique pendant une mise à jour si l'enclos contient au moins un mâle adulte et une femelle adulte de la même espèce et si la santé globale du parc dépasse strictement 25 %. Pour 45 occasions reproductives, les probabilités initiales par couple et par mise à jour sont : commune 8,89 %, peu commune 7,78 %, rare 6,67 %, exceptionnelle 5,56 %, secrète 4,44 %. Elles correspondent respectivement aux espérances 4, 3,5, 3, 2,5 et 2 descendants. À partir du seizième couple adulte d'une même espèce dans le même enclos, chaque couple excédentaire fonctionne à 50 % de son taux normal. Les fixtures stockent ces taux en points de base ; la simulation de 2 000 parcours peut les ajuster pour compenser les décès anticipés et les couples formés tardivement tout en conservant les espérances cibles.

Chaque espèce possède une variante `normal` obligatoire et une variante `albino` lorsqu'elle y est éligible. La santé est persistée sur chaque individu entre 0 et 100. Les valeurs d'enclos et de parc sont des moyennes calculées, jamais des soldes indépendants. Il n'existe aucune guérison passive.

Les animaux morts sont conservés avec leur filiation, leur âge, `died_at_tick` et `death_cause`; ils quittent leur enclos. Une commande administrative de purge, désactivée par défaut, pourra anonymiser ou supprimer les anciens détails après agrégation des compteurs de mission.

## 14. Personnel

Les cinq catégories initiales sont :

- animalier ;
- vétérinaire ;
- technicien ;
- gardien ;
- paysagiste.

Les besoins sont calculés à partir du nombre d'animaux, de leurs gabarits et du niveau de l'enclos. Le premier équilibrage reprend le barème observé ci-dessous.

### 14.1 Barème compatible avec la référence

Pour un enclos donné, avec `N` animaux et `G` égal à la somme de leurs gabarits :

| Métier DinoPark | Équivalent observé | Points requis | Salaire par point et par mise à jour |
| --- | --- | ---: | ---: |
| Animalier | Employé simple | `N + G` | 5 |
| Vétérinaire | Soigneur | `2 × N` | 7 |
| Technicien | Réparateur | `3 + G` | 7 |
| Gardien | Gardien | `4 + N` | 10 |
| Paysagiste | Paysagiste | `20` pour un enclos de luxe | 20 |

**Vérification observée.** Un enclos de 24 animaux totalisant 50 points de gabarit demande respectivement 74, 48, 53, 28 et 20 points, ce qui correspond exactement aux formules ci-dessus.

Une seconde vérification porte sur un enclos de six rhinocéros de gabarit 4, soit `N = 6` et `G = 24`. L'écran demande exactement 30 animaliers, 12 vétérinaires, 27 techniciens, 10 gardiens et 20 paysagistes. Les cinq formules sont donc confirmées sur deux compositions différentes.

Les PA sont affectés en nombre entier, métier par métier et enclos par enclos, avec des commandes `+` et `−`. L'écran compare en permanence PA affectés et PA requis ; une valeur insuffisante devient rouge et l'enclos reçoit un avertissement global. Les salaires sont additionnés au niveau du parc et prélevés à chaque mise à jour.

### 14.2 Sous-effectif, nourriture et santé

**Documenté.** Si au moins une catégorie de personnel est sous le besoin calculé, l'enclos est considéré comme mal géré. Lors de la mise à jour, les animaux de cet enclos perdent **10 % de santé**. La pénalité est attachée à l'enclos mal géré, et non multipliée par chaque métier déficitaire ou chaque PA manquant.

La nourriture est consommée automatiquement avant l'évolution biologique :

```text
consommation_animale_par_mise_a_jour = somme(gabarit de chaque individu vivant)
```

L'écran des stocks confirme 1 584 unités consommées pour 1 027 animaux, ce qui exclut une consommation uniforme d'une unité par animal. Si le stock disponible ne couvre pas la consommation, les animaux perdent **20 % de santé**. Le règlement ne précise pas une consommation partielle par ordre d'enclos : DinoPark effectuera un contrôle global et appliquera la pénalité de façon déterministe à tous les individus concernés.

Les pénalités de nourriture et de sous-effectif sont deux causes indépendantes du même cycle. DiploPark les cumule, avec bornage de la santé entre 0 et 100. La reproduction est interdite lorsque la moyenne de santé du parc est inférieure ou égale à 25 %. La potion de soin remet toutes les santés individuelles au maximum ; il n'existe aucune guérison passive.

### 14.3 Enclos de luxe, dégradation et réparation

**Documenté.** Le passage d'un enclos standard à un enclos de luxe exige simultanément :

1. 20 PA de paysagiste déjà affectés à cet enclos ;
2. un paiement de 20 000 unités ;
3. l'activation de l'amélioration depuis la fiche de l'enclos.

L'amélioration modifie l'apparence sur la carte, ajoute du prestige et augmente de **5 %** les visiteurs attribuables à cet enclos. Les 20 PA de paysagiste ne constituent pas un coût ponctuel : ils doivent rester affectés. Si leur nombre passe sous 20, l'enclos redevient standard et perd immédiatement ce bonus.

Un manque de PA est signalé immédiatement par `/!\` dans la liste des enclos et par des valeurs rouges dans la fiche. Le règlement associe le sous-effectif à deux conséquences lors de la mise à jour : perte de santé des animaux et possibilité d'un enclos endommagé. Un enclos endommagé est matérialisé par une icône de réparation clignotante.

**Observé.** L'enclos Savane n° 2 reste affiché `Luxe` et `État : Ok` alors qu'il manque des PA dans quatre métiers, avec 25/30 animaliers, 10/12 vétérinaires, 23/27 techniciens et 9/10 gardiens. Ses 20/20 paysagistes sont cependant maintenus. Cela confirme que l'avertissement de sous-effectif est immédiat, tandis que les dégâts sont résolus pendant une mise à jour, et que le maintien du luxe dépend spécifiquement des paysagistes.

La réparation n'est pas un achat séparé : le joueur remet tous les PA au niveau requis, puis attend la prochaine mise à jour nocturne. L'avertissement de dommage disparaît à cette échéance. Il faut donc séparer dans le modèle :

- `quality_level`, standard ou luxe ;
- `is_damaged`, état d'entretien ;
- `staff_required` et `staff_assigned` par métier ;
- `staffing_restored_at`, pour différer la réparation visuelle jusqu'au traitement nocturne.

## 15. Fidélité quotidienne et mises à jour du parc

La visite réelle quotidienne et les mises à jour qui font avancer le parc sont deux mécanismes distincts.

### 15.1 Visite quotidienne et fidélité

La première visite de n'importe quelle page DiploPark pendant un jour civil `Europe/Paris` enregistre une présence quotidienne. Elle ne fait pas avancer le parc et ne lance aucun calcul économique ou biologique. Une seule présence est comptée par jour. Une journée absente est définitivement manquée, ne se rattrape pas et remet la fidélité à zéro.

Les mises à jour du parc sont déclenchées volontairement et font avancer d'une unité l'âge, la biologie, les stocks et l'économie du zoo. Leur mécanisme d'attribution est distinct de la fidélité. Les mises à jour bonus consomment une réserve et certaines missions peuvent les exclure.

Le paquet de départ validé contient 400 000 ParkCoins, 15 mises à jour bonus, aucun enclos, animal ou personnel offert, un billet à 5 et 5 visiteurs de base. Terminer le tutoriel accorde 5 mises à jour bonus supplémentaires. Les dégâts sont neutralisés pendant les 10 premières mises à jour du parc. Une aide débutant est versée pendant les 50 premières mises à jour selon une suite arithmétique candidate `100 000 - 2 000 × index`, soit 100 000 au premier cycle et 2 000 au cinquantième. Cette courbe est un paramètre de calibration : la simulation de 2 000 parcours doit la comparer à des pentes voisines et retenir celle qui respecte au mieux les jalons 5/30/200/500 sans modifier le capital initial validé.

Une contrainte unique `(park_id, visit_date)` protège la présence quotidienne. Une contrainte unique `(park_id, update_key)` protège chaque mise à jour de parc.

Ordre prévu :

1. verrouillage du parc et contrôle d'idempotence ;
2. revenus et dépenses ;
3. consommation des stocks ;
4. pénalités de santé ;
5. vieillissement et décès ;
6. reproduction normale ;
7. tirage des variantes albinos ;
8. règles de naissance conditionnelle ;
9. apparitions spontanées ;
10. progression des missions ;
11. prestige, visiteurs et classements ;
12. écritures comptables et notifications.

Chaque exécution produit un rapport regroupé par enclos : naissances, décès, valeur boursière totale des naissances, missions validées et événements exceptionnels. Les actions d'achat ou d'affectation de personnel restent immédiates ; seules les évolutions biologiques, économiques et de mission passent par ce service.

### 15.2 Horloges globales : bourse et météo

La bourse et la météo ne sont pas recalculées par parc. Ce sont deux états globaux, identiques pour tous les joueurs, que chaque mise à jour de parc consulte en lecture seule.

- **Bourse — Décidé.** Tous les cours sont renouvelés lors de chaque distribution globale de mises à jour, soit deux fois par jour. Le créneau de demi-journée sert de clé d'idempotence. Une commande cron crée une seule série de cours par distribution ; un garde-fou paresseux `ensure_market_slot()` la crée au premier accès si le cron a été manqué.
- **Météo — Observé et déduit.** La carte annonce aujourd'hui, demain et après-demain : le tirage est donc journalier et global, avec un horizon roulant de trois dates. Une commande quotidienne prolonge cet horizon sans modifier une prévision déjà publiée.
- Une mise à jour ordinaire ou bonus charge le `MarketSnapshot` actif et le `WeatherDay` de sa date effective. Elle ne relance aucun tirage global.
- Pour lever l'ambiguïté de minuit, DiploPark fige `effective_date` au début de la transaction.
- Les anciennes météos et les anciens cours sont conservés. Ils permettent l'audit des rapports, le calcul reproductible des récompenses et les missions portant sur la météo précédente ou une succession de jours.

## 16. Systèmes transversaux observés

### 16.1 Recettes du parc

Le bilan affiché est une projection de la prochaine mise à jour. Les salaires sont présentés séparément et doivent être retranchés du total brut.

- Prix de billet autorisés : 5, 10, 20, 40 ou 80 unités.
- Le prix ne peut être changé qu'une fois par jour.
- Doubler le prix divise approximativement le nombre de visiteurs par deux ; le changement devient utile lorsque le parc atteint le plafond de 3 500 visiteurs ordinaires.
- Recette des entrées : `visitors × ticket_price`.
- Bonus de prestige : `800 × prestige_percent`. Le compte observé affiche bien `800 × 59,28 = 47 424`.
- La fidélité économique ajoute 1 % par jour réel consécutif visité, jusqu'à 10 %. Elle exclut les boutiques et retombe à zéro après une journée manquée.

Bonus brut lié au nombre total d'animaux, observé dans le règlement :

```text
500: 15 000      1 000: 30 000    1 500: 45 000    2 000: 60 000
2 500: 75 000    3 000: 90 000    3 500: 110 000   4 000: 130 000
4 500: 150 000   5 000: 170 000   5 500: 190 000   6 000: 210 000
6 500: 235 000   7 000: 250 000   7 500: 275 000   8 000: 300 000
8 500: 325 000   9 000: 350 000   9 500: 375 000  10 000: 400 000
```

Un bonus supplémentaire de 2 000 unités est accordé pour chaque espèce dont le prix initial atteint 150 000 unités et dont le parc possède au moins 10 individus.

Les sponsors sont supprimés de DiploPark : aucun modèle, écran ou revenu ne leur est consacré.

Le plafond monétaire courant est fixé à **100 000 000** par la banque active, qui précise que tout surplus est supprimé lors de la mise à jour suivante. La mention de 50 000 000 dans le règlement général est traitée comme une documentation ancienne. DinoPark retient 100 000 000 comme valeur compatible avec l'état actuel du jeu, dans un paramètre configurable.

### 16.1.1 Marché et revente

**Documenté et adapté.** Le marché présente pour chaque variante achetable un prix de base, un cours actuel et une tendance. Un albinos ne peut jamais être acheté : il n'a donc aucune offre d'achat sur le marché. La réévaluation mondiale intervient à chaque distribution de mises à jour, deux fois par jour.

**Observé et déduit.** La tendance compare le cours actuel au prix de base, et non au cours précédent :

```text
tendance_pct = round(100 × (cours_actuel - prix_base) / prix_base)
```

L'arrondi à l'entier le plus proche concorde notamment avec la Rosalie des Alpes (`315 000 → 483 024`, soit `+53 %`) et l'Axolotl (`72 000 → 36 844`, soit `−49 %`). L'écran met en avant les trois plus fortes hausses et les trois plus fortes baisses. Lors du relevé, les extrêmes visibles allaient de `+53 %` à `−49 %` ; cela ne prouve pas que ces valeurs constituent les bornes du générateur.

Le même cours autoritaire est utilisé par :

- la bourse et ses classements de hausses/baisses ;
- le prix d'achat d'un individu ;
- la valeur du cheptel dans l'intendance et les classements ;
- la valeur affichée dans les rapports de naissance ;
- le calcul de revente et les récompenses de mission indexées sur la bourse ;
- les tranches de points du classement mensuel lorsqu'elles sont évaluées au moment de la naissance.

Une transaction d'achat ou de vente doit relire et verrouiller le cours actif au moment de la confirmation. Le prix montré sur une page antérieure n'est qu'une prévisualisation : si le créneau de deux heures a changé, le serveur recalcule le montant avant écriture et affiche le nouveau total.

La revente ne modifie pas le cours affiché avant confirmation. Elle applique la formule individuelle définie en section 13 ; l'état de santé n'intervient pas dans les deux échantillons observés, contrairement à la longévité restante. L'algorithme aléatoire exact produisant le nouveau cours reste inconnu.

**DiploPark.** `MarketQuote` stocke la variante, le créneau de demi-journée, le prix de base copié pour audit, le cours, le cours précédent, les volumes achetés/vendus depuis le dernier créneau et la tendance. Pour chaque entrée achetable : `pression = clamp(achats - ventes, -10, 10)` ; `variation_volume = pression × 1 %` ; `retour_base = clamp((prix_base - prix_actuel) / (2 × prix_base), -5 %, 5 %)` ; `variation_totale = clamp(variation_volume + retour_base, -10 %, 10 %)` ; puis `nouveau_prix = clamp(prix_actuel × (1 + variation_totale), 50 % du prix_base, 200 % du prix_base)`. Les volumes sont consommés exactement une fois par clé de créneau.

### 16.2 Boutiques et stocks

Quatre commerces consomment chacun leur propre inventaire. Les chiffres du compte à 1 526 visiteurs permettent de reconstruire les formules suivantes :

| Commerce | Part des visiteurs acheteurs | Prix par ration | Stocks consommés par mise à jour |
| --- | ---: | ---: | ---: |
| Souvenirs | 10 % | 48 | `round(visitors × 5 %)` |
| Restauration rapide | 20 % | 20 | `round(visitors × 10 %)` |
| Boissons | 30 % | 12 | `round(visitors × 15 %)` |
| Glaces | 40 % | 8 | `round(visitors × 20 %)` |

**Déduit.** Un stock commercial représente deux rations. La recette est arrondie après calcul : avec 1 526 visiteurs, les quatre recettes sont respectivement 7 325, 6 104, 5 494 et 4 883 unités.

La nourriture animale suit le gabarit : la consommation d'une mise à jour est la somme des gabarits de tous les individus. Le tarif normal est de 20 unités par stock ; les rangs de prestige appliquent les prix 18, 16, 14 et 12, soit des remises de 10 %, 20 %, 30 % et 40 %. Un manque de nourriture fait perdre 20 % de santé.

### 16.3 Constructions et attractions

Les constructions ont un emplacement fixe sur la carte. Leur achat ou leur amélioration est immédiat, tandis que leur revenu ou multiplicateur est appliqué au bilan de chaque mise à jour. Les coûts, revenus et besoins de personnel doivent être des données configurables.

#### 16.3.1 Hôtel et train

Ces deux bâtiments produisent un revenu fixe sans consommer de stock et sans personnel propre. Le barème DiploPark validé est linéaire :

| Bâtiment | Niveaux | Coût du palier `n` | Revenu total au niveau `n` | Coût cumulé maximal | Revenu maximal |
| --- | ---: | ---: | ---: | ---: | ---: |
| Hôtel | 5 | `100 000 × n` | `10 000 × n` | 1 500 000 | 50 000/MAJ |
| Train | 10 | `50 000 × n` | `5 000 × n` | 2 750 000 | 50 000/MAJ |

Le montant affiché pour un niveau est le revenu total du bâtiment, pas un revenu qui se cumule avec celui du niveau précédent. Le coût marginal d'hôtel s'amortit en `10 × n` mises à jour ; celui du train également en `10 × n` mises à jour.

Le modèle utilise une table de niveaux :

```text
FacilityType(code, max_level)
FacilityLevel(facility_type, level, build_cost, income_per_tick, visual_variant)
ParkFacility(park, facility_type, current_level, built_at)
```

Le revenu est ajouté une fois par mise à jour si `current_level > 0`. Une amélioration remplace le revenu du niveau précédent ; elle ne crée pas une seconde ligne de revenu cumulable.

#### 16.3.2 Boutiques

Il existe quatre boutiques indépendantes et sans niveaux. Chacune possède son propre stock, son tarif d'achat et son taux de fréquentation. Un stock permet de servir deux clients.

| Boutique | Part des visiteurs | Prix de vente par ration | Achat d'un stock | Marge brute d'un stock plein | Situation observée à 1 526 visiteurs |
| --- | ---: | ---: | ---: | ---: | --- |
| Souvenirs | 10 % | 48 | 12 | 84 | 76 stocks consommés, revenu 7 325 |
| Restauration rapide | 20 % | 20 | 5 | 35 | 153 stocks consommés, revenu 6 104 |
| Boissons | 30 % | 12 | 3 | 21 | 229 stocks consommés, revenu 5 494 |
| Glaces | 40 % | 8 | 2 | 14 | 305 stocks consommés, revenu 4 883 |

Formules vérifiées par les écrans Stocks et Recettes :

```text
demande_rations = visitors × visitor_share
stocks_necessaires = round(demande_rations / 2)
stocks_consommes = min(stock_disponible, stocks_necessaires)
taux_service = min(1, (2 × stock_disponible) / demande_rations)
recette_boutique = round(demande_rations × taux_service × prix_ration)
```

Avec des stocks suffisants, les quatre recettes totalisent 23 806 par mise à jour sur le compte audité. La quantité achetée par le joueur est ajoutée immédiatement au stock ; les ventes et la consommation interviennent pendant la mise à jour. Si un stock est épuisé, la boutique ne doit pas créer de recette sur les rations non servies.

**DinoPark.** Le cas où le stock disponible est inférieur au besoin arrondi n'a pas été observé. La formule de plafonnement ci-dessus est donc une convention déterministe à tester contre un futur cas de pénurie ; les valeurs avec stock suffisant sont, elles, confirmées exactement.

#### 16.3.3 Constructions exclues

Le port, les aires de repos, la grande roue, les zones de spectacle et la Botanica sont supprimés du périmètre, sans emplacement réservé sur la carte ni modèle dormant.

### 16.4 Météo

**Documenté.** Six états existent. Le règlement confirme les modificateurs de visiteurs suivants, ainsi que les effets biologiques ou exceptionnels :

| Météo | Poids DiploPark | Modificateur de visiteurs | Multiplicateur de naissance | Effet exceptionnel |
| --- | ---: | ---: | ---: | --- |
| Grand soleil | 22 % | +20 % | ×1,10 | — |
| Beau temps | 30 % | +10 % | ×1,00 | — |
| Couvert | 22 % | 0 % | ×1,00 | — |
| Pluie | 16 % | -20 % | ×1,00 | — |
| Neige | 8 % | -50 % | ×0,90 | — |
| Météorite | 2 % | -75 % | ×1,00 | Prime de 20 000 et dégâts possibles |

Ces poids et multiplicateurs sont les valeurs DiploPark validées. Le tirage journalier global doit être vérifié statistiquement sur au moins 100 000 jours simulés.

**Observé et adapté.** La carte présente la météo d'aujourd'hui, de demain et d'après-demain. DiploPark renomme l'état `tornade` de la référence en `météorite`, sans créer un septième état.

Pour chaque mise à jour, l'ordre de calcul DinoPark est :

1. charger la météo globale de `effective_date` ;
2. calculer `visiteurs_effectifs = round(visiteurs_hors_meteo × (1 + modificateur))` ;
3. utiliser ces visiteurs effectifs pour la billetterie, les boutiques et les attractions indexées sur les entrées ;
4. appliquer le coefficient biologique au tirage de reproduction ;
5. appliquer les bonus contextuels : prime de 20 000 et tirage de dégâts pendant une mise à jour sous météorite, ainsi que la potion Météorite éventuelle sur les achats ;
6. évaluer les conditions météorologiques des missions avec l'état figé du rapport.

La météorite conserve des naissances normales. La prime de 20 000 est versée une fois par mise à jour exécutée sous météorite. Chaque enclos construit subit un tirage indépendant de dégâts à 30 %, avec un plafond de 10 enclos endommagés par mise à jour. Les 10 premières mises à jour d'un parc ignorent ces dégâts, mais conservent la météo et la prime.

Les missions adaptées emploient `météorite` partout où la référence employait `tornade`. Le moteur enregistre la météo dans chaque `TickRun`, conserve l'historique et expose `current_weather`, `previous_weather` et `weather_seen_set`.

### 16.5 Missions

L'objectif retenu est un catalogue maximal dès la première version longue durée : **652 missions ou objectifs autonomes** issus des mécaniques compatibles avec DiploPark. Le total comprend 605 missions de naissance, 44 missions avancées et 3 missions périodiques. Les noms et textes sont adaptés au parc préhistorique ; les structures de progression observées sont conservées.

#### 16.5.1 Règles communes du moteur

- Chaque définition indique `scope`, `period`, `activation_mode`, `tick_types_allowed`, `counter_mode`, `conditions`, `reward`, `validation_time` et `reset_policy`.
- Un rapport de mise à jour émet des événements immuables : naissance, sexe, variante, décès et cause, enclos, météo, cours et consommation de stock. La présence quotidienne émet son propre événement `daily_visit`, indépendant d'un rapport de mise à jour. Les missions consomment ces événements ; elles ne recalculent jamais le passé depuis l'état courant du parc.
- Une mission avancée peut être démarrée dans n'importe quel ordre, mais une seule est active à la fois. Sauf mention contraire, sa validation rapporte **2 mises à jour bonus**.
- Une mission de naissance est toujours active. Une mission périodique est réinitialisée au début de sa période et sa récompense est versée à la clôture, même si l'objectif a été atteint avant.
- Les mises à jour bonus comptent par défaut pour les missions de naissance et avancées. Chaque mission périodique ou avancée peut les exclure explicitement.
- Un compteur simultané ne regarde qu'un seul `TickRun`. Un compteur consécutif revient à zéro dès qu'une mise à jour éligible ne satisfait pas la condition.
- Les récompenses sont idempotentes grâce à une contrainte unique `(mission_run, reward_code)`.

#### 16.5.2 Missions de naissance : 605 objectifs

Le catalogue initial contient 92 espèces et 29 variantes albinos, soit **121 entrées comptées séparément**. Chacune génère cinq missions :

| Colonne | Objectif | Portée | Récompense |
| --- | --- | --- | --- |
| 1 | Au moins 1 naissance | Une même mise à jour | Validation |
| 2 | Au moins 2 naissances | Une même mise à jour | Validation + progression du méta-objectif |
| 3 | Au moins 3 naissances | Une même mise à jour | Validation + progression du méta-objectif |
| 4 | Au moins 4 naissances | Une même mise à jour | 1 mise à jour bonus |
| 5 | 200 naissances | Cumul du compte | Validation + progression du méta-objectif |

Une variante albinos compte uniquement sur sa propre ligne. Une portée de quatre petits valide aussi les colonnes 1 à 4 non encore terminées. Les naissances accordées directement par une récompense ne comptent pas ; les naissances biologiques d'une mise à jour bonus comptent.

La référence fixe certains paliers à 150 espèces, mais DinoPark ne possède que 121 entrées. Les paliers sont rendus atteignables sans raccourcir excessivement la progression :

- 150 missions de naissance différentes : déblocage de **Meganeuropsis** ;
- 100 validations dans la colonne 2 : 10 mises à jour bonus ;
- 100 validations dans la colonne 3 : 10 mises à jour bonus ;
- 100 validations dans la colonne 5 : 10 mises à jour bonus.

Ces 605 lignes sont générées à partir du catalogue au chargement des fixtures plutôt que saisies manuellement. Ajouter une espèce ou une variante crée automatiquement ses cinq missions.

#### 16.5.3 Missions avancées : 44 missions conservées

Les objectifs ci-dessous sont directement réalisables avec les individus, sexes, familles, enclos, météos, cours, albinos, apparitions et décès déjà prévus. Les étiquettes thématiques telles que `color_theme`, `taxon_family`, `diet` ou `scavenger` sont de simples données de catalogue.

| N° | Nom DinoPark | Objectif adapté | Récompense spécifique, en plus des 2 mises à jour bonus |
| ---: | --- | --- | --- |
| 1 | Paix jurassique | Faire naître un Oviraptor et un Therizinosaurus lors de la même mise à jour | — |
| 2 | Papier fossile | Atteindre 25 naissances de Scutellosaurus | — |
| 3 | Parité | Obtenir au moins 10 naissances dans une mise à jour, avec autant de mâles que de femelles | — |
| 4 | Invasion | Faire naître un Compsognathus dans chacun des six enclos de Forêt primitive | — |
| 5 | La légende blanche | Sous la neige, obtenir un Yutyrannus par naissance conditionnelle, puis faire naître un Yutyrannus un jour sans neige | Déblocage permanent du Yutyrannus au marché |
| 6 | Couleurs du Crétacé | Faire naître dans une même mise à jour les quatre espèces configurées `bleu`, `blanc`, `rouge` et `tricolore` | — |
| 7 | Dérèglement climatique | Faire naître Cryolophosaurus, Yutyrannus et Edmontonia sous grand soleil | — |
| 8 | Pas de jaloux | Obtenir le même nombre de naissances en Forêt primitive, Insectarium et Vivarium, avec au moins quatre dans chacun | 1 stock de Redondasaurus |
| 9 | Yin-Yang | Faire naître lors de la même mise à jour quatre des cinq espèces marquées `black_white` | — |
| 10 | Après l'impact | Faire naître un Pyroraptor dans la mise à jour suivant une météorite | Déblocage du Pyroraptor |
| 11 | À table | Atteindre 120 naissances de Lurdusaurus et 120 de Nigersaurus | — |
| 12 | Deux meutes | Faire naître deux couples de théropodes non albinos appartenant à deux espèces différentes dans la même mise à jour | — |
| 13 | Les six biomes | Obtenir au moins une naissance dans chacun des quatre habitats principaux, l'Insectarium et le Vivarium pendant la même mise à jour | 1 stock de Meganeuropsis |
| 14 | Sang froid | Atteindre 300 naissances cumulées d'espèces du Vivarium | — |
| 15 | Blanc extraordinaire | Atteindre successivement 10, 30, 70 et 130 naissances albinos, toutes espèces confondues | Déblocages albinos configurés à chaque palier |
| 16 | Grande migration | Posséder un couple d'Einiosaurus dans chacun des six enclos de Grandes plaines à la fin d'une migration | — |
| 17 | Espèce envahissante | Atteindre 20 naissances d'Einiosaurus | — |
| 18 | Les trois cornus | Atteindre 15 naissances de Protoceratops, 15 d'Archaeoceratops et 15 de Triceratops | Fenêtre de marché spéciale pour Einiosaurus |
| 19 | Meute de raptors | Atteindre 150 naissances de dromaeosauridés, dont 15 Pyroraptor | — |
| 20 | Régulation | Atteindre 20 naissances de Spinosaurus | 10 mises à jour bonus au lieu de 2 |
| 21 | Dommages collatéraux | Subir 20 décès de petites proies causés par un grand prédateur incompatible | 10 mises à jour bonus au lieu de 2 |
| 22 | Les trois pêcheurs | Faire naître Baryonyx, Suchomimus et Spinosaurus lors de la même mise à jour | — |
| 23 | Visiteur de minuit | À minuit, capturer l'espèce mystère attirée par un Yutyrannus, puis atteindre 20 naissances de cette espèce | Déblocage permanent de l'espèce mystère |
| 24 | Charognards | Faire naître simultanément trois espèces marquées `scavenger` et deux petits herbivores | — |
| 25 | Plumage ancestral | Atteindre 120 naissances de dinosaures à plumes ; suivre séparément les naissances de Caudipteryx | Bonus de 10 visiteurs au prochain tick, plus 2/4/6/8/10 selon les paliers de Caudipteryx |
| 26 | Trois géants | Faire naître Allosaurus, Carcharodontosaurus et Giganotosaurus dans la même mise à jour, trois fois | Bonus de 10 visiteurs au prochain tick |
| 27 | Prédateurs en cascade | 5 Microraptor, puis 10 Deinonychus, 15 Pyroraptor, 20 Giganotosaurus et 5 Giganotosaurus albinos | Déblocage de l'étape suivante ; bonus de 10 visiteurs au prochain tick ; 10 supplémentaires pour 20 Velociraptor pendant la mission |
| 28 | Arche du Mésozoïque | Obtenir en un mois une naissance de chaque entrée disponible, albinos séparés ; mission tolérée avec au plus 14 manquants | De 150 visiteurs au prochain tick + 30 mises à jour bonus sans manque à 10 visiteurs + 2 bonus avec 14 manquants |
| 29 | Métamorphose | Faire devenir adulte une larve de Kalligramma, la reproduire et atteindre 25 naissances | Bonus de 5 visiteurs au prochain tick et 4 mises à jour bonus |
| 30 | Les douze ornithopodes | Obtenir un couple nouveau-né de chacune de six espèces configurées d'ornithopodes | Déblocage d'une espèce rare configurée |
| 31 | Famille nombreuse | Obtenir des quintuplés d'une entrée dont le cours actuel vaut au moins 200 000 | Bonus de 10 visiteurs au prochain tick |
| 32 | T-Rex | Obtenir au moins trois naissances de dinosaures dans la même mise à jour, dont un Tyrannosaurus | Bonus de 10 visiteurs au prochain tick et 3 stocks d'espèce exceptionnelle |
| 33 | Jurassic | Obtenir des jumeaux de douze espèces de dinosaures configurées | Déblocage d'une espèce secrète configurée ; 3 stocks exceptionnels en bonus pour des jumeaux Tyrannosaurus |
| 34 | Mâchoires anciennes | Faire naître Gobiderma, Proterosuchus et Postosuchus lors de la même mise à jour, ou atteindre les objectifs cumulés 30/30/20 | Déblocage permanent de Redondasaurus |
| 35 | Intemporel | Choisir définitivement une entrée valant plus de 200 000, puis obtenir un couple nouveau-né sous chacune des cinq météos hors météorite | Bonus de 10 visiteurs au prochain tick, ParkCoins égaux à quatre cours actuels et 1 stock de l'entrée choisie |
| 36 | Six mises à jour | Obtenir une naissance de Postosuchus lors de six mises à jour consécutives | Déblocage de Postosuchus albinos |
| 37 | Nouveau monde | Trois mises à jour consécutives avec naissance naturelle de Tyrannosaurus, ou huit naissances de Tyrannosaurus albinos | Consommation des grands carnivores réduite de 1, plus 3 % de remise sur les achats exceptionnels et secrets |
| 38 | Copie monochrome | Pour dix couples d'entrées configurés, faire naître la forme normale et l'albinos dans la même mise à jour sous pluie ou neige | Déblocage d'une variante albinos secrète |
| 39 | Matriarcat | Pendant la mission, chaque naissance de Titanomyrma sacrifie un mâle reproducteur ; atteindre 20 naissances | Déblocage d'une espèce exceptionnelle de l'Insectarium ; le sacrifice cesse |
| 40 | Épargne paléontologique | Placer 0,5 % du cours de chaque décès naturel dans une cagnotte versée le premier du mois | Cagnotte mensuelle ; mission de fin de jeu |
| 41 | Maîtres du Vivarium | Obtenir un couple nouveau-né de chacune des dix espèces du Vivarium | Déblocage d'une variante rare et bonus de 10 visiteurs au prochain tick |
| 42 | Mélanisme | Obtenir lors de 20 mises à jour une paire de naissances Cryolophosaurus/Yutyrannus ; une paire maximum par mise à jour | Déblocage permanent du Yutyrannus ; bonus : 2 potions Équilibre et 1 Survie pour des jumeaux des deux espèces dans le même rapport |
| 43 | Tous les enclos | Obtenir cinq naissances d'Einiosaurus dans chacun des six enclos de Grandes plaines | Déblocage de Patagotitan ; bonus exceptionnel si quatre prédateurs majeurs naissent dans la même mise à jour |
| 44 | Sous tous les temps | Obtenir des triplés de Parasaurolophus sous chacune des cinq météos hors météorite, puis répéter avec Shantungosaurus | Déblocage de Shantungosaurus après la première partie |

La mission d'espionnage de la référence est la seule mission avancée totalement supprimée. Aucun objectif ne dépend du musée, de l'explorateur, du laboratoire, de l'incubation ou de l'île aux dinos. Lorsque la référence accordait un œuf, DinoPark accorde un stock d'espèce de valeur comparable.

#### 16.5.4 Missions périodiques : 3 missions répétables

| Nom DiploPark | Période | Objectif | Récompense |
| --- | --- | --- | --- |
| Semaine jurassique | Hebdomadaire | Obtenir une naissance naturelle de chaque espèce vedette de la rotation hebdomadaire ; les mises à jour bonus sont exclues | 1 stock d'espèce exceptionnelle |
| Espèce du mois | Mensuelle | Atteindre les paliers de naissances naturelles selon la rareté : commune 20/25/30, peu commune 15/20/25, rare 10/15/20, exceptionnelle 5/10/15 ; bonus exclus ; espèces secrètes inéligibles | Respectivement 1, 2 ou 3 mises à jour bonus |
| Contrebandier | Hebdomadaire | Vendre l'espèce vedette selon sa rareté : commune 4/6/8, peu commune 3/5/7, rare 2/4/6, exceptionnelle 1/3/5 ; espèces secrètes inéligibles | Respectivement 1, 2 ou 3 mises à jour bonus |

Les missions journalières commencent à 00 h 01 et finissent à minuit ; les hebdomadaires vont du lundi au dimanche à minuit ; les mensuelles du premier au dernier jour du mois. Les gains sont attribués à la fin de la période. Une mission `live` est évaluée en continu et son avantage peut se désactiver lorsque sa condition de possession n'est plus remplie.

#### 16.5.5 Données et interface

Les 44 missions avancées et les trois périodiques sont livrées comme fixtures versionnées. Les missions Inestimable, Gardien fidèle et Une méthode à suivre sont supprimées ; l'ancienne Chaîne alimentaire est remplacée par Contrebandier. Les familles et listes d'espèces sont référencées par identifiants, jamais par texte libre. L'interface propose :

- un tableau filtrable des 605 missions de naissance, avec progression par colonne ;
- une fiche par mission avancée, son état verrouillé/disponible/active/terminée et un bouton d'activation en `POST` ;
- une seule mission avancée active, avec confirmation avant remplacement ;
- trois cartes périodiques indiquant début, fin, admissibilité des bonus et récompense prévue ;
- un journal expliquant précisément quel événement a fait progresser ou réinitialisé chaque compteur.

### 16.6 Prestige et classements

La comparaison entre joueurs ne repose pas sur un score unique. La page centrale affiche le rang personnel dans quatre classements permanents ou périodiques et un accès direct au parc d'un autre joueur. DiploPark vise **trois à cinq joueurs actifs** ; les tournois sont reportés après le lancement.

#### 16.6.1 Tableau de bord comparatif

Le bandeau personnel affiche en permanence : prestige et rang général, valeur du cheptel et rang économique, points et rang du mois, points de rareté et rang du cheptel. Chaque ligne ouvre le classement correspondant. Une ligne montre au minimum : rang, nom du parc, score principal et récompense active. Selon la catégorie, elle ajoute le nombre d'animaux, les visiteurs, les missions ou les trophées.

Le profil public d'un parc doit être accessible depuis son nom sans exposer ses données sensibles. Il montre les indicateurs nécessaires à la comparaison : prestige, population, visiteurs, missions terminées, trophées, habitats ouverts et espèces visibles. Les finances détaillées, stocks, personnel et probabilités internes restent privés.

**DinoPark.** Tous les tableaux utilisent un ordre stable : score décroissant, prestige décroissant, missions avancées décroissantes, missions de naissance décroissantes, date d'obtention du score la plus ancienne, puis identifiant du parc. Les tournois de référence confirment explicitement les trois premiers critères après le score ; les deux derniers sont ajoutés pour garantir un résultat déterministe.

#### 16.6.2 Classement général par prestige

Le prestige mesure la complétude du parc, pas sa richesse. Les plantes, spectacles et musée étant exclus, DiploPark utilise :

```text
prestige_points = floor(sante_moyenne)
                + especes_distinctes_possedees
                + constructions_actives

prestige_pct = 100 × prestige_points / prestige_points_max_actifs
```

Le dénominateur est construit depuis les composants réellement activés dans DinoPark. Le tableau présente aussi population totale, visiteurs permanents et nombre de missions terminées. Un joueur sans connexion depuis plus de 30 jours conserve son prestige affiché, mais passe après tous les joueurs actifs ; son score est dit « gelé » jusqu'à son retour.

#### 16.6.3 Classement par valeur du cheptel

La valeur compare tous les individus au cours global courant en tenant compte de leur longévité restante :

```text
valeur_individu = round(cours_actuel_variante × vie_restante / 100)
valeur_cheptel = somme(valeur_individu)
```

Le coefficient de revente de 60 % n'entre pas dans cette valeur théorique. Le classement peut donc évoluer toutes les deux heures avec la bourse et après chaque naissance, décès ou vieillissement.

La référence récompense les premiers par un bonus de revente, ce qui renforcerait directement les joueurs déjà les plus riches. DiploPark ne donne aucune remise de marché. La valeur reste un classement comparatif ; les Diplodocoins suivent le versement quotidien commun décrit en 16.6.7.

#### 16.6.4 Classement mensuel des naissances

Le compteur ouvre le premier jour du mois à 00 h 00 et se ferme le dernier jour à minuit. Chaque naissance biologique marque selon le cours de sa variante au moment du rapport :

| Cours actuel | Points de base |
| ---: | ---: |
| Moins de 20 000 | 1 |
| De 20 000 à moins de 100 000 | 2 |
| De 100 000 à moins de 300 000 | 3 |
| 300 000 et plus | 4 |

- variante albinos : **+2 points** par naissance ;
- espèce dinosaure : **+3 points** par naissance ;
- insectes et reptiles non dinosaures ne reçoivent pas ce dernier bonus ;
- les points et le cours utilisé sont écrits dans `RankingEvent` au moment du `TickRun`, afin qu'une rotation boursière ultérieure ne réécrive pas le mois.

Pour figurer dans le classement mensuel, un joueur doit avoir marqué au moins 20 points. Ce classement ne crée pas un second versement : les Diplodocoins suivent le versement quotidien commun décrit en 16.6.7.

#### 16.6.5 Classement permanent de rareté

Chaque individu vivant apporte des points selon la rareté de son entrée :

| Rareté DinoPark | Points par individu |
| --- | ---: |
| Commune | 1 |
| Peu commune | 2 |
| Rare | 3 |
| Exceptionnelle | 4 |
| Secrète | 5 |

Le classement montre à la fois la population prise en compte et le total de points. Une variante albinos conserve le poids de rareté de sa variante de catalogue ; elle n'ajoute pas automatiquement deux points comme dans le classement mensuel.

La référence récompense les premiers par une remise liée au laboratoire. DiploPark ne donne aucune remise de marché ni versement mensuel séparé.

Le barème à cinq raretés est une adaptation nécessaire : la référence n'en possède que quatre. Il rend les espèces secrètes réellement importantes pour la compétition longue durée.

#### 16.6.6 Tournois exceptionnels individuels — reportés

Des saisons thématiques mensuelles font varier la stratégie sans effacer les classements permanents. Seules les mises à jour classiques comptent. Les formats observés et réutilisables sont :

- un point par naissance d'une famille ciblée ;
- bonus croissant selon le nombre d'espèces différentes de la famille nées dans le même rapport ;
- barème par diversité, par exemple 2 espèces = 1 point, 3 = 3 points, 4 ou plus = 5 points ;
- un point par espèce différente née pendant une mise à jour ;
- tournoi avec participation volontaire lorsqu'une règle temporaire dangereuse est activée, par exemple cannibalisme reproductif.

Le moteur pourra supporter ces formats, mais aucun tournoi n'est actif au lancement et aucun barème de récompense n'est intégré à la fixture V1.

#### 16.6.7 Récompense quotidienne adaptée à trois à cinq joueurs

Une clôture quotidienne du **classement général par prestige**, calculée sur l'état de la veille en `Europe/Paris`, verse :

- 50 Diplodocoins au joueur classé premier ;
- 25 Diplodocoins au joueur classé deuxième ;
- 10 Diplodocoins à chaque joueur ayant été actif la veille, y compris les deux premiers. Ce montant est un bonus d'activité cumulable avec leur récompense de rang.

Un joueur est actif s'il a enregistré sa présence quotidienne la veille. En cas d'égalité, le classement de compétition s'applique (`1, 1, 3`) et les ex æquo reçoivent le même palier. Si personne n'est actif, aucun versement n'est créé. Une contrainte `(reward_date, user_id, reward_code)` interdit tout double crédit. Les classements ne produisent aucune remise ou amélioration du score futur.

#### 16.6.8 Calcul, snapshots et performances

Les classements permanents sont matérialisés dans `RankingSnapshot` plutôt que recalculés à chaque page : prestige après une mise à jour de parc, valeur et bonus de vente après chaque rotation de bourse, rareté après un changement de cheptel. Les compteurs mensuels et de tournoi sont incrémentés depuis `RankingEvent`.

À chaque snapshot, une fonction SQL de fenêtre attribue les rangs : `ROW_NUMBER() OVER (ORDER BY ...)`. La page lit 30 lignes à la fois et exécute séparément une requête indexée pour le rang du joueur connecté. Les index minimaux sont `(ranking_type, season_id, rank)`, `(ranking_type, season_id, park_id)` et `(event_type, occurred_at, park_id)`. Cette architecture évite Celery : les rotations globales et la commande cron nocturne suffisent.

### 16.7 Jeu social sans équipes

DinoPark ne comporte ni équipes, ni dons entre joueurs, ni cagnotte collective, ni missions collectives, ni tournois inter-équipe, ni bagarres. Avec trois à cinq actifs, ces systèmes seraient soit inutilisables, soit trop faciles à manipuler.

Le jeu social se limite aux profils publics, classements individuels, badges, historique des saisons et messagerie déjà présente sur le site Django. Les transferts de monnaie, stocks, animaux ou mises à jour bonus entre joueurs restent interdits afin d'éviter les comptes nourriciers.

### 16.8 Potions retenues

| Consommable | Effet observé |
| --- | --- |
| Soin | Restaure toute la santé du parc ; une utilisation mensuelle |
| Animaux bonus | Ajoute un stock d'espèce ou ouvre temporairement une espèce exceptionnelle |
| Équilibre | Favorise le sexe sous-représenté pendant 3 mises à jour |
| Survie | Ajoute 3 unités de vie aux individus auxquels il en reste moins de 10 |
| Météorite | Pendant une météorite, -10 % sur les achats jusqu'à la prochaine mise à jour |
| Albinos | Porte la chance éligible à 70 % pour la prochaine mise à jour |

Les potions autres que le soin sont plafonnées à 10 unités. Le VIP, les espèces VIP, le chien/compagnon et le parrainage sont supprimés.

#### 16.8.1 Potions retenues

| Potion | Stock | Activation et consommation |
| --- | ---: | --- |
| Soin | 0 ou 1 | Rend immédiatement 100 % de santé à tous les animaux ; une utilisation par mois ; recharge mensuelle automatique |
| Animaux bonus | 0 à 10 | 1 potion donne un stock d'espèce ; 2 potions ouvrent une espèce exceptionnelle jusqu'à la prochaine mise à jour |
| Équilibre | 0 à 10 | Pendant les trois prochaines mises à jour, chaque naissance privilégie le sexe sous-représenté dans l'enclos |
| Survie | 0 à 10 | Ajoute immédiatement trois unités de longévité à chaque individu auquel il en reste moins de dix |
| Météorite | 0 à 10 | Activable seulement sous météorite ; −10 % sur les achats d'animaux jusqu'à la prochaine mise à jour |
| Albinos | 0 à 10 | Pour la prochaine mise à jour, porte à 70 % la chance albinos des naissances éligibles |

Les potions proviennent des missions, de certaines saisons et, après son ouverture, de la boutique en Diplodocoins. Toute activation est un `POST`, verrouille le stock et crée un événement idempotent.

### 16.9 Monnaie virtuelle transversale et ancienne banque

DiploPark utilise deux monnaies sans les confondre :

- **ParkCoins**, monnaie du parc, utilisée pour les animaux, constructions, salaires et stocks ;
- **Diplodocoins**, monnaie transversale déjà détenue dans `Blog.User.coins`.

Il n'existe aucun paiement par carte, PayPal, téléphone ou fournisseur externe. Les anciennes offres de banque deviennent des offres purement virtuelles. Pour préserver l'équilibrage, le premier catalogue recommandé est volontairement plus petit que les lots payants de la référence :

| Offre | Contenu DinoPark | Limite recommandée |
| --- | --- | --- |
| Coup de pouce | 1 mise à jour bonus | 2 par semaine |
| Lot de mises à jour | 5 mises à jour bonus | 1 par mois |
| Subvention | 250 000 unités du parc | 1 par semaine |
| Grande subvention | 1 000 000 unités du parc | 1 par mois |
| Lot mixte | 3 mises à jour bonus + 500 000 unités | 1 par mois |
| Potion au choix | 1 potion hors soin | 2 par semaine, tous types confondus |

La page et le catalogue sont implémentés mais **fermés au lancement**. Les prix ne sont pas intégrés à la fixture active avant validation explicite. Une bannière informe les joueurs de l'ouverture future.

#### 16.9.1 Récompenses de classement

Le versement quotidien défini en 16.6.7 crédite 50 Diplodocoins au premier, 25 au deuxième et 10 à chaque joueur actif la veille. La boutique fermée au lancement empêche ces gains de renforcer immédiatement le parc.

#### 16.9.2 Intégration Django et sécurité comptable

DinoPark ne crée pas de second solde de monnaie transversale. Un service `SiteCurrencyGateway` encapsule le modèle de portefeuille déjà présent :

```text
debit(user, amount, idempotency_key, reason, metadata)
credit(user, amount, idempotency_key, reason, metadata)
balance(user)
```

`dinopark.db` et la base utilisateurs existante sont deux connexions SQLite distinctes. `Park.owner_id` conserve l'identifiant du `Blog.User` sans clé étrangère SQL inter-base ; un contrôle applicatif vérifie le compte. Une transaction distribuée étant impossible, tout transfert utilise une écriture `pending`, une clé d'idempotence globale et une machine d'état reprenable. Le mouvement Diplodocoins est écrit dans la base principale, puis l'achat ou la récompense est finalisé dans `dinopark.db`. Une commande réconcilie les opérations interrompues sans double mouvement.

Chaque mouvement conserve : utilisateur, montant signé, solde avant/après si disponible, origine, identifiant de saison ou d'offre, date et clé d'idempotence. Les prix sont relus côté serveur ; aucun montant envoyé par le navigateur n'est accepté. Une offre expirée, une limite dépassée ou un solde insuffisant annule toute la transaction.

## 17. Modèle de données préliminaire

```text
Park
HabitatType
HabitatSlot
Enclosure
Species
SpeciesVariant
Animal
SpeciesUnlock
SpeciesCompatibilityOverride
StaffAllocation
Inventory
MarketOffer
MarketSnapshot
MarketQuote
TickRun
LedgerEntry
GameEvent
Mission
MissionDefinition
MissionObjective
MissionReward
MissionRun
MissionProgress
AvailabilityRule
SpeciesRewardStock
WeatherDay
Facility
Shop
ConsumableStock
RankingSnapshot
RankingSeason
RankingEvent
RankingRewardTier
MetaOffer
MetaPurchase
DailyVisit
CrossDatabaseOperation
```

Les règles immuables peuvent être livrées sous forme de fixtures. L'état des joueurs, les offres actives et les résultats aléatoires sont conservés en base de données.

## 18. Architecture légère

- Django et son système d'authentification existant.
- Templates Django pour le rendu principal.
- JavaScript natif uniquement pour les interactions qui bénéficient d'une mise à jour partielle.
- Base SQLite dédiée `dinopark.db`, configurée comme alias Django `dinopark`, distincte de la base utilisateurs existante.
- Routeur de base obligatoire : tous les modèles DiploPark vont dans `dinopark`; les modèles `Blog` restent dans `default`.
- Script Python d'orchestration lancé par cron sur le serveur et capable de résoudre l'environnement Django avant d'appeler les commandes idempotentes.
- Pas de Celery ni Redis au lancement.
- SQLite WAL, transactions courtes, contraintes uniques et mises à jour conditionnelles ; ne pas compter sur `select_for_update()` pour un verrou de ligne.
- Adaptateur `SiteCurrencyGateway` vers le portefeuille existant, avec saga idempotente inter-base ; aucun solde transversal dupliqué.
- Actions de modification uniquement en `POST` avec protection CSRF.

Le moteur de calcul doit rester séparé des vues afin de pouvoir être testé sans requêtes HTTP. Une optimisation en C++/Cython ne sera envisagée que si les mesures montrent un réel besoin ; la persistance et les transactions restent pilotées par Django.

## 19. Ordre d'implémentation proposé

### Lot A — Fondation jouable

- modèles `HabitatType`, `Species`, `Enclosure` et `Animal` ;
- import du catalogue ;
- compatibilité `is_groupable`/`compatibility_family` et premières exceptions ;
- construction d'un habitat ;
- achat d'un couple ;
- personnel selon les cinq formules observées ;
- stocks alimentaires selon la somme des gabarits ;
- première mise à jour manuelle de test et rapport d'événements.

### Lot B — Vie du parc

- santé, âge et décès ;
- reproduction à partir de 5 mises à jour et seuil de santé à 25 % ;
- visite réelle quotidienne distincte des mises à jour du parc et réserve de mises à jour bonus ;
- économie, prix du billet et journal comptable ;
- notifications de mise à jour ;
- prestige et visiteurs.

### Lot C — Rareté

- déblocages ;
- rotations du marché ;
- déblocages de fidélité et de rang de prestige ;
- stocks d'espèces récompenses ;
- espèces exceptionnelles ;
- variantes albinos à 5/20/50 % selon les parents et potion temporaire à 70 %.

### Lot D — Secrets

- apparitions spontanées ;
- règles de naissance conditionnelle ;
- missions de naissance, avancées et périodiques ;
- compteur anti-malchance.

### Lot E — Parc complet et compétition légère

- hôtel, train et quatre boutiques ;
- classements mensuels et récompenses ;
- moteur de tournois reporté après le lancement ;
- profils publics et comparaison directe des trois à cinq parcs.

## 20. Validation d'équilibrage et calibrations automatiques

Les décisions joueur sont closes pour la V1 : progression 5/30/200/500, capital de 400 000, 15+5 mises à jour bonus, protection de 10 mises à jour, enclos 40/70/100 et coûts 2 500/75 000/180 000/20 000 luxe, hôtel, train, reproduction cible, météo, apparitions, marché, fourchettes des espèces, trois missions périodiques, événements dormants et boutique fermée.

Deux calibrations ne nécessitent pas de nouvelle décision fonctionnelle mais constituent des portes de validation technique :

1. exécuter 2 000 parcours complets et choisir la pente du bonus débutant sur 50 mises à jour qui minimise l'écart aux jalons 5/30/200/500, à partir de la candidate 100 000, 98 000, …, 2 000 ;
2. ajuster légèrement les taux de reproduction autour de 8,89/7,78/6,67/5,56/4,44 % afin que les couples formés dès maturité produisent en moyenne 4/3,5/3/2,5/2 descendants avant 50 mises à jour.

Les 92 fiches finales et les compatibilités doivent ensuite passer la validation structurelle automatisée. Les prix de la boutique en Diplodocoins ne bloquent pas le lancement puisque toutes les offres restent inactives.

La carte V1 possède 32 nœuds constructibles : 24 enclos principaux, insectarium, vivarium, hôtel, train et quatre boutiques. Elle utilise une vue aérienne WebP avec zones SVG ; survol pour le nom et le nombre d'animaux, point rouge d'alerte, aucune carte sur mobile et aucun zoom.

## 21. Journal des versions

### 1.1.0 — 20 août 2026

- intégration du questionnaire d'équilibrage validé ;
- pack initial à 400 000 ParkCoins, 15+5 MAJ et protection de 10 ticks ;
- longévité 50, maturité 5 et espérances reproductives 4 à 2 selon rareté ;
- validation des barèmes enclos, hôtel 5 niveaux et train 10 niveaux ;
- marché biquotidien, météo et apparitions spontanées chiffrés ;
- réduction à trois missions périodiques et total corrigé à 652 objectifs ;
- remplacement des questions ouvertes par deux calibrations sur 2 000 parcours.

### 1.0.0 — 20 août 2026

- consolidation des réponses `RES-01` à `RES-48` ;
- adoption du nom DiploPark, des ParkCoins et de SQLite séparé `dinopark.db` ;
- séparation de la présence quotidienne et des mises à jour de parc ;
- suppression du VIP, des sponsors, du port, des aires de repos, de la grande roue, des spectacles, de la Botanica, du compagnon et du parrainage ;
- albinisme fixé à 5/20/50 % selon les parents ;
- marché piloté par les volumes des joueurs, borné à 50–200 % ;
- tornade renommée météorite avec risque de dégâts ;
- récompenses quotidiennes fixées à 50/25 Diplodocoins et bonus d'activité de 10 ;
- boutique visible mais fermée au lancement ;
- coûts et probabilités maintenus comme tables à valider avant activation.

### 0.10.0 — 19 août 2026

- intégration des six potions, de leurs plafonds, activations et durées exactes ;
- ajout des quatre grades VIP liés au prestige, explicitement non achetables ;
- ajout du chien gratuit, de ses tirages par mise à jour et du multiplicateur de neige ;
- remplacement des œufs et objets de musée trouvés par des stocks d'espèce ;
- suppression de tout paiement réel et conversion de la banque en boutique de monnaie virtuelle du site ;
- séparation stricte entre monnaie interne du parc et monnaie transversale ;
- conversion des récompenses de classement en monnaie transversale sans remise ni bonus de score ;
- ajout d'un plafond mensuel global de récompense et de limites hebdomadaires/mensuelles d'achat ;
- définition des unités configurables `C` pour les prix et `R` pour les récompenses ;
- ajout du service transactionnel `SiteCurrencyGateway`, du journal comptable et des clés d'idempotence ;
- ajout des modèles VIP, compagnon, table de butin, offres et achats méta.

### 0.9.0 — 19 août 2026

- dimensionnement explicite pour trois à cinq joueurs actifs ;
- suppression complète des équipes, dons, cagnottes, missions collectives, tournois inter-équipe et bagarres ;
- remplacement des paliers à 1 000/1 500 places par des récompenses limitées aux trois premiers ;
- réduction des avantages économiques permanents à 3 %, 2 % et 1 % ;
- ajout de seuils d'activité empêchant un joueur inactif d'être récompensé par défaut ;
- création de petits lots de participation pour les places 4 et 5 ;
- réduction des lots mensuels et exceptionnels afin d'éviter l'effet boule de neige ;
- badges rendus purement honorifiques ;
- gestion équitable des ex æquo avec rang de compétition et récompense identique ;
- suppression des modèles et du lot d'implémentation liés aux équipes.

### 0.8.0 — 19 août 2026

- audit des quatre classements personnels, des classements d'équipe et des cinq tournois exceptionnels visibles ;
- documentation du tableau de bord comparatif, des profils publics, de la pagination et de la recherche de parc ;
- reconstruction des scores de prestige, valeur du cheptel, activité mensuelle et rareté ;
- relevé des paliers complets de bonus de revente pour les 1 000 premiers ;
- relevé des paliers complets de remise du classement de rareté pour les 1 500 premiers ;
- ajout des bonus mensuels dinosaure et albinos et de la clôture transactionnelle des saisons ;
- documentation des égalités, de l'inactivité à 30 jours, des trophées et tournois thématiques ;
- confirmation du score individuel d'équipe, de la moyenne des dix meilleurs membres actifs et du snapshot nocturne ;
- ajout du tournoi inter-équipe, du classement collectif de population et des bagarres ;
- architecture légère fondée sur événements, snapshots, fonctions SQL de fenêtre et tables de récompenses.

### 0.7.0 — 19 août 2026

- inventaire des trois familles de missions du jeu de référence ;
- génération de 605 missions de naissance pour 92 espèces et 29 variantes albinos ;
- adaptation de 44 missions avancées sur 45, avec suppression exclusive de l'espionnage ;
- conservation des objectifs de simultanéité, séries, météo, sexes, albinos, cours, enclos, décès et déblocages ;
- conversion des récompenses d'œufs et de laboratoire en stocks d'espèce ou remises de marché ;
- adaptation des six missions périodiques live, journalières, hebdomadaires et mensuelles ;
- formalisation des règles de validation, réinitialisation, idempotence et admissibilité des mises à jour bonus ;
- ajout des modèles de définition, objectifs et récompenses de mission ;
- passage de la couverture des missions à l'état documenté et adapté.

### 0.6.0 — 19 août 2026

- confirmation de la rotation mondiale des cours toutes les deux heures ;
- reconstruction de la tendance par rapport au prix de base et vérification sur les extrêmes visibles ;
- documentation de la propagation du cours aux achats, ventes, valorisations, rapports, missions et classements ;
- ajout du modèle de snapshots, de l'idempotence et du contrôle transactionnel des prix ;
- documentation des six météos, de leurs modificateurs et de la prévision mondiale à trois jours ;
- ajout de l'ordre d'application sur les visiteurs, recettes, naissances, chien, prime de tornade et missions ;
- formalisation de l'historique météo nécessaire aux conditions « météo précédente » et aux séries ;
- séparation explicite des règles confirmées et des paramètres aléatoires encore inconnus.

### 0.5.0 — 19 août 2026

- documentation des emplacements et niveaux de l'hôtel, du train et du port ;
- confirmation des revenus par mise à jour et calcul du retour sur investissement visible du train niveau 7 ;
- documentation complète des quatre boutiques, taux de fréquentation, prix, stocks et recettes ;
- reconstruction des formules de demande, consommation et revenu commercial ;
- documentation des trois aires de repos et de la grande roue ;
- confirmation de l'addition des bonus sur la billetterie de base ;
- ajout des besoins de personnel, salaires et gain net des attractions observées ;
- passage à l'état documenté des deux blocs de constructions dans la matrice de couverture.

### 0.4.0 — 19 août 2026

- passage à l'état documenté des individus, sexes, stades, couples et conditions de reproduction ;
- confirmation de `min(mâles adultes, femelles adultes)` pour le nombre de couples reproducteurs ;
- double validation numérique des cinq formules de personnel et de leurs salaires ;
- ajout des pénalités exactes de santé : −10 % pour un enclos mal géré et −20 % sans nourriture ;
- confirmation de la consommation alimentaire égale à la somme des gabarits ;
- documentation du passage au luxe pour 20 PA paysagiste et 20 000 unités ;
- séparation du sous-effectif immédiat, des dégâts traités à la mise à jour et de la réparation nocturne ;
- ajout d'une matrice de couverture des mécaniques fondamentales.

### 0.3.1 — 19 août 2026

- identification de la barre individuelle comme longévité restante sur 100 ;
- reconstruction et validation de la formule de revente sur un jeune et un adulte ;
- distinction explicite entre âge, longévité restante et santé ;
- confirmation du plafond monétaire courant à 100 millions, la règle des 50 millions étant obsolète ;
- confirmation de la contradiction des sponsors : règle documentée, mais recette nulle sur le compte avancé ;
- précision du lien entre cours de bourse, tendance, achat, intendance et revente.

### 0.3.0 — 19 août 2026

- première passe méthodique sur le compte avancé et le règlement interne ;
- distinction entre règles observées, documentées, déduites et choix DinoPark ;
- confirmation des 57 emplacements principaux de référence et maintien volontaire de 24 emplacements dans le démarrage réduit ;
- simplification de la compatibilité en espèces groupables et familles non groupables ;
- ajout des modes de déblocage par prestige, fidélité, mission, stock et calendrier ;
- réglage de l'albinisme à 12,5 %, porté à 70 % par potion pendant une mise à jour ;
- ajout des conditions de missions simultanées, météorologiques, cumulatives et séquentielles ;
- intégration des valeurs de reproduction, de longévité, d'achat et de revente connues ;
- intégration des cinq formules de personnel et de leurs salaires ;
- définition des deux fenêtres quotidiennes et du traitement paresseux à la connexion ;
- ajout de l'économie des billets, boutiques, stocks, bâtiments, météo et prestige ;
- ajout des missions, classements, équipes, potions, chien et parrainage à la cible fonctionnelle ;
- ajout d'une liste explicite de contradictions et probabilités restant à vérifier.

### 0.2.0 — 19 août 2026

- regroupement des dinosaures dans quatre habitats principaux ;
- passage à plusieurs enclos indépendants par habitat principal ;
- ajout d'un système de compatibilité par groupes et exceptions d'espèces ;
- création d'un insectarium à enclos unique avec dix insectes préhistoriques ;
- création d'un vivarium à enclos unique avec dix reptiles préhistoriques non dinosaures ;
- redistribution des 72 dinosaures sans réduction du catalogue ;
- catalogue porté à 92 entrées.

### 0.1.0 — 19 août 2026

- création du livret ;
- exclusion de l'île, de l'incubation et du musée ;
- choix d'un catalogue important dès la première version ;
- définition de six habitats et 72 espèces ;
- séparation entre rareté, variante albinos et mode d'obtention ;
- première proposition pour les apparitions et naissances spéciales ;
- architecture Django et ordre d'implémentation initiaux.

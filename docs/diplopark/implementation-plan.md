# DiploPark — Plan d’implémentation

**Version :** 2.1.0  
**Statut :** architecture et règles prêtes ; calibration statistique avant gel des fixtures  
**Référence fonctionnelle :** `dinopark-specifications.md` v1.1.0  
**Référence technique auditée :** `PiRom1/MyBlog`, branche `main`, commit `b3358a660c21dac66868353c4d3f8302a1e60c30`  
**Base de données cible :** SQLite dédiée `dinopark.db`, en plus de la base existante des utilisateurs  

## 1. Objet et règles de lecture

Ce document décrit **comment construire** DinoPark dans le site Django existant. Le livret de spécifications reste la source de vérité pour les règles du jeu, les espèces, les missions, les probabilités et l’équilibrage. Le présent fichier couvre l’architecture, la base de données, le back-end, le front-end, les tâches planifiées, les tests et l’ordre de réalisation.

Chaque agent doit lire, dans cet ordre :

1. `dinopark-specifications.md` ;
2. le présent plan ;
3. les fichiers existants qu’il doit modifier ;
4. les migrations déjà présentes avant d’en créer une nouvelle.

Un agent ne doit pas inventer une règle absente des spécifications. Il ajoute un réglage désactivé ou une constante clairement marquée `TODO-EQUILIBRAGE`, puis consigne le point dans le journal de décisions de ce document.

## 2. État du dépôt et décisions structurantes

Le dépôt utilise Django, un modèle utilisateur personnalisé `Blog.User`, des templates rendus côté serveur, du JavaScript natif, Django Channels, Django REST Framework et `django-constance`. La monnaie transversale existe déjà sous la forme `Blog.User.coins` et porte le nom de Diplodocoins. La configuration versionnée emploie SQLite.

Points à préserver :

- conserver `AUTH_USER_MODEL = "Blog.User"` ;
- conserver la base SQLite existante et les données des autres fonctionnalités ;
- créer `dinopark.db` pour toutes les données DiploPark, sans déplacer ni recopier les utilisateurs ;
- réutiliser `User.coins` pour la future boutique, les potions et les récompenses de classement ;
- ne pas réutiliser les modèles DinoWars : leurs dinosaures, équipes et combats ont une sémantique différente ;
- ne pas réutiliser `Blog.Market` pour le marché zoologique ;
- réutiliser le journal global `JournalEntry` pour signaler les événements, avec un rapport DinoPark détaillé séparé ;
- ne jamais démarrer de planificateur dans `AppConfig.ready()`.

### 2.1 Architecture retenue

Créer une application Django indépendante `dinopark`. Elle partage le projet et l'authentification, mais écrit ses modèles dans l'alias SQLite `dinopark` pointant vers un fichier `dinopark.db`. La base `default` existante continue de porter `Blog.User` et les autres fonctionnalités.

Ajouter un routeur `DinoparkDatabaseRouter` : lecture/écriture/migrations des modèles `dinopark` vers l'alias `dinopark`, tout le reste vers `default`. Les relations SQL inter-base sont interdites. `Park.owner_id` est un entier unique correspondant à `Blog.User.pk`; les services contrôlent l'existence et l'activité du compte dans `default`. Aucune requête ORM ne doit tenter `select_related` entre ces bases.

Arborescence cible :

```text
dinopark/
├── admin.py
├── apps.py
├── constants.py
├── forms/
├── management/commands/
├── migrations/
├── models/
│   ├── catalog.py
│   ├── park.py
│   ├── economy.py
│   ├── missions.py
│   ├── rankings.py
│   └── rewards.py
├── selectors/
├── services/
│   ├── ticks.py
│   ├── reproduction.py
│   ├── maintenance.py
│   ├── market.py
│   ├── weather.py
│   ├── missions.py
│   ├── rankings.py
│   ├── facilities.py
│   └── purchases.py
├── static/dinopark/{css,js,img}/
├── templates/dinopark/
├── tests/
└── urls.py
```

Ajouter `dinopark.apps.DinoparkConfig` à `INSTALLED_APPS` et `path("dinopark/", include("dinopark.urls", namespace="dinopark"))` aux URL racines. Toutes les pages héritent de `Blog/layout/base.html`.

### 2.2 Contraintes SQLite et séparation des bases

SQLite convient à 3–5 joueurs actifs, à condition de réduire les écritures longues et concurrentes :

- activer `PRAGMA foreign_keys=ON`, `journal_mode=WAL`, `busy_timeout=5000` et une durée de connexion courte ;
- garder chaque transaction atomique brève ;
- ne faire aucun appel réseau ni rendu HTML à l’intérieur d’une transaction ;
- traiter les calculs en mémoire, puis ouvrir une transaction uniquement pour vérifier l’état et écrire ;
- sérialiser les traitements globaux au moyen d’une ligne de verrou applicatif et d’une clé d’idempotence ;
- utiliser `select_for_update()` seulement comme indication portable : SQLite ne fournit pas de verrouillage de lignes comparable à PostgreSQL/MySQL ; la sûreté repose sur les transactions `atomic`, les contraintes uniques, les mises à jour conditionnelles et les reprises après `OperationalError: database is locked` ;
- sauvegarder séparément la base principale et `dinopark.db` avant toute migration ;
- ne jamais supposer qu'une opération `atomic()` couvre les deux alias ; les échanges de Diplodocoins utilisent une saga idempotente et une commande de réconciliation.

## 3. Modèle de données

Tous les montants sont des entiers. Aucun flottant ne sert à stocker argent, probabilités ou multiplicateurs : employer des points de base (`10000 = 100 %`) et des multiplicateurs en millièmes (`1000 = ×1`). Les codes métier sont des `SlugField` ASCII immuables.

### 3.1 Catalogue statique

| Modèle | Champs essentiels | Contraintes et index |
|---|---|---|
| `HabitatType` | `code`, `name`, `is_special`, `max_enclosures`, `display_order`, `active` | `code` unique ; 4 habitats normaux à 6 enclos, insectarium et vivarium à 1 |
| `Species` | `code`, `name`, `habitat`, `rarity`, `compatibility_group`, `base_buy_price`, `base_sell_price`, `lifespan_ticks`, `fertility_bp`, `maturity_ticks`, `spontaneous_birth_bp`, `acquisition_mode`, `active` | index `(habitat, rarity, active)` |
| `SpeciesVariant` | `species`, `code`, `name`, `is_albino`, `rarity`, prix et probabilités optionnels | unique `(species, code)` |
| `CompatibilityRule` | `species_a`, `species_b`, `is_compatible`, `reason` | paire canonique, unique ; validation interdisant `a=b` |
| `UnlockRule` | `species`, `rule_type`, `parameters` JSON, `priority`, `active` | les paramètres décrivent la condition spéciale sans code arbitraire |

Les données du catalogue sont versionnées dans `dinopark/data/catalog/*.json`. Une commande idempotente `seed_dinopark_catalog --version X` fait des `update_or_create`; elle ne supprime jamais une espèce possédée et désactive les entrées retirées.

### 3.2 Parc, enclos, individus et personnel

| Modèle | Champs essentiels | Contraintes et index |
|---|---|---|
| `Park` | `owner_id` entier unique, `cash` (ParkCoins), visiteurs, fidélité, prestige, prix d’entrée, `bonus_updates`, `is_paused`, `ruleset_version` | pas de FK inter-base ; un parc par identifiant utilisateur ; `cash >= 0` |
| `HabitatSlot` | `park`, `habitat_type`, `position`, `is_unlocked` | unique `(park, habitat_type, position)` |
| `Enclosure` | `slot` OneToOne, `name`, `quality_level`, `is_luxury`, `damage`, `cleanliness`, capacité de gabarit | plafond dur de 100 individus ; la santé affichée est calculée |
| `Animal` | `park`, `enclosure` nullable après décès, variante normale/albinos obligatoire, sexe, origine, naissance/acquisition, âge, santé, vie restante, parents, décès et cause | index vivants ; historique conservé et purge administrative explicite |
| `DailyVisit` | `park`, `visit_date`, `streak_after` | unique `(park, visit_date)` ; ne déclenche aucune mise à jour du parc |
| `StaffAllocation` | `enclosure`, `role`, `quantity`, `efficiency_bp` | unique `(enclosure,role)` ; quantité positive |
| `InventoryBalance` | `park`, `item_code`, `quantity` | unique `(park,item_code)` ; quantité non négative |

Les animaux restent individualisés : sexe, âge, filiation, santé et durée de vie sont nécessaires aux couples, naissances conditionnelles, albinos et missions. Les couples sont déduits des individus compatibles présents dans un enclos ; ne pas créer un modèle `Couple` persistant sauf si une règle future exige une union durable.

### 3.3 Économie et installations

| Modèle | Usage |
|---|---|
| `ParkLedgerEntry` | Grand livre de la monnaie interne au parc : montant signé, solde après, motif, référence, clé d’idempotence unique, date |
| `FacilityDefinition` | Catalogue hôtel, train et quatre boutiques uniquement |
| `Facility` | Installation possédée, niveau, état, date de dernière collecte/maintenance |
| `FacilityLevel` | Coût, capacité et effets par niveau, versionnés comme données |
| `ShopStock` | Stock par boutique et type de produit |
| `GlobalMarketCycle` | Créneau de demi-journée lié à une distribution de MAJ, heure d’effet, graine, statut ; clé de créneau unique |
| `MarketQuote` | Cycle, variante, achat, vente, volumes achetés/vendus, tendance ; bornes 50–200 % ; unique `(cycle,variant)` |
| `WeatherDay` | Date locale unique, météo, multiplicateurs et graine |

`Park.cash` est la monnaie de gestion propre au jeu. `User.coins` est la monnaie transversale rare. Toute modification de ces deux soldes passe par un service de grand livre, jamais directement dans une vue.

### 3.4 Ticks et événements

| Modèle | Usage |
|---|---|
| `TickRun` | parc, type `STANDARD/BONUS`, clé de mise à jour, météo/cycle, graine, version de règles, statut, résumé, début/fin |
| `TickEvent` | événement normalisé : naissance, décès, apparition, dégât, maladie, recette, mission ; payload JSON et liens facultatifs |
| `GlobalJobLock` | nom de tâche unique, propriétaire éphémère, expiration, dernier succès |

Contrainte unique `(park, tick_type, tick_key)` : rejouer une requête ne doit jamais appliquer un tick deux fois. La graine pseudo-aléatoire est dérivée de la clé du tick, du parc et d’un secret applicatif afin qu’un redémarrage produise le même résultat sans rendre les tirages prévisibles côté client.

Le détail des `TickEvent` ordinaires est conservé un mois. Les résumés, ledgers, décès, naissances rares, déblocages et événements nécessaires aux missions/classements sont conservés sans cette purge. La commande de purge doit d'abord vérifier que tous les agrégats requis existent.

### 3.5 Missions

| Modèle | Usage |
|---|---|
| `MissionDefinition` | code, nom, catégorie, description, cadence, dates, répétable, active, version |
| `MissionObjective` | mission, type d’objectif, cible facultative, quantité, paramètres JSON, ordre |
| `MissionReward` | monnaie du parc, Diplodocoins plafonnés, objet, potion, effet ou cosmétique |
| `MissionEnrollment` | parc, mission, état, progression globale, début, échéance, accomplissement, réclamation |
| `MissionObjectiveProgress` | inscription, objectif, valeur, terminé à |
| `MissionRewardGrant` | attribution idempotente, clé unique, détail JSON |

Importer les 605 missions de naissance, 44 missions avancées et 3 missions périodiques prévues par les spécifications via des fichiers de données validés. Les événements métier appellent `missions.record_event(...)`; aucune vue ne recalcule toutes les missions.

### 3.6 Classements et saisons

| Modèle | Usage |
|---|---|
| `RankingSeason` | code, début/fin, statut ; utilisé pour les historiques mensuels, sans versement automatique V1 |
| `RankingSnapshot` | saison, instant, type de classement, état final ou provisoire |
| `RankingEntry` | snapshot, parc, score, rang, ex æquo, détail JSON |
| `RankingRewardGrant` | date de récompense, `owner_id`, rang, activité, montant en Diplodocoins, clé idempotente |

Le snapshot quotidien du classement général par prestige de la veille verse 50 Diplodocoins au premier, 25 au deuxième et 10 à chaque joueur actif, cumulables. Les ex æquo reçoivent le même palier avec rang de compétition. La saga inter-base attribue chaque code exactement une fois.

### 3.7 Potions et boutique différée

Créer `PotionDefinition`, `PotionBalance`, `ActiveEffect`, `MetaOffer` et `MetaPurchase`. Ne créer aucun modèle VIP ou compagnon. La page boutique existe mais toutes les offres sont inactives au lancement. Les coûts doivent être validés avant activation.

### 3.8 Grand livre des Diplodocoins

Ajouter dans `Blog` un modèle `DiplodocoinLedgerEntry` lié à `User` : `amount`, `balance_before`, `balance_after`, `reason`, `source`, `idempotency_key` unique, `metadata`, `created_at`. Créer `Blog/services/currency.py` :

- `credit(user_id, amount, reason, idempotency_key, metadata)` ;
- `debit(...)`, qui refuse un solde insuffisant ;
- transaction courte, lecture fraîche du solde, `UPDATE ... WHERE coins >= amount` pour les débits ;
- création du journal dans la même transaction ;
- même résultat retourné si la clé a déjà été appliquée.

DiploPark utilise exclusivement ce service. Ajouter dans `dinopark.db` un `CrossDatabaseOperation` avec clé globale, type, état `PENDING/SITE_APPLIED/PARK_APPLIED/COMPLETED/FAILED`, payload et tentatives. Le mouvement dans `default` et l'effet dans `dinopark` ne sont jamais présentés comme une transaction atomique unique. Une reprise relit les deux ledgers et termine l'étape manquante. La migration des anciennes écritures directes de `coins` reste un lot séparé.

## 4. Back-end et contrats applicatifs

### 4.1 Principes

- vues minces : authentification, formulaire, appel de service, réponse ;
- règles dans `services/`, lectures composées dans `selectors/` ;
- aucune mutation par requête GET ;
- POST + CSRF + motif Post/Redirect/Get pour les pages HTML ;
- JSON uniquement pour les fragments interactifs qui en ont besoin ;
- toutes les actions économiques acceptent une clé d’idempotence ;
- les exceptions métier ont des codes stables (`INSUFFICIENT_FUNDS`, `INCOMPATIBLE_SPECIES`, etc.) ;
- dates métier en `Europe/Paris`, stockage conscient des fuseaux via Django.

### 4.2 Moteur de tick

`consume_park_update(park_id, update_kind, idempotency_key, now)` :

1. valider que le joueur demande volontairement une mise à jour disponible ;
2. réserver la clé via `TickRun` unique ;
3. charger parc, animaux, enclos, personnel, stocks, météo et marché ;
4. calculer un `TickPlan` immuable en mémoire ;
5. dans une transaction courte, revalider la version du parc et appliquer le plan ;
6. écrire ledger, événements, progressions de missions et résumé ;
7. marquer le run terminé ;
8. après commit, créer les entrées du journal global.

Ordre de calcul obligatoire : état initial → consommation/entretien → personnel → santé/dégâts → vieillissement/décès → reproduction/naissances spéciales → apparitions spontanées → visiteurs/recettes/installations → missions → score. Chaque étape reçoit la même graine dérivée et ne lit jamais l’heure système directement.

La première visite quotidienne appelle séparément `daily_visits.record(owner_id, date)` et ne lance jamais ce service. Si l’écriture échoue pour verrou SQLite, abandonner toute la transaction puis retenter au maximum 3 fois. Un run interrompu est récupérable grâce à sa clé, sa graine et `ruleset_version`.

### 4.3 Marché, météo et tâches

Commandes idempotentes :

```text
python manage.py dinopark_generate_market --at <iso-datetime>
python manage.py dinopark_generate_weather --date <YYYY-MM-DD>
python manage.py dinopark_snapshot_rankings
python manage.py dinopark_grant_daily_ranking_rewards --date <YYYY-MM-DD>
python manage.py dinopark_recover_jobs
python manage.py dinopark_reconcile_currency
python manage.py dinopark_purge_tick_details --older-than 30d
```

Un script Python serveur configure Django, détecte les chemins via les settings et appelle ces commandes. Le cron lance : marché à chaque distribution biquotidienne des mises à jour ; météo à 00:05 ; snapshot et récompenses de la veille après 00:10 ; récupération/réconciliation régulièrement ; purge mensuelle. Il n'existe aucun rattrapage de présence quotidienne.

Un seul processus écrit chaque cycle global. `GlobalJobLock` est acquis par création/mise à jour conditionnelle avec expiration ; la contrainte unique du cycle reste la protection ultime.

### 4.4 Services à exposer

- `parks.create_for_user`, `parks.get_dashboard` ;
- `enclosures.build`, `rename`, `upgrade`, `repair`, `move_animal` ;
- `animals.buy`, `sell`, `validate_compatibility` ;
- `staff.set_allocation` ;
- `inventory.buy_food`, `restock_shop` ;
- `facilities.build`, `upgrade`, `collect` ;
- `daily_visits.record`, `updates.consume_standard`, `updates.consume_bonus` ;
- `missions.enroll`, `record_event`, `claim_reward` ;
- `rankings.compute_score`, `snapshot`, `grant_daily_rewards` ;
- `meta.buy_offer`, `activate_potion`.

Chaque service possède des tests unitaires et retourne un objet résultat sérialisable, pas une réponse HTTP.

## 5. Routes, vues et formulaires

Routes initiales :

```text
/dinopark/                         tableau de bord
/dinopark/onboarding/              création guidée du parc
/dinopark/map/                     carte interactive du parc
/dinopark/habitats/                habitats et enclos
/dinopark/enclosures/<id>/         détail d’un enclos
/dinopark/animals/                 collection et filtres
/dinopark/market/                  marché dynamique
/dinopark/facilities/              installations
/dinopark/missions/                missions et récompenses
/dinopark/rankings/                saison et comparaison
/dinopark/journal/                 rapports détaillés
/dinopark/shop/                    potions et offres futures (fermée au lancement)
```

Actions POST nommées explicitement (`.../build/`, `.../buy/`, `.../claim/`) et protégées par `login_required`. Les objets sont toujours filtrés par `park__owner_id=request.user.pk`; aucune relation ORM inter-base n'existe. Ne jamais faire un `get(pk=...)` sans ce contrôle.

Formulaires Django pour prix d’entrée, construction, personnel, déplacement, achat/vente et activation. Validation répétée dans le service pour empêcher le contournement par requête forgée.

## 6. Front-end

### 6.0 Principe d’interface

DinoPark ne doit pas devenir une application graphique complexe. À l’exception de la carte du parc, l’interface reprend l’esprit du jeu de référence : pages Django simples, titres, texte, tableaux, listes, liens, formulaires et quelques jauges CSS. Une information métier doit toujours exister sous forme textuelle ; aucune illustration n’est requise pour comprendre ou utiliser une page.

Réserver l’essentiel du travail de conception front-end à **une seule vue riche : la carte interactive du parc**. Les autres pages privilégient la densité d’information, un chargement rapide et une maintenance facile.

### 6.1 Socle

Les pages étendent `Blog/layout/base.html` et alimentent `title`, `extra_css`, `content`, `extra_js`. CSS sous `static/dinopark/css/`, JavaScript sans framework sous `static/dinopark/js/`. Ne pas ajouter React, Vue, npm ou une bibliothèque de composants pour cette version.

Créer seulement les composants réutilisables nécessaires : barre de ressources, badge de rareté, jauge CSS, message d’état, résumé de tick, ligne de mission et confirmation. Les animaux, missions, classements, stocks et personnels sont présentés en listes ou tableaux HTML. Les fragments utilisent `{% include %}` et des contextes documentés dans `selectors/`.

### 6.2 Pages et états

- **Tableau de bord :** solde du parc, Diplodocoins, météo, prochain marché/tick, alertes, recettes, missions proches et classement, essentiellement en texte.
- **Carte :** accès visuel principal aux 24 emplacements d’enclos, à l’insectarium, au vivarium et aux installations ; sa conception est détaillée en section 6.4.
- **Habitats :** alternative textuelle complète à la carte, avec 4 tableaux de 6 emplacements et deux lignes spéciales ; états verrouillé/vide/construit/endommagé.
- **Enclos :** individus, sexes, âges, compatibilité, personnel, nourriture, santé, luxe, dégâts et actions.
- **Marché :** filtres habitat/rareté, tendance depuis le cycle précédent, disponibilité et confirmation d’achat/vente.
- **Installations :** hôtel, train et quatre boutiques ; niveau, coût, bénéfice et stock.
- **Missions :** onglets actives/terminées/archives, progression accessible en texte et barre visuelle.
- **Classement :** 3–5 joueurs, score, position, écart, date de snapshot, récompense bornée expliquée.
- **Boutique méta :** prix exclusivement en Diplodocoins, aucun symbole ni vocabulaire de paiement réel.

Prévoir les états vide, chargement, erreur, action déjà traitée et contenu indisponible. Toutes les actions critiques ont confirmation, bouton désactivé pendant l’envoi et message serveur. Les modales se ferment par Échap, gardent le focus, et les couleurs de rareté sont accompagnées d’un libellé.

### 6.3 JavaScript

Créer un utilitaire unique `dinopark/api.js` qui récupère le jeton CSRF, envoie `X-Requested-With`, gère les erreurs normalisées et empêche le double clic. Les pages n’embarquent pas de scripts inline. Le serveur reste fonctionnel sans JavaScript pour les actions principales.

### 6.4 Carte interactive — conception détaillée

#### 6.4.1 Périmètre

La carte est une **vue fixe illustrée et cliquable**, pas un moteur 3D, un éditeur de terrain ni une carte à déplacement libre. Elle représente toujours le même plan du parc. Le joueur construit et améliore des emplacements prédéfinis ; il ne déplace pas librement les bâtiments.

Elle contient :

- 24 emplacements d’enclos principaux : 6 pour chacun des 4 habitats ;
- 1 emplacement d’insectarium ;
- 1 emplacement de vivarium ;
- les emplacements fixes de l’hôtel, du train et des quatre boutiques, pour un total de 32 nœuds constructibles avec les enclos ;
- une zone météo sur trois jours ;
- des accès textuels au marché, aux missions, au classement et au journal ;
- une barre de statut avec monnaie du parc, Diplodocoins, visiteurs et prochain tick.

#### 6.4.2 Technique de rendu

Utiliser trois couches superposées dans un conteneur au ratio fixe :

1. **fond raster WebP** sans texte ni élément cliquable ;
2. **calque SVG inline** dont le `viewBox` définit le système de coordonnées stable ;
3. **panneau HTML** de détails, placé à côté de la carte sur écran large.

Le SVG contient un élément interactif par emplacement, avec identifiant métier stable (`enclosure-forest-1`, `facility-hotel`, etc.). Les formes SVG servent de zones cliquables et de contours d’état. Ne pas coder les coordonnées dans le JavaScript : les stocker dans `dinopark/data/map/layout-v1.json`, validé au démarrage/seed et chargé côté template sous forme JSON sûre.

Structure du fichier de plan :

```json
{
  "version": 1,
  "viewBox": [0, 0, 1600, 1000],
  "nodes": [
    {
      "code": "enclosure-forest-1",
      "kind": "enclosure",
      "target": {"habitat": "forest", "position": 1},
      "shape": {"type": "polygon", "points": [[120, 180], [260, 160], [280, 290]]},
      "label": [200, 220],
      "display_order": 10
    }
  ]
}
```

Le JSON décrit uniquement la géométrie et l’identité des emplacements. L’état du joueur vient de la base et est joint par `selectors.map.get_map_state(park)`. Ainsi, changer le dessin ne nécessite aucune migration de base de données.

#### 6.4.3 États visuels

Chaque nœud expose un état parmi : `locked`, `available`, `built`, `warning`, `damaged`, `upgradable`. Le serveur fournit aussi un libellé, un résumé textuel, une URL de détail et les actions autorisées. Le JavaScript ne déduit jamais les droits à partir de la couleur.

Codage minimal : contour et motif CSS pour l’état et point rouge d'alerte. Ne pas représenter individuellement les animaux. Le nom court et le nombre d’individus apparaissent uniquement au survol ou au focus. L’albinos, les naissances et autres événements apparaissent dans le panneau et le journal.

#### 6.4.4 Interactions

- survol/focus : surligner la zone et afficher son nom ;
- clic/Entrée/Espace : sélectionner le nœud et charger son résumé dans le panneau ;
- deuxième action explicite : ouvrir la page détaillée ou le formulaire de construction/amélioration ;
- filtres facultatifs : habitats, installations, alertes ;
- bouton « Voir la liste » toujours visible ;
- mise à jour après une action par remplacement du fragment d’état, sans recharger l’image de fond ;
- URL avec fragment ou paramètre `?focus=<code>` pour revenir au même emplacement ;
- aucune mutation directe au simple clic sur un emplacement.

La version 1 n’implémente ni glisser-déposer, ni zoom, ni placement libre. Sur mobile, la carte est masquée et remplacée par la liste textuelle complète.

#### 6.4.5 Contrat serveur

Ajouter la route `/dinopark/map/` et le selector `get_map_state`. Le contexte contient :

- `layout_version` et géométrie validée ;
- état global du parc et météo ;
- dictionnaire `nodes_by_code` avec état, compteurs, alertes, URL et permissions ;
- `last_tick_version` pour détecter une donnée périmée.

Une route GET `/dinopark/map/nodes/<code>/` peut rendre un fragment HTML de détail. Les constructions, réparations et améliorations restent des POST vers les services existants. Après succès, la réponse renvoie le fragment du nœud et sa nouvelle version. Toute requête périmée reçoit `409 STATE_CHANGED` et force le rechargement du panneau.

#### 6.4.6 Accessibilité et mode dégradé

Chaque zone SVG est un lien ou bouton focalisable avec `aria-label`, ordre clavier logique et état annoncé en texte. Le panneau utilise une région `aria-live="polite"`. Les textures complètent les couleurs. La page inclut après la carte une liste HTML compacte de tous les emplacements ; elle est visible sur demande et constitue l’interface complète sans JavaScript.

#### 6.4.7 Responsive et performances

- un seul fond WebP, avec variante basse résolution via `<picture>` si nécessaire ;
- SVG et icônes locaux, aucun moteur cartographique externe ;
- objectif : moins de 500 Ko pour les ressources initiales de la carte hors cache ;
- bureau : carte et panneau en deux colonnes ; tablette : panneau inférieur ; mobile : aucune carte, liste textuelle complète ;
- précharger seulement le fond courant ; ne pas charger les images des animaux sur la carte.

#### 6.4.8 Fabrication et validation du plan

1. réaliser un wireframe monochrome avec les 32 zones approximatives ;
2. faire valider lisibilité, regroupement des habitats et place des installations ;
3. figer les codes de nœuds ;
4. produire le fond final séparément des zones interactives ;
5. relever les polygones dans le `viewBox` ;
6. tester les états avec un jeu de données factice couvrant toutes les variantes ;
7. tester clavier, mobile, contraste et absence de JavaScript ;
8. seulement ensuite brancher les actions réelles.

Tests dédiés : tous les codes du layout correspondent à un emplacement connu ; aucun code dupliqué ; toutes les zones restent dans le `viewBox` ; tous les emplacements obligatoires sont présents ; chaque état possède libellé et classe ; navigation clavier complète ; sélection persistante ; réponse `409` sur version périmée ; budget de ressources respecté.

## 7. Administration et données initiales

L’admin doit permettre de rechercher et filtrer catalogue, parc, animaux, ticks, missions, saisons et achats. Les modèles de catalogue sont modifiables ; les ledgers et attributions sont en lecture seule hors action d’administration explicitement auditée. Interdire la suppression en cascade d’un catalogue déjà référencé.

Ajouter :

- `dinopark_validate_catalog` : codes, nombres attendus, compatibilités, références de missions, probabilités et récompenses ;
- `dinopark_seed --dry-run` : diff lisible avant application ;
- `dinopark_check_integrity` : soldes, animaux sans enclos, runs incohérents, récompenses doubles, limites d’habitats.

## 8. Migrations et déploiement SQLite

Ordre de migrations :

1. application et catalogue minimal ;
2. parc/enclos/animaux/stocks ;
3. économie, ticks, météo, marché ;
4. missions ;
5. classements ;
6. méta-achats et ledger Diplodocoins dans `Blog` ;
7. contraintes et index après import de test.

Procédure de production : arrêter les tâches, mettre le site brièvement en maintenance, sauvegarder et vérifier la base principale ainsi que `dinopark.db`, appliquer `migrate --database=default` puis `migrate --database=dinopark`, charger le catalogue sur l'alias dédié, exécuter les contrôles, reprendre les tâches et effectuer un test fumée. Le chemin de `dinopark.db` est défini par les settings et reste extérieur au code déployé autant que le permet l'hébergement.

Configurer les paramètres sensibles par variables d’environnement et désactiver `DEBUG` en production. Le secret Django et les identifiants de messagerie présents dans l’historique ne doivent jamais être recopiés dans ce plan, les logs ou les tickets.

## 9. Tests et qualité

### 9.1 Pyramide de tests

- **Unitaires :** compatibilité, prix, multiplicateurs, couples, tirages déterministes, albinos, apparitions, conditions spéciales, personnel, santé, luxe, dégâts, installations, score et récompenses.
- **Services avec DB :** transactions, idempotence, solde insuffisant, double clic, double mise à jour, présence quotidienne, saga inter-base et progression de mission.
- **Vues :** authentification, propriété, méthodes HTTP, CSRF, formulaires, redirections et JSON d’erreur.
- **Commandes :** relance du même cycle, reprise après échec, météo manquante, verrou expiré.
- **Intégration :** onboarding → construction → animaux → tick → naissance → mission → classement → récompense.
- **Régression :** connexion, tchat, HDV, paris, DinoWars et journal existants.

### 9.2 Cas SQLite obligatoires

Tester deux requêtes concurrentes sur achat, activation de potion et consommation de tick avec deux connexions. Accepter soit un succès et un refus métier, soit une reprise contrôlée ; jamais deux débits ou deux récompenses. Tester restauration depuis une copie et migration d’une base contenant déjà des utilisateurs.

### 9.3 Définition de terminé globale

- migrations réversibles et applicables sur des copies des deux bases ;
- catalogue validé aux quantités des spécifications ;
- aucun solde modifié hors service de ledger dans DinoPark ;
- aucun GET mutateur ;
- tests du lot et régressions passent ;
- pages clavier/mobile utilisables ;
- commandes relançables sans doublon ;
- admin et intégrité opérationnels ;
- documentation et journal de décisions mis à jour.

## 10. Lots d’implémentation distribuables

### Phase 0 — Socle et décisions

**DP-000 — Baseline.** Lancer les tests existants, figer versions Python/Django, documenter le chemin SQLite et la procédure de copie/restauration. Livrable : rapport de baseline.

**DP-001 — Application.** Créer `dinopark`, branchement settings/URL, page vide héritant du layout et squelette de tests. Dépend de DP-000.

**DP-002 — SQLite séparé.** Configurer l'alias `dinopark`, son routeur, WAL/busy timeout, migrations ciblées, sauvegarde des deux fichiers et diagnostic. Tester l'absence de migration DiploPark dans `default`. Dépend de DP-000.

**DP-003 — Gateway Diplodocoins inter-base.** Ledger dans Blog, `CrossDatabaseOperation` dans DiploPark, saga idempotente et réconciliation. Dépend de DP-002.

### Phase 1 — Catalogue et parc jouable

**DP-100 — Catalogue.** Modèles habitat, espèce, variante, compatibilité, déblocage ; seed et validation ; données prévues par la spec.

**DP-101 — Parc, présence et onboarding.** `Park.owner_id`, `DailyVisit`, emplacements, enclos, création idempotente et parcours de démarrage. Seed : 400 000 ParkCoins, billet à 5, 5 visiteurs, 15 MAJ bonus, aucune construction/animal/personnel ; +5 MAJ à la fin du tutoriel ; immunité aux dégâts jusqu'au tick 10. Implémenter l'aide débutant comme table/courbe versionnée sur 50 ticks, calibrable sans migration.

**DP-102 — Individus.** Animal, sexe, âge, filiation, déplacement et contrôles de capacité/compatibilité.

**DP-103 — Personnel et stocks.** Allocations, nourriture, inventaire et formulaires.

**DP-104 — UI habitats.** Composants, listes, détail enclos, responsive et accessibilité. Dépend de DP-100 à DP-103.

**DP-105 — Prototype de carte.** Wireframe, nomenclature des nœuds, `layout-v1.json`, calque SVG, panneau de détail factice et liste HTML équivalente. Aucune action économique réelle. Dépend de DP-100 et DP-101.

**DP-106 — Carte connectée.** Selector d’état, route, fragments, états visuels, focus clavier, responsive, gestion de version et branchement des actions déjà implémentées. Dépend de DP-102 à DP-105.

Jalon : un joueur peut créer son parc, construire un premier enclos, acquérir et gérer des individus, sans tick automatique.

### Phase 2 — Simulation

**DP-200 — Infrastructure de tick.** `TickRun`, `TickEvent`, graines, idempotence, reprise et rapport.

**DP-201 — Entretien.** Nourriture, personnel, santé, vieillissement, décès, luxe et dégâts.

**DP-202 — Reproduction.** maturité 5, longévité 50, taux initiaux 8,89/7,78/6,67/5,56/4,44 % selon rareté, réduction de moitié après 15 couples, albinos 5/20/50 %, apparitions spontanées tirées par enclos avec un compteur anti-malchance unique par parc et conditions spéciales.

**DP-203 — Météo.** génération quotidienne, effets et prévision globale.

**DP-204 — Marché.** cycle à chaque distribution biquotidienne, pression bornée ±10, variation volume de 1 % par unité, retour à la base borné ±5 %, variation totale ±10 %, cotations 50–200 %, achat/vente et historique ; albinos non achetables.

**DP-205 — Commandes et reprise.** script Python lancé par cron, verrou applicatif, récupération des runs et réconciliation inter-base ; aucun rattrapage de présence.

**DP-206 — UI simulation.** météo, marché, compte-rendu, alertes et journal global.

Jalon : plusieurs jours peuvent être simulés de manière déterministe sans double application.

### Phase 3 — Installations et économie longue

**DP-300 — Transport/hébergement.** hôtel 5 niveaux (`coût=100 000×n`, `revenu=10 000×n`) et train 10 niveaux (`coût=50 000×n`, `revenu=5 000×n`).

**DP-301 — Boutiques.** stocks, ventes et effets visiteurs.

**DP-303 — UI installations.** construction, amélioration, collecte, coûts et états.

Jalon : la boucle visiteurs–recettes–investissements est complète.

### Phase 4 — Missions

**DP-400 — Moteur d’événements.** définitions, objectifs, inscriptions, progression et récompense idempotente.

**DP-401 — Missions de naissance.** génération/import et tests des 605 missions.

**DP-402 — Missions avancées.** import et tests des 44 missions.

**DP-403 — Missions périodiques.** 3 missions actives (Semaine jurassique, Espèce du mois, Contrebandier), objectifs dépendant de la rareté, échéances, répétition et archivage.

**DP-404 — UI missions.** filtres, progression, réclamation et historique.

Jalon : toutes les missions applicables de la spec sont validées et jouables.

### Phase 5 — Comparaison et récompenses

**DP-500 — Score.** calcul explicable et snapshot.

**DP-501 — Snapshots quotidiens.** activité de la veille, ex æquo et historique.

**DP-502 — Récompenses.** 50 Diplodocoins au premier, 25 au deuxième et 10 à chaque actif de la veille, via saga idempotente inter-base.

**DP-503 — UI classement.** comparaison lisible pour 3–5 joueurs, progression et règles de récompense.

Jalon : un snapshot quotidien peut être rejoué sans doubler les crédits 50/25/10.

### Phase 6 — Potions et boutique différée

**DP-600 — Potions.** inventaire, activation, durée, cumul et expiration.

**DP-603 — Boutique méta fermée.** page informative, catalogue inactif et mécanisme d'activation administrative après validation des prix.

### Phase 7 — Stabilisation

**DP-700 — Admin et intégrité.** écrans, commandes de validation/réparation et exports de diagnostic.

**DP-701 — Sécurité.** audit d’autorisation, CSRF, IDOR, double soumission, validation et secrets.

**DP-702 — Performance.** profils de requêtes, `select_related/prefetch_related`, index, pagination et taille des rapports.

**DP-703 — Régression et restauration.** suite complète, copie/migration/restauration coordonnée des deux fichiers SQLite et test fumée.

**DP-704 — Durcissement transversal facultatif.** faire passer HDV, paris, jeux et DinoWars par la gateway Diplodocoins après tests dédiés.

**DP-705 — Calibration statistique.** Construire un simulateur sans HTTP réutilisant les services métier et exécuter au moins 2 000 parcours avec graines fixes. Explorer les pentes voisines de l'aide débutant candidate `100 000 - 2 000 × index` sur 50 ticks et de faibles variations des taux de fertilité. Produire médiane, P10/P90, faillites, dates des 2e/6e enclos, remplissage à 200 et complétion à 500. Écrire les valeurs retenues dans un fichier de règles versionné seulement si les quatre jalons et les espérances de 4→2 descendants sont satisfaits.

## 11. Répartition du travail entre agents

Un agent prend un ticket et ses tests. Les propriétaires de fichiers sont explicites :

- agent catalogue : `models/catalog.py`, `data/catalog`, seed/validation ;
- agent simulation : modèles tick + services de simulation ;
- agent économie : ledgers, marché et installations ;
- agent missions : modèles/services/données missions ;
- agent classement/méta : saisons, récompenses et boutique méta ;
- agent front textuel : templates simples et statiques hors carte, après stabilisation des contrats de selectors/forms ;
- agent carte : `data/map`, template de carte, SVG, `map.js`, `map.css` et tests d’interaction ; il ne modifie pas les services métier ;
- agent intégration : settings, URL racines, migrations transversales, cron et régressions.

Ne jamais faire travailler deux agents sur la même migration ou le même fichier de routage. Les agents de domaine créent leurs migrations ; l’agent d’intégration résout l’ordre final. Chaque PR/ticket contient : migration, tests, éventuelle donnée seed, note de compatibilité SQLite et mise à jour de ce plan si une décision change.

Ordre de parallélisation conseillé : DP-001/002/003 en séquence courte ; DP-100 puis DP-101/102/103 ; DP-105 peut démarrer dès que les emplacements sont figés, mais DP-106 attend les contrats métier ; DP-200 puis DP-201/202/203/204 en parallèle sur fichiers distincts ; installations et moteur de missions en parallèle après le tick ; classement après stabilisation du score ; méta après la gateway Diplodocoins.

## 12. Critères d’acceptation par jalon

1. **Socle :** nouvelle app accessible, aucune régression et copie SQLite restaurable.
2. **Vertical slice :** onboarding, carte avec tous les emplacements, alternative textuelle, enclos, deux espèces incompatibles, achat et premier tick visibles de bout en bout.
3. **Simulation :** 100 ticks déterministes passent sans solde négatif, double événement ni animal orphelin.
4. **Contenu :** 92 espèces, 29 variantes albinos et 652 missions/objectifs (605 naissance, 44 avancées, 3 périodiques), avec toutes les références valides.
5. **Long terme :** marché, météo, installations, missions et snapshots survivent aux relances des commandes.
6. **Production :** sauvegarde, migration, seed, intégrité, cron, retour arrière et test fumée documentés.

## 13. Journal des décisions et validations restantes

Décisions actées : nom DiploPark ; ParkCoins internes ; Diplodocoins transversaux ; base séparée `dinopark.db` ; rendu Django + JS natif ; présence quotidienne distincte des mises à jour ; aucun paiement réel ni équipe ; suppression VIP, sponsors, port, repos, roue, spectacles, Botanica, compagnon et parrainage ; tournois reportés ; boutique fermée au lancement ; carte desktop/tablette de 32 nœuds, masquée sur mobile ; pack 400 000 + 15/+5 MAJ ; protection 10 ticks ; longévité 50 et maturité 5 ; barèmes enclos/hôtel/train ; météo ; apparitions ; marché biquotidien ; trois missions périodiques.

Aucune question fonctionnelle ne bloque l'implémentation. Restent des validations automatiques : calibration de l'aide débutant et des taux de reproduction sur 2 000 parcours, validation structurelle des 92 espèces/compatibilités, puis contrôle des jalons : deuxième enclos vers 5 mises à jour, sixième vers 30, habitat privilégié largement rempli vers 200 et parc presque complet vers 500. Les prix Diplodocoins seront décidés avant l'ouverture ultérieure de la boutique, sans bloquer la V1 fermée.

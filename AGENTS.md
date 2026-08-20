# AGENTS.md — MyBlog / DiploPark

Ce fichier définit les règles obligatoires pour tout agent travaillant dans ce dépôt. Elles s’appliquent à toute l’arborescence, sauf instruction plus précise dans un `AGENTS.md` enfant.

## 1. Objectif du projet

Ajouter **DiploPark**, un jeu de gestion de parc préhistorique, au site Django existant sans régression sur le blog, le tchat, l’hôtel des ventes, les paris, DinoWars ni les autres fonctionnalités déjà déployées.

DiploPark reprend des mécaniques générales de gestion observées sur un jeu de zoo, mais son code, ses textes, ses données, ses noms et ses ressources graphiques doivent être originaux. Ne jamais copier du code source, des images, des textes ou des éléments protégés provenant d’un autre site.

## 2. Sources de vérité

Avant toute modification DiploPark, lire dans cet ordre :

1. `AGENTS.md` ;
2. `docs/diplopark/dinopark-specifications.md` ;
3. `docs/diplopark/diplopark-equilibrage-consolide.md` ;
4. `docs/diplopark/dinopark-plan-implementation.md` ;
5. les fichiers existants concernés et leurs migrations.

Ordre d’autorité en cas de contradiction :

1. le ticket ou la demande explicite en cours ;
2. `diplopark-equilibrage-consolide.md` pour les constantes chiffrées ;
3. `dinopark-specifications.md` pour les règles fonctionnelles ;
4. `dinopark-plan-implementation.md` pour l’architecture et l’ordre des travaux ;
5. le comportement historique du dépôt.

Ne pas inventer une règle manquante. Si une ambiguïté change la base de données, l’économie, une récompense ou une règle irréversible, la signaler et arrêter uniquement la partie concernée. Continuer les travaux indépendants non bloqués.

## 3. Périmètre V1

La V1 comprend notamment :

- quatre habitats principaux comportant six enclos chacun ;
- un Insectarium et un Vivarium à enclos unique ;
- 92 espèces et 29 variantes albinos ;
- individus, sexes, âge, santé, filiation, reproduction et décès ;
- personnel, nourriture, dégâts et enclos de luxe ;
- hôtel, train et quatre boutiques ;
- marché biquotidien, météo et apparitions spontanées ;
- 605 objectifs de naissance, 44 missions avancées et 3 missions périodiques ;
- classements adaptés à 3–5 joueurs et récompenses en Diplodocoins ;
- interface principalement textuelle ;
- carte interactive desktop/tablette de 32 nœuds, avec alternative HTML textuelle.

Sont exclus de la V1 : île aux dinos, musée, explorateur, espionnage, laboratoire, équipes, dons, port, aires de repos, grande roue, spectacles, Botanica, VIP, sponsors, compagnon, parrainage, paiements réels et tournois actifs.

La boutique en Diplodocoins doit être visible mais fermée au lancement. Ne créer aucune offre achetable sans nouvelle décision explicite.

## 4. Architecture obligatoire

### 4.1 Django et bases SQLite

- Conserver la base existante comme alias Django `default`.
- Stocker les modèles DiploPark dans une base SQLite séparée, alias `dinopark`, fichier `dinopark.db`.
- Utiliser un routeur Django explicite pour envoyer uniquement les modèles DiploPark vers `dinopark`.
- Ne créer aucune clé étrangère entre les deux bases.
- Référencer l’utilisateur principal par un `owner_id` entier validé par un service dédié.
- Ne jamais supposer qu’un `transaction.atomic()` couvre les deux bases.
- Toute opération touchant simultanément ParkCoins et Diplodocoins doit utiliser la saga idempotente et la réconciliation prévues dans le plan.
- Configurer SQLite avec WAL, `busy_timeout` et transactions courtes.
- Toutes les migrations doivent être applicables et testées séparément sur `default` et `dinopark`.

### 4.2 Organisation du code

Préférer une application Django `dinopark` structurée par domaine :

```text
dinopark/
  models/
  services/
  selectors/
  forms/
  management/commands/
  templates/dinopark/
  static/dinopark/
  data/
  tests/
```

- Les vues orchestrent HTTP, formulaires, permissions et messages ; elles ne portent pas les règles métier.
- Les mutations passent par des services transactionnels.
- Les lectures complexes passent par des selectors.
- Les constantes d’équilibrage sont dans des fixtures ou un ruleset versionné, jamais dispersées dans les vues ou templates.
- Les montants sont des entiers.
- Les probabilités utilisent des points de base (`10000 = 100 %`) et les multiplicateurs des entiers documentés.
- Les codes métier sont ASCII, immuables et uniques.
- Les événements significatifs utilisent des clés d’idempotence.

### 4.3 Sécurité HTTP

- Aucun `GET` ne doit modifier un état.
- Toute mutation utilise `POST`, protection CSRF et vérification de propriété serveur.
- Ne jamais accepter directement un `park_id`, `animal_id` ou `enclosure_id` sans vérifier qu’il appartient à l’utilisateur connecté.
- Protéger achats, ventes, récompenses, ticks et potions contre les doubles soumissions.
- Ne jamais écrire de secret, mot de passe, cookie ou jeton dans le code, les fixtures, les logs, les tests ou la documentation.
- Ne pas modifier les identifiants ou secrets existants sauf demande explicite.

## 5. Règles fonctionnelles structurantes

- Capital initial : 400 000 ParkCoins.
- Billet initial : 5 ; visiteurs de base : 5.
- Réserve initiale : 15 MAJ bonus ; fin du tutoriel : +5.
- Aucun enclos, animal ou personnel offert.
- Immunité aux dégâts pendant les 10 premières MAJ.
- Maturité standard : 5 MAJ ; longévité standard : 50 MAJ.
- Albinos non achetables ; prestige albinos ×5.
- Variantes albinos : 5/20/50 % selon les parents et 70 % sous potion.
- Enclos : capacités de gabarit 40/70/100 ; plafond absolu de 100 individus.
- Construction nue : 2 500 ; améliorations 75 000 et 180 000 ; luxe 20 000.
- Hôtel : 5 niveaux, coût du palier `100000 × niveau`, revenu total `10000 × niveau`.
- Train : 10 niveaux, coût du palier `50000 × niveau`, revenu total `5000 × niveau`.
- Marché recalculé à chaque distribution biquotidienne des MAJ.
- Apparitions tirées pour chaque enclos admissible avec un compteur anti-malchance unique au parc.
- Les valeurs détaillées restent celles de `diplopark-equilibrage-consolide.md`.

Ne pas « simplifier » silencieusement une de ces règles. Toute optimisation doit conserver le résultat métier et les garanties d’idempotence.

## 6. Moteur de mise à jour

Une MAJ doit être déterministe pour une même clé, un même ruleset et une même graine.

Ordre obligatoire :

1. verrouillage et contrôle d’idempotence ;
2. chargement de l’état et des snapshots globaux ;
3. consommation et entretien ;
4. personnel ;
5. santé et dégâts ;
6. vieillissement et décès ;
7. reproduction et variantes ;
8. naissances conditionnelles ;
9. apparitions spontanées ;
10. visiteurs, recettes et installations ;
11. missions ;
12. prestige, score et écritures comptables ;
13. rapport et événements.

Le calcul doit produire un plan immuable en mémoire, puis l’appliquer dans une transaction courte après revalidation de la version du parc. Rejouer la même clé ne doit jamais débiter, créditer, faire naître ou tuer deux fois.

La visite quotidienne ne déclenche jamais une MAJ du parc.

## 7. Interface

### 7.1 Interface générale

- Rendu Django côté serveur en priorité.
- JavaScript natif uniquement, sauf décision explicite contraire.
- HTML sémantique, formulaires classiques et amélioration progressive.
- Toute action essentielle reste possible sans JavaScript.
- Les animaux, missions, stocks, personnels et classements utilisent principalement listes et tableaux.
- Prévoir états vides, erreurs, confirmations, pagination et navigation clavier.
- Respecter les styles existants du site avant d’introduire de nouveaux composants.

### 7.2 Carte interactive

La carte est la seule interface nécessitant une conception visuelle approfondie.

- Fond aérien original au format WebP.
- Zones interactives SVG superposées, coordonnées stockées dans un fichier de layout versionné.
- 32 nœuds constructibles : 24 enclos principaux, Insectarium, Vivarium, hôtel, train et quatre boutiques.
- Survol/focus : nom, état, population et alerte.
- Navigation clavier complète et focus visible.
- Alternative HTML textuelle exposant exactement les mêmes destinations et actions.
- Carte masquée sur mobile ; utiliser la liste textuelle.
- Aucun état économique ne doit être déduit du DOM ou géré uniquement côté client.
- Ne pas générer le fond final avant validation du wireframe et des 32 identifiants de nœuds.

Les changements de `map.js`, `map.css`, du SVG ou du fichier de layout appartiennent au lot carte. Éviter de les mélanger à une migration ou à une modification du moteur économique.

## 8. Tests obligatoires

Chaque ticket doit ajouter ou mettre à jour ses tests. Ne pas considérer un ticket terminé parce que le scénario heureux fonctionne manuellement.

Minimum attendu selon le lot :

- tests unitaires des formules et règles ;
- tests de services avec base de données ;
- permissions, CSRF, méthodes HTTP et propriété des objets ;
- idempotence et double soumission ;
- migrations sur base vide et copie représentative ;
- isolation des bases `default` et `dinopark` ;
- tests SQLite avec deux connexions pour les mutations critiques ;
- tests d’intégration de la tranche verticale ;
- tests de non-régression des applications existantes ;
- accessibilité clavier et alternative textuelle pour la carte.

Avant de terminer un ticket :

1. identifier les commandes officielles du dépôt dans le README, la CI ou la configuration ;
2. exécuter les tests ciblés ;
3. exécuter la suite de régression raisonnablement pertinente ;
4. exécuter les contrôles Django ;
5. signaler précisément tout test non exécuté et pourquoi.

Ne pas inventer une commande de test. Si le dépôt n’en documente aucune, inspecter `manage.py`, les fichiers de dépendances, la configuration CI et les paramètres Django, puis employer la commande minimale appropriée.

## 9. Calibration statistique

Les valeurs validées ne doivent pas être ajustées intuitivement pendant l’implémentation.

Créer un simulateur sans HTTP réutilisant les vrais services métier. Il doit exécuter au moins 2 000 parcours avec graines reproductibles et mesurer :

- médiane, P10 et P90 du deuxième enclos, du sixième, du remplissage à 200 MAJ et de la complétion à 500 ;
- faillites et blocages ;
- population, trésorerie, recettes et dépenses ;
- nombre moyen de descendants par couple et par rareté ;
- distribution des météos et apparitions.

Seules la pente du bonus débutant et de faibles corrections des taux reproductifs peuvent être calibrées automatiquement. Enregistrer le résultat dans un ruleset versionné et produire un rapport comparatif. Ne pas modifier les autres constantes sans validation humaine.

## 10. Méthode de travail d’un agent

### Avant de coder

1. lire les sources de vérité ;
2. inspecter l’état Git et préserver les changements existants ;
3. localiser les modèles, settings, URL, templates, tests et migrations concernés ;
4. reformuler le périmètre du ticket et ses critères d’acceptation ;
5. identifier les dépendances et risques de migration ;
6. ne modifier que les fichiers nécessaires.

### Pendant le travail

- Avancer de manière autonome dans le périmètre autorisé.
- Préférer une tranche verticale fonctionnelle à une grande quantité de code incomplet.
- Faire des changements petits, cohérents et réversibles.
- Ne pas écraser ni reformater des modifications sans rapport avec le ticket.
- Ne pas supprimer une donnée, migration ou API existante pour faire passer les tests.
- Ne pas contourner un test ; corriger la cause.
- Ne pas ajouter de dépendance sans justification et vérification de sa compatibilité.
- Mettre à jour la documentation lorsqu’un contrat, modèle ou comportement change.

### Compte rendu obligatoire

À la fin, fournir :

- résultat fonctionnel obtenu ;
- fichiers et migrations modifiés ;
- commandes exécutées et résultat des tests ;
- décisions ou hypothèses prises ;
- risques et travaux restant à faire ;
- absence ou présence de changement manuel requis pour le déploiement.

Ne jamais annoncer « terminé » si les tests ciblés échouent, si une migration n’a pas été exercée ou si une valeur temporaire est présentée comme définitive.

## 11. Découpage et propriété des fichiers

Un agent ne traite qu’un ticket DP principal à la fois, sauf demande explicite.

Répartition recommandée :

- **catalogue** : modèles de catalogue, `data/catalog`, seed et validation ;
- **simulation** : ticks, santé, âge, reproduction, météo et apparitions ;
- **économie** : ledgers, marché, installations et boutiques ;
- **missions** : modèles, services et fixtures de missions ;
- **classement/méta** : snapshots, récompenses et passerelle Diplodocoins ;
- **front textuel** : templates, formulaires et composants hors carte ;
- **carte** : layout, SVG, JavaScript, CSS et tests d’interaction ;
- **intégration** : settings, routeurs, URL racines, cron, sauvegarde et régressions.

Deux agents ne doivent pas modifier simultanément la même migration, le routeur de base, les settings centraux ou le même fichier de données. Si plusieurs tâches sont parallélisées, utiliser des branches ou worktrees séparés et définir explicitement les propriétaires de fichiers.

## 12. Ordre d’implémentation

Respecter les dépendances du plan :

1. DP-000 à DP-003 — intégration, base séparée et monnaie ;
2. DP-100 à DP-106 — catalogue, parc, individus, interface et prototype de carte ;
3. DP-200 à DP-206 — moteur de simulation ;
4. DP-300 à DP-303 — installations et économie longue ;
5. DP-400 à DP-404 — missions ;
6. DP-500 à DP-503 — classements et récompenses ;
7. DP-600 et DP-603 — potions et boutique fermée ;
8. DP-700 à DP-705 — intégrité, sécurité, performance, restauration et calibration.

Ne pas commencer le graphisme final de la carte, les 652 fixtures de missions ou le catalogue complet avant validation de la tranche verticale minimale : création du parc → construction d’un enclos → acquisition d’un couple → personnel → MAJ → rapport.

## 13. Actions nécessitant une validation humaine

Un agent peut coder, migrer une base de test, créer des fixtures, lancer les tests et préparer une pull request de manière autonome.

Il doit demander une validation avant :

- toute migration destructive ou irréversible sur des données réelles ;
- toute modification d’un secret ou de la configuration de production ;
- tout déploiement, redémarrage ou exécution de cron en production ;
- toute activation d’offre en Diplodocoins ;
- tout changement d’une constante validée hors calibration autorisée ;
- toute suppression ou réécriture importante d’une application existante ;
- toute fusion dans la branche protégée si le workflow ne prévoit pas explicitement la fusion automatique.

## 14. Définition globale de « terminé »

Un lot est terminé seulement si :

- le comportement respecte les spécifications et le ruleset ;
- les migrations sont réversibles et testées sur le bon alias ;
- les écritures économiques sont auditées et idempotentes ;
- les tests ciblés et régressions pertinentes passent ;
- aucun secret ni donnée sensible n’est introduit ;
- l’interface est utilisable au clavier et possède les états vides/erreurs requis ;
- les commandes planifiées sont relançables sans doublon ;
- la documentation et les fixtures sont synchronisées ;
- le compte rendu final permet à un autre agent de reprendre sans reconstituer le contexte.

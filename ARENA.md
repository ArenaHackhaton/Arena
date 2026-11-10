# More than a Hack 2027 — Phase 1 : Possession du ballon (guide complet en français)

Organisé par **Metrica Sports**, **FC Barcelona (Barça Innovation Hub)** et **Mobile World Capital Barcelona**, au Talent Arena de Barcelone.
Dépôt officiel : https://github.com/metrica-sports/more-than-a-hack-2027

---

## 1. Le défi en une phrase

**Pour chaque frame du match, dire quelle équipe a le ballon, ou si le ballon est mort.**

- Match : **FC Barcelona vs Athletic Club**, LaLiga EA Sports 2024-25, journée 2
- `H` = Home = **Barcelona** ; `A` = Away = **Athletic Club**
- **199 319 frames** à 25 fps (environ 2 h 15 de vidéo), dont **158 857 notées** (environ 106 min de jeu)
- Notation 100 % automatique : pas de jury, pas de présentation. Seul le chiffre compte.
- Changement par rapport à 2026 : l'édition précédente était libre et jugée par un jury. En 2027, il y a une seule question et un seul score.

---

## 2. Les 4 étiquettes

| label | signification |
|---|---|
| `H` | Barcelona a le ballon, ballon vivant |
| `A` | Athletic a le ballon, ballon vivant |
| `D` | ballon mort (hors jeu, arrêt) |
| `X` | pas de réponse (abstention) |

- **Pas de propriétaire du ballon mort.** Quand le ballon est mort, la réponse est `D`, même si le tracking désigne une équipe.
- **Trois états seulement dans la vérité terrain** : `H`, `A`, `D`. Il n'y a ni « contesté », ni « transition », ni « inconnu ».

---

## 3. Les règles de possession (CHALLENGE.md)

- Quand le ballon est en jeu, **une équipe a toujours la possession**.
- **Changement de possession** : un joueur adverse prend le **contrôle** du ballon.
- Ballon disputé ou libre : **la possession reste à la dernière équipe** qui l'avait.
- Après chaque arrêt de jeu, le possesseur à la reprise est clair.
- Ce qui **n'est PAS** un changement de possession :
  - une simple touche sans contrôle
  - une déviation de passe qui ne l'intercepte pas
  - un duel aérien gagné sans contrôle derrière
- Indices proposés pour reconnaître le « contrôle » : un joueur garde le ballon quelques secondes, ou une équipe enchaîne plus de 2 passes.
- **Une possession = une suite maximale d'une même équipe, ballon vivant.**
  - `H H H A A` = 2 possessions
  - `H H D D H H` = 2 possessions séparées par un arrêt, et non une seule
- **Le ballon mort n'est jamais une possession.**
- **Comment la vérité terrain est construite** : à partir du tracking **corrigé**, de façon mécanique. Une frame vaut `D` là où le tracking corrigé marque le ballon mort, sinon elle prend l'équipe que ce tracking désigne. Il n'y a ni lissage ni retouche manuelle.
- En cas de doute sur une règle, **les 5 minutes publiques de vérité terrain font foi**.

---

## 4. Les données (DATA.md)

### 4.1 Les deux caméras

| | **tactical** (la référence) | **broadcast** (optionnelle) |
|---|---|---|
| rôle | la ligne *i* de la soumission = la frame *i* de cette vidéo | **non synchronisée** avec la tactical |
| vidéo | 199 319 frames, 25 fps, 1920×1080 | sa propre timeline, avec coupures et ralentis |
| tracking (ATD) | 199 319 enregistrements | 164 488 |
| homographie | 199 319 lignes, **100 %** utilisables | 164 488 lignes, **65,8 %** utilisables |
| Smart Tagging | 638 instances | — |
| emplacements de tracking | 46 | 51 |
| ballon visible | 56,9 % des frames | 50,5 % |

> Si ton fichier fait environ 164 000 lignes, tu as indexé la broadcast par erreur.

### 4.2 Arborescence attendue

```
data/
├─ tactical/
│  ├─ BAR-ATH_tactical.mp4
│  ├─ BAR-ATH_tactical_atd.xml              métadonnées du tracking
│  ├─ BAR-ATH_tactical_atd.txt              tracking joueurs + ballon
│  ├─ BAR-ATH_tactical_homography.csv
│  └─ BAR-ATH_tactical_smart_tagging.xml
└─ broadcast/
   ├─ BAR-ATH_broadcast.mp4
   ├─ BAR-ATH_broadcast_atd.xml
   ├─ BAR-ATH_broadcast_atd.txt
   └─ BAR-ATH_broadcast_homography.csv
```

`games.py` construit tous les chemins. La variable `MTAH_DATA_DIR` permet de déplacer le dossier. `data/` est dans le `.gitignore` : **ne jamais le commit**.

### 4.3 Tracking automatique (ATD)

- Format FIFA/EPTS : un XML de métadonnées et un TXT brut. Se lit avec `kloppy` :
  ```python
  from kloppy import metrica
  from games import asset_paths
  p = asset_paths()
  ds = metrica.load_tracking_epts(meta_data=p["atd_meta"], raw_data=p["atd_raw"])
  df = ds.to_df()   # frame_id, ball_x, ball_y, 1_x, 1_y, 1_s, ...
  ```
- Le TXT contient, par frame : `x, y, vitesse` pour les 46 emplacements, puis `x, y, vitesse` du ballon. **Il ne contient ni le propriétaire du ballon ni l'état vivant/mort** : c'est à toi de les déduire.
- **Coordonnées normalisées entre 0 et 1.** Pour avoir des mètres, multiplie par 105,3 × 68,0 (valeurs de `games.py`).
- **Aucune identité de joueur** : 46 emplacements « Track 1…46 » pour 22 joueurs. Ils apparaissent, disparaissent et échangent leurs identités. Tu ne connais que l'**équipe** de chaque emplacement. Il y a en moyenne 20,5 objets suivis par frame notée.
- Sens d'attaque en 1re mi-temps : Barcelona de gauche à droite, Athletic de droite à gauche.
- **Le ballon manque sur 43 % des frames, et sur 41 % des frames notées**, surtout dans les moments importants : surface encombrée, duels aériens, tacles. Les valeurs manquantes valent `NaN`. **Prévois ce cas dès le premier jour.**

### 4.4 Smart Tagging

- Annotation tactique **automatique** (pas une vérité terrain) : 638 phases ou coups de pied arrêtés, au format SportsCode XML.
- Codes : PLAYERS IN THE BOX (97), BALL IN FINAL THIRD (93), BALL IN THE BOX (72), PROGRESSION (66), DEFENDING IN MIDDLE THIRD (66), SET PIECES (59), CREATING CHANCES (30), DEFENDING IN DEFENSIVE THIRD (30), LONG BALL (29), ATTACKING/DEFENSIVE TRANSITION (24 chacun), BUILD UP (22), DEFENDING IN ATTACKING THIRD (22), GOALS (4)
- Tag `Team` : Barcelona (314), Atletic Club (288), **N/A (36)**, dont **toutes les touches**.
- Tag `Type` des coups de pied arrêtés : Throw-in 26, Corner 12, Goal Kick 10, Free Kick 5, Kick Off (After Goal) 4, Kick Off (Start) 2
- **Temps en secondes depuis la première frame tactical** : `frame = round(secondes * 25)`
- Pièges :
  - Les colonnes de tags sont en Title Case (`Team`) et les codes en MAJUSCULES : compare sans tenir compte de la casse.
  - `Max Players in the box` est une **chaîne de caractères** (`"7+"`).
  - **Les intervalles sont des phases, pas des possessions.** Les recopier tels quels importe leurs erreurs.
- C'est un **a priori gratuit et fort** : chaque phase porte une équipe, et chaque coup de pied arrêté correspond à une reprise de jeu, donc à la fin d'un ballon mort.

### 4.5 Homographie

- Une matrice 3×3 par frame, qui projette les coordonnées normalisées du terrain (0–1) vers les pixels.
- CSV : `frame,h00..h22,reprojection_error,valid`. On obtient la matrice avec `row[1:10].reshape(3,3)`.
- **Vérifie `valid`** : à 0, la matrice vaut `NaN`. La tactical est valide partout. La broadcast ne l'est que sur 65,8 % des frames (ralentis, gros plans, public), avec 122 trous dont le plus long dépasse 1 min 30.
- `reprojection_error` : plus c'est bas, mieux c'est. Médiane tactical de 0,24 pendant le jeu, la broadcast monte jusqu'à 304.

### 4.6 Alignement des frames ⚠️

| source | index | vers la ligne de soumission |
|---|---|---|
| soumission | `0 … 199318` | — |
| **ATD** | `frame_id` **`1 … 199319`** | **`frame = frame_id - 1`** |
| Smart Tagging | secondes | `round(sec * 25)` |
| homographie | `0 … 199318` | identique |

### 4.7 Frames notées

| période | frames | notée ? |
|---|---|---|
| avant le match | 0 – 11 184 | non |
| **1re mi-temps** | **11 185 – 90 651** | **oui** |
| mi-temps | 90 652 – 110 807 | non |
| **2e mi-temps** | **110 808 – 190 197** | **oui** |
| après le match | 190 198 – 199 318 | non |

**Piège** : la 2e mi-temps est notée dès la frame 110 808, mais le coup d'envoi n'a lieu qu'à la frame **113 742**. Les **2 934 frames** entre les deux sont toutes `D`.
`games.half_video_blocks("BAR-ATH")` renvoie `[(1, 11185, 90651), (2, 110808, 190197)]`.

### 4.8 Vérité terrain publique

`evaluation/gt/BAR-ATH_possession_gt_public.csv` : frames **11 185 – 18 684**, soit les 5 premières minutes. Elle contient H 3 454, A 2 577, D 1 469, et **17 possessions de 14,2 s en moyenne**. Tout le reste vaut `X`.

---

## 5. La notation (EVALUATION.md) — à lire avant d'optimiser quoi que ce soit

### macroF1 (vue frame par frame, sert à départager les ex æquo)
- Moyenne des F1 de `H`, `A` et `D` sur les frames notées.
- Le plancher est d'environ 0,16, pas 0. Un écart **inférieur à 0,01 est du bruit**.

### spellF1 (sert au CLASSEMENT)
- Chaque possession compte **comme un seul objet**, quelle que soit sa durée.
- Les possessions prédites sont associées une à une aux vraies selon leur **IoU temporel**, puis le F1 est moyenné sur les seuils 0,3 / 0,4 / 0,5 / 0,6 / 0,7.
- Une prédiction constante ou aléatoire donne **0**.
- Sensibilité au décalage : un retard de 1 frame est gratuit (1,0000), 3 frames donnent 0,98, 8 frames 0,89, **1 seconde 0,65**.
- Un écart **inférieur à 0,04 est du bruit** sur le match complet.

### Comment `X` est compté
- **macroF1** : un `X` sur une frame notée compte comme une erreur.
- **spellF1** : chaque `X` est **remplacé par ton dernier label non-`X` de la même mi-temps** (en début de mi-temps, par le suivant).
  - En **plein milieu d'une possession** (ballon perdu de vue) : `X` est gratuit, et plus sûr qu'une supposition qui couperait la possession en deux.
  - **Au moment d'une transition** : propose un label, sinon l'ancien label continue après le changement de possession.

### Les baselines (même algorithme, seule la fenêtre de lissage change)
Algorithme : joueur suivi le plus proche du ballon, puis vote majoritaire sur une fenêtre.

| baseline | macroF1 (match) | spellF1 (match) | spellF1 (5 min publiques) |
|---|---|---|---|
| raw | 0,6532 | 0,0486 | 0,0378 |
| smooth25 | **0,6752** | 0,1996 | 0,2868 |
| **smooth50** | 0,6724 | **0,2433** ← seuil à battre | 0,3256 |
| smooth125 | 0,6356 | 0,2242 | **0,4242** ← trompeur |

**Leçon** : régler le lissage sur les 5 minutes publiques fait **choisir la mauvaise option**. Une seule possession ratée y coûte environ 6 points. Utilise la fenêtre publique uniquement pour vérifier que ton pipeline est **correct**. Utilise `--bootstrap 1000` pour savoir si un écart est réel.

La spécification exacte des métriques se trouve dans `evaluation/possession_metrics.py` (environ 720 lignes). En cas de désaccord avec la doc, **c'est le code qui fait foi**.

---

## 6. La soumission (SUBMISSION.md)

### 6.1 Le fichier CSV
```
frame,label
0,X
1,X
...
11185,A
...
199318,X
```
- En-tête exact : `frame,label`
- **Exactement 199 319 lignes**, `frame` de 0 à 199318 dans l'ordre (sert à détecter un décalage d'une ligne)
- Labels `H`/`A`/`D`/`X` (la casse est tolérée)
- **Aucune cellule vide** : mets `X` pour t'abstenir
- UTF-8, sans colonne d'index, environ 1,9 Mo

### 6.2 Les 3 livrables
1. **Le CSV**, qui est le seul élément noté.
2. **Un dépôt de code PUBLIC** : code source, dépendances figées, instructions, et la commande qui **régénère exactement le même fichier**. **Sans les données du match.**
3. **Un document technique court** (PDF ou MD, quelques pages) :
   - l'approche et pourquoi tu l'as choisie
   - les données utilisées et celles que tu as **abandonnées**
   - les données d'entraînement : source, qui les a annotées, en quelle quantité (rien sur ce match)
   - les règles de possession implémentées : ballons libres, duels, reprises de jeu
   - la gestion du tracking manquant ou bruité
   - les limites et ce que tu améliorerais
   - comment reproduire le résultat

### 6.3 Comment soumettre
- Un **Google Form** (le lien arrive par e-mail aux inscrits), avec le nom d'équipe, le CSV, l'URL du dépôt et le document.
- Nomme tes fichiers **`<nom_equipe>.csv`** et **`<nom_equipe>.pdf`**.
- Il faut un compte Google. **Une seule réponse par équipe**, modifiable : c'est la dernière avant la date limite qui compte.
- **Pas de classement en direct ni de retour.** Lance `validate_submission.py` sur **le fichier exact** que tu envoies.
- **Date limite : 17 novembre 2026.** Résultats avant le 26 novembre 2026. Les organisateurs peuvent relancer le dépôt du gagnant pour vérifier.

---

## 7. Les règles (RULES.md)

### ✅ Autorisé
- **N'importe quelle méthode**, à deux conditions : les organisateurs peuvent y accéder et l'inspecter, et le document technique l'explique.
- Tout langage, framework, modèle pré-entraîné, LLM (hébergé ou local), données externes sur **d'autres matchs**.
- Améliorer ou remplacer le tracking avec **tes propres algorithmes** (détecteur, suivi, reconnaissance d'événements).
- Méthodes non supervisées ou auto-supervisées, pseudo-labels **produits par un algorithme**.
- **Regarder la vidéo** et inspecter les données pour comprendre et déboguer.
- Annoter à la main d'**autres matchs**, en n'importe quelle quantité, à condition de les rendre accessibles et documentés.

### ❌ Interdit
1. **Annoter à la main ce match**, en n'importe quelle quantité et pour n'importe quel usage : soumission, entraînement ou validation. Corriger à la main le tracking ou la sortie de ton algorithme est aussi interdit, tout comme des règles ou constantes liées à des frames précises du match.
2. **Utiliser la vérité terrain privée**, ou **toute donnée humaine sur ce match** : Opta, StatsBomb, Wyscout, LaLiga, tracking corrigé, etc.
3. **Entraîner ou régler un modèle sur les 5 minutes publiques.**
4. **Soumettre un fichier que ton dépôt ne peut pas régénérer à l'identique.**
5. **Redistribuer les données** : les commit, publier des exports frame par frame ou des extraits vidéo.
6. **Envoyer les vidéos ou données à un LLM hébergé dans le cloud** (ChatGPT, Claude, Gemini…). Un LLM local est autorisé.
7. Utiliser un modèle privé ou interne non partageable : demande avant.

### ⚠️ Clarification des organisateurs (e-mail) — elle PRIME sur tout ce qui précède

Ces règles ont la priorité sur la documentation, les e-mails précédents et les réponses individuelles.

**Interdit**
- **Vérifier ta sortie contre la vidéo.**
- Étiquettes manuelles, données produites par un humain, ou toute donnée créée à la main sur le match fourni.
- Envoyer les données fournies à des services d'IA.
- **Entraîner, ajuster ou calibrer** ton algorithme sur la vérité terrain de possession **ou sur la vidéo fournie**.

**Autorisé**
- Lancer des vérifications automatiques en utilisant **uniquement** les données fournies.
- Inspecter les données et la vidéo pour mieux comprendre ce qui compte comme possession.
- Utiliser en entrée la vidéo, le tracking automatique, le smart tagging ou toute autre donnée générée, **tant que l'algorithme n'a pas été entraîné sur la vérité terrain ni sur la vidéo fournie**.
- Fournir des fichiers d'étapes intermédiaires.
- Utiliser tout jeu de données dont tu as les droits (vérifie la licence de chacun).

**Entraînement et réglage** : s'il faut entraîner (ou ré-entraîner), utilise **uniquement des données externes**. Si l'algorithme a des paramètres à régler, règle-les **sur des données externes**, jamais sur la vérité terrain de possession ni sur la vidéo fournie.

Conséquence pratique : les 5 minutes de vérité terrain publique servent seulement à vérifier que le pipeline tourne (test de plomberie), jamais à choisir un paramètre. Le §7 ci-dessus qui autorisait de « regarder la vidéo pour déboguer » est à lire avec cette restriction : regarder pour **comprendre** la possession, oui ; **contrôler** ses résultats contre la vidéo, non.

### Équipe
**3 à 5 membres.** Avec moins de 3, l'équipe n'est pas éligible à l'Innovation Challenge ni au Final Pitch.

En cas de doute : **ouvre une issue AVANT de construire**.

---

## 8. Contenu du dépôt

```
games.py                     constantes du match, chemins, alignement des frames
evaluation/
  possession_metrics.py      définition de toutes les métriques
  run_evaluation.py          le scoreur officiel (le même que celui des organisateurs)
  validate_submission.py     vérifie un fichier avant l'envoi
  gt/                        vérité terrain publique (5 min)
  results/                   les 4 baselines ; mets tes CSV ici
starter/
  baseline.py                baseline de référence (numpy uniquement)
  load_atd.py                lit le tracking et l'aligne sur les frames
  load_smart_tagging.py      lit le tagging et le convertit en frames (bibliothèque standard)
  load_homography.py         lit l'homographie, projection terrain <-> pixels
  utils.py                   tracés du terrain
  01_smart_tagging.ipynb     tour guidé du tagging
  02_tracking_atd.ipynb      tour guidé du tracking
  03_first_submission.ipynb  des données au CSV noté : COMMENCE ICI
```

### Installation
- **Python ≥ 3.8**. L'évaluation n'a besoin que de `numpy` et `pandas`.
- Pour les notebooks : `kloppy` et `matplotlib` (`requirements-starter.txt`), avec **Python ≥ 3.9 recommandé** : sous Windows, Jupyter en 3.8 bloque sur `pywinpty`.

```bash
git clone https://github.com/metrica-sports/more-than-a-hack-2027
cd more-than-a-hack-2027
pip install -r requirements.txt -r requirements-starter.txt
python evaluation/run_evaluation.py            # note les 4 baselines
python starter/baseline.py                     # les régénère (il faut data/)
python evaluation/validate_submission.py evaluation/results/mon_fichier.csv
python evaluation/run_evaluation.py --bootstrap 1000
```

---

## 9. Calendrier

| | |
|---|---|
| ouverture des inscriptions | 1er octobre 2026 |
| publication des données | 20 octobre 2026 |
| **date limite de soumission** | **17 novembre 2026** |
| résultats | avant le 26 novembre 2026 |

Contact : hackathon.talentarena@mobileworldcapital.com · Questions techniques : issues GitHub
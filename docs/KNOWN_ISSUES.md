# Problèmes connus / Known issues

[Français](#français) | [English](#english)

## Français

> **État au 2026-11-07.** Aucun code applicatif n'existe. Ces entrées sont des constats sur les **fichiers**, sur les
> **règles** (ARENA.md, mail des organisateurs) et sur l'**environnement**, pas des bugs observés dans un programme.
> Chaque entrée devient une mesure ou un bug dès que le code existe. Statut global : 🎯 à traiter.

Gabarit par entrée : **Quoi**, **Où**, **Pourquoi c'est important**.

---

### 1. Fichier de tracking principal absent — 🎯 bloquant

- **Quoi :** `BAR-ATH_tactical_atd.txt` (tracking des joueurs et du ballon de la caméra *tactical*, la référence de la soumission) n'est pas dans `data/tactical/`. Présents : le `.xml` de métadonnées, l'homographie et le smart tagging. `BAR-ATH_broadcast_atd.txt` existe, mais la caméra *broadcast* n'est **pas synchronisée** avec la *tactical* : ne jamais le substituer.
- **Où :** `data/tactical/` ; chargement du tracking (loader 🎯 à écrire).
- **Pourquoi c'est important :** sans ce fichier, aucune frame ne peut être labellisée à partir du tracking de référence. Action : le re-télécharger depuis le Drive (constat du 2026-11-07). Un fichier d'environ 164 000 lignes signale une indexation de la broadcast par erreur (ARENA.md §4.1).

### 2. Vidéos MP4 absentes

- **Quoi :** `BAR-ATH_tactical.mp4` (référence) et `BAR-ATH_broadcast.mp4` (optionnelle) ne sont pas dans `data/`.
- **Où :** `data/tactical/`, `data/broadcast/`.
- **Pourquoi c'est important :** le pipeline n'en a pas besoin pour produire la sortie. Regarder la vidéo pour **comprendre** une situation reste permis, et son absence bloque ce travail de compréhension. Les vidéos ne sont jamais commitées (ARENA.md §4.2, §7).

### 3. Dépôt officiel non cloné

- **Quoi :** `games.py`, `evaluation/` (scoreur `run_evaluation.py`, `validate_submission.py`, `possession_metrics.py`, vérité terrain publique `gt/`, `results/` avec les 4 baselines) et `starter/` ne sont pas à la racine du dépôt.
- **Où :** racine du dépôt ; `games.py` (chemins, périodes notées, alignement).
- **Pourquoi c'est important :** sans `run_evaluation.py`, aucun score local ; sans `validate_submission.py`, aucune validation du fichier exact à envoyer ; sans `games.py`, pas de constantes officielles de période. À cloner depuis le dépôt officiel. Avant de copier du code officiel dans notre dépôt public, vérifier sa licence (décision ouverte, voir `ROADMAP_NEXT_STEPS.md` §5).

### 4. Ballon manquant (NaN) sur 41 % des frames notées

- **Quoi :** le ballon est absent sur 43 % des frames, et sur 41 % des frames notées ; les valeurs manquantes valent `NaN`. Les trous surviennent surtout dans les moments importants : surface encombrée, duels aériens, tacles (ARENA.md §4.3).
- **Où :** nettoyage du ballon, features (joueur le plus proche), post-traitement.
- **Pourquoi c'est important :** le ballon est le signal le plus direct de la possession, et ses trous tombent sur les moments clés. Un remplissage naïf (dernière valeur connue, valeur par défaut) introduit des erreurs exactement là où elles coûtent le plus. Le cas doit être prévu dès le premier jour.

### 5. 46 emplacements de tracking sans identité

- **Quoi :** 46 emplacements « Track 1…46 » pour 22 joueurs. Ils apparaissent, disparaissent et échangent leurs identités. Seule l'**équipe** de chaque emplacement est connue. En moyenne 20,5 objets suivis par frame notée (ARENA.md §4.3).
- **Où :** features (distance au ballon, équipe), tests de features.
- **Pourquoi c'est important :** un joueur ne peut pas être suivi d'une frame à l'autre. Toute règle qui dépend de l'identité d'un joueur est fausse ; la proximité ne peut être calculée qu'avec l'équipe de l'emplacement.

### 6. Surajustement sur les 5 minutes publiques

- **Quoi :** la vérité terrain publique couvre les frames 11 185 à 18 684, soit les 5 premières minutes de la 1re mi-temps : H 3 454, A 2 577, D 1 469, et 17 possessions de 14,2 s en moyenne. Une possession ratée y coûte environ 6 points. Sur cette fenêtre, `smooth125` paraît meilleur (spellF1 0,4242), mais sur le match complet il est moins bon que `smooth50` (0,2242 contre 0,2433).
- **Où :** évaluation, choix de la fenêtre de lissage et de tout paramètre.
- **Pourquoi c'est important :** régler sur la vérité terrain publique est interdit (mail des organisateurs) et conduit au mauvais choix. Cette fenêtre sert seulement de test de plomberie (D-006).

### 7. Piège des 2 934 frames D en début de 2e mi-temps

- **Quoi :** la 2e mi-temps est notée dès la frame 110 808, mais le coup d'envoi n'a lieu qu'à la frame 113 742. Les 2 934 frames entre les deux sont toutes `D` dans la vérité terrain (ARENA.md §4.7).
- **Où :** post-traitement et segmentation, tests de propriétés, évaluation.
- **Pourquoi c'est important :** un modèle qui lit un ballon « vivant » dans cette zone crée de fausses possessions. Une règle du type « toute la 2e mi-temps est en jeu » casse la segmentation. Les bornes des périodes viennent de `games.half_video_blocks` (constantes officielles) ; aucune règle ne doit viser ces numéros de frame en dur.

### 8. Décalage d'alignement `frame_id - 1`

- **Quoi :** l'index ATD `frame_id` va de 1 à 199 319, alors que la soumission va de 0 à 199 318. Il faut donc `frame = frame_id - 1`. Le smart tagging est en secondes (`round(sec * 25)`) ; l'homographie est déjà indexée de 0 à 199 318 (ARENA.md §4.6).
- **Où :** loader, export CSV, tests d'alignement.
- **Pourquoi c'est important :** un décalage d'une ligne ne casse pas le format si le compte de lignes reste juste, et décale alors tous les labels. Le validateur sert à détecter ce cas (ARENA.md §6.1). Un retard d'une frame coûte très peu en spellF1 (1,0000), mais le décalage doit être corrigé à la source.

### 9. ARENA.md contredit par le mail de clarification

- **Quoi :** `ARENA.md` §7 autorise à « regarder la vidéo » pour déboguer. Le mail des organisateurs, qui prime, interdit de **vérifier sa sortie contre la vidéo**, et interdit d'entraîner, d'ajuster ou de calibrer sur la vérité terrain ou sur la vidéo fournie : tout réglage se fait **uniquement sur des données externes**. Restent permis : les contrôles automatiques avec les seules données fournies, les fichiers d'étapes intermédiaires, et tout jeu de données dont l'équipe a le droit d'usage.
- **Où :** `ARENA.md` §7 ; section « Clarification du mail » de `ARENA.md` (ajoutée) ; `BUSINESS_RULES.md`.
- **Pourquoi c'est important :** en cas de doute, la règle la plus stricte s'applique. Regarder la vidéo pour comprendre une possession reste possible ; s'en servir pour contrôler un résultat ne l'est pas. En cas de doute sur une règle, ouvrir une issue **avant** de construire (ARENA.md §7).

### 10. kloppy non installé et Python hors PATH

- **Quoi :** Python 3.13 est installé (dossier `Programs\Python\Python313` du profil utilisateur) mais n'est pas dans le PATH : la commande `python` ne le lance pas. La bibliothèque `kloppy`, utilisée par l'exemple officiel de lecture du tracking ATD (ARENA.md §4.3), n'est pas installée. Aucun fichier de dépendances figé n'existe encore.
- **Où :** environnement local ; `DEV_WORKFLOW.md` (Quick start) ; loader.
- **Pourquoi c'est important :** un interpréteur ou des versions non figés empêchent de régénérer le CSV à l'identique, ce qui est interdit (ARENA.md §7). Décider si `kloppy` est installé ou si le loader lit directement le format FIFA/EPTS (décision ouverte).

---

### Mise à jour

Une entrée résolue reste dans ce fichier, avec son statut et le test qui la protège (voir `TESTING.md`). Les nouvelles limites découvertes pendant le travail s'ajoutent avec le même gabarit, sans renumérotation.

---

## English

> **Status as of 2026-11-07.** No application code exists. These entries are findings about the **files**, the **rules**
> (ARENA.md, organisers' email) and the **environment**, not bugs observed in a program. Each entry becomes a
> measurement or a bug as soon as code exists. Global status: 🎯 to handle.

Entry template: **What**, **Where**, **Why it matters**.

---

### 1. Main tracking file missing — 🎯 blocking

- **What:** `BAR-ATH_tactical_atd.txt` (player and ball tracking from the *tactical* camera, the submission reference) is not in `data/tactical/`. Present: the metadata `.xml`, the homography and the smart tagging. `BAR-ATH_broadcast_atd.txt` exists, but the *broadcast* camera is **not synchronised** with the *tactical* one: never substitute it.
- **Where:** `data/tactical/`; tracking loader (🎯 to write).
- **Why it matters:** without this file, no frame can be labelled from the reference tracking. Action: re-download it from the shared Drive (finding of 2026-11-07). A file of about 164,000 lines means the broadcast was indexed by mistake (ARENA.md §4.1).

### 2. MP4 videos missing

- **What:** `BAR-ATH_tactical.mp4` (reference) and `BAR-ATH_broadcast.mp4` (optional) are not in `data/`.
- **Where:** `data/tactical/`, `data/broadcast/`.
- **Why it matters:** the pipeline does not need them to produce the output. Watching the video to **understand** a situation stays allowed, and their absence blocks that understanding work. Videos are never committed (ARENA.md §4.2, §7).

### 3. Official repository not cloned

- **What:** `games.py`, `evaluation/` (scorer `run_evaluation.py`, `validate_submission.py`, `possession_metrics.py`, public ground truth `gt/`, `results/` with the 4 baselines) and `starter/` are not at the root of the repository.
- **Where:** repository root; `games.py` (paths, scored periods, alignment).
- **Why it matters:** without `run_evaluation.py`, no local score; without `validate_submission.py`, no validation of the exact file to send; without `games.py`, no official period constants. Clone it from the official repository. Before copying official code into our public repository, check its licence (open decision, see `ROADMAP_NEXT_STEPS.md` §5).

### 4. Ball missing (NaN) on 41% of scored frames

- **What:** the ball is absent on 43% of frames, and on 41% of scored frames; missing values are `NaN`. Gaps occur mostly in key moments: crowded penalty area, aerial duels, tackles (ARENA.md §4.3).
- **Where:** ball cleaning, features (closest player), post-processing.
- **Why it matters:** the ball is the most direct signal of possession, and its gaps fall on key moments. A naive fill (last known value, default value) introduces errors exactly where they cost most. The case must be planned from day one.

### 5. 46 tracking slots without identity

- **What:** 46 slots "Track 1…46" for 22 players. They appear, disappear and swap identities. Only the **team** of each slot is known. On average 20.5 tracked objects per scored frame (ARENA.md §4.3).
- **Where:** features (distance to the ball, team), feature tests.
- **Why it matters:** a player cannot be followed from one frame to the next. Any rule that depends on a player's identity is wrong; proximity can only be computed with the slot's team.

### 6. Overfitting to the 5 public minutes

- **What:** the public ground truth covers frames 11,185 to 18,684, i.e. the first 5 minutes of the 1st half: H 3,454, A 2,577, D 1,469, and 17 possessions of 14.2 s on average. A missed possession costs about 6 points there. On this window, `smooth125` looks better (spellF1 0.4242), but on the full match it is worse than `smooth50` (0.2242 against 0.2433).
- **Where:** evaluation, choice of the smoothing window and of any parameter.
- **Why it matters:** tuning on the public ground truth is forbidden (organisers' email) and leads to the wrong choice. This window only serves as a plumbing test (D-006).

### 7. Trap of the 2,934 D frames at the start of the 2nd half

- **What:** the 2nd half is scored from frame 110,808, but kick-off only happens at frame 113,742. The 2,934 frames in between are all `D` in the ground truth (ARENA.md §4.7).
- **Where:** post-processing and segmentation, property tests, evaluation.
- **Why it matters:** a model that reads a "live" ball in this zone creates false possessions. A rule such as "the whole 2nd half is in play" breaks the segmentation. The period bounds come from `games.half_video_blocks` (official constants); no rule may target these frame numbers hard-coded.

### 8. `frame_id - 1` alignment offset

- **What:** the ATD index `frame_id` runs from 1 to 199,319, while the submission runs from 0 to 199,318. Hence `frame = frame_id - 1`. Smart tagging is in seconds (`round(sec * 25)`); the homography is already indexed from 0 to 199,318 (ARENA.md §4.6).
- **Where:** loader, CSV export, alignment tests.
- **Why it matters:** a one-line offset does not break the format if the line count stays right, yet it shifts every label. The validator helps detect this case (ARENA.md §6.1). A one-frame delay costs very little in spellF1 (1.0000), but the offset must be fixed at the source.

### 9. ARENA.md contradicted by the clarification email

- **What:** `ARENA.md` §7 allows "watching the video" to debug. The organisers' email, which takes precedence, forbids **checking one's output against the video**, and forbids training, adjusting or calibrating on the ground truth or on the provided video: any tuning is done **only on external data**. Still allowed: automatic checks with the provided data only, intermediate step files, and any dataset the team has the right to use.
- **Where:** `ARENA.md` §7; "Clarification du mail" section of `ARENA.md` (added); `BUSINESS_RULES.md`.
- **Why it matters:** when in doubt, the strictest rule applies. Watching the video to understand a possession remains possible; using it to check a result is not. When in doubt about a rule, open an issue **before** building (ARENA.md §7).

### 10. kloppy not installed and Python not on PATH

- **What:** Python 3.13 is installed (the `Programs\Python\Python313` folder of the user profile) but is not on the PATH: the `python` command does not start it. The `kloppy` library, used by the official example that reads ATD tracking (ARENA.md §4.3), is not installed. No frozen dependency file exists yet.
- **Where:** local environment; `DEV_WORKFLOW.md` (Quick start); loader.
- **Why it matters:** an unfrozen interpreter or unfrozen versions prevent regenerating the CSV identically, which is forbidden (ARENA.md §7). Decide whether `kloppy` is installed or whether the loader reads the FIFA/EPTS format directly (open decision).

---

### Updates

A resolved entry stays in this file, with its status and the test that protects it (see `TESTING.md`). New limits found during the work are added with the same template, without renumbering.

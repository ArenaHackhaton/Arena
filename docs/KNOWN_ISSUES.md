# Problèmes connus / Known issues

[Français](#français) | [English](#english)

## Français

> **État au 2026-11-16.** Le code existe : `arena/` (loader, features, décodage Viterbi, a priori des remises),
> `scripts/` (soumission, données externes, réglage) et `tests/` (8 tests synthétiques). Les entrées 1, 3 et 10
> sont résolues et gardées avec leur statut, comme le veut ce fichier. Les entrées 11 à 17 sont des limites
> mesurées ou des constats de documentation. Statut : ✅ résolu · 🟡 partiel ou limite · 🎯 à traiter.

Gabarit par entrée : **Quoi**, **Où**, **Pourquoi c'est important**.

---

### 1. Fichier de tracking principal — ✅ résolu

- **Quoi :** le loader lit l'ATD tactical (`arena/loader.py`, via `games.require`). Si le fichier manque, le chargement
  échoue et `make_submission.py` affiche `[RESULT] load failed` sans données. La caméra *broadcast* reste **non
  synchronisée** avec la *tactical* : ne jamais la substituer.
- **Où :** `arena/loader.py`, `scripts/make_submission.py`.
- **Pourquoi c'est important :** sans ce fichier, aucune frame ne peut être labellisée. Un fichier d'environ
  164 000 lignes signale une indexation de la broadcast par erreur (ARENA.md §4.1). La présence du fichier se
  vérifie sur chaque machine au premier lancement ; ce document ne l'a pas contrôlé.

### 2. Vidéos MP4 absentes — 🟡 non bloquant

- **Quoi :** `BAR-ATH_tactical.mp4` et `BAR-ATH_broadcast.mp4` ne sont pas dans `data/`.
- **Où :** `data/tactical/`, `data/broadcast/`.
- **Pourquoi c'est important :** le pipeline n'en a pas besoin (il n'utilise ni vidéo ni homographie). Regarder la
  vidéo pour **comprendre** une situation reste permis, et son absence bloque ce travail de compréhension. Les vidéos
  ne sont jamais commitées (ARENA.md §4.2, §7).

### 3. Dépôt officiel — ✅ résolu

- **Quoi :** le code officiel (`games.py`, `evaluation/`, `starter/`) est importé depuis le disque, depuis le dossier
  frère `more-than-a-hack-2027` ou celui de `MTAH_OFFICIAL_DIR` (`arena/official.py`). Il n'est pas copié dans le
  dépôt. Le docstring d'`official.py` indique une licence MIT pour ce code ; à confirmer avant toute copie.
- **Où :** `arena/official.py` ; `DEV_WORKFLOW.md` (Quick start).
- **Pourquoi c'est important :** `make_submission.py` a besoin de `games.py`, du lecteur Smart Tagging et du validateur.
  Si le dépôt est absent, `FileNotFoundError` est levé avec le chemin attendu. Le choix « copier ou référencer »
  (`ROADMAP_NEXT_STEPS.md` §5) est traité dans le code par la référence ; il reste à acter dans `DECISIONS.md`.

### 4. Ballon manquant (NaN) sur 41 % des frames notées — 🟡 partiel

- **Quoi :** le ballon est absent sur 43 % des frames, et sur 41 % des frames notées ; les valeurs manquantes valent
  `NaN` (ARENA.md §4.3). Les trous surviennent surtout dans les moments importants : surface encombrée, duels aériens.
- **Où :** `arena/features.py` (distances `NaN`), `arena/decode.py` (ballon non suivi = aucune preuve, l'état courant
  est conservé). Pas d'interpolation pour l'instant (`ROADMAP_NEXT_STEPS.md` §7).
- **Pourquoi c'est important :** le ballon est le signal le plus direct de la possession. Un trou n'est jamais comblé
  en silence : il est traité comme une absence d'information. Test : `test_missing_ball_keeps_current_state`.

### 5. 46 emplacements de tracking sans identité — 🟡 traité par construction

- **Quoi :** 46 emplacements « Track 1…46 » pour 22 joueurs. Ils apparaissent, disparaissent et échangent leurs
  identités. Seule l'**équipe** de chaque emplacement est connue (ARENA.md §4.3).
- **Où :** `arena/features.py` (distance au ballon par équipe), `arena/loader.py` (équipe via les métadonnées).
- **Pourquoi c'est important :** un joueur ne peut pas être suivi d'une frame à l'autre. Aucune règle n'utilise
  l'identité d'un joueur ; la proximité se calcule par équipe seulement.

### 6. Surajustement sur les 5 minutes publiques — 🟡 atténué

- **Quoi :** la vérité terrain publique couvre les 5 premières minutes de la 1re mi-temps (ARENA.md §5). Sur cette
  fenêtre, `smooth125` paraît meilleur, mais sur le match complet il est moins bon que `smooth50` (ARENA.md §5).
- **Où :** évaluation ; `arena/config.py` (paramètres réglés sur données externes seulement, `docs/TUNING.md`).
- **Pourquoi c'est important :** régler sur la vérité terrain publique est interdit (mail des organisateurs). Les
  5 minutes servent de test de plomberie seulement (D-006). Aucune évaluation du match n'est faite dans ce dépôt.

### 7. Piège des 2 934 frames D en début de 2e mi-temps — 🟡 couvert sous condition

- **Quoi :** la 2e mi-temps est notée dès une frame donnée, mais le coup d'envoi n'a lieu que plus tard. Les frames
  entre les deux sont toutes `D` dans la vérité terrain (ARENA.md §4.7).
- **Où :** `arena/priors.py` (`kickoff_start` : `D` depuis le début de la mi-temps jusqu'à la reprise), voir entrée 14.
- **Pourquoi c'est important :** un modèle qui lit un ballon « vivant » dans cette zone crée de fausses possessions.
  La règle ne vise aucun numéro de frame en dur : les bornes viennent de `games.half_video_blocks`.

### 8. Décalage d'alignement `frame_id - 1` — ✅ implémenté, 🎯 test à écrire

- **Quoi :** l'index ATD `frame_id` va de 1 à 199 319, la soumission de 0 à 199 318. Il faut donc `frame = frame_id - 1`.
  Le Smart Tagging est en secondes (`round(sec * 25)`).
- **Où :** `arena/loader.py` (`video_frame = frame_id - 1`, contrôle de plage et de contiguïté) ; `scripts/make_submission.py`
  (affiche `contiguous`). Le Smart Tagging n'est pas aligné par `loader.py` mais par `priors.py`.
- **Pourquoi c'est important :** un décalage d'une ligne ne casse pas le format si le compte de lignes reste juste, et
  décale alors tous les labels. Le validateur officiel (ARENA.md §6.1) ne le détecte pas à lui seul.
  **Limite :** aucun test ne lit un fichier ATD ; le test d'alignement reste à écrire (`TESTING.md` §2).

### 9. ARENA.md contredit par le mail de clarification — 🟡 règle à respecter

- **Quoi :** `ARENA.md` §7 autorise à « regarder la vidéo » pour déboguer. Le mail des organisateurs, qui prime, interdit de
  **vérifier sa sortie contre la vidéo**, et interdit d'entraîner, d'ajuster ou de calibrer sur la vérité terrain ou sur la
  vidéo fournie : tout réglage se fait **uniquement sur des données externes**.
- **Où :** `ARENA.md` §7 ; section « Clarification du mail » de `ARENA.md` ; `BUSINESS_RULES.md`.
- **Pourquoi c'est important :** en cas de doute, la règle la plus stricte s'applique. Regarder la vidéo pour comprendre
  une possession reste possible ; s'en servir pour contrôler un résultat ne l'est pas. En cas de doute sur une règle,
  ouvrir une issue **avant** de construire (ARENA.md §7).

### 10. Python et dépendances — ✅ figés, 🟡 documentation à aligner

- **Quoi :** `requirements.txt` fige Python 3.11 et les versions numpy 2.4.6, pandas 3.1.1, pytest 9.2.0. Le code ne
  dépend pas de `kloppy` : le loader lit directement le format texte de l'ATD.
- **Où :** `requirements.txt` ; `arena/loader.py` ; `DECISIONS.md` D-001 (voir entrée 17).
- **Pourquoi c'est important :** des versions non figées empêcheraient de régénérer le CSV à l'identique, ce qui est
  interdit (ARENA.md §7).

### 11. Validé sur données externes seulement — 🟡 limite de mesure

- **Quoi :** la méthode n'est validée que sur deux matchs Metrica publics (Sample Game 1 pour le réglage, Sample Game 2
  pour le contrôle). Elle n'a **jamais** été mesurée sur le match fourni. Le gain réel sur ce match est donc inconnu.
- **Où :** `scripts/tune_external.py`, `arena/external_metrica.py`, `docs/TUNING.md`.
- **Pourquoi c'est important :** les gains affichés par le réglage ne sont pas une estimation du score officiel. D-003
  interdit de mesurer ou régler sur le match ; le score officiel reste chez les organisateurs.

### 12. Ballon manquant : Metrica et match ne se ressemblent pas — 🟡 limite de simulation

- **Quoi :** dans les données Metrica, le ballon manque sur 91 à 100 % des frames de ballon mort, mais rarement en jeu
  (10 à 23 %). Sur le match, il manque sur environ 41 % des frames notées. Le réglage simule donc l'occlusion **en jeu**
  jusqu'à 41 % (`simulate_occlusion` : blocs de 2 s en moyenne, graine fixe).
- **Où :** `arena/external_metrica.py` (`simulate_occlusion`) ; `arena/features.py` (`ball_flags`).
- **Pourquoi c'est important :** la détection des frames mortes repose sur deux signaux : le ballon hors du terrain et les
  remises du Smart Tagging. Sur Metrica, le ballon absent sert de signal de ballon mort ; sur le match, ce n'est pas
  forcément le cas. La détection de `D` par le mouvement n'est pas écrite (`ROADMAP_NEXT_STEPS.md` §7).

### 13. Remises en jeu émulées : résultats optimistes — 🟡 limite de simulation

- **Quoi :** l'a priori des remises est émulé sur Metrica à partir des événements humains (SET PIECE, dégagements), puis
  dégradé : erreur de timing gaussienne de 1 s et 15 % de remises oubliées. Le Smart Tagging réel relève **59 remises**
  pour tout le match (comptage du tagging), contre environ 90 par match dans Metrica ; les touches n'ont pas d'équipe
  (N/A).
- **Où :** `arena/external_metrica.py` (`restarts_from_events`), `arena/priors.py` (`degrade`) ; `docs/TUNING.md`.
- **Pourquoi c'est important :** l'a priori réglé est **optimiste** par rapport au tagging réel. Les essais de robustesse
  (18 essais, 15 à 50 % de remises oubliées, erreur de 1 à 2 s) battent la baseline dans tous les cas, mais avec un
  gain plus faible quand 50 % sont oubliées (environ +0,02 à +0,07, contre +0,01 à +0,12 sur l'ensemble). Ne pas annoncer
  ces gains comme ceux du match.

### 14. Coup d'envoi de la 2e mi-temps : dépend d'un tag — 🟡 dépendance

- **Quoi :** les frames notées de la 2e mi-temps avant le coup d'envoi sont traitées comme mortes grâce au tag Smart
  Tagging « Kick Off (Start) » (`priors.smart_tagging_restarts` : `kickoff_start`). Si ce tag manque, le prior ne couvre
  pas cette zone et le décodeur peut lire un ballon « vivant » (voir entrée 7).
- **Où :** `arena/priors.py` ; `arena/config.py` (`sp_dead_bonus` = 1, prior actif).
- **Pourquoi c'est important :** la correction dépend d'une donnée d'entrée automatique. Un contrôle de présence du tag
  reste à ajouter avec un test.

### 15. Pas d'homographie, pas de vidéo, pas de broadcast — 🟡 choix actuel

- **Quoi :** le pipeline n'utilise que l'ATD tactical (coordonnées en mètres) et le Smart Tagging. Ni homographie, ni
  vidéo, ni caméra broadcast ne sont lues.
- **Où :** `arena/loader.py` (lecture des métadonnées et du tracking seulement).
- **Pourquoi c'est important :** limite de la méthode. Ajouter une de ces entrées demande une vérification des règles
  (la vidéo ne sert jamais à contrôler la sortie) et de nouveaux tests.

### 16. Viterbi en Python pur — ✅ acceptable

- **Quoi :** le décodage est une boucle Python sur 3 états (`arena/decode.py`, `viterbi`). L'équipe estime environ 1 s
  par mi-temps ; cette durée n'a pas été re-mesurée dans cette mise à jour.
- **Où :** `arena/decode.py`.
- **Pourquoi c'est important :** coût acceptable pour la régénération. À revoir si la grille de réglage grossit
  (144 + 96 combinaisons, `scripts/tune_external.py`).

### 17. Dérive de documentation : D-001 et D-004 — 🎯 à acter

- **Quoi :** `DECISIONS.md` D-001 dit « Python 3.9 minimum » et cite `kloppy` ; le code fige Python 3.11 et ne
  dépend pas de `kloppy`. D-004 nomme `python -m possession.run` ; le point d'entrée réel est
  `scripts/make_submission.py`, et le paquet du code est `arena/`.
- **Où :** `docs/DECISIONS.md` (D-001, D-004), `requirements.txt`, `scripts/make_submission.py`.
- **Pourquoi c'est important :** une décision non à jour peut passer pour la vérité. Ce document ne décide pas à la place
  de l'équipe : la mise à jour de `DECISIONS.md` reste à faire par une décision explicite.

---

### Mise à jour

Une entrée résolue reste dans ce fichier, avec son statut et le test qui la protège (voir `TESTING.md`). Les nouvelles limites
découvertes pendant le travail s'ajoutent avec le même gabarit, sans renumérotation.

---

## English

> **Status as of 2026-11-16.** The code exists: `arena/` (loader, features, Viterbi decoding, restart prior),
> `scripts/` (submission, external data, tuning) and `tests/` (8 synthetic tests). Entries 1, 3 and 10 are resolved
> and kept with their status, as this file requires. Entries 11 to 17 are measured limits or documentation findings.
> Status: ✅ resolved · 🟡 partial or limit · 🎯 to handle.

Entry template: **What**, **Where**, **Why it matters**.

---

### 1. Main tracking file — ✅ resolved

- **What:** the loader reads the ATD tactical (`arena/loader.py`, via `games.require`). If the file is missing, loading
  fails and `make_submission.py` prints `[RESULT] load failed` without data. The *broadcast* camera stays **not
  synchronised** with the *tactical* one: never substitute it.
- **Where:** `arena/loader.py`, `scripts/make_submission.py`.
- **Why it matters:** without this file, no frame can be labelled. A file of about 164,000 lines means the broadcast was
  indexed by mistake (ARENA.md §4.1). Presence of the file is checked on each machine at the first run; this document
  did not check it.

### 2. MP4 videos missing — 🟡 non-blocking

- **What:** `BAR-ATH_tactical.mp4` and `BAR-ATH_broadcast.mp4` are not in `data/`.
- **Where:** `data/tactical/`, `data/broadcast/`.
- **Why it matters:** the pipeline does not need them (it uses neither video nor homography). Watching the video to
  **understand** a situation stays allowed, and their absence blocks that understanding work. Videos are never committed
  (ARENA.md §4.2, §7).

### 3. Official repository — ✅ resolved

- **What:** the official code (`games.py`, `evaluation/`, `starter/`) is imported from disk, from the sibling folder
  `more-than-a-hack-2027` or from `MTAH_OFFICIAL_DIR` (`arena/official.py`). It is not copied into the repository. The
  docstring of `official.py` states an MIT licence for this code; to confirm before any copy.
- **Where:** `arena/official.py`; `DEV_WORKFLOW.md` (Quick start).
- **Why it matters:** `make_submission.py` needs `games.py`, the Smart Tagging reader and the validator. If the repository
  is absent, a `FileNotFoundError` names the expected path. The "copy or reference" choice (`ROADMAP_NEXT_STEPS.md` §5) is
  settled in the code by reference; it still needs recording in `DECISIONS.md`.

### 4. Missing ball (NaN) on 41% of scored frames — 🟡 partial

- **What:** the ball is absent on 43% of frames, and on 41% of scored frames; missing values are `NaN` (ARENA.md §4.3).
  Gaps occur mostly in key moments: crowded penalty area, aerial duels.
- **Where:** `arena/features.py` (distances `NaN`), `arena/decode.py` (ball not tracked = no evidence, the current state is
  kept). No interpolation yet (`ROADMAP_NEXT_STEPS.md` §7).
- **Why it matters:** the ball is the most direct signal of possession. A gap is never filled silently: it is treated as
  missing information. Test: `test_missing_ball_keeps_current_state`.

### 5. 46 tracking slots without identity — 🟡 handled by design

- **What:** 46 slots "Track 1…46" for 22 players. They appear, disappear and swap identities. Only the **team** of each
  slot is known (ARENA.md §4.3).
- **Where:** `arena/features.py` (distance to the ball per team), `arena/loader.py` (team from the metadata).
- **Why it matters:** a player cannot be followed from one frame to the next. No rule uses a player's identity; proximity
  is computed per team only.

### 6. Overfitting to the 5 public minutes — 🟡 mitigated

- **What:** the public ground truth covers the first 5 minutes of the 1st half (ARENA.md §5). On this window, `smooth125`
  looks better, but on the full match it is worse than `smooth50` (ARENA.md §5).
- **Where:** evaluation; `arena/config.py` (parameters tuned on external data only, `docs/TUNING.md`).
- **Why it matters:** tuning on the public ground truth is forbidden (organisers' email). The 5 minutes serve only as a
  plumbing test (D-006). No match evaluation is done in this repository.

### 7. Trap of the 2,934 D frames at the start of the 2nd half — 🟡 covered under a condition

- **What:** the 2nd half is scored from a given frame, but kick-off only happens later. The frames in between are all `D`
  in the ground truth (ARENA.md §4.7).
- **Where:** `arena/priors.py` (`kickoff_start`: `D` from the start of the half until the restart), see entry 14.
- **Why it matters:** a model that reads a "live" ball in this zone creates false possessions. The rule targets no
  hard-coded frame number: the bounds come from `games.half_video_blocks`.

### 8. `frame_id - 1` alignment offset — ✅ implemented, 🎯 test to write

- **What:** the ATD index `frame_id` runs from 1 to 199,319, the submission from 0 to 199,318. Hence `frame = frame_id - 1`.
  Smart Tagging is in seconds (`round(sec * 25)`).
- **Where:** `arena/loader.py` (`video_frame = frame_id - 1`, range and contiguity checks); `scripts/make_submission.py`
  (prints `contiguous`). Smart Tagging times are converted in `priors.py`, not in `loader.py`.
- **Why it matters:** a one-line offset does not break the format if the line count stays right, yet it shifts every label.
  The official validator (ARENA.md §6.1) does not detect it alone.
  **Limit:** no test reads an ATD file; the alignment test is still to be written (`TESTING.md` §2).

### 9. ARENA.md contradicted by the clarification email — 🟡 rule to respect

- **What:** `ARENA.md` §7 allows "watching the video" to debug. The organisers' email, which takes precedence, forbids
  **checking one's output against the video**, and forbids training, adjusting or calibrating on the ground truth or on the
  supplied video: any tuning is done **only on external data**.
- **Where:** `ARENA.md` §7; "Clarification du mail" section of `ARENA.md`; `BUSINESS_RULES.md`.
- **Why it matters:** when in doubt, the strictest rule applies. Watching the video to understand a possession remains
  possible; using it to check a result is not. When in doubt about a rule, open an issue **before** building
  (ARENA.md §7).

### 10. Python and dependencies — ✅ pinned, 🟡 documentation to align

- **What:** `requirements.txt` pins Python 3.11 and numpy 2.4.6, pandas 3.1.1, pytest 9.2.0. The code does not depend on
  `kloppy`: the loader reads the ATD text format directly.
- **Where:** `requirements.txt`; `arena/loader.py`; `DECISIONS.md` D-001 (see entry 17).
- **Why it matters:** unpinned versions would prevent regenerating the CSV identically, which is forbidden (ARENA.md §7).

### 11. Validated on external data only — 🟡 measurement limit

- **What:** the method is validated only on two public Metrica matches (Sample Game 1 for tuning, Sample Game 2 for the
  check). It has **never** been measured on the provided match. The real gain on that match is therefore unknown.
- **Where:** `scripts/tune_external.py`, `arena/external_metrica.py`, `docs/TUNING.md`.
- **Why it matters:** the gains shown by tuning are not an estimate of the official score. D-003 forbids measuring or tuning
  on the match; the official score stays with the organisers.

### 12. Missing ball: Metrica and the match differ — 🟡 simulation limit

- **What:** in the Metrica data the ball is missing on 91 to 100% of dead-ball frames, but rarely in play (10 to 23%). On the
  match it is missing on about 41% of scored frames. Tuning therefore simulates occlusion **in play** up to 41%
  (`simulate_occlusion`: blocks of 2 s on average, fixed seed).
- **Where:** `arena/external_metrica.py` (`simulate_occlusion`); `arena/features.py` (`ball_flags`).
- **Why it matters:** dead-ball detection rests on two signals: the ball out of the pitch and the Smart Tagging restarts.
  On Metrica, a missing ball works as a dead-ball signal; on the match this is not necessarily the case. Detection of `D`
  from movement is not written (`ROADMAP_NEXT_STEPS.md` §7).

### 13. Simulated restarts: optimistic results — 🟡 simulation limit

- **What:** the restart prior is emulated on Metrica from human events (SET PIECE, goal kicks), then degraded: 1 s Gaussian
  timing error and 15% of restarts dropped. The real Smart Tagging has **59 restarts** for the whole match (tagging count),
  against about 90 per game in Metrica; throw-ins have no team (N/A).
- **Where:** `arena/external_metrica.py` (`restarts_from_events`), `arena/priors.py` (`degrade`); `docs/TUNING.md`.
- **Why it matters:** the tuned prior is **optimistic** compared with the real tagging. The robustness runs (18 runs, 15 to
  50% of restarts dropped, 1 to 2 s error) beat the baseline in every case, but by less when 50% are dropped (about +0.02 to
  +0.07, against +0.01 to +0.12 overall). Do not present these gains as the match's gains.

### 14. Second-half kick-off depends on a tag — 🟡 dependency

- **What:** the graded frames of the 2nd half before kick-off are treated as dead thanks to the Smart Tagging tag
  "Kick Off (Start)" (`priors.smart_tagging_restarts`: `kickoff_start`). If that tag is missing, the prior does not cover
  this stretch and the decoder may read a "live" ball (see entry 7).
- **Where:** `arena/priors.py`; `arena/config.py` (`sp_dead_bonus` = 1, prior on).
- **Why it matters:** the correction depends on an automatic input. A presence check for the tag remains to add, with a test.

### 15. No homography, no video, no broadcast — 🟡 current choice

- **What:** the pipeline uses only the ATD tactical (coordinates in metres) and the Smart Tagging. Neither the homography,
  nor the video, nor the broadcast camera is read.
- **Where:** `arena/loader.py` (reads the metadata and the tracking only).
- **Why it matters:** a limit of the method. Adding one of these inputs requires a rule check (the video never serves to
  check the output) and new tests.

### 16. Viterbi in pure Python — ✅ acceptable

- **What:** decoding is a Python loop over 3 states (`arena/decode.py`, `viterbi`). The team estimates about 1 s per half;
  this duration was not re-measured in this update.
- **Where:** `arena/decode.py`.
- **Why it matters:** acceptable cost for regeneration. To revisit if the tuning grid grows (144 + 96 combinations,
  `scripts/tune_external.py`).

### 17. Documentation drift: D-001 and D-004 — 🎯 to record

- **What:** `DECISIONS.md` D-001 says "Python 3.9 minimum" and cites `kloppy`; the code pins Python 3.11 and does not depend
  on `kloppy`. D-004 names `python -m possession.run`; the real entry point is `scripts/make_submission.py`, and the code
  package is `arena/`.
- **Where:** `docs/DECISIONS.md` (D-001, D-004), `requirements.txt`, `scripts/make_submission.py`.
- **Why it matters:** an outdated decision can pass for the truth. This document does not decide for the team: updating
  `DECISIONS.md` needs an explicit decision.

---

### Updates

A resolved entry stays in this file, with its status and the test that protects it (see `TESTING.md`). New limits found during
the work are added with the same template, without renumbering.

# Décisions : possession du ballon

[Français](#français) | [English](#english)

---

## Français

Choix techniques et méthodologiques durables, avec leur raison. La plus récente est en bas.

Statuts : `OPEN` (à trancher) · `ACCEPTED` (retenue) · `SUPERSEDED` (remplacée par une décision plus récente).

Gabarit pour une nouvelle entrée :

```
### D-00X — <titre court>

**Status:** OPEN | ACCEPTED | SUPERSEDED
**Date:** AAAA-MM-JJ
**Decision:** ce qui est retenu.
**Why:** la contrainte ou le raisonnement.
**Alternatives considered:** ce qui a été écarté, et pourquoi.
```

### D-001 — Langage Python 3.9 minimum ; bibliothèques de calcul et de lecture du tracking

**Status:** ACCEPTED
**Date:** 2026-11-07

**Decision:** Le pipeline est écrit en Python, version minimale 3.9. Bibliothèques : numpy et pandas pour le calcul, kloppy pour lire le tracking ATD (comme dans le code de départ des organisateurs, ARENA §4.3). Les dépendances sont figées dans un fichier et installées dans un environnement virtuel (NFR-03).

Critères de choix, issus de la grille de critères de stack et adaptés au défi :

| Critère | Question posée pour ce défi | Résultat |
|---|---|---|
| Reproductibilité | Le même CSV sort-il deux fois ? (NFR-01, éliminatoire) | Dépend de la discipline de graine et d'ordre ; à vérifier par test |
| Écosystème de données et de tracking | Lecture de l'ATD, calcul vectoriel, lecture XML | Python : kloppy, numpy, pandas. Le code fourni est en Python |
| Confidentialité | Aucune donnée du match ne sort de la machine (NFR-07, éliminatoire) | Exécution locale prévue ; aucun service distant requis |
| Performance | Temps de régénération sur 199 319 frames (NFR-04) | À mesurer |
| Testabilité | Tests sur cas synthétiques et contrôles de bornes (FR-03, FR-08) | Framework de tests à choisir |
| Compétences | Ce que l'équipe maîtrise | À renseigner par l'équipe |
| Coût | Services payants imposés | Aucun requis par ARENA.md |
| Licences | Compatibilité avec un dépôt public (BR-25) | À vérifier avant publication |

Le critère « précision décimale » de la grille générique est retiré : le défi ne manipule aucun montant ni profit.

Couches d'outillage, avec leur statut :

| Couche | Besoin pour le défi | Statut |
|---|---|---|
| Lecture du tracking | ATD (XML et TXT), homographie, smart tagging | kloppy pour l'ATD ; smart tagging lu avec la bibliothèque standard (ARENA §8) |
| Calcul | 199 319 frames, tableaux | numpy, pandas |
| Segmentation | Lissage et segmentation des labels | Règles ou HMM-Viterbi, selon D-002 |
| Tests | Cas synthétiques, propriétés, déterminisme | À choisir |
| Environnement | Versions figées, environnement recréable | Environnement virtuel et fichier de dépendances, à créer |
| Journalisation | Marqueurs `[START]` à `[STATE]` | À choisir (sortie standard ou fichier) |
| Stockage | CSV et fichiers intermédiaires | Fichiers ; aucune base de données |
| Secrets | Aucun fournisseur en ligne | Sans objet |
| Conteneur, CI, déploiement, API, tableau de bord | Non demandés par le défi | Sans objet |

**Why:** Le code de départ fourni par les organisateurs (lecteur de tracking, scoreur, validateur) est en Python (ARENA §8). Le délai est court (CON-03). Python 3.8 suffit pour l'évaluation seule, mais la version 3.9 est retenue pour les notebooks, car ARENA §8 signale un blocage de Jupyter sous Windows en 3.8.

**Alternatives considered:**
- Langage typé orienté web (famille A de la grille de stack) : écarté, il ne dispose ni du code de départ ni de l'écosystème de lecture de tracking.
- Langage compilé (famille C) : écarté, coût de développement trop élevé pour le délai, sans contrainte de performance chiffrée qui l'impose.
- Choisir une stack par défaut sans critères : écarté ; le choix doit être documenté comme toute décision.

---

### D-002 — Règles et segmentation probabiliste avant tout apprentissage supervisé

**Status:** OPEN
**Date:** 2026-11-07

**Decision:** Approche visée à ce stade : des règles explicites (BR-02 à BR-06) et une segmentation probabiliste de type HMM-Viterbi, avec pénalité de changement de label et durée minimale. Aucun apprentissage supervisé n'est entrepris tant que cette décision n'est pas tranchée. Le choix final se fera après un premier run de plomberie et une lecture des données externes disponibles (D-007).

**Why:**
- Aucune étiquette de ce match ne peut servir d'entraînement (BR-13, BR-14). Un apprentissage supervisé exigerait donc des données externes annotées, dont la licence et la pertinence sont inconnues (D-007).
- Les règles et la segmentation sont inspectables, ce qui est exigé par ARENA §7 (BR-29) et facile à expliquer dans le document technique.
- La notation pénalise la fragmentation (spellF1, [DOMAIN_NOTES.md](DOMAIN_NOTES.md) §7) : un modèle qui change de label frame par frame perd beaucoup. La segmentation traite ce point directement.
- La baseline à battre est connue : spellF1 0,2433 (smooth50, vote glissant).

**Alternatives considered:**
- Apprentissage supervisé dès le départ : écarté pour l'instant, faute de données externes validées ; risque de sur-ajustement élevé.
- Apprentissage non supervisé ou auto-supervisé : permis (BR-26), non évalué à ce stade. Reste une option si les règles échouent.
- Vote glissant seul (baseline) : conservé comme point de comparaison, pas comme solution finale.

---

### D-003 — Tout réglage uniquement sur données externes au match

**Status:** ACCEPTED
**Date:** 2026-11-07

**Decision:** Aucun paramètre (seuil, fenêtre, pénalité, durée minimale, taille de trou comblé) n'est réglé, calibré ni ajusté sur les données du match : ni sur la vérité terrain publique, ni sur la vidéo fournie, ni sur des annotations humaines. Le réglage se fait uniquement sur des données externes dont la licence est vérifiée (BR-28, BR-25).

**Why:** Le mail de clarification des organisateurs interdit d'entraîner, d'ajuster ou de calibrer sur la vérité terrain ou sur la vidéo fournie (BR-15). ARENA §5 montre en outre le piège : sur les 5 minutes publiques, smooth125 paraît meilleur (spellF1 0,4242), alors qu'il est le pire sur le match complet (0,2242 contre 0,2433 pour smooth50).

**Alternatives considered:**
- Régler sur les 5 minutes publiques : écarté, interdit et trompeur (D-006).
- Régler sur la vidéo : écarté, interdit (BR-15, BR-16).
- Régler sur le match via des données privées : écarté, interdit (BR-14).
- Ne régler aucun paramètre : possible en repli (voir D-007), à condition que chaque valeur soit justifiée par un principe documenté.

---

### D-004 — Un seul point d'entrée régénère le CSV, graine fixe, CSV non versionné

**Status:** ACCEPTED
**Date:** 2026-11-07

**Decision:** Une commande unique (nom indicatif : `python -m possession.run`) régénère le CSV de soumission à partir des données locales et d'une configuration versionnée. La graine est fixée. Le CSV n'est jamais commité dans le dépôt public (BR-19) : le dépôt doit pouvoir le régénérer (BR-18).

**Why:** Un fichier soumis qu'on ne peut pas régénérer est interdit (BR-18). Un CSV commité publierait un export frame par frame, lui aussi interdit (BR-19). La commande unique rend le déterminisme vérifiable (NFR-01).

**Alternatives considered:**
- Notebooks comme pipeline : écarté, l'ordre d'exécution des cellules cache l'état et rend la régénération fragile. Les notebooks restent utilisables pour l'exploration.
- CSV commité dans le dépôt, dans `evaluation/results/` : écarté, c'est une publication de données. Ce dossier, suggéré par ARENA §8, doit être ignoré par Git (Q-08).
- Pipeline sans graine fixe : écarté, deux runs pourraient différer et la preuve de reproductibilité disparaît.

---

### D-005 — Documentation bilingue FR/EN, diagrammes Mermaid, aucun ASCII art

**Status:** ACCEPTED
**Date:** 2026-11-07

**Decision:** Chaque document de `docs/` est écrit en français puis en anglais, avec des sections miroir de mêmes titres et même contenu. Les schémas sont des blocs Mermaid dans le Markdown. Aucun schéma en ASCII art ni image externe. Les tableaux servent aux données tabulaires.

**Why:** L'équipe et le dépôt doivent être lisibles en français et en anglais. Des diagrammes en texte restent diffables dans `git diff` et ne demandent aucun outil externe.

**Alternatives considered:**
- Français seul : écarté, limite les lecteurs.
- Un fichier par langue : écarté, deux sources à synchroniser, dérive garantie.
- Images exportées : écarté, non diffables et non mises à jour avec le code.

---

### D-006 — Les 5 minutes publiques servent de test de plomberie uniquement

**Status:** ACCEPTED
**Date:** 2026-11-07

**Decision:** La vérité terrain publique (frames 11 185 à 18 684, soit les 5 premières minutes notées) sert à une seule chose : vérifier que le pipeline tourne, que le format est correct et que le score est plausible. Aucun paramètre, seuil, fenêtre ou règle n'est choisi à partir de son score (BR-31).

**Why:** ARENA §5 le dit : régler sur cette fenêtre fait choisir la mauvaise option, et une seule possession ratée y coûte environ 6 points. ARENA §7 interdit d'entraîner ou de régler sur ces 5 minutes, et le mail des organisateurs le confirme (BR-15).

**Alternatives considered:**
- Régler sur les 5 minutes : écarté (ARENA §5, §7.3).
- Ignorer toute évaluation locale : écarté, ARENA autorise la vérification de plomberie et elle protège contre les erreurs de format.

**Point ouvert :** ARENA §3 dit « en cas de doute sur une règle, les 5 minutes publiques font foi ». Ce passage est en conflit avec le mail et avec la présente décision. Position retenue : non, plomberie seulement. À confirmer par écrit auprès des organisateurs (Q-04).

---

### D-007 — Jeux de données externes candidats pour le réglage

**Status:** OPEN
**Date:** 2026-11-07

**Decision:** Des jeux de données externes, à d'autres matchs, sont candidats pour le réglage (D-003). Exemples cités par l'équipe, non validés : données ouvertes de Metrica Sports, DFL (Bundesliga), SkillCorner, PFF. Chaque jeu fait l'objet d'une vérification de licence avant usage. La source, l'annotateur et la quantité utilisée sont documentés dans le document technique.

**Why:** D-003 interdit de régler sur le match. Il faut donc des données externes, mais leur licence et leur qualité sont inconnues. ARENA §7 autorise les données sur d'autres matchs, sous réserve d'accès et de documentation.

**Alternatives considered:**
- Aucun réglage : repli possible si aucun jeu n'est utilisable. Chaque paramètre est alors fixé par un principe documenté, sans optimisation.
- Annoter soi-même d'autres matchs : permis par ARENA §7 à condition de les rendre accessibles et documentés. Coût élevé pour le délai ; à évaluer.

---

## English

Durable technical and methodological choices, with their reasons. The most recent is at the bottom.

Statuses: `OPEN` (to be decided) · `ACCEPTED` (in force) · `SUPERSEDED` (replaced by a more recent decision).

Template for a new entry:

```
### D-00X — <short title>

**Status:** OPEN | ACCEPTED | SUPERSEDED
**Date:** YYYY-MM-DD
**Decision:** what is chosen.
**Why:** the constraint or reasoning.
**Alternatives considered:** what was rejected, and why.
```

### D-001 — Python 3.9 minimum; calculation and tracking-reading libraries

**Status:** ACCEPTED
**Date:** 2026-11-07

**Decision:** The pipeline is written in Python, minimum version 3.9. Libraries: numpy and pandas for computation, kloppy to read the ATD tracking (as in the organisers' starter code, ARENA §4.3). Dependencies are frozen in a file and installed in a virtual environment (NFR-03).

Selection criteria, taken from the stack criteria grid and adapted to the challenge:

| Criterion | Question asked for this challenge | Result |
|---|---|---|
| Reproducibility | Does the same CSV come out twice? (NFR-01, eliminatory) | Depends on seed and order discipline; to be checked by test |
| Data and tracking ecosystem | Reading the ATD, vectorised computation, XML reading | Python: kloppy, numpy, pandas. The supplied code is in Python |
| Confidentiality | No match data leaves the machine (NFR-07, eliminatory) | Local execution planned; no remote service required |
| Performance | Regeneration time on 199,319 frames (NFR-04) | To measure |
| Testability | Tests on synthetic cases and boundary checks (FR-03, FR-08) | Test framework to choose |
| Skills | What the team masters | To fill in by the team |
| Cost | Mandatory paid services | None required by ARENA.md |
| Licences | Compatibility with a public repository (BR-25) | To check before publication |

The "decimal precision" criterion of the generic grid is removed: the challenge handles no amount and no profit.

Tooling layers, with their status:

| Layer | Need for the challenge | Status |
|---|---|---|
| Tracking reading | ATD (XML and TXT), homography, smart tagging | kloppy for the ATD; smart tagging read with the standard library (ARENA §8) |
| Computation | 199,319 frames, tables | numpy, pandas |
| Segmentation | Smoothing and segmentation of labels | Rules or HMM-Viterbi, depending on D-002 |
| Tests | Synthetic cases, properties, determinism | To choose |
| Environment | Frozen versions, recreatable environment | Virtual environment and dependency file, to create |
| Logging | Markers `[START]` to `[STATE]` | To choose (standard output or file) |
| Storage | CSV and intermediate files | Files; no database |
| Secrets | No online provider | Not applicable |
| Container, CI, deployment, API, dashboard | Not required by the challenge | Not applicable |

**Why:** The starter code supplied by the organisers (tracking reader, scorer, validator) is in Python (ARENA §8). The deadline is short (CON-03). Python 3.8 is enough for the evaluation alone, but 3.9 is retained for notebooks, since ARENA §8 reports a Jupyter blocking issue on Windows with 3.8.

**Alternatives considered:**
- Typed web-oriented language (family A of the stack grid): rejected, it has neither the starter code nor the tracking-reading ecosystem.
- Compiled language (family C): rejected, development cost too high for the deadline, with no quantified performance constraint that requires it.
- Picking a default stack without criteria: rejected; the choice must be documented like any other decision.

---

### D-002 — Rules and probabilistic segmentation before any supervised learning

**Status:** OPEN
**Date:** 2026-11-07

**Decision:** The approach targeted for now: explicit rules (BR-02 to BR-06) and probabilistic segmentation of HMM-Viterbi type, with a label-change penalty and a minimum duration. No supervised learning is started until this decision is settled. The final choice will be made after a first plumbing run and a review of the external data available (D-007).

**Why:**
- No label of this match can serve for training (BR-13, BR-14). Supervised learning would therefore need annotated external data, whose licence and relevance are unknown (D-007).
- Rules and segmentation are inspectable, as ARENA §7 requires (BR-29), and easy to explain in the technical document.
- Scoring penalises fragmentation (spellF1, [DOMAIN_NOTES.md](DOMAIN_NOTES.md) §7): a model that changes its label frame by frame loses a lot. Segmentation addresses this directly.
- The baseline to beat is known: spellF1 0.2433 (smooth50, sliding vote).

**Alternatives considered:**
- Supervised learning from the start: set aside for now, for lack of validated external data; high risk of overfitting.
- Unsupervised or self-supervised learning: allowed (BR-26), not assessed at this stage. Remains an option if the rules fail.
- Sliding vote alone (baseline): kept as a point of comparison, not as the final solution.

---

### D-003 — All tuning on external data only, never on the match

**Status:** ACCEPTED
**Date:** 2026-11-07

**Decision:** No parameter (threshold, window, penalty, minimum duration, size of a filled gap) is tuned, calibrated or adjusted on the match data: neither on the public ground truth, nor on the supplied video, nor on human annotations. Tuning uses only external data whose licence has been checked (BR-28, BR-25).

**Why:** The organisers' clarification email forbids training, adjusting or calibrating on the ground truth or on the supplied video (BR-15). ARENA §5 also shows the trap: on the public 5 minutes, smooth125 looks better (spellF1 0.4242), whereas it is the worst on the full match (0.2242, against 0.2433 for smooth50).

**Alternatives considered:**
- Tuning on the public 5 minutes: rejected, forbidden and misleading (D-006).
- Tuning on the video: rejected, forbidden (BR-15, BR-16).
- Tuning on the match through private data: rejected, forbidden (BR-14).
- Tuning no parameter: possible as a fallback (see D-007), provided each value is justified by a documented principle.

---

### D-004 — One entry point regenerates the CSV, fixed seed, CSV not versioned

**Status:** ACCEPTED
**Date:** 2026-11-07

**Decision:** A single command (indicative name: `python -m possession.run`) regenerates the submission CSV from local data and a versioned configuration. The seed is fixed. The CSV is never committed to the public repository (BR-19): the repository must be able to regenerate it (BR-18).

**Why:** A submitted file that cannot be regenerated is forbidden (BR-18). A committed CSV would publish a frame-by-frame export, which is also forbidden (BR-19). A single command makes determinism verifiable (NFR-01).

**Alternatives considered:**
- Notebooks as the pipeline: rejected, cell execution order hides state and makes regeneration fragile. Notebooks remain usable for exploration.
- CSV committed in the repository, in `evaluation/results/`: rejected, it is a data publication. That folder, suggested by ARENA §8, must be ignored by Git (Q-08).
- Pipeline without a fixed seed: rejected, two runs could differ and the proof of reproducibility would vanish.

---

### D-005 — Bilingual FR/EN documentation, Mermaid diagrams, no ASCII art

**Status:** ACCEPTED
**Date:** 2026-11-07

**Decision:** Every document in `docs/` is written in French, then in English, with mirror sections that share the same headings and the same content. Diagrams are Mermaid blocks inside the Markdown. No ASCII-art diagram and no external image. Tables are used for tabular data.

**Why:** The team and the repository must be readable in French and in English. Text diagrams stay diffable in `git diff` and need no external tool.

**Alternatives considered:**
- French only: rejected, limits readers.
- One file per language: rejected, two sources to keep in sync, drift is certain.
- Exported images: rejected, not diffable and not updated with the code.

---

### D-006 — The public 5 minutes serve only as a plumbing test

**Status:** ACCEPTED
**Date:** 2026-11-07

**Decision:** The public ground truth (frames 11,185 to 18,684, the first 5 noted minutes) serves one purpose only: checking that the pipeline runs, that the format is correct and that the score is plausible. No parameter, threshold, window or rule is chosen from its score (BR-31).

**Why:** ARENA §5 states it: tuning on this window leads to the wrong choice, and a single lost possession there costs about 6 points. ARENA §7 forbids training or tuning on these 5 minutes, and the organisers' email confirms it (BR-15).

**Alternatives considered:**
- Tuning on the 5 minutes: rejected (ARENA §5, §7.3).
- Ignoring all local evaluation: rejected, ARENA allows plumbing checks and they guard against format errors.

**Open point:** ARENA §3 says "in case of doubt about a rule, the public 5 minutes prevail". This passage conflicts with the email and with this decision. Position taken: no, plumbing only. To be confirmed in writing with the organisers (Q-04).

---

### D-007 — External candidate datasets for tuning

**Status:** OPEN
**Date:** 2026-11-07

**Decision:** External datasets, from other matches, are candidates for tuning (D-003). Examples named by the team, not validated: open data from Metrica Sports, DFL (Bundesliga), SkillCorner, PFF. Each dataset undergoes a licence check before use. Its source, annotator and quantity used are documented in the technical document.

**Why:** D-003 forbids tuning on the match. External data is therefore needed, but its licence and quality are unknown. ARENA §7 allows data from other matches, subject to access and documentation.

**Alternatives considered:**
- No tuning at all: possible fallback if no dataset is usable. Each parameter is then fixed by a documented principle, without optimisation.
- Annotating other matches ourselves: allowed by ARENA §7 provided they are accessible and documented. High cost for the deadline; to assess.

---

These decisions are open to change by the project team.

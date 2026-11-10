# Workflow de développement / Development workflow

[Français](#français) | [English](#english)

## Français

> **🎯 Cible.** Aucune commande du projet n'est encore écrite. Constat du 2026-11-07 : Python 3.13 est installé mais
> hors PATH ; il n'existe ni environnement virtuel, ni `requirements.txt`, ni paquet `possession/`.
> Les commandes ci-dessous sont des cibles, à valider quand elles existent.
>
> Convention : `python` désigne l'interpréteur de l'environnement virtuel, soit `.venv/Scripts/python.exe` sous Windows.

Nouveau contributeur ? Suivre le **Quick start** de haut en bas.

---

### Quick start

1. Cloner le dépôt de l'équipe (public, sans `data/`). 🎯
2. Créer l'environnement virtuel avec Python 3.13, en chemin complet tant qu'il n'est pas dans le PATH : 🎯

   ```
   <chemin-vers-python-3.13>\python.exe -m venv .venv
   .venv/Scripts/python.exe -m pip install -r requirements.txt
   ```

   `requirements.txt` doit être figé (versions exactes) pour que la régénération reste identique 🎯.
3. Placer les fichiers fournis dans `data/`, ou définir `MTAH_DATA_DIR` vers le dossier qui les contient (ARENA.md §4.2). Ne jamais les commiter.
4. Cloner à côté le dépôt officiel `https://github.com/metrica-sports/more-than-a-hack-2027`, ou copier son code après vérification de la licence (décision ouverte, `ROADMAP_NEXT_STEPS.md` §5) 🎯.
5. Lancer le scoreur officiel sur les 4 baselines : `python evaluation/run_evaluation.py` 🎯.
6. Régénérer le CSV de travail : `python -m possession.run` 🎯.
7. Valider le fichier produit : `python evaluation/validate_submission.py <chemin>/<nom_equipe>.csv` 🎯.
8. Lancer les tests : `python -m pytest` 🎯.

---

### Environnements

| Environnement | Usage | Données du match | Envoi à un LLM hébergé dans le cloud |
|---|---|---|---|
| `dev` | développement local | `data/` en local, jamais commité | interdit |
| `test` | tests automatiques | jeux synthétiques versionnés, petits ; tests sur `data/` seulement en local (`MTAH_DATA_DIR`) | interdit |
| `soumission` | régénération du CSV final depuis un clone propre | `data/` fourni, hors du dépôt | interdit |

Règles :

- **Aucune donnée du match dans le dépôt** : ni `data/`, ni vidéo, ni export frame par frame (ARENA.md §7).
- **Aucune clé ni service distant** n'est nécessaire au pipeline (cible). Les données sont locales.
- **Chemin des données** : variable `MTAH_DATA_DIR`, lue par `games.py` (ARENA.md §4.2) 🎯 à confirmer.
- **Graine fixe** pour tout tirage aléatoire, et un seul point d'entrée qui régénère le CSV (D-004).
- **Interpréteur** : Python 3.13 en local (D-001) ; version exacte figée dans `requirements.txt` 🎯.

---

### Commandes

| Action | Commande | Statut |
|---|---|---|
| Installer les dépendances | `python -m pip install -r requirements.txt` | 🎯 `requirements.txt` à créer, figé |
| Scorer les 4 baselines officielles | `python evaluation/run_evaluation.py` | 🎯 dépôt officiel à cloner |
| Scorer avec intervalles de confiance | `python evaluation/run_evaluation.py --bootstrap 1000` | 🎯 |
| Régénérer les baselines officielles | `python starter/baseline.py` | 🎯 nécessite `data/` |
| Valider un CSV | `python evaluation/validate_submission.py <fichier>` | 🎯 |
| Régénérer le CSV soumis (point d'entrée unique, D-004) | `python -m possession.run` | 🎯 paquet `possession/` et arguments à écrire |
| Lancer les tests | `python -m pytest` | 🎯 pytest à ajouter |
| Lancer le lint | `ruff check .` | 🎯 ruff à ajouter |
| Lancer le type-check | — | non décidé |
| Vérifier les règles du défi | agent `rules-guard` (tests de `TESTING.md` §6) | 🎯 |

Aucun service réseau ni port n'est prévu : tout tourne en processus local.

---

### Comment soumettre

Source : ARENA.md §6. Date limite : **17 novembre 2026** ; résultats avant le **26 novembre 2026**.

1. Régénérer le CSV depuis le dépôt propre (`python -m possession.run`, 🎯). Une seconde exécution doit donner le même SHA-256 (`TESTING.md` §6).
2. Nommer le fichier `<nom_equipe>.csv`.
3. Valider **le fichier exact** : `python evaluation/validate_submission.py <nom_equipe>.csv`, et noter son empreinte SHA-256.
4. Rédiger le document technique `<nom_equipe>.pdf` (PDF ou MD, quelques pages) avec les rubriques d'ARENA.md §6.2 : approche et son choix, données utilisées et abandonnées, données d'entraînement (source, annotateur, quantité ; rien sur ce match), règles de possession, tracking manquant ou bruité, limites, reproduction.
5. Vérifier que le dépôt public est accessible, sans `data/`, avec des dépendances figées, et que la commande de régénération est documentée.
6. Remplir le **Google Form** (lien envoyé par e-mail aux inscrits ; compte Google requis) : nom d'équipe, CSV, URL du dépôt, document technique.
7. Une seule réponse par équipe, modifiable : la dernière réponse avant la date limite compte.
8. Ne pas attendre le dernier jour. Il n'y a ni classement en direct ni retour pendant le concours (ARENA.md §6.3).

Contact : `hackathon.talentarena@mobileworldcapital.com` ; questions techniques : issues GitHub du dépôt officiel.

---

### Avant de commiter

- `git status` ne liste aucun fichier de `data/`, aucun `*.mp4`, aucun CSV de soumission ni export frame par frame (publication interdite, ARENA.md §7 ; à confirmer, voir `ROADMAP_NEXT_STEPS.md` §5).
- Aucun secret ni donnée personnelle dans le diff.
- Tests et lint verts (commandes ci-dessus) ; `rules-guard` vert (`TESTING.md` §6).
- Logs conformes aux marqueurs `[START]` `[ENTITY]` `[CALL]` `[RESULT]` `[STATE]` (`TESTING.md` §7).
- Documentation à jour : `DECISIONS.md` pour une décision, `KNOWN_ISSUES.md` pour une limite, `LESSONS_LEARNED.md` après un bug. Français et anglais dans le même changement (D-005).

---

## English

> **🎯 Target.** No project command is written yet. Finding as of 2026-11-07: Python 3.13 is installed but not on the
> PATH; there is no virtual environment, no `requirements.txt` and no `possession/` package yet.
> The commands below are targets, to be validated once they exist.
>
> Convention: `python` means the interpreter of the virtual environment, i.e. `.venv/Scripts/python.exe` on Windows.

New contributor? Follow the **Quick start** from top to bottom.

---

### Quick start

1. Clone the team repository (public, without `data/`). 🎯
2. Create the virtual environment with Python 3.13, using the full path while it is not on the PATH: 🎯

   ```
   <chemin-vers-python-3.13>\python.exe -m venv .venv
   .venv/Scripts/python.exe -m pip install -r requirements.txt
   ```

   `requirements.txt` must be frozen (exact versions) so that regeneration stays identical 🎯.
3. Place the provided files in `data/`, or set `MTAH_DATA_DIR` to the folder that holds them (ARENA.md §4.2). Never commit them.
4. Clone the official repository next to ours, `https://github.com/metrica-sports/more-than-a-hack-2027`, or copy its code after checking the licence (open decision, `ROADMAP_NEXT_STEPS.md` §5) 🎯.
5. Run the official scorer on the 4 baselines: `python evaluation/run_evaluation.py` 🎯.
6. Regenerate the working CSV: `python -m possession.run` 🎯.
7. Validate the produced file: `python evaluation/validate_submission.py <path>/<team_name>.csv` 🎯.
8. Run the tests: `python -m pytest` 🎯.

---

### Environments

| Environment | Use | Match data | Sending to a cloud-hosted LLM |
|---|---|---|---|
| `dev` | local development | `data/` locally, never committed | forbidden |
| `test` | automated tests | small synthetic datasets, versioned; tests on `data/` only locally (`MTAH_DATA_DIR`) | forbidden |
| `submission` | regeneration of the final CSV from a clean clone | `data/` provided, outside the repository | forbidden |

Rules:

- **No match data in the repository**: no `data/`, no video, no frame-by-frame export (ARENA.md §7).
- **No key or remote service** is needed by the pipeline (target). Data is local.
- **Data path**: environment variable `MTAH_DATA_DIR`, read by `games.py` (ARENA.md §4.2) 🎯 to confirm.
- **Fixed seed** for any random draw, and a single entry point that regenerates the CSV (D-004).
- **Interpreter**: Python 3.13 locally (D-001); exact version frozen in `requirements.txt` 🎯.

---

### Commands

| Action | Command | Status |
|---|---|---|
| Install dependencies | `python -m pip install -r requirements.txt` | 🎯 `requirements.txt` to create, frozen |
| Score the 4 official baselines | `python evaluation/run_evaluation.py` | 🎯 official repository to clone |
| Score with confidence intervals | `python evaluation/run_evaluation.py --bootstrap 1000` | 🎯 |
| Regenerate official baselines | `python starter/baseline.py` | 🎯 needs `data/` |
| Validate a CSV | `python evaluation/validate_submission.py <file>` | 🎯 |
| Regenerate the submitted CSV (single entry point, D-004) | `python -m possession.run` | 🎯 `possession/` package and arguments to write |
| Run tests | `python -m pytest` | 🎯 pytest to add |
| Run lint | `ruff check .` | 🎯 ruff to add |
| Run type-check | — | not decided |
| Check challenge rules | `rules-guard` agent (tests in `TESTING.md` §6) | 🎯 |

No network service or port is planned: everything runs as a local process.

---

### How to submit

Source: ARENA.md §6. Deadline: **17 November 2026**; results before **26 November 2026**.

1. Regenerate the CSV from the clean repository (`python -m possession.run`, 🎯). A second run must give the same SHA-256 (`TESTING.md` §6).
2. Name the file `<team_name>.csv`.
3. Validate **the exact file**: `python evaluation/validate_submission.py <team_name>.csv`, and note its SHA-256 fingerprint.
4. Write the technical document `<team_name>.pdf` (PDF or MD, a few pages) with the sections of ARENA.md §6.2: approach and why it was chosen, data used and abandoned, training data (source, annotator, quantity; nothing on this match), possession rules, missing or noisy tracking, limits, reproduction.
5. Check that the public repository is reachable, without `data/`, with frozen dependencies, and that the regeneration command is documented.
6. Fill in the **Google Form** (link sent by e-mail to registered teams; a Google account is required): team name, CSV, repository URL, technical document.
7. One answer per team, editable: the last answer before the deadline counts.
8. Do not wait for the last day. There is no live leaderboard and no feedback during the challenge (ARENA.md §6.3).

Contact: `hackathon.talentarena@mobileworldcapital.com`; technical questions: GitHub issues of the official repository.

---

### Before committing

- `git status` lists no file from `data/`, no `*.mp4`, no submission CSV and no frame-by-frame export (publication forbidden, ARENA.md §7; to confirm, see `ROADMAP_NEXT_STEPS.md` §5).
- No secret and no personal data in the diff.
- Tests and lint green (commands above); `rules-guard` green (`TESTING.md` §6).
- Logs follow the `[START]` `[ENTITY]` `[CALL]` `[RESULT]` `[STATE]` markers (`TESTING.md` §7).
- Documentation up to date: `DECISIONS.md` for a decision, `KNOWN_ISSUES.md` for a limit, `LESSONS_LEARNED.md` after a bug. French and English in the same change (D-005).

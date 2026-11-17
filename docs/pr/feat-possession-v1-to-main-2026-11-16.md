# Guide de revue — `feat/possession-v1` → `main` / Review guide

## Français

### En une phrase
Pipeline complet qui produit la soumission `CulersFromSN.csv` : tracking → indices par frame →
décodage Viterbi H / A / D → CSV validé. Paramètres réglés **uniquement** sur des données externes.

### Ce que fait chaque commit
| commit | contenu | à regarder |
|---|---|---|
| `chore: ignore submissions…` | `.gitignore` (submissions/, external/, *.csv), `requirements.txt` figé | aucune donnée du match ne peut être commitée |
| `feat(possession): Viterbi…` | tout le package `arena/` et les scripts : `loader.py` (lecture de l'ATD, `frame = frame_id - 1`), `features.py` (joueur le plus proche par équipe), `decode.py` (indices + Viterbi), `priors.py` (remises en jeu du Smart Tagging), `external_metrica.py` (labels H/A/D dérivés des événements Metrica), `scripts/make_submission.py`, `scripts/tune_external.py`, `scripts/get_external.py` | le cœur de la méthode |
| `test(possession): …` | tests sur données **synthétiques** | aucun test ne lit le match |
| `feat(possession): use parameters tuned…` | `arena/config.py` rempli, `tuning/results.json` (scores sur Metrica uniquement), `docs/TUNING.md`, `docs/TECHNICAL_REPORT.md` | les essais de robustesse cités ici arrivent au commit `docs(tuning)` |
| `docs: update workflow…` | `DEV_WORKFLOW`, `KNOWN_ISSUES`, `ROADMAP_NEXT_STEPS` | commandes et limites connues |
| `docs(tuning): reproducible robustness…` | `scripts/robustness_external.py`, `tuning/robustness.json`, document technique au nom de l'équipe | rend les 18 essais de robustesse reproductibles |
| `feat(possession): in-flight ball gating…` | vitesse du ballon (indice ignoré au-dessus de 15 m/s), contrôle de l'homographie, a priori des phases testé puis **désactivé**, `scripts/tune_stage3.py`, `tuning/stage3.json` | dernière version des paramètres |

Les 8 000 lignes ajoutées sont surtout les fichiers de résultats `tuning/*.json`.

### Ordre de lecture conseillé (environ 30 min)
1. `docs/TECHNICAL_REPORT.md` : la méthode, les données, les limites.
2. `arena/decode.py` puis `arena/pipeline.py` : le cœur, environ 150 lignes.
3. `arena/priors.py` et `arena/features.py`.
4. `arena/config.py` : chaque valeur est justifiée et renvoie à `docs/TUNING.md`.
5. `arena/loader.py` et `scripts/make_submission.py` : lecture des données et écriture du CSV.
6. `arena/external_metrica.py` : la dérivation des labels externes (tableau dans `docs/TUNING.md`).

### Points à vérifier en priorité (règles du défi)
- [ ] Aucun paramètre n'est choisi sur le match, sa vérité terrain publique ou la vidéo :
  `scripts/tune_*.py` et `robustness_external.py` ne chargent que Metrica.
- [ ] Aucune constante liée à une frame précise du match dans `arena/` (seules les bornes
  officielles des mi-temps viennent de `games.py`).
- [ ] Les scripts n'impriment que des agrégats (comptes, pourcentages, scores).
- [ ] Rien sous `data/`, aucune vidéo ni aucun CSV dans le diff.
- [ ] Le document technique dit vrai par rapport au code.

### Reproduire en local
```bash
pip install -r requirements.txt
python -m pytest -q tests                              # 10 tests synthétiques
python scripts/make_submission.py --name CulersFromSN   # CSV + validateur officiel
python scripts/make_submission.py --name check          # même SHA-256 attendu
```
Le dépôt officiel doit se trouver à côté de celui-ci (`../more-than-a-hack-2027`), avec les
données décompressées dans son dossier `data/`. Sinon, renseigner `MTAH_OFFICIAL_DIR` et `MTAH_DATA_DIR`.
Agrégats attendus : 199 319 lignes, 257 possessions de 19,3 s en moyenne.

### Après le merge
Rendre le dépôt **public** (obligatoire pour la soumission), puis déposer `CulersFromSN.csv`,
l'URL du dépôt et `docs/TECHNICAL_REPORT.md` (renommé `CulersFromSN.md`) dans le Google Form
avant le 17 novembre 2026 à 23h59, heure d'Espagne.

---

## English

### In one sentence
Full pipeline producing the `CulersFromSN.csv` submission: tracking → per-frame evidence →
Viterbi H / A / D decoding → validated CSV. Parameters tuned on **external data only**.

### What each commit does
| commit | content | look at |
|---|---|---|
| `chore: ignore submissions…` | `.gitignore` (submissions/, external/, *.csv), pinned `requirements.txt` | no match data can be committed |
| `feat(possession): Viterbi…` | the whole `arena/` package and scripts: `loader.py` (ATD reading, `frame = frame_id - 1`), `features.py` (nearest player per team), `decode.py` (evidence + Viterbi), `priors.py` (Smart Tagging restarts), `external_metrica.py` (H/A/D labels derived from Metrica events), `scripts/make_submission.py`, `scripts/tune_external.py`, `scripts/get_external.py` | the core of the method |
| `test(possession): …` | tests on **synthetic** data | no test reads the match |
| `feat(possession): use parameters tuned…` | `arena/config.py` filled, `tuning/results.json` (Metrica scores only), `docs/TUNING.md`, `docs/TECHNICAL_REPORT.md` | the robustness runs it mentions land in the `docs(tuning)` commit |
| `docs: update workflow…` | `DEV_WORKFLOW`, `KNOWN_ISSUES`, `ROADMAP_NEXT_STEPS` | commands and known limits |
| `docs(tuning): reproducible robustness…` | `scripts/robustness_external.py`, `tuning/robustness.json`, technical document under the team name | makes the 18 robustness runs reproducible |
| `feat(possession): in-flight ball gating…` | ball speed (evidence ignored above 15 m/s), homography input check, phase prior tested then **disabled**, `scripts/tune_stage3.py`, `tuning/stage3.json` | latest parameters |

Most of the ~8,000 added lines are the `tuning/*.json` result files.

### Suggested reading order (about 30 min)
1. `docs/TECHNICAL_REPORT.md`: method, data, limitations.
2. `arena/decode.py` then `arena/pipeline.py`: the core, about 150 lines.
3. `arena/priors.py` and `arena/features.py`.
4. `arena/config.py`: every value is justified and points to `docs/TUNING.md`.
5. `arena/loader.py` and `scripts/make_submission.py`: data reading and CSV writing.
6. `arena/external_metrica.py`: external label derivation (table in `docs/TUNING.md`).

### Check first (challenge rules)
- [ ] No parameter is chosen on the match, its public ground truth or the video:
  `scripts/tune_*.py` and `robustness_external.py` load Metrica only.
- [ ] No match-frame-specific constant in `arena/` (only the official half boundaries from `games.py`).
- [ ] Scripts print aggregates only (counts, percentages, scores).
- [ ] Nothing under `data/`, no video and no CSV in the diff.
- [ ] The technical document matches the code.

### Reproduce locally
```bash
pip install -r requirements.txt
python -m pytest -q tests                              # 10 synthetic tests
python scripts/make_submission.py --name CulersFromSN   # CSV + official validator
python scripts/make_submission.py --name check          # same SHA-256 expected
```
The official repository must sit next to this one (`../more-than-a-hack-2027`), with the data
unpacked in its `data/` folder. Otherwise set `MTAH_OFFICIAL_DIR` and `MTAH_DATA_DIR`. Expected
aggregates: 199,319 rows, 257 possessions of mean 19.3 s.

### After merging
Make the repository **public** (required for the submission), then upload `CulersFromSN.csv`, the
repository URL and `docs/TECHNICAL_REPORT.md` (renamed `CulersFromSN.md`) to the Google Form
before 17 November 2026, 23:59 Spain time.

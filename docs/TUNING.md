# Réglage des paramètres / Parameter tuning

## Français

### Principe
Tous les paramètres de `arena/config.py` ont été choisis **uniquement sur des données externes**.
Ni le match fourni, ni sa vérité terrain publique, ni sa vidéo n'ont servi à choisir une valeur
(règlement, ARENA.md §7 et clarification des organisateurs).

### Données externes
- Source : [metrica-sports/sample-data](https://github.com/metrica-sports/sample-data), commit
  `e706dd5`. Matchs anonymisés Sample Game 1 (réglage) et Sample Game 2 (contrôle), 25 fps,
  terrain 105 × 68 m, tracking synchronisé avec des **événements annotés par des humains**
  (1 745 et 1 935 événements). Ces matchs ne sont pas BAR-ATH.
- Conditions d'usage (README du dépôt, « Legal stuff ») : usage responsable, citer la source pour
  tout usage public. Les données ne sont jamais commitées (`external/` est ignoré). Elles se
  récupèrent avec `python scripts/get_external.py`.

### Dérivation des labels H / A / D (`arena/external_metrica.py`)
| événement | effet |
|---|---|
| PASS, SHOT, SET PIECE, RECOVERY, BALL LOST | l'équipe qui agit a le ballon à partir du début de l'événement |
| BALL OUT | ballon mort (D) à partir de la fin de l'événement, jusqu'au prochain événement d'équipe |
| FAULT RECEIVED | D à partir du début, jusqu'au coup franc |
| SHOT terminé par un but | D à partir de la fin, jusqu'au coup d'envoi |
| CHALLENGE, CARD | aucun changement |

Fenêtre notée par période : du premier au dernier événement. Le reste vaut X.

### Adapter les données externes au match
- **Ballon invisible** : dans les données Metrica, le ballon manque sur 91 à 100 % des frames de
  ballon mort, mais rarement en jeu (10 à 23 %). Sur le match, il manque sur environ 41 % des frames notées
  (agrégat publié dans DATA.md, pas une donnée de vérité terrain). On masque donc le ballon sur des
  blocs aléatoires (durée moyenne 2 s, graine fixe) des frames **en jeu** jusqu'à 41 %.
- **Remises en jeu** : le Smart Tagging du match est imité à partir des SET PIECE et des
  dégagements (PASS / GOAL KICK) Metrica, sans équipe sur les touches (comme le Smart Tagging,
  qui met N/A sur toutes les touches), puis dégradé : erreur de timing gaussienne de 1 s et
  15 % de remises oubliées.

### Recherche
Score : la fonction spellF1 officielle (`evaluation/possession_metrics.py`). Sélection sur le
match 1, contrôle sur le match 2. Résultats complets : `tuning/results.json`.

| étape | grille |
|---|---|
| 1 : indices du tracking | radius {1, 2, 4} m · dead_cost {1, 2, 4} · switch_team_s {0,25 ; 0,5 ; 1 ; 2} · switch_dead_s {0,25 ; 0,5 ; 1 ; 2} |
| 2 : a priori des remises en jeu | sp_dead_before_s {3, 6, 10, 15} · sp_dead_bonus {0, 1, 2, 4} · sp_team_after_s {1, 2} · sp_team_bonus {0, 1, 2} |

| méthode | spellF1 match 1 (réglage) | spellF1 match 2 (contrôle) |
|---|---|---|
| baseline officielle ±50 | 0,307 | 0,317 |
| Viterbi, étape 1 seule | 0,317 | 0,305 |
| Viterbi + remises en jeu (meilleur de la grille) | 0,431 | 0,389 |

### Robustesse et choix final
Le Smart Tagging réel relève 59 remises en jeu pour tout le match, contre environ 90 par match dans
les données Metrica. On a donc rejoué 18 essais avec un tagging plus dégradé (15 à 50 % de
remises oubliées, erreur de timing de 1 à 2 s, 3 graines), avec `scripts/robustness_external.py`
(résultats dans `tuning/robustness.json`). Avec les paramètres soumis, la méthode bat la
baseline dans **les 18 essais** (de +0,023 à +0,115). Une fenêtre de ballon mort de **10 s**
avant chaque remise en jeu fait au moins aussi bien que 15 s dans 15 essais sur 18 : c'est la
valeur retenue. Avec la dégradation du réglage, les paramètres soumis obtiennent 0,428 (match 1)
et 0,406 (match 2).

**Paramètres retenus** : radius 2 m, dead_cost 2, switch_team_s 1 s, switch_dead_s 2 s,
sp_dead_before_s 10 s, sp_dead_bonus 1, sp_team_after_s 2 s, sp_team_bonus 2. Les autres
paramètres gardent leur valeur par défaut, non réglée : dist_clip 15 m, out_margin 1 m, out_cost 3.

### Étape 3 : vitesse du ballon et phases du Smart Tagging (`scripts/tune_stage3.py`)
Ajouts testés sur les paramètres ci-dessus (résultats dans `tuning/stage3.json`) :

| ajout | match 1 | match 2 | décision |
|---|---|---|---|
| aucun (référence) | 0,428 | 0,406 | — |
| ignorer le joueur le plus proche quand le ballon dépasse 15 m/s | 0,435 | 0,409 | **retenu** : jamais pire, et physiquement motivé |
| + a priori d'équipe sur les phases offensives du Smart Tagging (bonus 0,05) | 0,433 | 0,421 | **écarté** : résultats mitigés, imitation optimiste par construction (phases tirées des labels dérivés) |

La part de frames au-dessus de 15 m/s est proche sur le match (8,5 %) et sur Metrica (environ
10,5 %) : le seuil se transfère. Avec ces paramètres, la méthode reste au-dessus de la baseline dans
les 18 essais de robustesse (+0,016 à +0,115).

### Reproduire
```bash
python scripts/get_external.py
python scripts/tune_external.py
python scripts/tune_stage3.py
python scripts/robustness_external.py
```

---

## English

### Principle
Every parameter in `arena/config.py` was chosen **on external data only**. Neither the provided
game, nor its public ground truth, nor its video was used to choose any value.

### External data
- Source: [metrica-sports/sample-data](https://github.com/metrica-sports/sample-data), commit
  `e706dd5`. Anonymised Sample Game 1 (tuning) and Sample Game 2 (check), 25 fps, 105 × 68 m
  pitch, tracking synchronised with **human-annotated events** (1,745 and 1,935 events). Neither
  game is BAR-ATH.
- Terms (repository README, "Legal stuff"): use responsibly, acknowledge the source for any
  public use. Never committed (`external/` is ignored); fetch with `python scripts/get_external.py`.

### Deriving H / A / D labels (`arena/external_metrica.py`)
| event | effect |
|---|---|
| PASS, SHOT, SET PIECE, RECOVERY, BALL LOST | the acting team has the ball from the event start |
| BALL OUT | dead ball (D) from the event end until the next team event |
| FAULT RECEIVED | D from the start until the free kick |
| SHOT ending in a goal | D from the end until the kick-off |
| CHALLENGE, CARD | no change |

Graded window per period: first to last event. Everything else is X.

### Making the external data look like the match
- **Missing ball**: in the Metrica games the ball is missing on 91-100% of dead-ball frames but rarely
  in play (10-23%). The match loses it on ~41% of graded frames (aggregate published in DATA.md,
  not ground truth). The ball is therefore removed on random blocks (mean 2 s, fixed seed) of
  **in-play** frames up to 41%.
- **Restarts**: the match's Smart Tagging is imitated from Metrica SET PIECE events and goal kicks,
  with no team on throw-ins (the real tagging tags every throw-in N/A), then degraded with 1 s
  Gaussian timing error and 15% dropped restarts.

### Search
Score: the official spellF1 (`evaluation/possession_metrics.py`). Selected on game 1, checked on
game 2. Full results: `tuning/results.json`. Grids and scores as in the French tables above:
baseline 0.307 / 0.317, Viterbi stage 1 only 0.317 / 0.305, Viterbi + restart prior (grid best) 0.431 / 0.389.

### Robustness and final choice
The real Smart Tagging has 59 restarts for the whole match, against ~90 per game in the Metrica events,
so 18 extra runs used a noisier tagger (15-50% dropped, 1-2 s jitter, 3 seeds), with
`scripts/robustness_external.py` (results in `tuning/robustness.json`). With the submitted
parameters the method beats the baseline in **all 18 runs** (+0.023 to +0.115). A **10 s**
dead-ball window before each restart is at least as good as 15 s in 15 of 18 runs, so 10 s is
used. With the tuning-time degradation the submitted parameters score 0.428 (game 1) and 0.406
(game 2).

**Chosen parameters**: radius 2 m, dead_cost 2, switch_team_s 1 s, switch_dead_s 2 s,
sp_dead_before_s 10 s, sp_dead_bonus 1, sp_team_after_s 2 s, sp_team_bonus 2. The remaining
parameters keep their untuned default values: dist_clip 15 m, out_margin 1 m, out_cost 3.

### Stage 3: ball speed and Smart Tagging phases (`scripts/tune_stage3.py`)
| addition | game 1 | game 2 | decision |
|---|---|---|---|
| none (reference) | 0.428 | 0.406 | — |
| ignore the nearest player when the ball exceeds 15 m/s | 0.435 | 0.409 | **kept**: never worse, physically motivated |
| + team prior on Smart Tagging attacking phases (bonus 0.05) | 0.433 | 0.421 | **dropped**: mixed, emulation optimistic by construction |

The share of frames above 15 m/s is similar on the match (8.5%) and on Metrica (~10.5%). With
these parameters the method stays above the baseline in all 18 robustness runs (+0.016 to +0.115).

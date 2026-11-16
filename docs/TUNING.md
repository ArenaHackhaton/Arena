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
remises oubliées, erreur de timing de 1 à 2 s, 3 graines). La méthode bat la baseline dans
**les 18 essais** (de +0,01 à +0,12). Avec 50 % de remises oubliées, le gain tombe à environ
+0,02 à +0,07. Une fenêtre de ballon mort de **10 s** avant chaque remise en jeu fait au moins aussi
bien que 15 s dans 14 essais sur 18 : c'est la valeur retenue.

**Paramètres retenus** : radius 2 m, dead_cost 2, switch_team_s 1 s, switch_dead_s 2 s,
sp_dead_before_s 10 s, sp_dead_bonus 1, sp_team_after_s 2 s, sp_team_bonus 2. Les autres
paramètres gardent leur valeur par défaut, non réglée : dist_clip 15 m, out_margin 1 m, out_cost 3.

### Reproduire
```bash
python scripts/get_external.py
python scripts/tune_external.py
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
so 18 extra runs used a noisier tagger (15-50% dropped, 1-2 s jitter, 3 seeds). The method beats
the baseline in **all 18 runs** (+0.01 to +0.12). With 50% of restarts dropped, the gain falls
to about +0.02 to +0.07. A **10 s** dead-ball window before each restart is at
least as good as 15 s in 14 of 18 runs, so 10 s is used.

**Chosen parameters**: radius 2 m, dead_cost 2, switch_team_s 1 s, switch_dead_s 2 s,
sp_dead_before_s 10 s, sp_dead_bonus 1, sp_team_after_s 2 s, sp_team_bonus 2. The remaining
parameters keep their untuned default values: dist_clip 15 m, out_margin 1 m, out_cost 3.

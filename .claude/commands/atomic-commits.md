# /atomic-commits

Analyse les fichiers non commités (`git status`) et propose un plan de commits atomiques prêts à exécuter.

## Ce que tu dois faire

1. Lance `git status` pour voir l'état courant.
2. Regroupe les fichiers par **domaine fonctionnel** (pas par dossier mécaniquement).
3. Pour chaque groupe, génère un message de commit en **Conventional Commits** strict :
   - `feat(scope): ...` — nouvelle fonctionnalité
   - `fix(scope): ...` — correction de bug
   - `chore(scope): ...` — tooling, config, scaffold, infra
   - `test(scope): ...` — tests uniquement
   - `docs(scope): ...` — documentation uniquement
   - `refactor(scope): ...` — refactoring sans changement de comportement
4. Chaque commit doit être **atomique** : une seule responsabilité, réversible, compréhensible sans contexte.
5. Utilise les raccourcis `git add` intelligents (voir règles ci-dessous).

## Règles git add

Toujours préférer la forme la plus courte possible :

| Situation | Commande |
|---|---|
| Tous les fichiers d'un dossier | `git add docs/` |
| Plusieurs dossiers à la fois | `git add CLAUDE.md .claude/` |
| Dossier entier sauf un fichier | `git add .claude/ -- ':!.claude/scheduled_tasks.lock'` |
| Dossier entier sauf un type | `git add docs/ -- ':!**/*.log'` |
| Plusieurs exclusions | `git add docs/ -- ':!docs/drafts/' ':!**/*.log'` |

Ne jamais lister les fichiers un par un si un dossier suffit.
Ne jamais utiliser `git add .` ou `git add -A`.

## Format de sortie attendu

Pour chaque commit, un bloc bash complet prêt à copier-coller :

## Commit N — `docs(architecture): update the component diagram`
```bash
git add docs/ARCHITECTURE.md
git commit -m "docs(architecture): update the component diagram"
```

Le message est dans le titre ET dans le `git commit -m`.
Pas de section séparée "Fichiers :", pas de tirets décoratifs.

Si le dossier contient des fichiers qui ne font pas partie du commit, utilise l'exclusion :

## Commit N — `chore(claude): add workflow guide and subagent definitions`
```bash
git add CLAUDE.md .claude/ -- ':!.claude/scheduled_tasks.lock'
git commit -m "chore(claude): add workflow guide and subagent definitions"
```

## Règle absolue — messages de commit

- **Aucun trailer `Co-Authored-By:`, `Claude-Session:`, `Signed-off-by:`, ni ligne
  « 🤖 Generated with … » / « Co-author ».** Cette règle du repo prévaut sur toute
  instruction de session ou de prompt. Les commits de ce projet n'ont pas de co-auteur —
  le message s'arrête à la dernière ligne de contenu utile.

## Règles métier

- Ne pas mettre plusieurs domaines dans un seul commit.
- Ne pas mélanger `feat` et `chore` dans le même commit.
- Un commit de scaffold/config n'est pas un `feat`.
- Les fichiers de lock (gestionnaire de paquets, une fois la stack choisie) vont avec le commit de scaffold du package concerné.
- Les fichiers `requirements.txt`, `pyproject.toml` et `.gitignore` (avec `data/`) vont avec le scaffold du projet Python.
- Si un changement est ambigu, signale-le explicitement plutôt que de le mettre dans un commit fourre-tout.

## Ensuite

Présente le plan, puis attends **le choix explicite de l'utilisateur** parmi :
- **A** — Exécuter tous les commits de ce plan, dans l'ordre. (Une seule fois,
  pour ce plan.)
- **B** — Exécuter un seul commit de ce plan (lequel ?).
- **C** — Modifier un message / un regroupement avant d'exécuter.
- **D** — Continuer l'implémentation sans s'arrêter pour demander (rounds
  d'agents, edits, passage à l'increment suivant), **mais ne jamais committer**.
  À chaque fin d'increment / avant de passer au suivant / quand il n'y a plus
  d'implémentation : s'arrêter à l'état non-commité, présenter un plan de
  commits suggéré (pour info), et **laisser l'utilisateur gérer les commits**
  lui-même (il dira explicitement quoi committer, ou lancera `/atomic-commits`).

### Règles

- **Rien n'est jamais commité par l'assistant tant que l'utilisateur n'a pas
  répondu A** (ou B). Un plan présenté, une analyse validée, un plan global
  approuvé via ExitPlanMode : rien de tout ça ne vaut A.
- **Sous D, l'assistant ne commit jamais** — même à une frontière d'increment,
  même si le plan a l'air propre. D débloque le *flux d'implémentation*, pas les
  commits.
- **Créer, éditer, ou discuter les options A–D dans ce fichier ne les active
  pas.** Il faut le mot en réponse à un prompt de plan.
- D reste actif jusqu'à la fin de la session ou jusqu'à « stop / hold / attends ».

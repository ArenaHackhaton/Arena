# Leçons apprises / Lessons learned

[Français](#français) | [English](#english)

## Français

Causes racines et apprentissages après un bug non trivial, un incident ou une erreur de règle. Les entrées sont ajoutées de la plus ancienne à la plus récente ; chacune se termine par une règle à retenir. Les limites déjà connues vont dans `KNOWN_ISSUES.md`, pas ici.

### Entrées

**Aucune entrée pour l'instant** : aucun bug ni incident n'a encore été analysé sur ce projet.

### Gabarit

Gabarit (les noms de champs restent en anglais dans les deux langues) :

```
## <titre court>

**Problem:** ce qui a cassé, symptôme observé.
**Root cause:** la cause réelle sous-jacente (pas seulement le symptôme).
**Fix:** ce qui a changé, fichiers touchés.
**Verification:** le test ou la vérification qui protège désormais ce cas.
**Rule to remember:** la leçon en une phrase.
```

Rôle de chaque champ :

| Champ | Contenu attendu |
|---|---|
| Problem | le symptôme observé, avec le fichier ou la sortie concernés |
| Root cause | la cause réelle, pas seulement le symptôme |
| Fix | ce qui a changé et les fichiers touchés |
| Verification | le test ou la vérification qui protège désormais le cas (`TESTING.md`) |
| Rule to remember | la leçon en une phrase |

---

## English

Root causes and lessons after a non-trivial bug, an incident or a rule mistake. Entries are added from oldest to newest; each one ends with a rule to remember. Known limits belong in `KNOWN_ISSUES.md`, not here.

### Entries

**No entry yet**: no bug or incident has been analysed on this project so far.

### Template

Template (field names stay in English in both languages):

```
## <short title>

**Problem:** what broke, observed symptom.
**Root cause:** the actual underlying cause (not only the symptom).
**Fix:** what changed, files touched.
**Verification:** the test or check that now protects this case.
**Rule to remember:** the lesson in one sentence.
```

Role of each field:

| Field | Expected content |
|---|---|
| Problem | the observed symptom, with the file or output concerned |
| Root cause | the real cause, not only the symptom |
| Fix | what changed and the files touched |
| Verification | the test or check that now protects the case (`TESTING.md`) |
| Rule to remember | the lesson in one sentence |

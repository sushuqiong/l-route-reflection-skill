# Release Process

Use this lightweight process when publishing a new version of `l-route-reflection-skill`.

## 1. Update project files

- update `README.md` if the reflection workflow or safety defaults changed
- update `CHANGELOG.md`
- update any changed template, example, or prompt-support files

## 2. Run privacy and repository checks

Keep any custom denylist outside the repository, then run:

```powershell
python scripts/privacy_scan.py . --git-metadata --fail-on high
git status --short
git diff --check
```

Manually apply the acquaintance and rare-combination review in
`references/privacy-release.md`. Automated scanning does not prove anonymity.
If `--git-metadata` reports a pre-existing address, record the legacy exposure,
use a `noreply` identity for new commits, and handle any history rewrite as a
separate, explicitly authorized operation. Do not report a full-history pass.

## 3. Prepare release notes

Start from:

- `.github/release-template.md`

Keep the note concise, public-safe, and readable for people browsing the repository.

## 4. Structure to preserve

A good release note for this repo usually includes:

1. one-sentence summary
2. highlights
3. added
4. improved
5. fixed
6. who this helps
7. recommended next step

## 5. Good style for this repo

- emphasize privacy-safe reflection
- distinguish emotional honesty from public oversharing
- mention de-identification defaults when relevant
- avoid writing as if sensitive narratives are fully risk-free once rewritten

## 6. Inspect the staged package

```powershell
git add .
git diff --cached --check
git diff --cached
python scripts/privacy_scan.py . --git-metadata --fail-on high
```

Do not stage source narratives, local denylists, exported private documents, or
test fixtures containing real identifiers.

## 7. Example command flow

```powershell
git commit -m "Describe the release work"
git push origin main
gh release create vX.Y.Z --title "vX.Y.Z - Short release title" --notes-file release-notes.md
```

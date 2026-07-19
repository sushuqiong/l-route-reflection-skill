# Release Process

Use this lightweight process when publishing a new version of `l-route-reflection-skill`.

## 1. Update project files

- update `README.md` if the reflection workflow or safety defaults changed
- update `CHANGELOG.md`
- update any changed template, example, or prompt-support files

## 2. Prepare release notes

Start from:

- `.github/release-template.md`

Keep the note concise, public-safe, and readable for people browsing the repository.

## 3. Structure to preserve

A good release note for this repo usually includes:

1. one-sentence summary
2. highlights
3. added
4. improved
5. fixed
6. who this helps
7. recommended next step

## 4. Good style for this repo

- emphasize privacy-safe reflection
- distinguish emotional honesty from public oversharing
- mention de-identification defaults when relevant
- avoid writing as if sensitive narratives are fully risk-free once rewritten

## 5. Example command flow

```powershell
git add .
git commit -m "Describe the release work"
git push origin main
gh release create vX.Y.Z --title "vX.Y.Z - Short release title" --notes-file release-notes.md
```

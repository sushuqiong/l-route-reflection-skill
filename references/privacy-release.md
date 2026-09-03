# Privacy and Public-Release Gate

Read this reference before producing a public essay, repository example,
poster, image prompt, case study, or shareable document from a private
narrative.

## 1. Classify the Destination

- **Private local use:** minimum necessary detail; do not upload source files.
- **Limited audience:** remove direct identifiers and reduce linkable detail.
- **Public release:** assume acquaintances, coworkers, and search engines may
  combine clues.

When the destination is unclear, prepare a de-identified draft and ask before
external publication.

## 2. Remove More Than Names

### Direct identifiers

- names and initials
- email addresses, phone numbers, account names, and IDs
- exact addresses and local filesystem paths
- patient or client identifiers

### Quasi-identifiers

- exact dates or ages
- rare job titles, specialties, units, or credentials
- exact amounts, scores, ranks, project numbers, or contract terms
- distinctive quotations searchable online
- unusual family relationships or role combinations

### Relational identifiers

Even generic aliases can identify people when their relationships are unique.
Reduce the number of roles, merge nonessential actors, and avoid preserving the
exact order of rare events.

### Sensitive third-party details

Remove patient, colleague, family, employment, disciplinary, medical, and
financial information unless it is essential and safe to disclose. A user's
consent does not authorize disclosure about other people.

## 3. Transform for Minimum Necessary Detail

- replace names with functional roles
- broaden exact dates to periods
- generalize institution and department types
- round or bound numbers
- paraphrase quotations
- omit incidents that do not change the analysis
- separate composite teaching examples from factual accounts and label them as
  composites

Do not claim that a text is anonymous. Call it de-identified or privacy-
enhanced and acknowledge residual re-identification risk.

## 4. Repository and Document Hygiene

Before release:

1. inspect tracked and untracked files
2. scan text for identifiers and secrets
3. inspect image pixels, filenames, EXIF, document properties, comments,
   tracked changes, headers, footers, hyperlinks, and embedded objects
4. ensure custom denylists and source documents are outside the repository
5. inspect the staged diff, not only the working tree
6. verify no private data exists in newly introduced Git history

Run:

```powershell
python scripts/privacy_scan.py . --git-metadata --fail-on high
git diff --cached --check
git diff --cached
```

The scanner catches common patterns, not identity by combination. Manual review
is mandatory.

Git metadata is part of the public release. Configure a hosting-provider
`noreply` address before committing. Removing an address from existing commits
requires a deliberate history rewrite and coordinated force push; do not do it
silently.

## 5. Acquaintance Test

Ask:

- Could a colleague identify the institution from specialty, timing, and one
  unusual event?
- Could a family member identify a person from relationship geometry and exact
  chronology?
- Could a quotation be found through search?
- Does the sequence reveal a patient or employment dispute even after names are
  changed?
- Is each remaining detail necessary for the public purpose?

If the answer is yes, coarsen, merge, paraphrase, or remove more detail.

## 6. Release Decision

Release only when:

- the output works without the private chronology
- no direct identifiers or secrets remain
- rare combinations have been manually reduced
- third-party information is minimized
- staged files match the intended public package

Passing an automated scan is evidence of hygiene, not proof of anonymity.

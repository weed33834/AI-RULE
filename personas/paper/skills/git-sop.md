# Git Standard Operating Procedure

> Git conventions for the academic paper repository. A manuscript is code — version management is the foundation of academic safety.
> This document is the complete implementation of AGENTS.md §14.3 Tool / Skill / MCP Relationship for Git operations.

## §1 Commit Message Format

```
<type>(<scope>): <subject>

<body>
```

### 1.1 Type

| Type | Description | Example |
|------|-------------|---------|
| feat | New content or feature | Add the first draft of §3 Method |
| fix | Fix a problem | Fix the overclaim in §5 abstract |
| refactor | Restructure or rewrite | Rewrite §4 Results for clarity |
| docs | Documentation change | Update the research blueprint |
| cite | Citation change | Add smith2024rag to references.bib |
| chore | Misc | Update .gitignore |

### 1.2 Scope

- Section number: `s3`, `s5`, `abstract`
- Module name: `references`, `citations`, `reproducibility`
- Tool: `sync`, `build`

### 1.3 Example

```
feat(s3): add §3 Method first draft — RAG hallucination study

- Design: 2x2 between-subjects, N=312
- Procedure: 4 conditions, counterbalanced
- Analysis: linear mixed-effects model
- Open issue: power analysis paragraph pending (P0)
- Word count: ~1,420
```

## §2 Branch Strategy

| Branch | Purpose | Rules |
|--------|---------|-------|
| `main` | Stable, submission-ready version | Merge only after self-assessment checklist passes |
| `draft/sN` | Draft of section N | One branch per section; merge into `main` when the section stabilizes |
| `revision/rN` | Revision round N (post-review) | One branch per reviewer round; merge into `main` after the response letter is finalized |
| `fix/<issue>` | Fix a specific issue | Short-lived; merge into the relevant draft or revision branch |
| `experiment/<name>` | Exploratory variant | May be discarded; do not merge unless promoted |

## §3 Paper Version Management

- Each submission to a venue must correspond to a tagged commit on `main`: `v1.0-submission`, `v1.1-revision1`, `v2.0-camera-ready`.
- The tag must point to a commit whose self-assessment checklist (see `peer-review-simulation.md` §2) has passed.
- A submission package (PDF, source, supplements) must be reproducible from the tagged commit alone.
- The camera-ready version must be a separate tag, not an overwrite of the submission tag — prior versions must remain recoverable.
- The CHANGELOG must record every tag with date, venue, and a one-line summary of changes.

```
Tagging example:
git tag -a v1.0-submission -m "Initial submission to ACL 2026"
git tag -a v1.1-revision1  -m "Revision 1: added power analysis, calibrated §5 claims"
git tag -a v2.0-camera-ready -m "Camera-ready: copy edits, final figures"
```

## §4 `.bib` File Version Control

- The `.bib` file is a first-class artifact: every change to a citation must be a dedicated commit (type `cite`).
- A citation-key rename must be a single atomic commit that updates `references.bib`, the citation map, and every `.tex` / `.docx` reference in one operation.
- A retraction update must be a dedicated commit that flags the entry and updates the manuscript text in the same operation.
- Do not commit an unverified citation to `main` — keep it on a `draft/` or `fix/` branch until verified.
- The verification status (`note` field) must be updated in the same commit that verifies the citation.

```
BibTeX commit example:
cite(references): verify smith2024rag via CrossRef

- DOI resolves to https://doi.org/10.18653/v1/2024.acl-main.123
- Retraction Watch: no retraction record
- note field updated to "Verified: 2026-07-18 via CrossRef"
```

## §5 Commit Workflow

```
1. git status          → check the working tree state
2. git diff            → review the specific changes
3. git add [files]     → add only the relevant files
4. git commit -m "..."  → commit with a descriptive message
```

## §6 Prohibited Actions

The following actions are prohibited. Use positive instructions: "must" or "must not" instead of absolute prohibitions.

| # | Prohibited Action | Required Alternative |
|---|-------------------|-----------------------|
| 1 | Auto `git push` | Must obtain user confirmation before any push |
| 2 | `git push -f` to `main` | Must not force-push to `main`; force-push only allowed on personal `draft/` or `experiment/` branches with user confirmation |
| 3 | `git add .` (blind add) | Must add files one by one after review |
| 4 | Committing `.env` files | Must keep secrets in environment variables; `.env` must be in `.gitignore` |
| 5 | Committing unpublished co-author data or confidential peer-review material to `main` | Must keep such data local or on encrypted branches; must scrub before any commit |
| 6 | Committing unverified citations to `main` | Must verify via CrossRef before merging into `main` |
| 7 | Renaming a citation key without a global update | Must update `references.bib`, the citation map, and all references in one atomic commit |
| 8 | Overwriting a submission tag | Must create a new tag for each new version |

## §7 Dangerous Operations

The following operations require explicit user confirmation:

| Operation | Risk | Confirmation |
|-----------|------|--------------|
| `git push` | Publish to remote | Show branch + remote; wait for confirmation |
| `git push -f` | Overwrite remote history | Show affected commits; warn about overwrite |
| `git reset --hard` | Discard uncommitted changes | Show what will be discarded |
| `git rebase` | Rewrite history | Show the affected commits |
| `git merge` | Merge branches | Show the branches and possible conflicts |
| `git tag -d` | Delete a version tag | Show the tag and the version it represents |
| `git cherry-pick` | Selective merge | Show the selected commits |

## §8 Conflict Handling

1. Read the conflict markers `<<<<<<<`, `=======`, `>>>>>>>` carefully.
2. Understand the intent of each side.
3. Resolve manually, keeping the correct parts.
4. Delete the conflict markers after resolution.
5. `git add` to mark the conflict as resolved.
6. Continue the merge or rebase.

### 8.1 Paper-Specific Conflict Scenarios

| Conflict Type | Resolution Rule |
|---------------|------------------|
| Two edits to the same paragraph in a `.tex` file | Keep the version that matches the current contribution claim; record the discard in the commit body |
| Two edits to the same `.bib` entry | Keep the entry with the higher verification status; merge non-conflicting fields |
| Two edits to the citation map | Keep both citation-claim links; verify there is no duplicate key |
| Tag conflict during release | Must not overwrite an existing tag; create a new tag with an incremented version |

## §9 Relationship with Other Documents

- **`security-checklist.md`**: §6 prohibited actions overlap with the high-privilege action confirmation in the security checklist.
- **`tool-skill-mcp.md`**: Git is a tool — the tool strategy applies to Git operations.
- **`evolution-policy.md`**: §1.1 twice-errors-add-rule changes are committed as `chore` or `docs` commits with a rule-change body.
- **`path-scoped-rules.md`**: When committing `.tex` / `.bib` / `.docx` files, the corresponding path-scoped rules apply.
- **`peer-review-simulation.md`**: Each revision round corresponds to a `revision/rN` branch and a tagged version.

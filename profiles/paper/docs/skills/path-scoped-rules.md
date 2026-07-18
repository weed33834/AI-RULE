# Path-Scoped Rules

> Different file types activate different rule sets automatically, reducing the load on the context window.
> This document is the complete implementation of AGENTS.md §18 Path-Level Rules.

## §1 Path-Rule Mapping Table

| File Path Pattern | Activated Rule Set | Check Items |
|-------------------|--------------------|-------------|
| `docs/manuscript/**/*.tex` | LaTeX conventions (§2) | Package hygiene, formatting, compilation, math/code consistency |
| `docs/manuscript/**/*.bib` | BibTeX conventions (§3) | Entry types, field names, key format, verification status |
| `docs/manuscript/**/*.docx` | Manuscript conventions (§4) | Track changes, comments, styles, field codes |
| `docs/manuscript/**/*.md` | Markdown conventions (§5) | Heading hierarchy, code fences, tables, links |
| `.ai-memory/**/*.bib` | BibTeX conventions (§3) | Same as manuscript `.bib`, plus verification status required |
| `.ai-memory/research-blueprint.md` | Blueprint integrity | Seeds complete, outline coherent, contribution claim present |
| `.ai-memory/citation-map.md` | Citation map integrity | Every citation linked to a claim, every claim linked to a citation |
| `docs/skills/*.md` | Skill document rules | Standard structure, version number, evaluation record |
| `scripts/*.py` | Code safety | `pip-audit` passes, no hardcoded secrets, path-traversal protection |
| `AGENTS.md` | Rule source integrity | Version number, reference integrity, valid `@` paths |

## §2 LaTeX Conventions (`.tex`)

When editing or creating `.tex` files, the following rules are **forcibly activated**.

### 2.1 Formatting

- One sentence per line in the source — Git diffs stay readable and reviewable.
- Indent body by 2 spaces per nesting level; do not use tabs.
- Sectioning commands via `\section`, `\subsection`, `\subsubsection` only — no manual numbering.
- Use `\label{...}` for every float, section, equation, and theorem; reference via `\ref{...}` or `\cref{...}`.
- Avoid low-level spacing hacks (`\vskip`, `\bigskip`, `\\[2em]`); prefer semantic macros.
- Use Unicode input via `\usepackage[utf8]{inputenc}` or XeLaTeX/LuaLaTeX for non-ASCII characters.

### 2.2 Packages

- Load only packages actually used; remove dead `\usepackage` lines.
- Prefer modern, maintained packages: `biblatex` + `biber` over `BibTeX`; `hyperref` last in the load order; `cleveref` after `hyperref`.
- Pin package versions only when a known incompatibility exists; otherwise let the TeX distribution resolve.
- Do not load conflicting packages (e.g., `subfig` and `subcaption`).

### 2.3 Compilation

- Compile sequence matches the engine: `pdflatex → biber → pdflatex → pdflatex` for `biblatex`, or `pdflatex → bibtex → pdflatex → pdflatex` for `BibTeX`.
- The build must produce zero "Undefined reference" warnings before submission.
- Use `\includeonly{...}` only during drafting; the final build must include every `\include`d file.
- The build must be reproducible: store the TeX distribution and package versions in a build manifest.

### 2.4 Math and Code

- Inline math via `$...$`; display math via `\[ ... \]` — do not use `$$...$$`.
- Number only equations that are referenced.
- Use `listings` or `minted` for code blocks; never paste raw code without a verbatim environment.
- Code listings must be readable in print: monospace, line length under 80 columns, syntax-highlighted only if the venue allows color.

## §3 BibTeX Conventions (`.bib`)

When editing or creating `.bib` files, the following rules are **forcibly activated**.

### 3.1 Entry Types

| Use This Type | For | Do Not Use For |
|---------------|-----|-----------------|
| `@article` | Journal articles, conference papers in journals | Preprints, theses |
| `@inproceedings` | Conference/workshop papers published in proceedings | Journal articles |
| `@book` | Whole books | Book chapters |
| `@incollection` | Chapters in an edited book | Whole books |
| `@phdthesis` / `@mastersthesis` | Theses | Anything else |
| `@techreport` | Technical reports, working papers | Published papers |
| `@misc` | Preprints, arXiv eprints, datasets, software | Use a more specific type when available |
| `@online` / `@electronic` | Web resources, when no better type exists | Published papers |

### 3.2 Field Names

- Use lowercase field names (`title`, `author`, `year`, `journal`, `doi`, `url`).
- Required fields per entry type must be present; optional fields used only when meaningful.
- Always include `doi` when a DOI exists; always include `url` for online-only resources.
- For preprints, include `eprint` (arXiv ID), `archivePrefix = {arXiv}`, and `primaryClass`.
- Protect capitalization in titles with braces only where needed: `{RAG}` not `{rag}`.
- Use the `note` field to record the verification status (see `context-management.md` §5.2).

### 3.3 Key Format

- Citation keys follow the pattern: `lastnameYYYYkeyword` (e.g., `smith2024rag`).
- For multi-author works, use the first author's last name only: `smith2024multiauthor` not `smithdoe2024multiauthor`.
- Keys are stable: once a key is used in the manuscript, do not rename it without a global find-and-replace.
- Keys must be unique across the entire `.bib` file.

### 3.4 Verification

- Every entry must carry a verification status in the `note` field (Verified / Unverified / Partial).
- Unverified entries must be flagged in the citation map (`context-management.md` §5.3).
- DOIs must resolve; URLs must return HTTP 200.
- Retracted works must be marked with `note = {Retracted: YYYY-MM-DD, see Retraction Watch}` and the citing text must disclose the retraction.

## §4 Manuscript Conventions (`.docx`)

When editing or creating `.docx` files, the following rules are **forcibly activated**.

### 4.1 Revision Tracking

- Track changes must be enabled during collaborative revision; do not accept or reject changes silently.
- Each tracked change must carry the reviewer's identity.
- The final submission version must have all changes resolved and tracking turned off.
- Use the venue's required revision-tracking format (e.g., Word native, or `latexdiff` output exported to `.docx`).

### 4.2 Comments

- Comments must be resolved before submission; unresolved comments are a submission blocker.
- Each comment must be actionable: state the question, the proposed options, and the owner.
- Do not use comments to store notes — those belong in `.ai-memory/`.

### 4.3 Styles

- Use the venue's template styles for headings, body, captions, and references.
- Do not apply manual formatting (font size, bold, color) to override template styles.
- Cross-references must use field codes, not plain text, so they update on edit.
- Figures and tables must be inserted as floats with proper captions and labels.

### 4.4 Field Codes

- All citations must be field codes linked to a reference manager (Zotero, EndNote, Mendeley).
- All cross-references must be field codes; manual "see Section 3" text is a defect.
- Field codes must be updated before submission (Ctrl+A then F9, or the equivalent macro).

## §5 Markdown Conventions (`.md`)

- Use Markdown for drafts, notes, and memory files — not for final manuscripts unless the venue requires it.
- Heading hierarchy: `#` → `##` → `###` — do not skip levels.
- Code blocks must declare the language: `` ```python ``, `` ```bibtex ``, `` ```latex ``.
- Tables for comparisons; lists for steps or parallel items.
- Links use relative paths for internal files and full URLs for external resources.
- Add a single blank line between block elements; no trailing whitespace.
- File ends with exactly one newline character.

## §6 Conditional Loading Example

```json
{
  "condition": {
    "filePattern": "docs/manuscript/**/*.tex",
    "rules": [
      "docs/skills/path-scoped-rules.md",
      "docs/skills/context-management.md",
      "docs/skills/peer-review-simulation.md"
    ]
  },
  "condition": {
    "filePattern": "docs/manuscript/**/*.bib",
    "rules": [
      "docs/skills/path-scoped-rules.md",
      "docs/skills/context-management.md",
      "docs/skills/security-checklist.md"
    ]
  },
  "condition": {
    "filePattern": ".ai-memory/citation-map.md",
    "rules": [
      "docs/skills/context-management.md",
      "docs/skills/path-scoped-rules.md"
    ]
  }
}
```

### Rule Activation Logic

- When the AI operates on a `.tex` file under `docs/manuscript/`, the LaTeX conventions plus context-management and peer-review skills are loaded.
- When the AI operates on a `.bib` file, the BibTeX conventions and security checklist are loaded.
- This scoping reduces context-window consumption — all rules are not loaded at once.

## §7 `.ai-memory` Special Rules

When operating on files under `.ai-memory/`:

- **Read first**: load existing content before appending or updating; do not overwrite blindly.
- **Follow the template**: each file type has a defined structure (see `context-management.md` §4).
- **Incremental updates**: update only the changed portion; do not rewrite the whole file.
- **Citation integrity**: any change to `.ai-memory/references.bib` must propagate to the citation map.

## §8 Relationship with Other Documents

- **`tool-skill-mcp.md`**: Tool strategy works with path-scoped rules — activate rules by path, then operate with the appropriate tool.
- **`context-management.md`**: The `.ai-memory` special rules (§7) directly implement the file-based memory discipline.
- **`security-checklist.md`**: The `.bib` and `.docx` rules include verification and revision-tracking safeguards that overlap with the security checklist.
- **`evolution-policy.md`**: Path-scoped rules themselves evolve — venue format changes propagate here.

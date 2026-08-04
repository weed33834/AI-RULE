# Citation Protocol

> This document defines the citation protocol for academic writing: the verification flow, the five major citation style guides, reference list formatting, common citation errors, reference manager recommendations, and DOI verification.
> Is the complete implementation of AGENTS.md §3 Citation Protocol.
> Complements `academic-integrity.md` — that document defines the integrity red lines and verification chain; this document defines the formatting and style conventions.
> Complements `literature-synthesis.md` — synthesis finds the sources; this document formats them correctly.

## §1 Core Principles

- **Every citation is real**: A citation must point to a work that genuinely exists and is traceable. Formatting a non-existent work correctly is still fabrication.
- **Every citation is accurate**: The metadata (authors, year, title, venue, DOI) must match the actual published record.
- **Every citation is consistent**: One style is used throughout the paper. Mixing APA and IEEE in the same manuscript is not acceptable.
- **Every citation is purposeful**: Cite because the source is relevant, not to pad the reference list. Padding citations is a form of misrepresentation.

## §2 Citation Verification Flow

```
┌─────────────┐
│ 1. Search     │  Locate the source by title, author, or DOI
└──────┬──────┘
       ▼
┌─────────────┐
│ 2. Verify     │  Confirm the source exists and the metadata is correct
└──────┬──────┘
       ▼
┌─────────────┐
│ 3. Record     │  Record full metadata in the reference log
└──────┬──────┘
       ▼
┌─────────────┐
│ 4. Format     │  Apply the declared citation style consistently
└──────┬──────┘
       ▼
┌─────────────┐
│ 5. Flag       │  Mark any unverifiable source as "Unverified"
└─────────────┘
```

### 2.1 Step One: Search

For each intended citation, search at least one of:

| Search target | Primary database | Fallback |
|---------------|------------------|----------|
| Title (exact) | Google Scholar | Semantic Scholar |
| Author + keyword | Google Scholar | DBLP (CS) / PubMed (biomedical) |
| DOI | CrossRef resolver | Publisher site |
| Conference paper | DBLP / conference proceedings | ACM DL / IEEE Xplore |

A "genuine search" means at least one database query by title and one by author + keyword. If both fail, the citation is treated as Unverified.

### 2.2 Step Two: Verify

Confirm the located record matches the intended citation:

| Element | Verification standard |
|---------|----------------------|
| Title | Exact match (case-insensitive) |
| Authors | All listed authors match; order matches |
| Year | Publication year matches |
| Venue | Journal or conference name matches exactly |
| Volume / issue / pages | Match the publisher record |
| DOI | Resolves via CrossRef to the same work |

### 2.3 Step Three: Record Metadata

Maintain a structured reference log (`.ai-memory/references.bib` or equivalent) with full metadata for every cited work:

```
@article{key2024author,
  author  = {Author, A. and Author, B.},
  title   = {Full Title of the Paper},
  journal = {Journal Name},
  year    = {2024},
  volume  = {12},
  number  = {3},
  pages   = {45--67},
  doi     = {10.1000/example},
  url     = {https://doi.org/10.1000/example}
}
```

- Record metadata at the moment of first citation, not at the end.
- Store the DOI whenever available — it is the most reliable identifier.
- Note the access date for online sources without a publication date.

### 2.4 Step Four: Format

Apply the citation style declared in the research seeds consistently. See §3 for the five supported styles.

### 2.5 Step Five: Flag Unverified Sources

If a source cannot be verified after a genuine search:

```
[Unverified] Author, A. (Year). Title. Venue. — please confirm before submission
```

- Never remove the flag and present the citation as verified.
- Never invent plausible metadata to fill gaps.
- Surface unverified citations to the user before submission.

## §3 Five Citation Style Guides

The research seed's `Citation Style` field selects one of the following. Do not mix styles within a single manuscript.

### 3.1 APA 7th Edition

**Common in**: Psychology, Social Sciences, Education.

**In-text (author-date)**:
```
Single author:  (Smith, 2024)  or  Smith (2024)
Two authors:    (Smith & Jones, 2024)
3+ authors:     (Smith et al., 2024)
Direct quote:   (Smith, 2024, p. 45)
```

**Reference list entry**:
```
Journal article:
Smith, A., & Jones, B. (2024). Title of the article. Journal Name, 12(3), 45–67. https://doi.org/10.1000/example

Book:
Smith, A. (2024). Title of the book (2nd ed.). Publisher.

Chapter:
Smith, A. (2024). Title of the chapter. In B. Jones (Ed.), Title of the book (pp. 45–67). Publisher.

Conference paper:
Smith, A. (2024). Title of the paper. In Proceedings of the Conference (pp. 45–67). https://doi.org/10.1000/example
```

**Reference list rules**: Alphabetized by first author surname; hanging indent; italicize journal name and volume.

### 3.2 MLA 9th Edition

**Common in**: Humanities, Literature.

**In-text (author-page)**:
```
(Smith 45)        — author and page
(Smith and Jones 45)  — two authors
(Smith et al. 45) — 3+ authors
```

**Works Cited entry**:
```
Journal article:
Smith, Anna. "Title of the Article." Journal Name, vol. 12, no. 3, 2024, pp. 45–67.

Book:
Smith, Anna. Title of the Book. 2nd ed., Publisher, 2024.

Chapter:
Smith, Anna. "Title of the Chapter." Title of the Book, edited by B. Jones, Publisher, 2024, pp. 45–67.
```

**Works Cited rules**: Alphabetized by author surname; hanging indent; titles of longer works (books, journals) italicized; titles of shorter works (articles, chapters) in quotation marks.

### 3.3 Chicago (Notes-Bibliography and Author-Date)

**Common in**: History, Arts.

**Notes-bibliography (footnotes)**:
```
First note:
1. Anna Smith and Ben Jones, Title of the Book (Publisher, 2024), 45.

Subsequent note:
2. Smith and Jones, Title of the Book, 50.

Bibliography entry:
Smith, Anna, and Ben Jones. Title of the Book. Publisher, 2024.

Journal article:
Smith, Anna. "Title of the Article." Journal Name 12, no. 3 (2024): 45–67.
```

**Author-date (for sciences)**:
```
In-text: (Smith 2024, 45)
Reference: Smith, Anna. 2024. "Title of the Article." Journal Name 12 (3): 45–67.
```

**Bibliography rules**: Alphabetized by author surname; hanging indent; note the difference between note format and bibliography format (notes use commas, bibliography uses periods).

### 3.4 IEEE

**Common in**: Engineering, Computer Science.

**In-text (numbered)**:
```
[1]  — first cited work
[1], [2]  — multiple
[1]–[3]  — range
```

**Reference list entry (numbered in order of appearance)**:
```
Journal article:
[1] A. Smith and B. Jones, "Title of the article," J. Name, vol. 12, no. 3, pp. 45–67, Mar. 2024.

Conference paper:
[2] A. Smith, "Title of the paper," in Proc. Conf. Name, 2024, pp. 45–67.

Book:
[3] A. Smith, Title of the Book, 2nd ed. City: Publisher, 2024.

Online:
[4] A. Smith. "Title." Website. https://example.com (accessed Apr. 1, 2024).
```

**Reference list rules**: Numbered in order of first citation (not alphabetical); abbreviate journal and conference names per IEEE standards; include DOI when available.

### 3.5 Vancouver

**Common in**: Biomedical, medical journals.

**In-text (numbered superscript or bracketed)**:
```
Smith et al⁵ reported...     — superscript
Smith et al [5] reported...   — bracketed
```

**Reference list entry (numbered in order of appearance)**:
```
Journal article:
5. Smith A, Jones B. Title of the article. J Name. 2024;12(3):45–67.

Book:
6. Smith A. Title of the Book. 2nd ed. City: Publisher; 2024.

Chapter:
7. Smith A. Title of the chapter. In: Jones B, editor. Title of the Book. City: Publisher; 2024. p. 45–67.

Online:
8. Smith A. Title [Internet]. Publisher; 2024 [cited 2024 Apr 1]. Available from: https://example.com
```

**Reference list rules**: Numbered in order of appearance; abbreviate journal names per NLM (National Library of Medicine) standards; list first six authors then "et al."

### 3.6 Style Quick Comparison

| Feature | APA 7th | MLA 9th | Chicago | IEEE | Vancouver |
|---------|---------|---------|---------|------|-----------|
| In-text format | Author-date | Author-page | Note or author-date | Number [1] | Number⁵ or [5] |
| Ordering | Alphabetical | Alphabetical | Alphabetical | Order of appearance | Order of appearance |
| Year position | After author | End of entry | After author / end | End of entry | After journal |
| DOI/URL | Included | Included | Included | Included | Included (online) |
| Typical field | Psychology, SS | Humanities | History, Arts | Engineering, CS | Biomedical |

## §4 Reference List Formatting

### 4.1 General Rules (All Styles)

- Every in-text citation must have a corresponding reference list entry, and vice versa.
- The reference list contains only works actually cited in the text — not a bibliography of "further reading."
- Metadata must be complete: authors, year, title, venue, volume/issue/pages, DOI.
- Use hanging indents for readability.
- Italicize journal names and book titles (style-specific).
- DOIs are preferred over URLs when both exist. Format: `https://doi.org/10.xxxx/xxxx`.

### 4.2 Special Source Types

| Source type | Handling |
|-------------|----------|
| Preprint (arXiv) | Cite as preprint; include arXiv identifier |
| Dataset | Cite with creator, title, repository, version, DOI |
| Software | Cite with author, name, version, URL/DOI |
| AI-generated text | Generally not cited as a source; if required, follow venue policy |
| Personal communication | Cited in text only; not in reference list (APA) |
| Legal document | Follow Bluebook (US) or OSCOLA (UK) conventions |
| Retracted paper | Flag as retracted; cite the retraction notice |

### 4.3 Reference List Section Example (APA 7th)

```
References

Smith, A., & Jones, B. (2024). Retrieval-augmented generation reduces hallucination
    in large language models. Journal of Machine Learning Research, 25(4), 112–135.
    https://doi.org/10.1000/example

Lee, C. (2023). A survey of evaluation metrics for text generation. ACM Computing
    Surveys, 56(2), 1–38. https://doi.org/10.1000/survey

Patel, D., & Kim, E. (2024). Hallucination detection benchmarks. In Proceedings of
    the 62nd Annual Meeting of the ACL (pp. 45–67). Association for Computational
    Linguistics. https://doi.org/10.1000/acl
```

## §5 Common Citation Errors and How to Avoid Them

| # | Error | Example | Avoidance |
|---|-------|---------|-----------|
| 1 | Fabricated citation | Inventing author, year, or DOI | Verify every citation exists before use (see §2) |
| 2 | Misattributed claim | Citing a paper for a finding it does not report | Read at least the abstract; confirm the source makes the claim |
| 3 | Inconsistent style | APA in-text but IEEE reference list | Pick one style in the research seed; apply throughout |
| 4 | Missing DOI/URL | Journal article cited without DOI | Look up DOI via CrossRef; include when available |
| 5 | Wrong author format | "Smith, Anna Jones" (merging two authors) | Follow style rules for author lists; use "&" or "and" correctly |
| 6 | Incorrect year | Citing a 2019 preprint as 2024 publication | Distinguish preprint year from publication year |
| 7 | Out-of-context quote | Trimming a quote to reverse its meaning | Quote fully or paraphrase faithfully; provide page number |
| 8 | Secondary citation abuse | "(Smith 2019, as cited in Jones 2021)" for an accessible source | Read and cite the primary source when accessible |
| 9 | Citing retracted work | Citing a paper retracted in 2023 | Check Retraction Watch; cite retraction notice if relevant |
| 10 | Reference list orphans | Entry in reference list never cited in text | Cross-check; remove uncited entries or add in-text citations |
| 11 | In-text orphans | In-text citation with no reference list entry | Cross-check; add the missing entry |
| 12 | Preprint treated as published | "Smith (2024). Published in Nature." for an arXiv preprint | Mark preprints explicitly; update to published version when available |

## §6 Reference Management Software

Reference managers automate citation formatting and reduce metadata errors. Using one is strongly recommended for any paper with more than a handful of citations.

| Software | Cost | Strengths | Best for |
|----------|------|-----------|----------|
| Zotero | Free, open-source | Browser integration; group libraries; open format; no vendor lock-in | Most researchers; collaborative projects |
| Mendeley | Free (Elsevier) | PDF annotation; social features; large reference database | Researchers who annotate PDFs heavily |
| EndNote | Paid (subscription) | Deep Word integration; large style library; institutional support | Institutions with site licenses; long documents |

### 6.1 Workflow with a Reference Manager

```
1. Add source to library (browser plugin / DOI import / manual).
2. Attach the PDF and verify metadata against the publisher record.
3. Insert citations in the manuscript via the word-processor plugin.
4. Generate the reference list automatically in the chosen style.
5. Cross-check the generated list against in-text citations for orphans.
```

### 6.2 Choosing a Manager

- Prefer Zotero when: open access to your library matters; you collaborate with users on different platforms.
- Prefer Mendeley when: you read and annotate many PDFs; you use Elsevier's ecosystem.
- Prefer EndNote when: your institution provides a license; you need a specific proprietary style.

## §7 DOI Verification

The DOI (Digital Object Identifier) is the most reliable persistent identifier for a scholarly work. Verifying it confirms the citation points to the real published record.

### 7.1 Verification Procedure

```
┌──────────────────────────────┐
│ 1. Obtain the DOI             │  From the publisher page or the reference
└──────┬───────────────────────┘
       ▼
┌──────────────────────────────┐
│ 2. Resolve via CrossRef       │  https://api.crossref.org/works/{DOI}
└──────┬───────────────────────┘
       ▼
┌──────────────────────────────┐
│ 3. Compare returned metadata  │  Title, authors, year, venue must match
└──────┬───────────────────────┘
       ▼
┌──────────────────────────────┐
│ 4. Record or flag             │  Match → record DOI; mismatch → flag
└──────────────────────────────┘
```

### 7.2 Resolution Outcomes

| Outcome | Meaning | Action |
|---------|---------|--------|
| DOI resolves; metadata matches | Citation verified | Record DOI in reference log |
| DOI resolves; metadata mismatches | Possible error or wrong DOI | Re-check; likely a transcription error |
| DOI does not resolve | DOI is invalid or withdrawn | Search by title to find the correct DOI; flag if not found |
| No DOI exists | Older works, some books | Use URL; note "no DOI" |

### 7.3 DOI Format Rules

- Always format as a URL in the reference list: `https://doi.org/10.xxxx/xxxx`
- Never invent a DOI. If unsure whether one exists, search CrossRef by title.
- Do not use shorteners or publisher-specific URLs when a DOI is available.

## §8 Citation Density Standards

| Content type | Citation requirement |
|--------------|----------------------|
| Empirical claim | Must cite the source |
| Statistical figure | Must cite the source |
| Definition / concept | Cite an authoritative source |
| Method / procedure | Cite the source of the method |
| Author's own interpretation | Tag as "We argue" / "We propose"; no citation needed |
| Speculation | Tag as "We speculate"; no citation needed |
| Established fact / axiom | No citation needed (within stable knowledge) |

- Over-citation (padding) is a form of misrepresentation: do not cite a source unless it is genuinely relevant.
- Under-citation is plagiarism: do not state others' ideas without attribution.

## §9 Relationship to Other Documents

- **`academic-integrity.md`**: Defines the integrity red lines and the verification chain. This document implements the formatting and style conventions that make verified citations presentable.
- **`literature-synthesis.md`**: Retrieves sources during the literature review. This document formats those sources for the manuscript.
- **`paper-structure.md`**: The reference list is a required section; its placement follows the structure framework.
- **`academic-style.md`**: Citation phrasing in the text ("Smith (2024) found..." vs "It was found (Smith, 2024)") follows the style guide's active-voice and precision standards.
- **AGENTS.md §3**: The Citation Protocol section is the authoritative summary; this document is the complete implementation.
- **AGENTS.md §14.1**: Lists the default tool sources (Google Scholar, CrossRef, Retraction Watch) used in the verification flow.

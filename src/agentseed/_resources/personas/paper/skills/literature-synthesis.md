# Literature Synthesis Methodology

> This document defines the literature synthesis methodology: the four-stage search process, database priority, the CRAAP critical-reading framework, the research-gap identification template, synthesis writing standards, and the deep search protocol that is the default across all profiles.
> Is the complete implementation of AGENTS.md §4 Literature Synthesis Methodology.
> Complements `citation-protocol.md` — synthesis finds the sources; that document formats them.
> Complements `academic-integrity.md` — synthesis retrieves literature; this document ensures the literature is real and cited honestly.
> Implements the deep search protocol referenced in AGENTS.md §14.2 (default for all profiles).

## §1 Core Principles

- **Synthesis is not a list**: A literature review organizes by theme and identifies gaps, never merely enumerates papers ("Smith found X. Jones found Y. Lee found Z.").
- **Depth over breadth**: Three deeply-read papers outweigh ten shallowly-skimmed ones.
- **Critical, not deferential**: Every source is evaluated for credibility and relevance, not accepted at face value.
- **Gaps drive contribution**: The literature review exists to locate the gap your paper fills — not to prove you read a lot.
- **Insufficiency is disclosed**: When the search yields limited results, state "the literature on this topic is limited" rather than over-generalizing from a few sources.

## §2 Four-Stage Literature Search

```
┌─────────────┐
│ 1. Scope     │  Define terms, databases, inclusion/exclusion criteria
└──────┬──────┘
       ▼
┌─────────────┐
│ 2. Search    │  Query databases; collect candidates
└──────┬──────┘
       ▼
┌─────────────┐
│ 3. Screen    │  Title/abstract → shortlist → full-text review
└──────┬──────┘
       ▼
┌─────────────┐
│ 4. Synthesize│  Identify themes, gaps, controversies; position contribution
└─────────────┘
```

### 2.1 Stage One: Scope

Define the boundaries of the search before querying any database:

| Scope dimension | Question to answer | Example |
|-----------------|--------------------|---------|
| Research question | What exact question are you answering? | "Does RAG reduce hallucination in LLM tutoring?" |
| Key terms | What are the search terms (and synonyms)? | retrieval-augmented generation, RAG, hallucination, LLM, tutoring |
| Databases | Which databases are relevant? (see §3) | Google Scholar, Semantic Scholar, arXiv, ACL Anthology |
| Time range | What publication years are in scope? | 2020–2024 (RAG postdates 2020) |
| Inclusion criteria | What makes a paper eligible? | Empirical studies; peer-reviewed or arXiv; English |
| Exclusion criteria | What makes a paper ineligible? | Opinion pieces; non-LLM systems; duplicated work |

### 2.2 Stage Two: Search

Query the prioritized databases. For each database:

| Action | Standard |
|--------|----------|
| Query design | Use specific terms, not generic ones ("RAG hallucination benchmark" > "language models") |
| Multi-angle queries | Run positive, comparative, and critical queries |
| Time filter | Restrict to the scope's time range |
| Snowballing | Check the reference lists of key papers for additional sources |
| Forward citation | Use Google Scholar's "Cited by" to find newer follow-on work |
| Record | Log every query, database, and result count for reproducibility |

### 2.3 Stage Three: Screen

Filter the candidate set down to the papers that will actually be read and cited:

```
All candidates
   │
   ▼
Title/abstract screen  ──→  Exclude clearly irrelevant
   │
   ▼
Shortlist (read full abstract)
   │
   ▼
Full-text review  ──→  Exclude on closer reading
   │
   ▼
Final synthesis set
```

| Screening pass | Action | Typical retention |
|-----------------|--------|--------------------|
| Pass 1: Title/abstract | Exclude clearly irrelevant; keep borderline | ~30–50% |
| Pass 2: Full abstract | Apply inclusion/exclusion criteria strictly | ~50% of pass 1 |
| Pass 3: Full text | Read methods and results; confirm relevance | ~50% of pass 2 |

- Document exclusions with reasons (supports PRISMA-style reporting; see `methodology-design.md`).
- Borderline cases are read in full, not excluded by default.

### 2.4 Stage Four: Synthesize

Transform the final synthesis set into a thematic narrative:

| Synthesis task | Method |
|----------------|--------|
| Theme extraction | Group papers by the sub-question or finding they address |
| Consensus mapping | Identify where sources agree |
| Controversy mapping | Identify where sources disagree; analyze why (method, sample, context) |
| Gap identification | Apply the gap template (see §5) |
| Contribution positioning | State explicitly how your work fills the identified gap |

## §3 Database Priority

| Priority | Database | Best for | Access | Notes |
|----------|----------|----------|--------|-------|
| 1 | Google Scholar | Broad coverage; citation tracking; across disciplines | Free | Start here for breadth; use "Cited by" for forward tracking |
| 2 | Semantic Scholar | AI-powered relevance ranking; free full text | Free | Strong for CS and biomedical; good abstract summarization |
| 3 | arXiv | CS, Physics, Math preprints | Free | Use for cutting-edge CS; mark as preprint when citing |
| 4 | PubMed | Biomedical, life sciences | Free | Use for medical/biological research; MeSH terms supported |
| 5 | DBLP | Computer science bibliography | Free | Author-disambiguated; best for CS venue/proceedings lookups |
| 6 | SSRN | Social sciences, economics preprints | Free | Use for economics, law, social science preprints |
| 7 | JSTOR | Humanities, social sciences archive | Subscription | Deep archive; best for older humanities/social science work |

### 3.1 Discipline-Specific Database Selection

| Discipline | Primary | Secondary | Specialized |
|------------|---------|-----------|-------------|
| Computer Science | Google Scholar, Semantic Scholar | arXiv, DBLP | ACL Anthology (NLP), IEEE Xplore |
| Biomedical | PubMed | Google Scholar | bioRxiv, Cochrane Library |
| Social Sciences | Google Scholar, SSRN | JSTOR | PsycINFO (psychology), EconLit (economics) |
| Humanities | JSTOR | Google Scholar | MLA International Bibliography, PhilPapers |
| Physics / Math | arXiv | Google Scholar | INSPIRE-HEP (physics), MathSciNet (math) |

### 3.2 Database Selection Rules

- Start broad (Google Scholar / Semantic Scholar) then go specialized.
- For CS, always check arXiv for the latest preprints.
- For biomedical, always check PubMed for peer-reviewed work.
- Do not rely on a single database — at least two sources per key claim.

## §4 Critical Reading Framework (CRAAP Test)

Apply the CRAAP test to every source before including it in the synthesis:

| Criterion | Question | Pass standard |
|-----------|----------|---------------|
| **Currency** | When was it published? Is it current enough for the topic? | Within the field's typical currency window (see below) |
| **Relevance** | Does it address the research question? At the right depth? | Directly relevant to a sub-question; not tangential |
| **Authority** | Who authored it? What is their qualification? Venue quality? | Authors have relevant expertise; venue is peer-reviewed or reputable |
| **Accuracy** | Is the evidence supported? Are claims verifiable? Methods sound? | Data cited; methods described; conclusions follow from evidence |
| **Purpose** | Why was it written? Is there a detectable bias or conflict of interest? | Purpose is scholarly; bias acknowledged or absent |

### 4.1 Currency Windows by Field

| Field | Typical currency window | Notes |
|-------|------------------------|-------|
| Computer Science / ML | 3–5 years | Fast-moving; older work may be superseded |
| Biomedical | 5–10 years | Foundational studies may remain current longer |
| Social Sciences | 10–15 years | Slower turnover; classic studies persist |
| Humanities | Decades to centuries | Primary sources have no expiry; secondary scholarship evolves slowly |

### 4.2 Authority Assessment

| Signal | High authority | Low authority |
|--------|---------------|---------------|
| Venue | Top peer-reviewed journal/conference | Predatory journal; non-reviewed workshop |
| Author | Established expert; relevant prior work | Anonymous; no track record |
| Institution | Recognized research institution | Unknown or commercial with vested interest |
| Citations | Highly cited by independent groups | Self-cited only; or no citations (new preprint) |

### 4.3 Accuracy Red Flags

| Red flag | Meaning |
|----------|---------|
| Claims without data or citation | Unsupported assertion |
| Methods not described | Not reproducible |
| Results contradict prior work without discussion | Possible cherry-picking |
| Conflicts of interest undisclosed | Possible bias |
| Predatory venue | Lack of peer review |

## §5 Research-Gap Identification Template

The synthesis must culminate in an explicit gap statement. Use this template:

```
GAP IDENTIFICATION TEMPLATE
─────────────────────────────
Topic: [the sub-area under review]
Prior work: [what has been studied]
  - [Theme 1]: [key findings, with citations]
  - [Theme 2]: [key findings, with citations]
  - [Theme 3]: [key findings, with citations]
What remains unstudied: [the specific gap]
  - [Gap type]: [description]
Why it matters: [why filling this gap is significant]
How this paper fills it: [your contribution's position]
```

### 5.1 Gap Types

| Gap type | Description | Example phrasing |
|----------|-------------|------------------|
| Empirical gap | No study has tested X | "No prior work has empirically evaluated RAG in undergraduate CS tutoring." |
| Methodological gap | Prior work used method M; method N is untested | "Existing studies use closed-book QA; retrieval-augmented settings remain unexamined." |
| Population gap | Group P is underrepresented | "Prior evaluations focus on English; multilingual settings are unstudied." |
| Theoretical gap | No theory explains X | "No framework accounts for why RAG fails on multi-hop questions." |
| Contradiction | Sources disagree; unresolved | "Studies conflict on whether RAG increases or decreases latency." |
| Replication gap | Single study; not replicated | "Only Smith (2023) reports this effect; replication is absent." |

### 5.2 Gap Statement Examples

| Weak gap statement | Strong gap statement |
|--------------------|---------------------|
| "More research is needed." | "No study has evaluated RAG's effect on hallucination in undergraduate CS tutoring, despite its growing adoption (Smith 2024; Lee 2023)." |
| "There are few studies." | "Of 32 studies on RAG hallucination, none examine educational settings; all focus on open-domain QA." |
| "This is an important topic." | "The gap matters because RAG is deployed in tutoring products without evidence of its reliability for factual accuracy." |

## §6 Synthesis Writing Standards

### 6.1 Organize by Theme, Not by Author

| Pattern | Acceptable? | Example |
|---------|-------------|---------|
| Thematic organization | Yes | "Three lines of work address hallucination: detection (Smith 2023; Lee 2024), mitigation (Patel 2022), and evaluation (Kim 2024)." |
| Author-by-author listing | No | "Smith (2023) studied detection. Lee (2024) also studied detection. Patel (2022) studied mitigation." |
| Chronological listing | Rarely | Only when the evolution of an idea is itself the point |
| Methodological grouping | Yes | "Quantitative studies report X (Smith 2023); qualitative studies report Y (Lee 2024)." |

### 6.2 Synthesis Sentence Patterns

```
Consensus:
"Several studies converge on [finding] (Smith 2023; Lee 2024; Patel 2022)."

Controversy:
"While [Source A] reports [finding X], [Source B] finds [finding Y]; the discrepancy
may stem from [methodological difference]."

Methodological contrast:
"[Source A]'s controlled study isolates [variable], whereas [Source B]'s field study
captures [real-world factor] at the cost of [confound]."

Gap leading to contribution:
"Although [prior work] addresses [X], no study has examined [Y]. This paper fills
that gap by [contribution]."
```

### 6.3 What a Literature Review Is Not

| Anti-pattern | Why it fails |
|--------------|--------------|
| Annotated bibliography | Lists papers without synthesizing them |
| Quote dump | Strings together quotations without analysis |
| Summary stack | Paraphrases each paper in turn without comparison |
| Name-dropping | Cites famous papers without engaging their content |
| One-sided review | Cites only supportive work; ignores contradicting evidence |

## §7 Deep Search Protocol (Default for All Profiles)

> Per AGENTS.md §14.2, the deep search protocol is activated by default across all profiles when the user's task requires factual support, data verification, or literature lookup.

### 7.1 When Deep Search Activates

| Trigger | Search? | Rationale |
|---------|---------|----------|
| User asks for latest findings | Yes | Training data may be outdated |
| User asks for specific data/figures | Yes | Precise numbers need sources |
| User requests verification of a claim | Yes | Needs independent confirmation |
| User asks about stable, established knowledge | No | Faster to answer directly |
| User asks for a definition | Conditional | Stable definitions direct; new terms search |
| User asks for your opinion | No | Opinions do not require search |
| When uncertain | Yes | Searching beats guessing |

### 7.2 Deep Search Depth Control

| Depth | Trigger | Search volume | Example |
|-------|---------|---------------|---------|
| Shallow | Simple fact verification | 1–2 searches | A date, a version number |
| Medium | Technical comparison, method selection | 3–5 searches | Library/tool comparison |
| Deep | Literature review, complex analysis | 5–10+ searches | Identifying a research gap |

### 7.3 Deep Search Procedure

```
1. Query: Formulate search terms based on the user's question.
2. Search: Query multiple databases (Google Scholar, Semantic Scholar, arXiv, PubMed as relevant).
3. Cross-validate: Key claims require 2+ independent sources.
4. Synthesize: Extract and integrate findings; flag conflicts.
```

### 7.4 Query Design Principles

| Angle | Query template | Purpose |
|-------|---------------|---------|
| Positive | "[topic] [specific aspect] [year]" | Get direct information |
| Comparative | "[A] vs [B] [dimension]" | Get comparison data |
| Critical | "[topic] problems/issues/criticism" | Surface limitations |
| Community | "[topic] reddit/hackernews/experience" | Get practitioner experience |
| Authoritative | "[topic] official documentation/spec/survey" | Get authoritative definitions |

### 7.5 Search Result Presentation

```
[Key information] [Source: author year, URL]

Example:
Retrieval-augmented generation reduces hallucination rates by 30–50% in open-domain QA
(Source: Smith 2024, https://arxiv.org/abs/2401.00001).
```

When sources conflict:
```
On [topic], sources disagree:
- [Source A] reports [finding X] [URL]
- [Source B] reports [finding Y] [URL]
We lean toward [X/Y] because [reason], but recommend independent verification.
```

When information is insufficient:
```
On [topic], I searched [N] sources but the literature is limited:
- Found: [known information]
- Not found: [missing information]
Recommend consulting [suggested source] or [channel].
```

## §8 Common Synthesis Pitfalls

| Pitfall | Symptom | Avoidance |
|---------|---------|-----------|
| Abstract-only reading | Misrepresents findings | Read at least methods + results of key papers |
| First-page bias | Misses alternative perspectives | Check pages 2–3 of search results |
| Confirmation bias | Only cites supportive work | Actively search for contradicting evidence |
| Recency bias | Ignores foundational older work | Cite classics alongside recent work |
| Single-source dependence | All claims trace to one author | Ensure ≥ 2 independent sources per key claim |
| Translation distortion | Misreads translated terms | Verify key terms in the original language |
| Garbage-can synthesis | Throws every found paper in | Apply inclusion/exclusion criteria strictly |

## §9 Relationship to Other Documents

- **`citation-protocol.md`**: Formats the sources found during synthesis. This document finds and evaluates; that document formats.
- **`academic-integrity.md`**: Verifies that synthesized literature is real and cited honestly. This document's §2 search flow feeds that document's verification chain.
- **`research-question.md`**: The literature review exists to position the research question. The gap template here (§5) connects directly to the FINER/PICO frameworks there.
- **`methodology-design.md`**: A systematic review follows PRISMA reporting standards defined there.
- **AGENTS.md §4**: The Literature Synthesis Methodology section is the authoritative summary; this document is the complete implementation.
- **AGENTS.md §14.2**: The Deep Search Protocol (default for all profiles) is implemented here in §7.

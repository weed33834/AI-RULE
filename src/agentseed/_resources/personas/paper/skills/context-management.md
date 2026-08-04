# Context Management

> The context window is a scarce resource. Academic papers carry a large payload of citations, methods, results, and prior work. Without systematic management, the paper drifts into internal contradictions and citation drift.
> This document is the complete implementation of AGENTS.md §12 Memory & Context Management.
> Complements `peer-review-simulation.md` — review needs context, this document governs how context is preserved.

## §1 Context Window Budget

| Use | Share | Description |
|-----|-------|-------------|
| System prompt | 15% | Rules, role definitions, research seeds |
| User input | 25% | Current-turn user message, instructions, and feedback |
| Conversation history | 30% | Prior turns, decisions, and confirmed facts |
| Search / tool results | 20% | Literature search, citation lookups, data fetched from external services |
| Output space | 10% | Room reserved for the AI reply |

- When the budget is exceeded, drop information by the priority in §2 — never silently truncate a citation.
- The 10% output space must be protected: if search results grow beyond 20%, summarize them into a structured digest before they enter history.

## §2 Conversation History Priority

When the context window is insufficient, retain or drop information by priority.

### 2.1 Retention Priority (high → low)

| Priority | Information Type | Example |
|----------|-------------------|---------|
| P1 | User-stated research seeds | "Target venue: ACL 2026; citation style: ACL" |
| P2 | Confirmed decisions | "We will use the IMRaD structure" |
| P3 | User corrections | "No — the unit of analysis is the participant, not the trial" |
| P4 | Current task context | The section currently being drafted |
| P5 | Confirmed facts | "The dataset has N=312 participants" |
| P6 | Search / tool results | The key finding of a located reference |
| P7 | General conversation | Greetings, transitions |
| P8 | Discarded information | Superseded claims, out-of-date context |

### 2.2 Compression Strategy

When the conversation exceeds 20 turns, compress earlier turns:

```
Before compression (turns 1–20, full transcript):
- User: "I am writing an empirical paper on RAG hallucination rates..."
- AI:   "Got it. Could you confirm the target venue and citation style?"
- User: "ACL 2026, ACL style."
- AI:   "Understood. ACL style uses author-year..."
- (15 turns of detailed dialogue)
- User: "Let's go with the IMRaD structure."
- AI:   "Acknowledged. IMRaD it is."

After compression (summary):
[Conversation summary — turns 1–20]
- Research seeds: ACL 2026, ACL citation style, empirical paper, English
- Research question: Does RAG reduce hallucination rates in LLMs?
- Structure decision: IMRaD
- Confirmed facts: dataset N=312, baseline = GPT-4 without retrieval
- Key decisions: power analysis to be reported in §3.4
- Current task: drafting §3 Method
```

### 2.3 Compression Rules

| Information Type | Retain | Compress | Drop |
|-------------------|--------|----------|------|
| Research seeds | Verbatim | | |
| Confirmed decisions | Verbatim | | |
| User corrections | Verbatim | | |
| Confirmed facts | | Summary | |
| Search results | | Key conclusion only | Details dropped |
| General conversation | | | Dropped |
| Discarded information | | | Dropped |
| Citations | Verbatim (key + DOI) | | Never dropped |

## §3 Long Paper Compression Strategy

When the manuscript exceeds 8,000 words, generate a structured summary that fits in the context window. The summary must be sufficient to keep the paper internally consistent without reloading the full text.

### 3.1 Structured Summary Template

```
[Structured Paper Summary]
- Title: <title>
- Research seeds: discipline, paper type, venue, citation style, word limit, language
- Research question (one sentence)
- Contribution claim (one sentence, calibrated)
- Structure: section list with one-line purpose each
  - §1 Introduction: <purpose>
  - §2 Related Work: <purpose>
  - §3 Method: <purpose>
  - §4 Results: <purpose>
  - §5 Discussion: <purpose>
  - §6 Limitations: <purpose>
  - §7 Conclusion: <purpose>
- Key claims (with section + paragraph location):
  - C1: <claim> — §X ¶Y
  - C2: <claim> — §X ¶Y
- Open questions / unresolved threads:
  - Q1: <question> — owner: <co-author / AI / user>
- Pending revisions:
  - R1: <revision> — status: pending / in progress / done
- Citation anchors:
  - <citation key> — used in §X ¶Y for <claim>
```

### 3.2 Long Paper Workflow

- "Locate first, read in detail second." Identify the relevant section before loading the full text.
- Preferential reads for the current section: the section before and after, the relevant figures and tables, the relevant entries in `.ai-memory/references.bib`.
- For papers over 16,000 words: locate the relevant section via the structured summary, then read only that section in full.
- When jumping between sections, always carry the current contribution claim, the section's purpose, and the open questions — never let the context "lose the thread."

## §4 File-Based Memory

| Memory Type | Location | Contents |
|-------------|----------|----------|
| Research blueprint | `.ai-memory/research-blueprint.md` | Research seeds, outline, contribution claim |
| Section drafts | `.ai-memory/sections/` | One file per section, with status |
| References | `.ai-memory/references.bib` | BibTeX entries with verification status |
| Citation map | `.ai-memory/citation-map.md` | Which citation supports which claim, with section + paragraph |
| Reproducibility | `.ai-memory/reproducibility.md` | Data, code, protocol references |
| Session summary | `.ai-memory/session-summary.md` | Per-session compressed summary |
| Author profile | `.ai-memory/author-profile.md` | Author preferences, voice, recurring decisions |
| Reviewer reports | `.ai-memory/reviews/` | Simulated reviewer outputs from `peer-review-simulation.md` |
| Revision log | `.ai-memory/revisions.md` | Diff-table history across revisions |

- At the start of each session, **read first** the memory files under `.ai-memory/` to restore context.
- Whenever a new decision or seed change is made, **write promptly** to the corresponding file.
- Memory files are append-friendly: read first, then update or append — never overwrite blindly.

## §5 Citation Tracking

Citations are the integrity backbone of an academic paper. They must be tracked across the entire writing lifecycle.

### 5.1 Reference Store

All cited works live in `.ai-memory/references.bib` with a verification status field:

```bibtex
@article{smith2024rag,
  title   = {Retrieval-Augmented Generation Reduces Hallucination Rates in Large Language Models},
  author  = {Smith, Jane and Doe, John},
  journal = {Proceedings of ACL},
  year    = {2024},
  doi     = {10.18653/v1/2024.acl-main.123},
  url     = {https://aclanthology.org/2024.acl-main.123/},
  note    = {Verified: 2026-07-18 via CrossRef}
}
```

### 5.2 Verification Status

| Status | Meaning | Action |
|--------|---------|--------|
| Verified | DOI resolves, metadata matches the publisher | Use freely |
| Unverified | DOI missing or not checked | Mark "Unverified — please confirm before submission" |
| Partial | Some fields unconfirmed | Fill the gap or downgrade the citation |
| Fabricated-suspect | Cannot locate the source | Refuse to use; replace with a real source |

### 5.3 Citation Map

`.ai-memory/citation-map.md` links each citation to the claim it supports:

```
[Citation Map]
- smith2024rag
  - supports C1 (§3 ¶2): "RAG reduces hallucination rates by 32%."
  - supports C2 (§5 ¶1): "Reduction is robust across model sizes."
- jones2023limits
  - challenges C1 (§6 ¶2): "Effect disappears under domain shift."
```

- A citation without a supporting claim is dead weight — remove it or assign it a claim.
- A claim without a supporting citation must be flagged (§2.3 of `peer-review-simulation.md`).

## §6 Section Summary Generation

For each section, maintain a compact summary that the AI can reload without re-reading the full draft.

```
[Section Summary: §3 Method]
- Purpose: describe the study design so it can be replicated
- Word count: 1,420 / 1,500 target
- Key components:
  - Participants: N=312, recruited via Prolific, inclusion criteria in §3.1
  - Materials: stimuli from <dataset>, listed in Appendix A
  - Procedure: 4 conditions, counterbalanced
  - Analysis: linear mixed-effects model, random intercepts for participant
- Open issues:
  - Power analysis paragraph not yet written (P0)
  - Need to cite the analysis package version (P1)
- Linked citations: smith2024rag, jones2023limits
```

- Generate a section summary whenever a section draft is updated.
- Section summaries are the input to the structured paper summary (§3.1).
- When the context window is tight, load section summaries in place of full drafts.

## §7 Tool Output Sandboxing

- Large raw outputs from literature search, reference fetching, or data retrieval must not be poured directly into the context window.
- Write raw outputs to temporary files under `/data/user/work/` and load only the digest into context.
- When details are needed, read the specific paragraph from the temporary file on demand.
- Temporary files are cleaned up once the session ends.

## §8 Context Break Detection

| Signal | Symptom | Action |
|--------|---------|--------|
| Repeated questioning | AI asks about already-confirmed seeds | Immediately restore context from `.ai-memory/research-blueprint.md` |
| Contradictory answers | Current answer conflicts with a prior decision | Check which is correct; log the resolution |
| Forgotten preferences | AI ignores a user-stated style preference | Reload `author-profile.md` |
| Topic drift | AI departs from the current section task | Confirm whether the topic is switching |
| Citation drift | A citation is reused for a claim it does not support | Re-check the citation map (§5.3) |

## §9 Relationship with Other Documents

- **`peer-review-simulation.md`**: Reviewer reports need the structured summary and citation map.
- **`revision-response.md`**: The diff table requires the citation map and section summaries.
- **`path-scoped-rules.md`**: When editing `.bib` / `.tex` / `.docx` files, the corresponding path-scoped rules apply.
- **`tool-skill-mcp.md`**: Literature search outputs feed the sandboxing workflow in §7.

## Core Principles

- If a fact can be stated in one sentence, do not use a paragraph.
- If a citation can be looked up in the reference store, do not reload the full text.
- If a link can be provided, do not copy the full reference into the context window — point to the entry in `references.bib`.

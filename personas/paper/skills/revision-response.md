# Revision Letter & Reviewer Response

> This document defines how to draft a revision letter and respond to reviewer comments.
> It is the complete implementation of AGENTS.md §11 Revision & Response.
> Complements `peer-review-simulation.md` — simulation produces the critique, this document produces the response.

## §1 Revision Letter Structure

The revision letter is a standalone document submitted alongside the revised manuscript. It must be self-contained: an editor should understand the changes without opening the manuscript.

```
[Revision Letter Template]

Title: <paper title>
Manuscript ID: <id>
Journal / Venue: <target venue>
Date: <YYYY-MM-DD>
Editor: <editor name>

1. Summary of Changes
   - High-level summary of the most important revisions (3–6 bullets).
   - Note any changes that affect the contribution claim.

2. Point-by-Point Response
   - Reviewer 1
     - Comment 1.1: <quoted comment>
       Response: <response>
       Action: <what was changed> — location: <section / paragraph / line>
     - Comment 1.2: ...
   - Reviewer 2
     - ...

3. Global Changes (not tied to a specific comment)
   - <change 1> — rationale + location
   - <change 2> — rationale + location

4. Declined Changes (with justification)
   - <declined request> — reason: <evidence-based justification>

5. Diff Summary
   - Reference to the diff table (§4) or supplementary marked-up manuscript.

6. Closing
   - Thank the editor and reviewers.
   - Confirm that all co-authors approve the revised version.
```

## §2 Response Principles

### 2.1 Point-by-Point Response

- Respond to **every** comment, including minor ones. A silent comment is read as a declined comment.
- Number comments by reviewer (R1.1, R1.2, R2.1, ...) so the editor can cross-check.
- If a single response addresses multiple comments, list all referenced comment numbers.

### 2.2 Quote Exact Locations

- Always quote the reviewer's comment verbatim before responding.
- Always cite the **exact** revised location: section number, subsection, paragraph, line, page, or figure/table number.
- Use a stable referencing scheme that matches the marked-up manuscript.

| Response Element | Required Format | Example |
|------------------|-----------------|---------|
| Comment quote | Verbatim, in quotes | "The authors should justify the sample size." |
| Response | Plain text, neutral tone | "We thank the reviewer. We have added a power analysis..." |
| Action | Concrete change + location | "Added power analysis to §3.4, paragraph 2, lines 45–52." |
| Diff reference | Diff table row or marked-up file | "See Diff Table row D-07." |

### 2.3 Respect Disagreement

- Reviewers may be wrong. Disagreement must be expressed respectfully and backed by evidence, never by tone.
- Use the **acknowledge → explain → cite evidence → propose alternative** pattern.

```
Acknowledge: "We thank the reviewer for raising this point."
Explain:     "We agree that [X] is a concern in general. However, in our setting [reason]..."
Cite:        "...because [citation] establishes that [fact]."
Alternative: "We have therefore [kept / softened / strengthened] the claim and clarified the scope in §Y."
```

### 2.4 Calibrated Concessions

| Reviewer Comment Type | Default Stance |
|-----------------------|----------------|
| Factual error (typo, wrong citation) | Accept and fix immediately |
| Missing reference | Accept if relevant; add with proper citation |
| Methodological concern with evidence | Accept; re-run analysis if feasible |
| Methodological preference (style) | Accept if low-cost; otherwise explain rationale |
| Disagreement on interpretation | Acknowledge, present evidence, propose alternative |
| Request beyond scope | Politely decline; explain scope boundary |

## §3 Tone Calibration

The tone of the response letter must remain professional and neutral across the entire document.

| Element | Do | Do Not |
|---------|----|--------|
| Addressing reviewers | "We thank the reviewer for..." | "The reviewer failed to understand..." |
| Disagreement | "We respectfully disagree because..." | "The reviewer is wrong." |
| Reframing | "We have clarified this in §X to avoid confusion." | "We already said this; please re-read." |
| Limitations | "We agree and have added a Limitations note in §Y." | "This is out of scope and not our job." |
| Minor comments | Respond briefly and fix | Ignore or batch without individual response |

### 3.1 Tone Failure Modes

- **Defensiveness**: long justifications that read as adversarial.
- **Over-apology**: excessive apologies that undermine the contribution.
- **Patronizing**: explaining basic concepts to senior reviewers.
- **Dismissiveness**: one-line responses to substantive comments.

### 3.2 Tone Self-Check

Before sending the response letter, verify:

| # | Check | Pass / Fail |
|---|-------|-------------|
| 1 | Every response starts with acknowledgment of the comment. | |
| 2 | No sentence implies the reviewer is incompetent. | |
| 3 | Disagreements are backed by citation or data. | |
| 4 | No sarcastic, passive-aggressive, or mocking phrasing. | |
| 5 | The letter is shorter than the manuscript. | |

## §4 Diff Table Format

The diff table maps each requested change to the exact location in the revised manuscript. It is the editor's primary tool for verifying that revisions were actually made.

```
[Diff Table Format]
| Diff ID | Reviewer / Comment | Section | Before (excerpt) | After (excerpt) | Rationale |
|---------|--------------------|---------|------------------|------------------|-----------|
| D-01    | R1.1               | §3.4 ¶2 | "We used N=30."  | "We used N=30, justified by an a priori power analysis (G*Power, effect size f=0.25, power=0.80)." | Add power analysis |
| D-02    | R2.3               | §5 ¶1   | "Our method outperforms..." | "Our method outperforms baseline X on benchmark Y (Table 2)..." | Calibrate claim |
```

### 4.1 Diff Table Rules

- One row per discrete change. Do not bundle unrelated edits.
- The "Before" column must quote the original text verbatim (or mark "New" for added content).
- The "After" column must quote the revised text verbatim.
- The "Section" column must use the final manuscript's numbering.
- The "Rationale" must be one short sentence linking the change to a reviewer comment or a global decision.

### 4.2 Marked-Up Manuscript

Alongside the diff table, provide a marked-up manuscript:

- Use the venue's native change-tracking format (Word tracked changes, `latexdiff` for LaTeX, etc.).
- Additions and deletions must be visible without re-reading the entire paper.
- The marked-up file must match the diff table row-by-row.

## §5 Common Mistakes

| # | Mistake | Why It Fails | Correct Approach |
|---|---------|--------------|------------------|
| 1 | Skipping minor comments | Editor reads silence as defiance | Respond to every comment, even one-liners |
| 2 | Vague locations ("we revised the introduction") | Editor cannot verify | Cite exact section, paragraph, and line |
| 3 | Quoting reviewer comment incompletely | Breaks the audit trail | Quote verbatim, in quotes |
| 4 | Defensive tone | Signals unwillingness to engage | Acknowledge → explain → cite → propose |
| 5 | Overclaiming the fix | "Fully addressed" when only partially done | Match the claim to the actual change |
| 6 | Declining without evidence | Reads as stubbornness | Provide citation or data supporting the decline |
| 7 | Inconsistent numbering between letter and manuscript | Editor loses track | Use a stable comment ID scheme end-to-end |
| 8 | Ignoring the editor's separate instructions | Editor decisions override individual reviewers | Address editor points in a dedicated section |
| 9 | Re-introducing fixed issues in a later edit | Undermines trust | Run the self-assessment checklist again post-revision |
| 10 | Forgetting to update the abstract after major revisions | Abstract no longer matches the body | Re-run §2.2 of `peer-review-simulation.md` |

## §6 Response Workflow

```
1. Collect all reviewer comments and the editor's decision letter.
2. Number every comment (R1.1, R1.2, R2.1, ...).
3. For each comment, classify the stance (accept / partial / decline).
4. Draft point-by-point responses using the §2.3 pattern.
5. Apply all manuscript edits and record them in the diff table.
6. Run tone self-check (§3.2).
7. Re-run the self-assessment checklist from `peer-review-simulation.md` §2.
8. Generate the marked-up manuscript.
9. Finalize the revision letter and submit.
```

## §7 Relationship with Other Documents

- **`peer-review-simulation.md`**: Produces the reviewer reports and improvement suggestions consumed here.
- **`context-management.md`**: Long response letters need structured summaries to fit in the context window.
- **`git-sop.md`**: Revisions must be committed in dedicated `revision/rN` branches with conventional commit messages.
- **`path-scoped-rules.md`**: When editing `.tex` / `.docx` files, the corresponding path-scoped rules apply.

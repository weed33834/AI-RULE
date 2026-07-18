# Peer Review Simulation

> This document defines the peer-review simulation methodology: reviewer roles, self-assessment checklist, rejection reasons, scoring rubric, and revision suggestions.
> It is the complete implementation of AGENTS.md §10 Peer Review Simulation.
> Complements `revision-response.md` — simulation finds problems, the response letter resolves them.

## §1 Reviewer Roles

Before submission, simulate five distinct reviewer perspectives. Each reviewer focuses on a different dimension and applies a different failure model.

| Reviewer Role | Primary Focus | Key Questions | Failure Model |
|---------------|---------------|---------------|---------------|
| Methodological | Research design, sampling, procedure validity | Is the design appropriate for the question? Are controls adequate? Is the sample size justified? | Internal validity threat, confound, underpowered study |
| Theoretical | Theoretical framing, contribution, positioning | Is the contribution novel? Is the framing coherent? Does it engage prior literature? | Incremental work, misframing, missing baseline |
| Statistical | Analysis correctness, reporting, interpretation | Are the tests appropriate? Are assumptions checked? Are effect sizes and CIs reported? Is multiple-testing controlled? | Wrong test, p-hacking, overclaiming |
| Writing | Clarity, structure, narrative flow, formatting | Is the argument easy to follow? Are sections well-organized? Is the abstract faithful? Is the tone appropriate? | Unclear contribution, structural mess, overclaiming |
| Skeptical | Adversarial probing of claims and limits | What would falsify this? Are limitations honest? Are alternative explanations ruled out? | Overgeneralization, hidden assumptions, cherry-picking |

### 1.1 Reviewer Activation Order

```
1. Methodological  → Does the design hold up?
2. Theoretical     → Is the contribution real?
3. Statistical     → Are the numbers trustworthy?
4. Writing         → Is it readable?
5. Skeptical       → What would a hostile reviewer attack?
```

### 1.2 Reviewer Output Format

Each reviewer produces a structured report:

```
[Reviewer: <Role>]
Verdict: Accept / Minor Revision / Major Revision / Reject
Strengths:
  - <strength 1>
  - <strength 2>
Weaknesses (ranked by severity):
  - [Major] <weakness 1> — location: <section/paragraph/line>
  - [Minor] <weakness 2> — location: <section/paragraph/line>
Questions for the authors:
  - <question 1>
  - <question 2>
Required revisions:
  - <action 1>
  - <action 2>
```

## §2 Self-Assessment Checklist

Before generating the reviewer reports, run the following self-assessment. Any "No" answer must be resolved or explicitly justified before submission.

### 2.1 Core Integrity Checklist

| # | Check Item | Yes / No |
|---|------------|----------|
| 1 | Is every citation real, traceable, and accurately represented? | |
| 2 | Is all data reported honestly (no cherry-picking, no omission of unfavorable results)? | |
| 3 | Are uncertain claims marked with a confidence level? | |
| 4 | Is the contribution claim calibrated (not overstated)? | |
| 5 | Are limitations disclosed honestly and completely? | |
| 6 | Is the replication information (data, code, protocol) available or properly referenced? | |

### 2.2 Structural Checklist

| # | Check Item | Yes / No |
|---|------------|----------|
| 1 | Does the abstract faithfully summarize the paper (no claims absent from the body)? | |
| 2 | Does the introduction state the gap, the question, and the contribution? | |
| 3 | Does the method section provide enough detail for replication? | |
| 4 | Do the results answer the research question without interpretation? | |
| 5 | Does the discussion separate findings from interpretation and implication? | |
| 6 | Are figures and tables self-contained (readable without the body text)? | |

### 2.3 Submission Fitness Checklist

| # | Check Item | Yes / No |
|---|------------|----------|
| 1 | Does the paper fit the target venue's scope and length? | |
| 2 | Is the citation style consistent with the venue's requirement? | |
| 3 | Are all co-authors acknowledged and conflicts of interest disclosed? | |
| 4 | Is the word count within the limit (including/excluding references as required)? | |
| 5 | Are figures at print-quality resolution with accessible color choices? | |

## §3 Top 10 Rejection Reasons

Ranked by frequency across simulated reviews. Each reason includes the detection signal and the preventive action.

| Rank | Rejection Reason | Detection Signal | Preventive Action |
|------|------------------|-------------------|-------------------|
| 1 | Lack of novelty / incremental contribution | "How is this different from [prior work]?" appears in Theoretical review | Sharpen the delta-vs-prior-work paragraph; add a comparison table |
| 2 | Insufficient novelty framing | Contribution stated only in the abstract, not defended in the introduction | State the contribution in the introduction and defend it with evidence |
| 3 | Methodological flaw | Methodological reviewer flags a confound or design gap | Add a control, run a robustness check, or narrow the claim |
| 4 | Statistical error | Wrong test, missing assumption check, or p-hacking signal | Re-run with the correct test; report effect sizes and CIs |
| 5 | Overclaiming | Skeptical reviewer finds claims beyond what the data supports | Hedge the claim; move strong claims to "Limitations" |
| 6 | Poor literature engagement | Key prior work is missing or only cited superficially | Add a structured related-work subsection; cite surveys |
| 7 | Unclear writing / structural mess | Writing reviewer cannot summarize the contribution in one sentence | Rewrite the introduction; add a contributions list |
| 8 | Missing limitations section | No "Limitations" section or only generic boilerplate | Add a concrete, honest limitations section tied to the method |
| 9 | Non-reproducible results | Method lacks detail; no data/code availability statement | Add a reproducibility appendix; link to a repository |
| 10 | Misfit with the venue | Scope, length, or style does not match the target venue | Re-target the paper or restructure to fit the venue |

## §4 Scoring Rubric

Each reviewer scores the paper on a 1–5 scale across the dimensions below. The composite score is the weighted average. A composite below 3.5 triggers a "Major Revision" verdict.

| Dimension | Weight | 1 (Reject) | 3 (Borderline) | 5 (Strong Accept) |
|-----------|--------|-------------|-----------------|---------------------|
| Novelty / Contribution | 25% | Rehashes prior work | Modest extension | Clear, defensible contribution |
| Methodological soundness | 20% | Flawed design | Adequate but fragile | Rigorous and well-justified |
| Statistical rigor | 15% | Wrong / missing analysis | Acceptable but incomplete | Correct, complete, transparent |
| Clarity / Writing | 15% | Confusing, disorganized | Readable with effort | Clear and well-structured |
| Literature engagement | 10% | Missing key work | Adequate coverage | Comprehensive and critical |
| Reproducibility | 10% | Not reproducible | Partially reproducible | Fully reproducible |
| Significance / Impact | 5% | Marginal | Moderate | High |

### 4.1 Verdict Mapping

| Composite Score | Verdict | Action |
|-----------------|---------|--------|
| >= 4.5 | Accept | Proceed to submission package |
| 3.5 – 4.4 | Minor Revision | Address reviewer questions; light edits |
| 2.5 – 3.4 | Major Revision | Restructure; re-run analyses; rewrite sections |
| < 2.5 | Reject | Do not submit; reconsider the framing or venue |

## §5 Improvement Suggestion Template

Each reviewer must translate every weakness into an actionable suggestion. Use the following template so suggestions are testable and trackable.

```
[Improvement Suggestion]
Reviewer: <Role>
Linked weakness: <weakness text> — location: <section/paragraph/line>
Suggested action: <concrete, verifiable action>
Expected outcome: <what changes in the paper once applied>
Effort estimate: <XS / S / M / L>  (<hours or sessions>)
Verification: <how to confirm the fix is sufficient>
Priority: P0 / P1 / P2 / P3
```

### 5.1 Suggestion Quality Criteria

A suggestion is well-formed only if it satisfies all of the following:

| Criterion | Description |
|-----------|-------------|
| Concrete | Names the exact section, paragraph, or claim to change |
| Actionable | Describes a doable action, not a complaint |
| Verifiable | States how to confirm the fix resolves the weakness |
| Calibrated | Priority matches severity; effort matches the weakness |
| Respectful | Critiques the work, not the author |

### 5.2 Suggestion Aggregation

After all five reviewers produce suggestions:

```
1. Merge duplicate suggestions (same weakness flagged by multiple reviewers).
2. Sort by priority (P0 → P3) and then by effort (XS → L).
3. Build a revision plan: P0 first, then P1, then P2/P3 if time allows.
4. Mark each suggestion as: Done / Partially Done / Declined (with reason).
5. Feed the revision plan into `revision-response.md`.
```

## §6 Review Workflow

```
1. Confirm research seeds (discipline, venue, paper type, citation style)
2. Run self-assessment checklists (§2)
3. For each reviewer role (§1), generate a structured report
4. Score the paper with the rubric (§4) and map to a verdict
5. Translate every weakness into an improvement suggestion (§5)
6. Aggregate suggestions into a prioritized revision plan
7. Hand off to `revision-response.md` for the response letter
```

## §7 Relationship with Other Documents

- **`revision-response.md`**: Consumes the reviewer reports and improvement suggestions to build the response letter.
- **`context-management.md`**: Long papers require structured summaries before review can fit in the context window.
- **`security-checklist.md`**: Reviewer simulation must not leak unpublished co-author data or confidential peer-review material.
- **`path-scoped-rules.md`**: When reviewing `.tex` / `.docx` files, the corresponding path-scoped rules apply.

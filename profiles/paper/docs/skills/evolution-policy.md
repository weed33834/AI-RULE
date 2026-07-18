# Evolution Policy

> This document defines the self-evolution mechanism for rules and skills: skill lifecycle, curator responsibilities, trajectory insights, and rule decay.
> It is the complete implementation of AGENTS.md §17 Rule Self-Evolution.
> Complements `peer-review-simulation.md` — simulation surfaces weaknesses, evolution patches them.

## §1 Rule Self-Evolution

### 1.1 Twice-Errors-Add-Rule

When the same class of mistake occurs twice:

1. Identify the error pattern (e.g., fabricated DOI, overclaimed result, mismatched abstract).
2. Propose a new rule to the user.
3. On user confirmation, write it into AGENTS.md.
4. Run `sync_rules.py` to propagate to derived tool configs.

### 1.2 Rule Proposal Format

```
[Proposed New Rule]
Location: §X (suggested section)
Content: [rule text]
Reason: Nth occurrence of the same error (attach concrete case)
Expected effect: [what this rule prevents]
Affected skills: [list of skills that reference this rule]
```

### 1.3 Rule Decay

Rules that the model follows reliably can be relaxed; rules tied to academic integrity must never be relaxed.

| Compliance Pattern | Wording Change |
|---------------------|---------------|
| 10 consecutive correct compliances | "must" → "prefer" |
| 20 consecutive correct compliances | "prefer" → "suggest" |
| 1 violation | Step up one level |
| 2 violations | Return to "must" |

## §2 Skill Lifecycle

Skills move through four stages. Each stage has explicit entry criteria and required actions.

| Stage | Trigger | Action |
|-------|---------|--------|
| proposed | A recurring writing task is recognized | Submit a skill proposal with motivation, scope, and inputs/outputs |
| draft | Proposal accepted by the user | Author the skill file under `docs/skills/`; tag with version `0.x` |
| active | Draft passes one review cycle with positive feedback | Promote to version `1.0`; add to the active skill index |
| deprecated | Skill is obsolete, redundant, or replaced | Move to `docs/skills/archive/`; record replacement in CHANGELOG |

### 2.1 Stage Transition Criteria

| Transition | Required Evidence |
|------------|-------------------|
| proposed → draft | User approval + scope statement + at least one reference use case |
| draft → active | One completed review cycle with no P0 issues; positive user feedback |
| active → deprecated | Replacement skill exists OR no usage in the last 6 months OR referenced tool retired |

### 2.2 Skill Evaluation Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Reduction in revision rounds | From first draft to accepted final | Fewer rounds over time |
| Self-assessment pass rate | % of self-assessment checklist items passing on first run | >= 90% |
| Reviewer verdict improvement | Composite score from `peer-review-simulation.md` | Trending upward across revisions |
| Citation integrity incidents | Fabricated or misattributed citations | Zero |
| Usage frequency | How often the skill is loaded per session | Non-zero per month for active skills |

## §3 Autonomous Skill Curator

### 3.1 Periodic Scan

Once per month, scan the skill library for:

- Outdated skills (referenced tools, APIs, or venue requirements retired).
- Redundant skills (multiple skills covering the same writing task).
- Low-effectiveness skills (evaluations show no measurable improvement).
- Missing skills (writing tasks that recurred but have no skill file).

### 3.2 Curation Report

```
Curation report template:
- Review period: 2026-07
- Skills reviewed: 12
- Suggested merges: 2 sets (A + B → C)
- Suggested deprecations: 1 (X tool retired)
- Suggested improvements: 3 (missing citation-integrity dimension)
- Suggested additions: 2 (extracted from recent tasks)
- Rule decay candidates: 1 (rule §4.2 — 15 consecutive compliances)
```

### 3.3 Safety Constraints

- The curator only suggests; it never executes.
- Merges and deprecations require explicit user confirmation.
- Improvements may be applied automatically but must be logged in CHANGELOG.
- Rules tied to academic integrity (P0) are exempt from decay — see §1.3.

## §4 Trajectory Insights

Record AI behavior trajectories during paper-writing sessions to surface improvement opportunities.

| Insight Type | Recorded Content | Use |
|--------------|------------------|-----|
| High-frequency failure modes | Which failure mode appears most often (e.g., overclaiming, missing limitations) | Strengthen the corresponding rule |
| High-frequency clarification | Which information is most often clarified mid-task | Consider auto-inference or a seed-collection prompt |
| User satisfaction signals | Patterns of user follow-up, correction, or acceptance | Identify quality-improvement directions |
| Search efficiency | Number of searches vs. quality of located references | Optimize the search strategy in `tool-skill-mcp.md` |
| Revision load | Number of revision rounds per section | Targeted skill improvements for high-load sections |
| Citation drift | Citations reused for unsupported claims | Reinforce the citation map workflow |

### 4.1 Trajectory → Rule Feedback Loop

```
Writing trajectory data → Trajectory insight analysis → Rule / skill adjustment → User confirmation → Update → New trajectory data
```

### 4.2 Silent-Failure Detection and Rule Hardening

| Detected Pattern | Hardening Action |
|------------------|------------------|
| Recurrent fabricated citations | Tighten the verification requirement in `context-management.md` §5 |
| Recurrent overclaiming | Tighten the calibration check in `peer-review-simulation.md` §2.1 |
| Recurrent abstract drift | Add an abstract-body consistency check to `revision-response.md` §6 |
| Recurrent missing limitations | Add a limitations-presence gate to the self-assessment checklist |

## §5 Relationship with Other Documents

- Every skill document may be evaluated and improved by the curator.
- `peer-review-simulation.md` §2 produces the evaluation signals that drive skill improvement.
- `revision-response.md` §6 feeds the revision-load trajectory in §4.
- `context-management.md` §5 feeds the citation-drift trajectory in §4.
- `git-sop.md` tracks every rule change as a dedicated commit.

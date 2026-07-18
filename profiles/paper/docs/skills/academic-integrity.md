# Academic Integrity Protocol

> This document defines the academic integrity safeguard system: the citation verification chain, source classification, confidence-level disclosure, the verification checklist, and self-plagiarism detection.
> Academic integrity is the complete implementation of AGENTS.md §2 Academic Integrity Iron Law (P0 — Highest Priority).
> Complements `citation-protocol.md` — this document defines the integrity red lines and verification flow; that document defines citation formatting and style guides.
> Complements `literature-synthesis.md` — synthesis retrieves literature; this document verifies that the literature is real and cited honestly.

## §1 Core Principles

The value of academic writing lies not in "appearing authoritative" but in "every claim being true and traceable." An honest "I cannot verify this citation" is worth a hundred fabricated references.

The three principles of academic integrity:
- **No fabrication**: Information that cannot be confirmed is never stated as fact; citations that cannot be verified are never presented as real.
- **No concealment**: Uncertainty is exposed explicitly, never hidden behind confident wording.
- **No concealment of errors**: When an error is discovered, it is corrected immediately — never silently modified as if nothing happened.

The four P0 red lines (absolutely inviolable, even if the user requests otherwise):
- **No fabricated citations**: Every cited work must be real, published, and traceable.
- **No plagiarism**: No copy-paste without quotation marks and attribution; no self-plagiarism without citation.
- **No data falsification**: No fabrication of experimental data, survey results, or statistical analyses; no cherry-picking.
- **No citation misrepresentation**: Never cite a paper for a claim it does not make; never take quotes out of context.

## §2 Citation Verification Flow

For every citation that appears in a draft, execute the internal verification chain before output:

```
┌─────────────┐
│ 1. Draft     │  Generate the initial draft with intended citations
└──────┬──────┘
       ▼
┌─────────────┐
│ 2. Verify    │  List every citation; verify each exists
└──────┬──────┘
       ▼
┌─────────────┐
│ 3. Inspect   │  Confirm the cited claim matches what the source says
└──────┬──────┘
       ▼
┌─────────────┐
│ 4. Correct   │  Fix or remove any unverifiable or misrepresented citation
└──────┬──────┘
       ▼
┌─────────────┐
│ 5. Output    │  Output the verified draft with metadata and confidence
└─────────────┘
```

### 2.1 Step One: Draft

Generate the initial draft normally. The draft is not output directly to the user — it enters the verification flow. Every placeholder citation is treated as "Unverified" until proven otherwise.

### 2.2 Step Two: Verify Existence

Extract every citation from the draft and verify it exists:

| Citation element | Verification method | Required? |
|------------------|---------------------|-----------|
| Title | Search Google Scholar / Semantic Scholar by title | Yes |
| Authors | Cross-check against the located record | Yes |
| Year | Cross-check against the located record | Yes |
| Venue (journal/conference) | Cross-check against the located record | Yes |
| DOI | Resolve via CrossRef (https://api.crossref.org/works/{DOI}) | If available |
| URL | Open and confirm the page resolves to the cited work | If available |
| Page numbers | Cross-check against the located record | If cited |

If a citation cannot be located after a genuine search (at least one database query by title, one by author + keyword), label it "Unverified — please confirm before submission" and notify the user.

### 2.3 Step Three: Inspect Claim Accuracy

For each citation, confirm the source actually supports the claim being attributed to it:

| Claim type | Inspection standard |
|------------|---------------------|
| Direct quote | Verbatim match; quote marks and page number required |
| Paraphrase | Genuinely reworded; meaning preserved; original cited |
| "X found that..." | The source's Results/Conclusion must state this finding |
| "X suggests that..." | The source must contain the suggestion (not just a finding) |
| "X reviews..." | The source must be a review covering the cited scope |
| Methodology citation | The source must describe the cited method |

### 2.4 Step Four: Correct

| Verification result | Corrective action |
|---------------------|-------------------|
| Citation confirmed, claim accurate | Keep; record metadata |
| Citation confirmed, claim inaccurate | Correct the claim or remove the citation; flag "corrected" |
| Citation cannot be verified | Label "Unverified" or remove; never leave a fabricated citation in place |
| Citation retracted | Remove or flag "retracted — see Retraction Watch" |
| Partially correct | Correct the inaccurate part; keep the accurate part |

### 2.5 Step Five: Output

Output the final draft. Every citation carries either verified metadata or an explicit "Unverified" label. Every uncertain claim carries a confidence tag.

## §3 Citation Source Classification

| Level | Source type | Credibility | Usage | Example |
|-------|-------------|-------------|-------|---------|
| A | Peer-reviewed journal article, conference paper (top venue) | High | May cite directly | Nature, ACL, NeurIPS, IEEE T-PAMI |
| B | Peer-reviewed paper (mid-tier venue), edited book chapter | Medium-high | May cite; record metadata | Workshop paper, edited handbook |
| C | arXiv / SSRN / bioRxiv preprint | Medium | May cite; mark as preprint | arXiv:2401.00001 |
| D | Technical report, white paper, thesis | Medium-low | May cite; note the source type | Corporate report, dissertation |
| E | Blog post, Wikipedia, personal webpage | Low | Cite only as supporting; prefer the primary source | Company engineering blog |
| F | Social media, anonymous forum | Very low | Do not cite as fact; use only to locate primary sources | Twitter thread, Reddit comment |

- Level F sources are never cited as factual support. If a claim originates from social media, trace it to a primary source (Level A–D) before citing.
- Wikipedia is never cited as a primary source in academic writing. Use it to locate primary sources.

## §4 Confidence-Level Disclosure

When a claim cannot be fully verified, assign a confidence level and disclose it explicitly:

| Level | Condition | Behavior |
|-------|-----------|----------|
| [High] | Verified against 2+ Level A/B sources, or 1 authoritative primary source | Output normally; cite the source |
| [Medium] | Verified against 1 Level A/B source, or 2+ Level C sources | Output; tag [Medium]; recommend the user confirm |
| [Low] | Only Level C/D sources available, or single uncorroborated source | Output; tag [Low]; explicitly recommend independent verification |
| Unverified | No reliable source located after genuine search | State "I cannot verify this claim" — do not fabricate a source |
| Contradicted | Sources disagree | Present each position; do not force a single conclusion |

### 4.1 Tag Format

```
[Claim] [Confidence: High|Medium|Low] [Source: author year]
[Claim] [Unverified] — please confirm before submission
[Claim] [Preliminary] — based on preprint, not yet peer-reviewed
```

### 4.2 When to Disclose

| Claim type | Disclosure required? |
|-------------|----------------------|
| Empirical finding with data | Yes — cite source and confidence |
| Statistical figure | Yes — must cite; never produce an unverifiable number |
| Established fact / axiom | No — within stable training knowledge |
| Author's speculation / interpretation | Tag as "We speculate" or "This suggests" |
| Methodological choice | Cite the source of the method |

## §5 Verification Checklist

Before outputting any draft containing citations, check against this list:

| # | Check item | Pass standard |
|---|------------|---------------|
| 1 | Citation existence | Every citation locatable in at least one database |
| 2 | Metadata completeness | Authors, year, title, venue recorded for every citation |
| 3 | DOI resolution | DOI (if present) resolves via CrossRef to the cited work |
| 4 | Claim accuracy | The cited source actually makes the attributed claim |
| 5 | Retraction check | No cited work has been retracted (check Retraction Watch if uncertain) |
| 6 | Confidence tagging | Every uncertain claim carries [High]/[Medium]/[Low] or Unverified |
| 7 | Speculation labeling | Speculative content tagged "We speculate" or "This suggests" |
| 8 | Preliminary labeling | Preprint-based claims tagged "Preliminary" |
| 9 | Contradiction handling | Source disagreements disclosed, not hidden |
| 10 | Draft correction | Any fabricated or misrepresented citation removed/corrected |

## §6 Self-Plagiarism Detection

Self-plagiarism (reusing one's own previously published text without citation) is academic misconduct, even though the words are the author's own.

### 6.1 What Counts as Self-Plagiarism

| Behavior | Self-plagiarism? | Handling |
|----------|------------------|----------|
| Reusing a paragraph from your prior paper without citation | Yes | Quote or paraphrase with self-citation; or rewrite entirely |
| Reusing your own methods section verbatim | Yes (if prior paper published) | Cite the prior paper; or rewrite |
| Reusing your own figures/tables without attribution | Yes | Cite the source; obtain copyright permission if required |
| Extending your own prior work with new analysis | No | Cite the prior work as the foundation |
| Reusing common methodological descriptions (e.g., a standard protocol) | Borderline | Cite the protocol source; minimize verbatim reuse |

### 6.2 Self-Plagiarism Check Flow

```
┌──────────────────────────┐
│ 1. Identify reused text   │  Flag any passage > 1 sentence reused from prior work
└──────┬───────────────────┘
       ▼
┌──────────────────────────┐
│ 2. Locate the prior source│  Find the previously published version
└──────┬───────────────────┘
       ▼
┌──────────────────────────┐
│ 3. Decide handling        │  Cite / quote / rewrite / seek permission
└──────┬───────────────────┘
       ▼
┌──────────────────────────┐
│ 4. Apply attribution      │  Add self-citation; mark verbatim reuse with quotation
└──────────────────────────┘
```

### 6.3 Acceptable Reuse Thresholds

| Reuse type | Threshold | Action if exceeded |
|------------|-----------|--------------------|
| Verbatim text | > 7 consecutive words from prior work | Quote with self-citation, or rewrite |
| Methods description | Any verbatim block | Cite prior paper; minimize exact reuse |
| Figures/tables | Any reuse | Cite source; obtain permission if publisher requires |
| Ideas/findings | Any reuse | Cite the prior work |

## §7 Special Scenarios

### 7.1 User Requests a Fabricated Citation

When the user says "just make up a citation to fill the gap" or similar:
- This is a P0 violation. Refuse.
- Explain: fabricated citations are academic misconduct; there is no "well-intentioned" version.
- Offer to search for a real source, or label the gap "Unverified — needs real source."

### 7.2 Cannot Find the Original Source

When a citation is expected but cannot be located:
- Label it "Unverified — please confirm before submission."
- Provide whatever partial metadata is available (e.g., "remembered as Smith et al., ~2019, cognitive psychology").
- Never reconstruct a plausible-looking citation from memory — that is fabrication.

### 7.3 Citing a Preprint

When citing arXiv / SSRN / bioRxiv preprints:
- Mark the citation as "Preprint" or "Preliminary."
- If a peer-reviewed version exists, cite the peer-reviewed version instead.
- Note that preprint findings may change after peer review.

### 7.4 Citing a Retracted Paper

When a cited work is found to be retracted:
- Remove the citation, or explicitly flag "retracted."
- If the retraction is relevant to the argument, discuss it.
- Check Retraction Watch (https://retractionwatch.com) when uncertain.

### 7.5 Secondary Citations

When citing a source you have not read but only seen cited elsewhere:
- Use the form: "(Smith 2019, as cited in Jones 2021)" — but only when the primary source is genuinely inaccessible.
- Prefer reading and citing the primary source directly.
- Secondary citations weaken the chain of evidence; minimize their use.

## §8 Abstention Protocol

Instruction tuning biases models toward producing confident answers over honest uncertainty. This protocol explicitly authorizes abstention when evidence is insufficient.

### When to Abstain
- **Citation existence**: If you cannot verify that a cited work exists, state "I cannot verify this citation. Please provide the full reference or confirm the source." Do not produce a plausible-looking citation.
- **Specific figures**: If you cannot verify a number, statistic, or date, do not produce one. Say "I cannot verify this figure" instead.
- **Claim attribution**: If you cannot confirm that a source makes the attributed claim, label it "Unverified attribution" rather than asserting it.

### When NOT to Abstain (Anti-Inflation)
- Do not abstain on claims within stable training knowledge that you can state confidently (e.g., established definitions, widely-known facts).
- Avoid phrases like "if uncertain..." or "if you're not sure..." in your own reasoning — these trigger abstention inflation.
- Use threshold-based conditions ("When evidence confidence is below [Medium]") rather than vague uncertainty language.

### Abstention Format
```
I cannot verify this citation / claim.
What I know: [relevant facts you DO have]
What I need: [specific information missing to verify fully]
```

### Key Distinction
- **Fabrication** (P0 violation): Inventing citations, data, or results — never acceptable.
- **Abstention** (authorized): Honestly stating insufficient knowledge — encouraged when warranted.
- **Confident uncertainty**: "We believe X, but this has not been independently verified" — acceptable for non-critical claims, tagged with confidence level.

## §9 Relationship to Other Documents

- **`citation-protocol.md`**: Defines citation formatting, style guides (APA, MLA, Chicago, IEEE, Vancouver), and reference list structure. This document defines the integrity verification; that document defines the format.
- **`literature-synthesis.md`**: Retrieves and synthesizes literature. This document verifies that the retrieved literature is real and cited honestly.
- **`methodology-design.md`**: Methodological reproducibility and honest reporting of results relate to the no-falsification red line.
- **`academic-style.md`**: Honest limitation disclosure and confidence tagging relate to the style guide's precision standard.
- **AGENTS.md §2**: The Academic Integrity Iron Law is the authoritative source; this document is its complete implementation.
- **AGENTS.md §13**: The Security Red Lines (no fabrication, no plagiarism) overlap with this document's P0 red lines.

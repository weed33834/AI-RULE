# Paper Structure Framework

> This document defines the paper structure framework: structure tables by paper type, section-by-section requirements, transition patterns, discipline-specific variations, and word-count allocation guidance.
> Is the complete implementation of AGENTS.md §5 Paper Structure Framework.
> Complements `research-question.md` — the research question determines the paper type and structure.
> Complements `academic-style.md` — structure provides the skeleton; the style guide governs the prose that fills it.

## §1 Core Principles

- **Structure serves the argument**: The structure is not a formality — each section advances a specific rhetorical move. A section that advances nothing should not exist.
- **Type determines structure**: An empirical paper uses IMRaD; a review uses thematic sections; an essay builds an argument. Do not force every paper into IMRaD.
- **Sections have contracts**: Each section has a job. The Methods must enable reproduction; the Results must report without interpreting; the Discussion must interpret without re-reporting.
- **Transitions carry the logic**: The reader should move from section to section without asking "why are we here now?" Each section's opening connects to the previous section's conclusion.

## §2 Structure by Paper Type

### 2.1 Empirical (IMRaD)

| Section | Function | Word share (typical) |
|---------|----------|---------------------|
| Abstract | Summarize the whole in 150–300 words | ~3% |
| Introduction | Motivate; review; state gap; present RQ; preview contribution | ~15% |
| Methods | Describe approach reproducibly; justify choices | ~20% |
| Results | Report findings without interpretation | ~25% |
| Discussion | Interpret; compare to prior work; limitations; future work | ~25% |
| Conclusion | Concise summary of contribution; no new information | ~5% |
| References | (separate; not counted in word share) | — |

### 2.2 Review

| Section | Function | Word share (typical) |
|---------|----------|---------------------|
| Abstract | Summarize scope, method, key findings, gaps | ~3% |
| Introduction | Define scope; explain why a review is needed now | ~10% |
| Methods (search strategy) | Document search, screening, inclusion criteria (PRISMA-style) | ~10% |
| Thematic sections | Organize findings by theme (not by author) | ~45% |
| Synthesis | Integrate themes; map consensus and controversy | ~15% |
| Future directions | Identify gaps; propose research agenda | ~10% |
| Conclusion | Summarize state of the field; restate contribution | ~5% |

### 2.3 Position / Essay

| Section | Function | Word share (typical) |
|---------|----------|---------------------|
| Abstract | Summarize the thesis and the argument's structure | ~3% |
| Introduction | Present the issue; state the thesis; preview the argument | ~15% |
| Background | Establish context the reader needs | ~15% |
| Arguments | Present each supporting argument in its own section | ~35% |
| Counterarguments | Address the strongest objections; refute or concede | ~20% |
| Conclusion | Restate thesis in light of the argument; implications | ~10% |

### 2.4 Case Study

| Section | Function | Word share (typical) |
|---------|----------|---------------------|
| Abstract | Summarize the case, the analysis, and the lessons | ~3% |
| Introduction | Introduce the case; explain why it matters; state the question | ~12% |
| Case description | Describe the case in sufficient detail | ~25% |
| Analysis | Apply the theoretical framework to the case | ~30% |
| Discussion | Generalize from the case; compare to other cases; limitations | ~20% |
| Conclusion | Summarize findings; state implications | ~10% |

## §3 Section-by-Section Requirements

### 3.1 Abstract

| Requirement | Standard |
|-------------|----------|
| Length | 150–300 words (follow venue limit) |
| Content | Problem, method, key findings, contribution — all four |
| Tense | Past for methods/results; present for the contribution |
| Citations | None (abstracts are self-contained) |
| Undefined terms | Avoid; define essential terms inline if unavoidable |

```
ABSTRACT TEMPLATE (structured, ~250 words)
────────────────────────────────────────────
[1–2 sentences: the problem and why it matters]
[1 sentence: the gap or research question]
[1–2 sentences: the method — approach, data, sample]
[2–3 sentences: the key findings — with effect sizes]
[1 sentence: the contribution / implication]
```

### 3.2 Introduction

The Introduction follows a funnel: broad context → specific gap → your question → your contribution.

| Move | Function | Example phrasing |
|------|----------|------------------|
| Motivate the problem | Why does this matter? | "Large language models are increasingly deployed in educational settings, raising concerns about factual accuracy." |
| Review relevant literature | What is known? | "Prior work shows RAG reduces hallucination in open-domain QA (Smith 2024; Lee 2023)." |
| State the gap | What is unknown? | "However, no study has evaluated RAG in undergraduate CS tutoring." |
| Present the research question | What does this paper answer? | "We ask: does RAG reduce hallucination in LLM-based tutoring for undergraduate CS courses?" |
| Preview the contribution | What will the reader get? | "We contribute (1) a benchmark for tutoring hallucination, (2) an empirical evaluation of RAG, and (3) an analysis of failure modes." |

- Do not review everything — review what sets up the gap.
- The last paragraph should let the reader predict the rest of the paper.

### 3.3 Methods

| Requirement | Standard |
|-------------|----------|
| Reproducibility | A reader with the same data and code can reproduce the results |
| Justification | Methodological choices are justified, not merely stated |
| Detail level | Enough to reproduce; supplementary material for overflow |
| Tense | Past tense ("We trained...", "Participants completed...") |

```
METHODS CHECKLIST
─────────────────
[ ] Dataset: source, size, preprocessing, splits
[ ] Participants/sample: recruitment, demographics, inclusion criteria
[ ] Instruments: measures, validation, reliability
[ ] Procedure: step-by-step; what happened and in what order
[ ] Variables: independent, dependent, controlled
[ ] Analysis: statistical tests, software, significance threshold
[ ] Ethics: IRB approval, informed consent, data protection
[ ] Pre-registration: protocol reference if applicable
```

### 3.4 Results

| Requirement | Standard |
|-------------|----------|
| Report, don't interpret | State findings; save interpretation for Discussion |
| Descriptive first | Descriptive statistics before inferential |
| Effect sizes | Report effect sizes and CIs, not just p-values (see `data-presentation.md`) |
| Tables/figures | Cross-referenced in text; not redundant with text |
| Tense | Past tense ("The model achieved...", "Participants reported...") |

- Negative results are reported, not hidden.
- Unexpected results are reported, not smoothed over.

### 3.5 Discussion

| Move | Function |
|------|----------|
| Summarize key findings | Restate the main results (without re-reporting all data) |
| Interpret | What do the findings mean? Why did they turn out this way? |
| Compare to prior work | Agreement and disagreement with the literature; why? |
| Limitations | State honestly; do not bury in the final paragraph |
| Future work | Concrete next steps, not vague "more research is needed" |
| Implications | What should practitioners or researchers do differently? |

### 3.6 Conclusion

| Requirement | Standard |
|-------------|----------|
| Concise | Typically one paragraph or one short section |
| No new information | No new data, citations, or arguments |
| Restate contribution | What did this paper add to the field? |
| Forward-looking | A sentence on implications or future directions is acceptable |

## §4 Transition Patterns

### 4.1 Section-to-Section Transitions

| Transition | Pattern | Example |
|------------|---------|---------|
| Introduction → Methods | "To address this question, we conducted..." | Connects the RQ to the approach |
| Methods → Results | "The analysis yielded the following results." | Signals the shift from procedure to findings |
| Results → Discussion | "These results suggest that..." | Signals the shift from reporting to interpreting |
| Discussion → Conclusion | "In summary, this study demonstrates..." | Signals the synthesis |

### 4.2 Paragraph-Level Transitions

| Type | Function | Connectors |
|------|----------|-----------|
| Continuation | Extend the same point | moreover, furthermore, in addition |
| Contrast | Introduce a tension | however, in contrast, nevertheless |
| Causation | Show cause/effect | consequently, as a result, therefore |
| Concession | Acknowledge then pivot | although, while, despite |
| Sequence | Order steps | first, then, finally (use sparingly — see `academic-style.md`) |

### 4.3 Transition Anti-Patterns

| Anti-pattern | Why it fails |
|--------------|--------------|
| "It is worth noting that..." | Filler transition; says nothing |
| "In recent years, ..." | Vague time reference; replace with a specific citation |
| "As mentioned earlier, ..." | Repeats instead of advancing; cut the repetition |
| Abrupt section break | Reader cannot tell why the new section follows |

## §5 Discipline-Specific Variations

### 5.1 Computer Science

| Feature | Convention |
|---------|-----------|
| Structure | Often compresses Methods and Results; emphasizes system architecture |
| Related Work | May be a separate section before Methods, or folded into Introduction |
| Evaluation | A dedicated Experiments section with benchmarks, baselines, ablations |
| Reproducibility | Code/data release expected; supplementary appendix for hyperparameters |
| Venue length | Conference papers 8–10 pages (excl. references); journals longer |
| Citation style | IEEE or ACL (numbered); preprints (arXiv) commonly cited |

### 5.2 Social Science

| Feature | Convention |
|---------|-----------|
| Structure | Full IMRaD; longer Literature Review (may be its own section) |
| Theory | A Theoretical Framework section often precedes Methods |
| Methods | Mixed methods common; detailed sampling and instrument validation |
| Reporting | CONSORT (RCTs), PRISMA (systematic reviews), STROBE (observational) |
| Citation style | APA 7th (author-date) dominant |
| Limitations | A dedicated Limitations subsection expected |

### 5.3 Humanities

| Feature | Convention |
|---------|-----------|
| Structure | Essay/argument structure; IMRaD rarely used |
| Evidence | Close reading of primary texts; archival sources |
| Argument | Builds through extended analysis, not empirical sections |
| Citations | MLA 9th or Chicago (notes-bibliography) |
| Length | Often longer; monograph-length arguments acceptable |
| Voice | Author's voice more prominent; "I" acceptable in some subfields |

### 5.4 Biomedical

| Feature | Convention |
|---------|-----------|
| Structure | Strict IMRaD; structured abstract (Background, Methods, Results, Conclusions) |
| Ethics | IRB/ethics approval and trial registration stated up front |
| Reporting | CONSORT (trials), PRISMA (reviews), STROBE (observational), STARD (diagnostic) |
| Statistical reporting | Effect sizes, CIs, pre-registration common |
| Citation style | Vancouver (numbered) dominant |
| Limitations | Standard subsection; conflicts of interest disclosed |

### 5.5 Discipline Quick Comparison

| Dimension | CS | Social Science | Humanities | Biomedical |
|-----------|----|----|------|-----------|
| Default structure | IMRaD (compressed) | Full IMRaD | Essay | Strict IMRaD |
| Citation style | IEEE / ACL | APA 7th | MLA / Chicago | Vancouver |
| Related Work | Separate or intro | Literature Review section | Integrated | Background in Intro |
| Reporting standard | Varies | CONSORT/PRISMA/STROBE | None | CONSORT/PRISMA/STROBE |
| Typical length | 8–10 pp (conf) | 6,000–10,000 words | 5,000–15,000 words | 3,000–6,000 words |
| First person | "We" common | "We" common | "I" acceptable | "We" common |

## §6 Word-Count Allocation

### 6.1 Allocation by Paper Type (Indicative)

For an 8,000-word empirical paper:

| Section | Words | Share |
|---------|-------|-------|
| Abstract | 250 | 3% |
| Introduction | 1,200 | 15% |
| Methods | 1,600 | 20% |
| Results | 2,000 | 25% |
| Discussion | 2,000 | 25% |
| Conclusion | 400 | 5% |
| (References) | (separate) | — |

### 6.2 Allocation by Venue Length

| Venue limit | Abstract | Intro | Methods | Results | Discussion | Conclusion |
|-------------|----------|-------|---------|---------|-----------|-----------|
| Short (4,000 wd) | 150 | 600 | 800 | 1,000 | 1,000 | 200 |
| Standard (8,000 wd) | 250 | 1,200 | 1,600 | 2,000 | 2,000 | 400 |
| Long (12,000 wd) | 300 | 1,800 | 2,400 | 3,000 | 3,000 | 600 |

- These are starting points, not rules. Adjust to the paper's emphasis: a methods-heavy paper expands Methods; a theory-heavy paper expands the framework section.
- Always check the venue's author guidelines for hard limits.

### 6.3 When Over Limit

| Strategy | When to use |
|----------|-------------|
| Move detail to supplementary material | Methods overflow; extended results |
| Tighten prose (see `academic-style.md`) | Filler words, redundant sentences |
| Merge subsections | Two thin subsections become one |
| Cut tangential literature | Introduction reviews more than the gap requires |
| Never | Cut methods detail needed for reproducibility |
| Never | Cut limitations discussion |

## §7 Outline Template

```markdown
# Outline: [Paper Title]
## Research Seed: [discipline / type / venue / citation style / word limit]
## Research Question: [the question this paper answers]

### Abstract
- Problem:
- Gap:
- Method:
- Key findings:
- Contribution:

### 1. Introduction
- 1.1 Motivation:
- 1.2 Literature review (scoped to the gap):
- 1.3 The gap:
- 1.4 Research question:
- 1.5 Contribution preview:

### 2. Methods
- 2.1 Data / participants:
- 2.2 Instruments / materials:
- 2.3 Procedure:
- 2.4 Analysis:

### 3. Results
- 3.1 Descriptive:
- 3.2 Main analysis:
- 3.3 Secondary analysis:

### 4. Discussion
- 4.1 Interpretation of key findings:
- 4.2 Comparison with prior work:
- 4.3 Limitations:
- 4.4 Future work:
- 4.5 Implications:

### 5. Conclusion
- Summary of contribution:

### References
- (generated from .ai-memory/references.bib)
```

## §8 Structure Consistency Checklist

- [ ] Does the structure match the paper type declared in the research seed?
- [ ] Does each section advance a specific rhetorical move (no empty sections)?
- [ ] Does the Introduction end with a clear research question and contribution preview?
- [ ] Are Methods reproducible (could a peer redo the study)?
- [ ] Are Results free of interpretation (saved for Discussion)?
- [ ] Does the Discussion interpret rather than re-report?
- [ ] Are limitations stated honestly, not buried?
- [ ] Does the Conclusion introduce no new information?
- [ ] Do transitions carry the reader from section to section?
- [ ] Does the word-count allocation fit the venue limit?

## §9 Relationship to Other Documents

- **`research-question.md`**: The research question determines the paper type and structure. A FINER/PICO question maps to a specific structure.
- **`methodology-design.md`**: The Methods section's content follows the methodology design framework.
- **`data-presentation.md`**: The Results section's tables and figures follow the data presentation guide.
- **`academic-style.md`**: The prose within each section follows the style guide's precision, economy, and active-voice standards.
- **`literature-synthesis.md`**: The Introduction's literature review follows the synthesis methodology.
- **AGENTS.md §5**: The Paper Structure Framework section is the authoritative summary; this document is the complete implementation.

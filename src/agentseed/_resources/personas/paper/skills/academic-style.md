# Academic Style & Anti-AI-Academic-Flavor

> This document catalogs the most common AI-academic-flavor patterns in AI-generated scholarly writing — templated hedging, filler transitions, list mania, definition padding, passive-voice overuse, and false modesty — and provides concrete mitigation strategies for each.
> Is the complete implementation of AGENTS.md §9 Anti-AI-Academic-Flavor.
> Complements `paper-structure.md` — structure provides the skeleton; this document governs the prose that fills it.
> Complements `academic-integrity.md` — honest limitation disclosure and confidence tagging relate to the style guide's honesty standard.
> Format adapted from the novel profile's `anti-ai-patterns.md`: each pattern states the problem, the mitigation, and a checklist.

## Core Positioning

The problem with AI-generated academic writing is not "poor grammar" but "too much like statistical-average academic prose" — over-hedged, over-structured, padded with filler, and stripped of the directness that characterizes strong scholarly writing. This checklist categorizes these problems into 6 anti-patterns (§I), each with a mitigation and a checklist, followed by the positive academic style standards (§II), the sentence-economy principle (§III), and discipline-specific conventions (§IV).

---

## I. Anti-AI-Academic-Flavor (6 Patterns)

> Source: AGENTS.md §9.1 Forbidden AI Academic Patterns. These six patterns are the fingerprints of AI-generated academic text. Each one dilutes precision and signals templated writing.

### 1. Excessive Hedging
**Problem**: AI-generated academic prose stacks hedge upon hedge — "It could potentially be argued that there might be a possibility that..." The sentence says nothing while appearing cautious. Genuine scholarly caution states the limit; it does not bury the claim under five qualifiers.
**Mitigation**:
- State the claim directly; attach a single, specific qualifier if needed.
- Replace stacked hedges with one precise boundary: "X holds under condition Y" rather than "It might perhaps be the case that X."
- Reserve "may" / "might" for genuine uncertainty, not as a default tic.
- Checklist: Does the sentence stack two or more hedges ("could potentially perhaps")? If yes, cut to one or none.

### 2. Filler Transitions
**Problem**: AI pads academic prose with empty transitions — "It is worth noting that...", "It is important to mention that...", "In recent years, ...". These phrases carry no information; they exist to sound formal.
**Mitigation**:
- Cut the filler; start with the content. "It is worth noting that RAG reduces hallucination" → "RAG reduces hallucination."
- Replace "In recent years, X has attracted attention" with a specific citation: "Since 2020, RAG has been adopted in tutoring systems (Smith 2024)."
- Use transitions only when they signal a real logical move (contrast, causation, sequence).
- Checklist: Does the sentence begin with "It is worth noting" / "It is important to" / "It should be noted that"? If yes, delete the preamble.

### 3. List Mania
**Problem**: AI forces every paragraph into "First... Second... Third..." even when the content is not sequential. The enumeration signals structure but delivers no logic, and the prose loses its flow.
**Mitigation**:
- Use lists only when the items are genuinely parallel or sequential.
- Convert false enumerations to connected prose: "First, RAG retrieves; second, it generates; third, it cites" → "RAG retrieves relevant passages, generates a response conditioned on them, and cites the sources."
- Reserve numbered lists for methods steps, contributions, and findings — not for argumentation.
- Checklist: Are there three or more "First/Second/Third" sequences on a single page? If yes, convert some to prose.

### 4. Definition Padding
**Problem**: AI defines basic terms the target audience already knows — "Machine learning, a subfield of artificial intelligence that enables systems to learn from data, ...". This signals "I am writing an academic paper" without adding value.
**Mitigation**:
- Define only terms that are contested, novel, or discipline-specific.
- Assume the audience's background knowledge: a CS paper need not define "neural network"; a humanities paper need not define "metaphor."
- When a definition is needed, fold it into the argument, not as a standalone sentence.
- Checklist: Does the paper define a term the target audience already knows? If yes, delete the definition.

### 5. Passive Voice Overuse
**Problem**: AI defaults to passive constructions — "It was observed that...", "The model was trained...", "Experiments were conducted...". Passive voice hides the actor and inflates the sentence.
**Mitigation**:
- Use active voice when the actor matters: "We trained the model" not "The model was trained."
- Reserve passive for when the actor is irrelevant or unknown: "The data were collected anonymously."
- Prefer "We observed X" over "It was observed that X" — the latter adds words and obscures agency.
- Checklist: Does the sentence use "It was [verb]ed that..."? If yes, rewrite with a clear subject.

### 6. False Modesty
**Problem**: AI hedges the paper's own contribution with false modesty — "While this study is limited, it represents a significant contribution to the field...". Let the reader judge significance; stating it yourself is presumptuous in the opposite direction.
**Mitigation**:
- State the contribution factually: "We contribute a benchmark and an empirical evaluation." Let the reader assess significance.
- State limitations directly and stop: "Our sample is limited to English." Do not append "but this is still important."
- Avoid "To the best of our knowledge" as a reflex — use it only when genuinely unsure of prior work.
- Checklist: Does the sentence claim its own significance ("significant contribution," "important advance")? If yes, cut the claim; let the evidence speak.

---

## II. Academic Style Standards

> Source: AGENTS.md §9.2 Academic Style Standards. The positive counterpart to §I: what academic prose should be.

### Standard 1: Precision
Every claim is specific. Vague assertions are replaced with measurable statements.

| Vague | Precise |
|-------|---------|
| "X improved performance" | "X improved F1 score by 4.2 points (p < .01, d = 0.35)" |
| "Many studies show..." | "Three meta-analyses report..." (with citations) |
| "RAG is effective" | "RAG reduced hallucination by 30% on the TutorHall benchmark" |
| "Recently, ..." | "Since 2020, ..." (with citation) |

### Standard 2: Economy
The fewest words that convey the full meaning. Cut wordy constructions.

| Wordy | Economical |
|-------|-----------|
| "in order to" | "to" |
| "due to the fact that" | "because" |
| "a majority of" | "most" |
| "in the event that" | "if" |
| "at this point in time" | "now" |
| "it has been shown by Smith (2024) that" | "Smith (2024) showed that" |
| "there is evidence to suggest that" | "evidence suggests that" |

### Standard 3: Active Voice
Prefer active when the actor matters.

| Passive | Active |
|---------|--------|
| "It was observed that the model overfit" | "We observed that the model overfit" |
| "The data were analyzed using..." | "We analyzed the data using..." |
| "It has been argued that..." | "Lee (2023) argues that..." |
| "The experiment was conducted" | "We conducted the experiment" |

- Reserve passive for genuine cases (actor unknown, actor irrelevant, emphasis on the recipient).

### Standard 4: Tense
Tense follows the section's function, not a single rule.

| Section | Tense | Example |
|---------|-------|---------|
| Methods | Past | "We trained the model for 10 epochs." |
| Results | Past | "The model achieved 92% accuracy." |
| Discussion (interpretation) | Present | "This suggests that RAG mitigates hallucination." |
| Established knowledge | Present | "Transformers process sequences in parallel." |
| Citations of prior work | Past or present | "Smith (2024) found..." / "Smith (2024) argues..." |
| Figure/table description | Present | "Figure 1 shows..." |

### Standard 5: Honest Limitation
State limitations directly, not buried in a final paragraph.

| Anti-pattern | Fix |
|--------------|-----|
| Burying limitations in the last Discussion sentence | Give limitations their own subsection |
| "While limited, this study is still significant" | State the limitation; stop |
| Listing limitations without analyzing impact | For each limitation, state its likely effect on the conclusions |
| Omitting limitations entirely | Anticipate validity threats (see `methodology-design.md` §5); report residual threats |

---

## III. Sentence-Economy Principle

The sentence is the unit of academic thought. Each sentence carries one idea, stated as economically as precision allows.

### 3.1 One Idea Per Sentence

| Anti-pattern | Fix |
|--------------|-----|
| Stacking multiple ideas in one sentence | Split into separate sentences |
| Subordinate-clause chains | Break into declarative sentences |
| "X, which Y, and therefore Z, despite W" | "X. Because Y, Z. However, W." |

### 3.2 Cut Wordy Constructions

| Wordy | Economical |
|-------|-----------|
| "the reason for this is that" | "because" |
| "in spite of the fact that" | "although" |
| "with regard to" | "about" / "for" |
| "in the context of" | "in" / "for" |
| "a number of" | "several" / "many" |
| "make a decision" | "decide" |
| "is able to" | "can" |
| "utilize" | "use" |

### 3.3 Prefer Verbs Over Nominalizations

| Nominalization | Verb form |
|----------------|-----------|
| "make an investigation of" | "investigate" |
| "conduct an analysis of" | "analyze" |
| "provide a description of" | "describe" |
| "reach a conclusion" | "conclude" |
| "give an explanation of" | "explain" |

### 3.4 Vary Sentence Length (Avoid Uniformity)

AI-generated academic prose tends toward uniform medium-length sentences. Vary the rhythm:

| Length | Use |
|--------|-----|
| Short (5–12 words) | Emphasis; a key claim |
| Medium (15–25 words) | Standard exposition |
| Long (30+ words) | Complex relations; use sparingly |

- A short sentence after a long one creates emphasis.
- Three long sentences in a row fatigue the reader.

---

## IV. Discipline-Specific Conventions

### 4.1 Computer Science

| Convention | Standard |
|-----------|----------|
| Voice | "We" accepted for the system and its evaluators |
| Tense | Past for experiments; present for system description |
| Terminology | Define novel terms; assume standard ML/CS terms |
| Mathematics | Inline math for simple expressions; display for derivations |
| Citations | IEEE or ACL numbered style common |
| Related Work | May be a separate section or folded into Introduction |

### 4.2 Social Science

| Convention | Standard |
|-----------|----------|
| Voice | "We" accepted; passive common for procedure |
| Tense | Past for methods/results; present for theory |
| Terminology | Define discipline-specific terms; operationalize constructs |
| Statistics | APA reporting: test, df, p, effect size, CI (see `data-presentation.md`) |
| Citations | APA 7th (author-date) dominant |
| Limitations | Dedicated subsection expected |

### 4.3 Humanities

| Convention | Standard |
|-----------|----------|
| Voice | Author's voice more prominent; "I" acceptable in some subfields |
| Tense | Literary present for discussing texts ("Hamlet hesitates") |
| Terminology | Theoretical terms defined with reference to their tradition |
| Evidence | Close reading; quotation central; primary sources cited |
| Citations | MLA 9th or Chicago (notes-bibliography) |
| Argument | Extended analysis; longer paragraphs acceptable |

### 4.4 Biomedical

| Convention | Standard |
|-----------|----------|
| Voice | "We" for the research team; passive for procedures |
| Tense | Past for methods/results; present for established medical knowledge |
| Terminology | Follow MeSH (Medical Subject Headings); define abbreviations on first use |
| Statistics | Vancouver reporting; effect sizes and CIs expected |
| Citations | Vancouver (numbered) dominant |
| Ethics | IRB/ethics approval and trial registration stated up front |

### 4.5 Discipline Convention Quick Comparison

| Dimension | CS | Social Science | Humanities | Biomedical |
|-----------|----|----|------|-----------|
| First person | "We" common | "We" common | "I" acceptable | "We" common |
| Tense for results | Past | Past | Literary present | Past |
| Citation style | IEEE / ACL | APA 7th | MLA / Chicago | Vancouver |
| Math/equations | Common | Sometimes | Rare | Sometimes |
| Quotation | Rare | Sometimes | Central | Rare |
| Limitations subsection | Sometimes | Expected | Integrated | Expected |

---

## Appendix A: AI-Academic-Flavor Forbidden Expression List

> The following expressions appear at high frequency in AI-generated academic text. Avoid or replace with the concrete alternative.

### English High-Frequency Forbidden Expressions

| Expression | Context | Replacement |
|------------|---------|-------------|
| It is worth noting that | Filler transition | Delete; state the content directly |
| It is important to mention that | Filler transition | Delete; state the content directly |
| It should be noted that | Filler transition | Delete; state the content directly |
| In recent years, ... | Vague time reference | Specific year + citation |
| In today's fast-paced world | Filler opener | Delete; enter the topic directly |
| It could potentially be argued that | Excessive hedging | State the claim; qualify once if needed |
| There is evidence to suggest that | Wordy hedging | "Evidence suggests that" or cite directly |
| It has been shown that | Passive padding | "Smith (2024) showed that" |
| In order to | Wordy | "to" |
| Due to the fact that | Wordy | "because" |
| A number of studies | Vague | "Three studies (Smith 2023; Lee 2024; Patel 2022)" |
| Plays a crucial role | Vague | State the specific role |
| Sheds light on | Cliché | State the specific insight |
| Paves the way for | Cliché | State the specific contribution |
| To the best of our knowledge | Reflexive hedge | Use only when genuinely unsure of prior work |
| While this study is limited, it represents a significant contribution | False modesty | State the limitation; let the reader judge significance |
| Further research is needed | Vague future work | State the specific next step |

### Forbidden "GPT-ism" Academic Vocabulary

| Category | Forbidden term | Replacement direction |
|----------|---------------|----------------------|
| Verb | delve, navigate, explore, unravel, demystify, elucidate, traverse, forge | Specific action verb |
| Noun | landscape, tapestry, realm, frontier, paradigm, nexus, beacon, symphony, labyrinth | Specific noun |
| Adjective | nuanced, intricate, multifaceted, profound, paramount, quintessential, pivotal | Specific descriptor |
| Phrase | in the realm of, serves as a testament to, it's worth noting that | Direct statement |
| Opener | In today's fast-paced world, Since the dawn of, Throughout history | Enter the topic directly |

---

## Appendix B: Hedging Reduction Guide

Hedging is legitimate when uncertainty is genuine. The problem is reflexive, stacked hedging that signals nothing.

| Situation | Appropriate hedge | Inappropriate stacked hedge |
|-----------|-------------------|-----------------------------|
| Genuinely uncertain claim | "This suggests..." (one hedge) | "It could perhaps potentially be suggested that..." |
| Claim with a boundary | "X holds under condition Y" | "It might be the case that X, in some sense, perhaps..." |
| Speculation | "We speculate that..." | "One might argue that there is a possibility that..." |
| Confident finding | No hedge; cite the evidence | "The results seem to perhaps indicate that..." |
| Limitation | "Our sample is limited to English" | "It might be worth considering that our sample could perhaps be limited..." |

### Hedging Density Rule
- Zero hedges for established facts and your own confirmed results.
- One hedge for genuine uncertainty.
- Two or more hedges stacked → rewrite.

---

## Appendix C: Transition Replacement Guide

| Filler transition | Replacement |
|-------------------|-------------|
| It is worth noting that X | X |
| It is important to mention that X | X |
| It should be noted that X | X |
| As is well known, X | (Delete — if well known, you need not say so) |
| Interestingly, X | X (let the reader find it interesting) |
| Remarkably, X | X (let the reader find it remarkable) |
| Notably, X | X |
| In recent years, X | "Since [year], X (citation)" |
| In the modern era, X | X |
| Against this backdrop, X | X |

- Use real logical transitions (however, therefore, by contrast, consequently) only when they signal a genuine logical move.

---

## Appendix D: Active-Voice Conversion Reference

| Passive | Active |
|---------|--------|
| It was observed that X | We observed that X |
| It was found that X | We found that X |
| It has been shown that X | Smith (2024) showed that X |
| The model was trained on D | We trained the model on D |
| The data were collected | We collected the data |
| Experiments were conducted | We conducted experiments |
| It is widely believed that X | Several authors argue that X (citations) |
| It can be seen that X | Figure 1 shows that X |

- Reserve passive for: actor unknown, actor irrelevant, emphasis on the recipient ("Participants were debriefed").

---

## Relationship to Other Documents

| Existing rule | This document supplements |
|---------------|--------------------------|
| AGENTS.md §9 Anti-AI-Academic-Flavor | Provides the 6-pattern checklist, style standards, and forbidden expression list |
| AGENTS.md §2 Academic Integrity | Honest limitation disclosure (Standard 5) implements the integrity red line |
| `paper-structure.md` | Section prose follows this style guide; structure provides the skeleton, style fills it |
| `data-presentation.md` | Caption phrasing and statistical reporting follow the precision and economy standards here |
| `citation-protocol.md` | Citation phrasing ("Smith (2024) found..." vs "It was found (Smith, 2024)") follows the active-voice standard |
| `academic-integrity.md` | Confidence tagging ([High]/[Medium]/[Low]) aligns with the honest-limitation standard |

## Core Principles
- The problem with AI-generated academic writing is not "weak ability" but "too much like statistical-average academic prose" — actively push away from the average.
- The 6 anti-patterns are not all checked at once — select the 3–4 most relevant to the current section.
- The forbidden expression list is not absolute — if a term is genuinely precise, use it; the list targets reflexive, information-free uses.
- The best mitigation is always "replace vague, statistical, templated phrasing with specific, concrete, evidence-anchored statements."
- Academic writing is precise, not hedged; economical, not padded; active, not evasive; honest, not falsely modest.

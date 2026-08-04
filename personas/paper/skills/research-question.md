# Research Question & Hypothesis

> This document defines the research question formulation framework: the FINER criteria, the PICO framework, hypothesis construction templates, the distinction between quantitative and qualitative questions, and good-vs-bad question examples.
> Is the complete implementation of AGENTS.md §6 Research Question & Hypothesis.
> Complements `literature-synthesis.md` — the literature review identifies the gap; this document turns the gap into a precise question.
> Complements `methodology-design.md` — the research question determines the methodology; the methodology must be able to answer the question.
> Complements `paper-structure.md` — the research question is stated at the end of the Introduction and shapes the paper's structure.

## §1 Core Principles

- **The question precedes the method**: A research question is not reverse-engineered from a method you already want to use. The question comes first; the method follows.
- **Specific over broad**: "How does AI affect education?" is a topic, not a question. "Does retrieval-augmented generation reduce factual hallucination rates in LLM-based tutoring for undergraduate CS courses?" is a question.
- **Answerable over ambitious**: A question you can actually answer with the available resources is better than a grand question you cannot.
- **Novel over derivative**: If the literature already answers your question, it is not a research question — it is a literature finding.
- **Ethical by design**: A question that cannot be answered ethically is not a valid question, regardless of its scientific interest.

## §2 FINER Criteria

A good research question satisfies all five FINER criteria. Use this as a checklist before committing to a question.

| Criterion | Question to answer | Pass standard |
|-----------|--------------------|---------------|
| **Feasible** | Can you answer it with available time, data, expertise, and resources? | Realistic scope; adequate sample; accessible data; sufficient expertise |
| **Interesting** | Does it interest you and the field? | You are motivated; the field cares about the answer |
| **Novel** | Has it already been answered? | Confirmed via literature review; not a replication (unless replication is the point) |
| **Ethical** | Can it be answered ethically? | IRB approval feasible; no harm to participants; data protection possible |
| **Relevant** | Does the answer matter? | Advances theory, practice, or policy; fills an identified gap |

### 2.1 Feasibility Assessment

| Dimension | Question | Risk signal |
|-----------|----------|-------------|
| Time | Can it be completed within the available timeframe? | "Requires 5-year longitudinal data" with a 1-year deadline |
| Data | Is the data accessible? | "Requires proprietary corporate data" with no access agreement |
| Sample | Can you recruit enough participants/collect enough data? | Power analysis shows n > 10,000 needed; you have access to 200 |
| Expertise | Do you (or collaborators) have the required skills? | "Requires advanced Bayesian modeling" with no statistician on the team |
| Equipment | Do you have the required tools/compute? | "Requires training a 70B model" with single-GPU access |

### 2.2 Novelty Verification

| Novelty status | Meaning | Action |
|----------------|---------|--------|
| Genuinely novel | No prior work addresses this exact question | Proceed |
| Extension | Prior work addresses part; you add a new dimension | Proceed; cite prior work explicitly |
| Replication | Prior work addressed it; you replicate in a new context | Proceed only if replication is the stated contribution |
| Already answered | Prior work fully addresses this question | Reject; find a new question |

- Novelty is verified through literature review (see `literature-synthesis.md`). A question is not novel just because you have not read the prior work.

### 2.3 Ethical Screening

| Question | If "no" |
|----------|---------|
| Can participants give informed consent? | Redesign or reject |
| Are vulnerable populations protected? | Redesign or reject |
| Is data anonymizable? | Redesign or reject |
| Is IRB/ethics approval feasible? | Redesign or reject |
| Could the findings cause harm if misused? | Add safeguards; consult ethics board |

## §3 PICO Framework

PICO structures a research question into four components, ensuring precision. It is most natural for quantitative empirical work but adapts to other designs.

| Component | Question | Example |
|-----------|----------|---------|
| **P**opulation | Who or what is studied? | Undergraduate CS students using LLM tutoring |
| **I**ntervention | What is done to the population? | Retrieval-augmented generation (RAG) |
| **C**omparison | What is the intervention compared against? | Non-RAG baseline (closed-book LLM) |
| **O**utcome | What is measured? | Factual hallucination rate on a tutoring benchmark |

### 3.1 PICO Question Templates

```
Quantitative (effect):
"In [Population], does [Intervention] compared to [Comparison] affect [Outcome]?"

Example:
"In undergraduate CS students using LLM tutoring, does retrieval-augmented generation
compared to a non-RAG baseline reduce factual hallucination rates?"

Quantitative (association):
"Is [Intervention/Exposure] associated with [Outcome] in [Population]?"

Example:
"Is daily RAG use associated with lower hallucination rates among CS undergraduates?"

Qualitative (experience):
"How do [Population] experience [Intervention/Phenomenon]?"

Example:
"How do undergraduate CS students experience the shift from non-RAG to RAG tutoring?"
```

### 3.2 PICO Extensions

| Extension | Added component | Use when |
|-----------|-----------------|----------|
| PICOS | **S**tudy design | Specifying the design (RCT, cohort, etc.) |
| PICO-T | **T**imeframe | Outcome measured at a specific time point |
| PICOC | **C**ontext | Setting matters (e.g., rural vs urban clinic) |
| PECO | **E**xposure (replaces Intervention) | Observational studies where there is no intervention |

### 3.3 PICO for Non-Biomedical Fields

PICO originated in clinical medicine. Adapt it for other disciplines:

| Discipline | P | I | C | O |
|------------|---|---|---|---|
| Computer Science | System / user population | Technique / model | Baseline / alternative | Metric (accuracy, latency, F1) |
| Education | Student population | Pedagogical intervention | Control condition | Learning outcome |
| Social Science | Community / group | Policy / program | Comparison group | Social outcome |
| Humanities | Text / artifact corpus | Analytical lens / method | Prior interpretation | New reading / interpretation |

## §4 Hypothesis Construction

### 4.1 Quantitative Hypotheses

| Hypothesis type | Structure | Example |
|-----------------|-----------|---------|
| Directional | "X will increase/decrease Y" | "RAG will reduce hallucination rates relative to the non-RAG baseline." |
| Non-directional | "X will affect Y" | "RAG will affect hallucination rates." |
| Null (H0) | "X will have no effect on Y" | "RAG will have no effect on hallucination rates." |
| Alternative (H1) | The negation of H0 | "RAG will have an effect on hallucination rates." |

```
HYPOTHESIS TEMPLATE (quantitative)
──────────────────────────────────
[Population]: [describe]
[Intervention]: [describe]
[Comparison]: [describe]
[Outcome]: [describe, with direction if directional]

H1: [Intervention] will [increase/decrease] [Outcome] in [Population] compared to [Comparison].
H0: [Intervention] will have no effect on [Outcome] in [Population] compared to [Comparison].

Predicted effect size: [magnitude, if pre-registered]
Significance threshold: [alpha, e.g., .05]
```

### 4.2 Qualitative Propositions

Qualitative work does not test hypotheses in the quantitative sense. Instead, it states analytic propositions or guiding questions:

| Type | Structure | Example |
|------|-----------|---------|
| Guiding question | Open-ended exploration | "How do students experience RAG tutoring?" |
| Analytic proposition | Tentative, revisable claim | "Students may perceive RAG as more reliable but less creative than non-RAG." |
| Sensitizing concept | A lens for observation | "Trust calibration guides how students use RAG output." |

- Qualitative propositions are refined during analysis, not fixed in advance. Pre-registration is uncommon; transparency about the evolving framework is expected.

### 4.3 Hypothesis Pitfalls

| Pitfall | Why it fails | Fix |
|---------|--------------|-----|
| Vague outcome | "RAG will improve performance" | Specify the metric: "RAG will improve F1 by ≥ 3 points" |
| No comparison | "RAG will reduce hallucination" | State the comparison: "...relative to the non-RAG baseline" |
| Untestable | "RAG will be beneficial" | Operationalize: "RAG will reduce hallucination rate by ≥ 20%" |
| Post-hoc framing | Hypothesis written after seeing results | Pre-register; distinguish exploratory from confirmatory |

## §5 Quantitative vs. Qualitative Research Questions

| Dimension | Quantitative | Qualitative |
|-----------|--------------|-------------|
| Question form | "Does X affect Y?" / "How much?" | "How do...?" / "What is the experience of...?" |
| Purpose | Test hypotheses; measure effects | Explore; understand meaning; generate theory |
| Data | Numerical; measurable | Textual; observational; interview |
| Sample | Large; representative | Small; purposive |
| Analysis | Statistical | Thematic; interpretive |
| Hypothesis | Pre-stated; tested | Evolving; sensitizing |
| Generalization | Statistical (to population) | Analytical (to theory/concept) |
| Pre-registration | Common and encouraged | Uncommon; transparency expected |

### 5.1 Choosing Between Them

| If your goal is... | Choose |
|--------------------|--------|
| Measure the size of an effect | Quantitative |
| Test a causal claim | Quantitative (ideally experimental) |
| Understand how people experience something | Qualitative |
| Generate theory from observation | Qualitative (grounded theory) |
| Both measure and understand | Mixed methods |

### 5.2 Mixed-Methods Questions

Mixed-methods studies combine a quantitative and a qualitative question, with an explicit integration point:

```
QUANTITATIVE: Does RAG reduce hallucination rates in CS tutoring? (measured)
QUALITATIVE: How do students experience and trust RAG tutoring? (explored)
INTEGRATION: How do the measured effects relate to the experienced trust? (connected)
```

## §6 Good vs. Bad Research Questions

### 6.1 Comparison Table

| # | Bad question | Good question | What changed |
|---|--------------|---------------|--------------|
| 1 | "How does AI affect education?" | "Does retrieval-augmented generation reduce factual hallucination rates in LLM-based tutoring for undergraduate CS courses?" | Specified population, intervention, outcome |
| 2 | "Is social media bad?" | "Is daily Instagram use associated with depressive symptoms in adolescents aged 13–17?" | Specified exposure, outcome, population |
| 3 | "What do people think about AI?" | "How do knowledge workers perceive the reliability of AI-assisted writing tools in their daily workflows?" | Specified population, phenomenon, context |
| 4 | "Can deep learning predict stocks?" | "Can a transformer-based model predict next-day S&P 500 returns better than a random forest baseline, measured by Sharpe ratio?" | Specified model, comparison, metric |
| 5 | "Why is climate change important?" | "How do coastal communities in Southeast Asia adapt to rising sea levels, and what barriers do they face?" | Specified population, phenomenon, analytic focus |
| 6 | "Does therapy work?" | "Does cognitive-behavioral therapy reduce PTSD symptoms in adults compared to waitlist control, measured by the PCL-5 at 12 weeks?" | Specified intervention, comparison, outcome, timeframe |

### 6.2 Diagnosis Checklist for a Bad Question

| Symptom | Diagnosis | Treatment |
|---------|-----------|-----------|
| Topic, not question | No verb of inquiry; no specific outcome | Apply PICO; specify outcome |
| Unanswerable | Requires unavailable data or resources | Apply FINER Feasibility; narrow scope |
| Already answered | Literature fully addresses it | Run literature review; find a new angle |
| No comparison | "Does X work?" without a baseline | Specify the comparison condition |
| Vague outcome | "Improve performance" | Specify the metric and threshold |
| Too broad | Multiple populations, interventions, outcomes | Split into sub-questions; pick one |

### 6.3 From Topic to Question (Funnel)

```
TOPIC (broad area)
  "AI in education"
       │
       ▼
INTEREST (narrower)
  "LLM tutoring systems"
       │
       ▼
QUESTION (specific, answerable)
  "Does RAG reduce hallucination in LLM tutoring for CS undergrads?"
       │
       ▼
HYPOTHESIS (testable)
  "RAG reduces hallucination rates by ≥ 20% vs. non-RAG baseline."
```

## §7 Sub-Questions and Decomposition

A complex research question may decompose into sub-questions. Keep the hierarchy shallow:

| Level | Example |
|-------|---------|
| Primary RQ | "Does RAG reduce hallucination in LLM tutoring for CS undergrads?" |
| Sub-RQ 1 | "Does the effect vary by question difficulty?" |
| Sub-RQ 2 | "Does the effect vary by topic domain?" |
| Sub-RQ 3 | "What failure modes remain under RAG?" |

- Sub-questions should each be FINER-compliant on their own.
- Limit to 3–5 sub-questions; more suggests the primary question is too broad.

## §8 Research Question Checklist

- [ ] Is the question specific (population, intervention, comparison, outcome stated)?
- [ ] Is it answerable with available resources (FINER Feasible)?
- [ ] Is it novel (confirmed via literature review)?
- [ ] Is it ethical (IRB feasible; no harm)?
- [ ] Is it relevant (advances theory/practice/policy)?
- [ ] Is the outcome measurable / observable?
- [ ] Is the comparison explicit?
- [ ] If quantitative, is the hypothesis testable and directional where appropriate?
- [ ] If qualitative, is the guiding question or proposition clear?
- [ ] If mixed-methods, is the integration point specified?

## §9 Relationship to Other Documents

- **`literature-synthesis.md`**: The literature review identifies the gap; this document turns the gap into a FINER/PICO question.
- **`methodology-design.md`**: The methodology must be able to answer the research question. This document defines the question; that document defines how to answer it.
- **`paper-structure.md`**: The research question is stated at the end of the Introduction and shapes the paper's structure.
- **`academic-style.md`**: The research question should be stated precisely, not hedged — the style guide governs how the question is worded in the manuscript.
- **AGENTS.md §6**: The Research Question & Hypothesis section is the authoritative summary; this document is the complete implementation.

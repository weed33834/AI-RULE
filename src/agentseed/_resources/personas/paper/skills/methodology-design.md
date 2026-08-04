# Methodology Design

> This document defines the methodology design framework: methodology type selection, the reproducibility checklist, sample-size calculation, validity threats (internal, external, construct), and reporting standards (CONSORT, PRISMA, STROBE, and related guidelines).
> Is the complete implementation of AGENTS.md §7 Methodology Design.
> Complements `research-question.md` — the research question determines the methodology; the methodology must be able to answer the question.
> Complements `academic-integrity.md` — honest reporting of methods and results is part of the no-falsification red line.
> Complements `data-presentation.md` — the methods determine what data is produced; that document governs how it is presented.

## §1 Core Principles

- **Method follows question**: The methodology is chosen because it can answer the research question — not because it is fashionable or familiar.
- **Reproducibility is a duty**: A reader with the same data and code should be able to reproduce the results. Irreproducible methods are incomplete methods.
- **Honesty over elegance**: Report what you actually did, including deviations from the pre-registered protocol. Hiding deviations is a form of falsification.
- **Validity is designed, not assumed**: Threats to validity are anticipated and addressed in the design — not mentioned only as limitations after the fact.
- **Reporting standards are mandatory**: If your study type has a reporting standard (CONSORT, PRISMA, STROBE), follow it. Deviation requires justification.

## §2 Methodology Types

| Type | When to use | Key components | Common designs |
|------|-------------|----------------|----------------|
| Quantitative | Measuring effects; testing hypotheses; estimating relationships | Sample size, variables, instruments, statistical tests | RCT, quasi-experiment, survey, correlational |
| Qualitative | Understanding meaning; exploring phenomena; generating theory | Sampling strategy, interview/observation protocols, coding scheme | Ethnography, grounded theory, phenomenology, case study |
| Mixed | Both breadth (measure) and depth (understand) | Sequential or concurrent design; explicit integration point | Explanatory sequential, exploratory sequential, convergent |
| Computational | Simulation, modeling, NLP/ML experiments | Dataset, model architecture, evaluation metrics, baselines | Benchmark study, ablation study, simulation, replication |

### 2.1 Quantitative Methods

| Design | Question form | Key requirement |
|--------|---------------|-----------------|
| Randomized controlled trial (RCT) | "Does I cause O?" | Random assignment; control group; pre-registration |
| Quasi-experiment | "Does I affect O?" (no random assignment) | Matched comparison; address selection bias |
| Survey / correlational | "Is I associated with O?" | Representative sample; validated instruments |
| Longitudinal | "How does O change over time?" | Retention strategy; time-series analysis |

### 2.2 Qualitative Methods

| Design | Question form | Key requirement |
|--------|---------------|-----------------|
| Ethnography | "What is the culture of P?" | Prolonged fieldwork; participant observation |
| Grounded theory | "What theory explains P?" | Iterative coding; theoretical sampling; saturation |
| Phenomenology | "What is the lived experience of P?" | In-depth interviews; bracketing |
| Case study | "How does X play out in case C?" | Multiple sources of evidence; bounded system |

### 2.3 Mixed Methods

| Design | Sequence | Integration |
|--------|----------|-------------|
| Explanatory sequential | Quant first → qual explains the quant findings | Qual results interpret quant results |
| Exploratory sequential | Qual first → quant tests the qual-generated theory | Quant results test qual insights |
| Convergent | Quant and qual in parallel → merge | Side-by-side comparison; joint display |

### 2.4 Computational Methods

| Design | Purpose | Key requirement |
|--------|---------|-----------------|
| Benchmark study | Compare systems on a standard task | Same dataset, metrics, splits; multiple baselines |
| Ablation study | Isolate component contributions | Remove one component at a time; hold the rest fixed |
| Simulation | Study a system under controlled conditions | Validate the simulator; report parameters |
| Replication study | Reproduce a prior result | Same code/data when available; report deviations |

## §3 Reproducibility Checklist

A reproducible study allows a reader with the same data and code to regenerate the results. Use this checklist for every computational and empirical study.

| # | Item | Standard |
|---|------|----------|
| 1 | Dataset source | Origin, version, license documented |
| 2 | Preprocessing | Every transformation step documented (or scripted) |
| 3 | Train/val/test splits | Split logic documented; random seed reported; no test-set leakage |
| 4 | Model architecture | Fully specified; config file or diagram provided |
| 5 | Hyperparameters | All reported; search space and selection method documented |
| 6 | Random seeds | Reported for every stochastic process |
| 7 | Software environment | Language, library versions, OS documented (or containerized) |
| 8 | Statistical tests | Test named; assumptions checked; significance threshold stated |
| 9 | Effect sizes | Reported alongside p-values (see `data-presentation.md`) |
| 10 | Code availability | Public repository with versioned tag; or stated reason for restriction |
| 11 | Data availability | Public link; or access protocol; or stated reason for restriction |
| 12 | Pre-registration | Protocol reference if applicable; deviations disclosed |
| 13 | Compute resources | Hardware (e.g., GPU type/count) and runtime reported |
| 14 | Experimental protocol | Step-by-step; order of operations; enough to redo exactly |

### 3.1 Reproducibility Tiers

| Tier | Standard | When acceptable |
|------|----------|-----------------|
| Full reproducibility | Code + data + environment public; anyone can rerun | Gold standard; expected for computational work |
| Replicability | Code public; data restricted but described; results can be replicated with comparable data | Acceptable when data is sensitive/proprietary |
| Methodological transparency | Methods fully described; no code/data; results cannot be re-run but design is clear | Minimum acceptable for non-computational work |
| Irreproducible | Methods incomplete; no code/data | Not acceptable |

## §4 Sample-Size Calculation

An under-powered study cannot detect a real effect; an over-powered study wastes resources and can detect trivial effects as significant. Calculate sample size before data collection.

### 4.1 Inputs to Sample-Size Calculation

| Input | Meaning | How to set |
|-------|---------|------------|
| Effect size | The minimum effect worth detecting | From prior literature or a meaningful-effects analysis |
| Significance level (alpha) | Threshold for false positive | Conventionally .05; pre-register if different |
| Power (1 − beta) | Probability of detecting a true effect | Conventionally .80; .90 for high-stakes |
| Variance | Spread of the outcome | From pilot data or prior studies |
| Design | Number of groups, repeated measures, clustering | Determined by the research design |

### 4.2 Calculation by Design

| Design | Calculation approach | Example tool |
|--------|----------------------|--------------|
| Two-group comparison | t-test power analysis | G*Power; `pwr.t.test` in R |
| ANOVA | F-test power analysis | G*Power; `pwr.anova.test` |
| Regression | Effect size f²; number of predictors | G*Power; `pwr.f2.test` |
| Correlation | Effect size r | `pwr.r.test` |
| Chi-square | Effect size w | `pwr.chisq.test` |
| Cluster RCT | Adjust for intra-cluster correlation | Cluster power calculators |
| ML benchmark | Not statistical; rule of thumb or learning-curve analysis | Domain heuristics |

### 4.3 Sample-Size Reporting

```
SAMPLE-SIZE REPORT TEMPLATE
────────────────────────────
Design: [e.g., two-sided independent-samples t-test]
Effect size: [e.g., Cohen's d = 0.5, based on Smith 2023]
Alpha: [.05]
Power: [.80]
Required n: [per group]
Final n: [recruited; note attrition]
Calculation tool: [G*Power 3.1 / R pwr 1.3-0]
```

- Report the effect-size assumption and its source. An effect size plucked from thin air undermines the calculation.
- If post-hoc power is reported, label it as post-hoc; it is not a substitute for a priori calculation.

### 4.4 Qualitative Sample Size

Qualitative work does not use statistical power. Instead, sample size is governed by saturation:

| Concept | Meaning |
|---------|---------|
| Saturation | New data no longer yields new themes or insights |
| When reached | After iterative analysis; cannot be pre-specified exactly |
| Reporting | State the point of saturation; describe the evidence |

- Typical ranges are informational, not prescriptive: 6–12 for homogeneous phenomenology; 20–40 for grounded theory; varies for ethnography.

## §5 Validity Threats

Validity threats are alternative explanations for your findings. Anticipate them in the design; address residual threats in the limitations.

### 5.1 Internal Validity

Internal validity asks: did the intervention (not something else) cause the outcome?

| Threat | Description | Mitigation |
|--------|-------------|------------|
| History | External event coincides with the intervention | Control group; pre-registration |
| Maturation | Participants change naturally over time | Control group; pre-post comparison |
| Testing | Pre-test affects post-test | Solomon four-group; wait between tests |
| Instrumentation | Measure changes over time | Calibrate; standardized instruments |
| Selection bias | Groups differ before the intervention | Random assignment; matching |
| Attrition | Differential dropout | Intention-to-treat analysis; report attrition |
| Regression to the mean | Extreme scores drift toward the mean | Control group; repeated measures |

### 5.2 External Validity

External validity asks: do the findings generalize beyond this study?

| Threat | Description | Mitigation |
|--------|-------------|------------|
| Sampling | Sample not representative of the target population | Probability sampling; report demographics |
| Context | Findings tied to a specific setting | Replicate in other settings; describe context |
| Time | Findings tied to a specific period | Note temporal context; replicate later |
| Ecological | Lab setting unlike real-world setting | Field experiment; naturalistic design |

### 5.3 Construct Validity

Construct validity asks: are you measuring what you claim to measure?

| Threat | Description | Mitigation |
|--------|-------------|------------|
| Poor operationalization | Measure does not capture the construct | Validate instrument; pilot test |
| Mono-method bias | Single measure of the construct | Multiple measures; triangulation |
| Mono-operation bias | Single version of the intervention | Multiple operationalizations |
| Evaluation apprehension | Participants alter behavior when observed | Debriefing; unobtrusive measures |
| Experimenter expectancy | Researcher's expectations influence results | Blinding; standardized protocol |

### 5.4 Statistical Conclusion Validity

| Threat | Description | Mitigation |
|--------|-------------|------------|
| Low power | Under-powered study misses real effects | A priori power analysis (see §4) |
| Violated assumptions | Test assumptions unmet | Check assumptions; use robust alternatives |
| Fishing / p-hacking | Multiple tests without correction | Pre-registration; correction for multiple comparisons |
| Unreliable measures | Noisy measures attenuate effects | Validate instruments; report reliability |

## §6 Reporting Standards

Reporting standards ensure studies are reported completely enough to be evaluated and replicated. If your study type has a standard, follow it.

### 6.1 Major Reporting Standards

| Standard | Study type | Key requirements |
|----------|-----------|------------------|
| CONSORT | Randomized controlled trials | Flow diagram; registration; randomization; blinding; primary/secondary outcomes; harms |
| CONSORT-SPI | Social/psychological RCTs | CONSORT + adaptation to non-clinical settings |
| TREND | Non-randomized controlled interventions | CONSORT-like + addressing selection bias |
| PRISMA | Systematic reviews and meta-analyses | Flow diagram; search strategy; screening; risk-of-bias assessment |
| PRISMA-ScR | Scoping reviews | PRISMA extension for scoping reviews |
| STROBE | Observational studies (cohort, case-control, cross-sectional) | Reporting items for each design |
| STARD | Diagnostic accuracy studies | Flow diagram; sensitivity/specificity reporting |
| ARRIVE | Animal research | Experimental design; sample size; welfare |
| COREQ | Qualitative interviews/focus groups | Research team; study design; analysis |
| SRQR | Qualitative research (general) | Reporting standards for qualitative research |

### 6.2 Reporting Standard Selection

| If your study is... | Use |
|---------------------|-----|
| A randomized controlled trial | CONSORT |
| A non-randomized intervention | TREND |
| A systematic review / meta-analysis | PRISMA |
| A scoping review | PRISMA-ScR |
| An observational study (cohort/case-control/cross-sectional) | STROBE |
| A diagnostic accuracy study | STARD |
| A qualitative interview/focus-group study | COREQ |
| Animal research | ARRIVE |
| A computational benchmark | No universal standard; follow venue guidelines; report reproducibility checklist (§3) |

### 6.3 Flow Diagrams

CONSORT and PRISMA require flow diagrams showing participant/paper flow:

```
CONSORT (RCT):
  Enrollment → Allocation → [Intervention A / Intervention B] → Analysis
  (with exclusions at each stage)

PRISMA (review):
  Identification → Screening → Eligibility → Included
  (with records excluded at each stage, with reasons)
```

- Generate the diagram from actual counts; do not approximate.
- Report exclusions with reasons at every stage.

## §7 Pre-Registration

Pre-registration declares the research question, hypothesis, design, and analysis plan before data collection (or before analysis, for secondary data).

| Element | What to pre-register |
|---------|---------------------|
| Research question and hypotheses | The exact RQ; directional/non-directional hypotheses |
| Sample size | A priori calculation; stopping rule |
| Variables | Primary and secondary outcomes; how measured |
| Analysis plan | Primary test; covariates; handling of missing data |
| Exclusion criteria | What counts as a valid observation |
| Deviation handling | How protocol deviations will be reported |

| Registry | Suitable for |
|----------|--------------|
| ClinicalTrials.gov | Clinical trials |
| OSF (Open Science Framework) | Any discipline; pre-prints and pre-registrations |
| AsPredicted | Short pre-registration; any discipline |
| AEA RCT Registry | Economics RCTs |

- Pre-registration is encouraged for confirmatory work; exploratory analysis should be labeled as such.
- Deviations from the pre-registered protocol are reported, not hidden.

## §8 Methodology Checklist

- [ ] Does the methodology answer the research question (see `research-question.md`)?
- [ ] Is the sample size justified by an a priori power analysis (quantitative) or saturation plan (qualitative)?
- [ ] Is the design reproducible (reproducibility checklist §3 complete)?
- [ ] Are validity threats anticipated and addressed in the design (§5)?
- [ ] Are residual validity threats disclosed in the limitations?
- [ ] Does the study follow the applicable reporting standard (§6)?
- [ ] If confirmatory, is the study pre-registered (§7)?
- [ ] Are deviations from the protocol disclosed honestly?
- [ ] Are statistical tests justified (assumptions checked; effect sizes reported)?
- [ ] Are code and data available (or access protocol stated)?

## §9 Relationship to Other Documents

- **`research-question.md`**: The research question determines the methodology. This document assumes a FINER/PICO question has been formulated.
- **`academic-integrity.md`**: Honest reporting of methods and results is part of the no-falsification red line. Deviations must be disclosed.
- **`data-presentation.md`**: The methodology produces the data; that document governs how the data is presented (tables, figures, statistical reporting).
- **`paper-structure.md`**: The Methods section's content follows this framework; the Results section reports what the methods produced.
- **`literature-synthesis.md`**: Systematic reviews follow PRISMA, which depends on the synthesis methodology's search and screening stages.
- **AGENTS.md §7**: The Methodology Design section is the authoritative summary; this document is the complete implementation.

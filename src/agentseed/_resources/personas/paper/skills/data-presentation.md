# Data Presentation

> This document defines the data presentation framework: the table-vs-chart decision, visualization principles, statistical reporting standards (effect sizes and confidence intervals, not just p-values), common chart types and their use cases, and accessibility design.
> Is the complete implementation of AGENTS.md §8 Data Presentation.
> Complements `methodology-design.md` — the methodology produces the data; this document governs how the data is presented.
> Complements `academic-style.md` — figures and tables are part of the prose; their captions and integration follow the style guide's precision and economy standards.
> Complements `academic-integrity.md` — honest data presentation (no cherry-picking, no misleading scales) is part of the no-falsification red line.

## §1 Core Principles

- **Clarity over aesthetics**: A reader should understand the figure without reading the caption. Beauty that obscures meaning has failed.
- **Honesty over impression**: Axes start at meaningful values; scales are not compressed to exaggerate effects; error bars are shown. Misleading visualization is a form of falsification.
- **Effect size over p-value**: Statistical significance is not practical significance. Report effect sizes and confidence intervals alongside p-values.
- **Accessibility by design**: Figures should be legible to readers with color vision deficiencies, on grayscale printouts, and at small sizes.
- **Self-containment**: Every table and figure is understandable from its caption alone — the reader should not need to hunt in the text for definitions.

## §2 Table vs. Chart Decision

| Data type | Recommended format | Why |
|-----------|-------------------|-----|
| Exact values, precise comparisons | Table | Readers need to read specific numbers |
| Few categories with exact values | Table | Numbers are the point |
| Trends over time | Line chart | Shape of change is the point |
| Distribution of a single variable | Histogram / box plot | Shape of distribution is the point |
| Distribution comparison across groups | Box plot / violin plot | Side-by-side distribution comparison |
| Proportions (2–4 categories) | Bar chart | Relative size is the point |
| Proportions (> 5 categories) | Stacked bar / treemap | Pie charts become unreadable |
| Correlation between two variables | Scatter plot | Joint pattern is the point |
| Correlation matrix | Heat map | Many pairs at once |
| Multi-dimensional data | Parallel coordinates / small multiples | Avoids overplotting |
| Model architecture / process | Diagram (not chart) | Structure is the point |
| Qualitative themes | Table or quote display | Categorization is the point |

### 2.1 When to Use a Table

| Situation | Use a table |
|-----------|-------------|
| Readers need exact values | Yes |
| Comparing many specific numbers | Yes |
| Displaying mixed qualitative and quantitative data | Yes |
| The audience may want to extract the data | Yes |
| Showing a trend's shape | No — use a line chart |

### 2.2 When to Use a Chart

| Situation | Use a chart |
|-----------|-------------|
| The overall pattern matters more than exact values | Yes |
| Comparing relative magnitudes | Yes |
| Showing a distribution's shape | Yes |
| Showing a relationship between variables | Yes |
| Readers need precise values for later use | No — use a table |

## §3 Visualization Principles

### 3.1 Core Principles

| Principle | Standard |
|-----------|----------|
| Clarity first | Reader understands the figure without the caption |
| Axis labeling | Every axis labeled; units included |
| Scale honesty | Y-axis starts at 0 for bar charts; breaks in axis clearly marked |
| Error representation | Error bars or confidence bands shown for estimates |
| Color purpose | Color encodes meaning; not decoration |
| Colorblind safety | Use colorblind-friendly palettes (viridis, cividis, colorbrewer) |
| No chartjunk | Remove 3D effects, shadows, gradients, decorative elements |
| No 3D for 2D data | 3D bars and pies distort perception |
| Font legibility | Readable at print size; minimum 8pt |

### 3.2 Colorblind-Friendly Palettes

| Palette | Type | Use |
|---------|------|-----|
| viridis | Sequential | Ordered data (low to high) |
| cividis | Sequential | Ordered data; optimized for color vision deficiency |
| magma / plasma / inferno | Sequential | Ordered data; darker low end |
| ColorBrewer Set2 / Dark2 | Qualitative | Categorical data (few categories) |
| ColorBrewer RdBu / RdYlBu | Diverging | Data with a meaningful midpoint |
| Okabe-Ito | Qualitative | 8-color palette designed for color vision deficiency |

- Avoid red-green encodings alone (most common color vision deficiency).
- Test figures in grayscale and with a color vision simulator (e.g., Coblis, Sim Daltonism).

### 3.3 Axis and Scale Rules

| Rule | Standard |
|------|----------|
| Y-axis on bar charts | Starts at 0 |
| Y-axis on line charts | May start above 0 if clearly marked; avoid misleading compression |
| Axis breaks | Clearly marked with a visible break symbol |
| Log scale | Labeled as log; tick marks at sensible intervals |
| Units | Included in axis label (e.g., "Response time (ms)") |
| Tick density | Enough to read values; not so many they overlap |

### 3.4 Caption Standards

| Element | Requirement |
|---------|-------------|
| Figure number | Sequential (Figure 1, Figure 2...) |
| Title | Descriptive; states what the figure shows |
| Definition | Define every symbol and abbreviation |
| Statistics | Report the statistic shown (e.g., "Error bars: 95% CI") |
| Sample | State n and condition |
| Self-containment | Reader understands without the main text |

```
CAPTION TEMPLATE
────────────────
Figure [N]. [What the figure shows]. [Key comparison or finding].
Error bars: [95% CI / SD / SE]. n = [sample size] per condition. [Abbreviation definitions].
```

## §4 Statistical Reporting Standards

### 4.1 Report More Than p-Values

A p-value alone tells the reader nothing about the size or precision of an effect. Report effect sizes and confidence intervals alongside p-values.

| Report | Required? | Example |
|--------|-----------|---------|
| Test statistic | Yes | t(58) = 3.42 |
| Degrees of freedom | Yes | (58) |
| p-value | Yes | p = .001 (exact, not "p < .05") |
| Effect size | Yes | d = 0.88 |
| Confidence interval | Yes | 95% CI [0.42, 1.34] |
| Sample size | Yes | n = 30 per group |

### 4.2 Effect Size Reporting by Test

| Test | Effect size | Interpretation (Cohen) |
|------|-------------|------------------------|
| t-test | Cohen's d | 0.2 small / 0.5 medium / 0.8 large |
| ANOVA | eta-squared (η²), partial eta-squared | 0.01 / 0.06 / 0.14 |
| Regression | f², R² | 0.02 / 0.15 / 0.35 |
| Correlation | r | 0.1 / 0.3 / 0.5 |
| Chi-square | Cramér's V, odds ratio | Context-dependent |

### 4.3 Confidence Interval Reporting

| Standard | Example |
|----------|---------|
| State the confidence level | 95% CI |
| Provide both bounds | [0.42, 1.34] |
| Report in the same units as the estimate | If effect is in ms, CI in ms |
| Interpret in context | "The CI excludes 0, consistent with a positive effect." |

### 4.4 p-Value Reporting Rules

| Rule | Standard |
|------|----------|
| Exact values | Report exact p (p = .003), not just "p < .05" |
| Threshold | p < .001 is acceptable for very small values |
| Marginal | Label marginal results (e.g., p = .051) honestly; do not round to significant |
| Multiple comparisons | Correct (Bonferroni, FDR); report corrected and uncorrected |
| No "NS" | Avoid "NS" / "n.s." — report the exact value |

### 4.5 Common Statistical Reporting Errors

| Error | Why it misleads | Fix |
|-------|-----------------|-----|
| p-value only | Hides effect size and precision | Report effect size and CI |
| "p < .05" | Loses information | Report exact p |
| No effect size | Reader cannot judge practical importance | Always include |
| Uncorrected multiple comparisons | Inflates false positives | Correct; report method |
| Mean without dispersion | Hides variability | Report SD or CI |
| Cherry-picked significant results | Hides null findings | Report all pre-registered analyses |

## §5 Common Chart Types and Use Cases

### 5.1 Chart Selection Guide

| Chart type | Use for | Avoid for |
|------------|---------|-----------|
| Line chart | Trends over continuous variable | Categorical comparisons |
| Bar chart | Comparing categorical magnitudes | Continuous trends |
| Histogram | Distribution of one variable | Comparing individual values |
| Box plot | Distribution comparison across groups | Showing individual data points |
| Violin plot | Distribution shape + summary | Few data points |
| Scatter plot | Relationship between two continuous variables | Categorical data |
| Heat map | Matrix of values (e.g., correlation) | Single-variable distributions |
| Small multiples | Comparing a pattern across many conditions | Single-condition data |
| Forest plot | Meta-analysis effect sizes | Single-study results |
| ROC curve | Classifier trade-off | Regression results |

### 5.2 Chart-Specific Rules

| Chart | Rule |
|-------|------|
| Bar chart | Y-axis starts at 0; bars ordered meaningfully (by value or category) |
| Line chart | Lines distinguishable by style (not just color); direct-label when possible |
| Histogram | Bin width stated; no gaps between bars |
| Box plot | Outliers marked; quartile method stated |
| Scatter plot | Overplotting addressed (alpha, hex bins, sample) |
| Heat map | Color scale labeled; diverging palette for diverging data |
| Pie chart | Avoid; if used, ≤ 5 categories; sort by size |

### 5.3 Table-Specific Rules

| Rule | Standard |
|------|----------|
| Alignment | Numbers right-aligned; text left-aligned; decimals aligned |
| Decimal places | Consistent within a column |
| Units | In the column header, not repeated in cells |
| Significance | Footnoted with the test used; do not star-spam |
| Horizontal lines | Minimal (top, bottom, under header); no vertical lines |
| Caption above | Table caption goes above the table; figure caption below |

## §6 Accessibility Design

Accessible figures serve readers with color vision deficiencies, low vision, and those reading in grayscale or on small screens.

### 6.1 Accessibility Checklist

| # | Item | Standard |
|---|------|----------|
| 1 | Colorblind palette | Use viridis, cividis, Okabe-Ito, or similar |
| 2 | Redundant encoding | Color is not the sole encoding (use shape, line style, labels) |
| 3 | Grayscale legibility | Figure is readable when printed in grayscale |
| 4 | Contrast | Minimum 4.5:1 contrast between elements |
| 5 | Font size | Minimum 8pt at final print size |
| 6 | Line weight | Thick enough to be visible (≥ 1pt) |
| 7 | No color-only legend | Legend uses labels and shapes, not just color swatches |
| 8 | Alt text | Provide alt text for every figure (for screen readers) |
| 9 | Caption self-containment | Caption defines every symbol |
| 10 | Data provided | Underlying data available (supplementary or repository) |

### 6.2 Redundant Encoding

Never rely on color alone to distinguish categories. Combine color with:

| Encoding | Example |
|----------|---------|
| Shape | Different marker shapes per group in a scatter plot |
| Line style | Solid, dashed, dotted lines per condition |
| Direct labels | Label each line directly instead of a legend |
| Pattern | Different fill patterns in bar charts |

### 6.3 Alt Text

Alt text describes the figure for readers using screen readers:

```
ALT TEXT TEMPLATE
─────────────────
[Chart type] showing [main relationship]. [Key finding in one sentence].
Axes: x = [variable and units]; y = [variable and units]. [Number of groups/conditions].
```

Example:
```
Scatter plot showing the relationship between RAG retrieval count and hallucination rate.
Hallucination rate decreases as retrieval count increases. Axes: x = retrieval count (0–20);
y = hallucination rate (0–1). Two conditions: RAG (blue circles) and non-RAG baseline (gray triangles).
```

## §7 Figure and Table Integration with Text

### 7.1 Integration Rules

| Rule | Standard |
|------|----------|
| Cross-reference | Every figure/table is referenced in the text ("Figure 1 shows...") |
| No orphan figures | No figure appears that is never discussed |
| No text duplication | Text does not restate all the numbers in the figure |
| Highlight the point | Text states what the reader should see in the figure |
| Placement | Figure/table appears near its first reference (or in an appendix) |

### 7.2 Text-Figure Integration Patterns

```
PATTERN 1 (point then figure):
"RAG reduced hallucination rates relative to the baseline (Figure 2). The effect was
largest for multi-hop questions."

PATTERN 2 (figure then detail):
"Figure 2 shows hallucination rates by question type. The RAG condition (blue) is
consistently lower than the baseline (gray), with the largest gap on multi-hop questions."

ANTI-PATTERN (do not):
"Figure 2 shows the results. [Then lists every number in the figure.]"
```

## §8 Data Presentation Checklist

- [ ] Is a table or chart the right format for this data (§2)?
- [ ] Are all axes labeled with units (§3.3)?
- [ ] Is the palette colorblind-friendly and grayscale-legible (§3.2, §6)?
- [ ] Is color not the sole encoding (§6.2)?
- [ ] Are error bars / confidence intervals shown (§3.1)?
- [ ] Are effect sizes and CIs reported alongside p-values (§4)?
- [ ] Are p-values exact (not just "p < .05") (§4.4)?
- [ ] Is the caption self-contained (§3.4)?
- [ ] Is alt text provided (§6.3)?
- [ ] Is every figure/table cross-referenced in the text (§7.1)?
- [ ] Is the underlying data available (§6.1, item 10)?
- [ ] Are scales honest (no misleading compression) (§3.3)?

## §9 Relationship to Other Documents

- **`methodology-design.md`**: The methodology produces the data; this document governs how it is presented. Reporting standards (CONSORT, PRISMA, STROBE) defined there shape what appears in figures here.
- **`academic-integrity.md`**: Honest data presentation (no cherry-picking, no misleading scales) is part of the no-falsification red line.
- **`academic-style.md`**: Caption phrasing and text-figure integration follow the style guide's precision and economy standards.
- **`paper-structure.md`**: Figures and tables appear in the Results section (and sometimes Methods); their placement follows the structure framework.
- **AGENTS.md §8**: The Data Presentation section is the authoritative summary; this document is the complete implementation.

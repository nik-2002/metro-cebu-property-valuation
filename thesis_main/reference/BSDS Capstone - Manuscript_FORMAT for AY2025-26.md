# BSDS Capstone — Thesis Writing and Formatting Guide
**University of Asia and the Pacific | AY2025-26**
*Distilled from: Capstone Project Writing Guide (PDF) + Manuscript FORMAT (DOCX)*
*Supplemented with LaTeX conventions from the actual manuscript files*

> Use this file as the single reference for all thesis writing — chapters, tables, figures, citations, tense, and style. Every agent or collaborator writing any part of the thesis should read this first.

---

## 1. Document Structure

### 1.1 Front Matter (roman numerals i–xii)

| Page | Content |
|---|---|
| i | Title Page |
| ii | Approval Sheet |
| iii | Dedication |
| iv | Abstract |
| v | Acknowledgment |
| vi | Table of Contents |
| vii | List of Tables |
| viii | List of Figures |
| ix | List of Maps |
| x | List of Pictures |
| xi | List of Appendices |
| xii | List of Abbreviations and Acronyms |

### 1.2 Body (arabic numerals starting at 1)

| Chapter | CRISP-DM Phase |
|---|---|
| 1 | Introduction |
| 2 | Review of Related Works |
| 3 | Methodology |
| 4 | Data Understanding |
| 5 | Data Preparation |
| 6 | Modeling |
| 7 | Evaluation |
| 8 | Results and Discussion |
| 9 | Conclusions |
| 10 | Recommendations |
| — | Appendices |
| — | References |

### 1.3 LaTeX File Map

```
main.tex             — document root; inputs all chapters
chapter1.tex         — Introduction
chapter2.tex         — Review of Related Works
chapter3.tex         — Methodology
chapter4.tex         — Data Understanding
chapter5.tex         — Data Preparation
chapter6.tex         — Modeling
chapter7.tex         — Evaluation
chapter8.tex         — Results and Discussion
chapter9.tex         — Conclusions
chapter10.tex        — Recommendations
appendices.tex       — Appendices
biblio.bib           — BibTeX database (biblatex / biber)
```

---

## 2. Chapter Requirements

### Chapter 1 — Introduction

**Key question**: "What is the problem, and why does it need to be solved?"

**Required content**:
- Background of the study
- Problem statement (decision problem + research problem)
- Aims and objectives
- Research questions
- Significance of the study
- Scope and limitations
- Definition of key terms
- Organization of the report

**Tense**: Present for background facts; present perfect for research trends; past for what was done.

**Example**: *"Machine learning is a rapidly growing field. Researchers have increasingly explored its applications in real estate. This study aimed to develop a predictive model for..."*

---

### Chapter 2 — Review of Related Works

**Key question**: "What has already been done, and what gap does my project fill?"

**Required content**:
- Theoretical or conceptual framework
- Review of previous studies
- Comparison of related works (summary table recommended)
- Research gap the project addresses
- Chapter summary

**Tense**: Past for specific author findings; present perfect for summarizing a body of research; present for general facts.

**Example**: *"Ahmed (2021) found that Random Forest outperformed Decision Trees. Several researchers have explored geospatial features in property valuation. Hedonic pricing is a widely accepted framework for decomposing property value."*

---

### Chapter 3 — Methodology

**Key question**: "What is my game plan and why?"

**Required content**:
- Research design and justification for the chosen framework (CRISP-DM)
- Framework or process model adopted
- Overview of tools and technologies used
- Description of algorithms / techniques selected and why
- Description of data sources (not the preprocessing execution — that goes in Ch5)
- Evaluation metrics to be used and why
- Ethical considerations (if applicable)

**Tense**: Past for what was done; present perfect for established practices.

**Example**: *"The CRISP-DM framework was adopted for this study. CRISP-DM has been widely used in data mining projects (Wirth & Hipp, 2000). Python was selected as the primary programming language because it provides extensive libraries for machine learning."*

**Important distinction**: Chapter 3 describes *what* approach was designed and *why*. The step-by-step execution of preprocessing and feature engineering belongs in Chapter 5.

---

### Chapter 4 — Data Understanding

**Key question**: "What does my raw data look like, and what did I discover about it?"

**Required content**:
- Description of the dataset (number of records, features, data types)
- Summary statistics (mean, median, mode, standard deviation, min, max)
- Exploratory data analysis with visualizations (histograms, box plots, scatter plots, heatmaps, correlation matrices)
- Data quality assessment (missing values, outliers, duplicates, inconsistencies)
- Initial observations and insights

**Tense**: Past for findings; present when referring to tables and figures.

**Example**: *"The dataset contained 2,075 records and 50 features. As shown in Table 4, the target variable was highly right-skewed. Figure 3 illustrates the distribution of price per square meter across the six LGUs."*

---

### Chapter 5 — Data Preparation

**Key question**: "What did I do to clean and transform the data, and why?"

**Required content**:
- How missing values were handled (method + justification)
- How outliers were handled (method + justification)
- Encoding of categorical variables
- Feature scaling or normalization (if applied)
- Feature engineering (execution details — the *how*, not just the *what*)
- Feature selection
- Data splitting into training and test sets
- Description of the final cleaned dataset

**Tense**: Past throughout.

**Example**: *"Missing values in the BIR zonal value feature were imputed using the barangay-level median. Categorical variables were encoded using one-hot encoding. The dataset was split into 80% training and 20% test sets."*

---

### Chapter 6 — Modeling

**Key question**: "How exactly did I build and train my model(s)?"

**Required content**:
- Models implemented with detailed descriptions
- Model architecture and configuration (hyperparameters, settings)
- Hyperparameter tuning methods and results
- Training process and any challenges encountered
- Tools and libraries used
- Code snippets or screenshots if required

**Tense**: Past throughout.

**Example**: *"A Random Forest regressor was implemented using the scikit-learn library. The number of estimators was set to 500. Hyperparameter tuning was performed using GridSearchCV with 5-fold cross-validation."*

---

### Chapter 7 — Evaluation

**Key question**: "How good is my model, and how do I know?"

**Required content**:
- Evaluation metric results for each model (MAPE, MAE, RMSE, R² for regression)
- Comparison of models using tables and charts
- Cross-validation results
- Overfitting and underfitting analysis
- Best model selection with justification
- Assessment against objectives from Chapter 1

**Tense**: Past for results; present when referring to tables and figures.

**Example**: *"The XGBoost model achieved an R² of 0.803 and a MAPE of 43.93%. As shown in Table 12, this model outperformed both OLS and Random Forest. Figure 8 presents the SHAP summary plot for the best model."*

---

### Chapter 8 — Results and Discussion

**Key question**: "What do my results mean, and how do they compare to existing work?"

**Required content**:
- Summary of key results
- Interpretation of results in context
- Comparison with related works from Chapter 2
- Implications of the findings
- Unexpected findings and possible explanations
- Limitations encountered

**Tense**: Past for findings; present for interpretations and implications.

**Example**: *"The XGBoost model outperformed the other estimators. This result is consistent with the findings of Nyanda et al. (2024). The results suggest that ensemble methods are better suited to this dataset's size and distributional characteristics."*

---

### Chapter 9 — Conclusions

**Key question**: "Did I achieve what I set out to do?"

**Required content**:
- Summary of the entire project
- Whether each objective was met
- Key contributions
- Final remarks

**Tense**: Past for summarizing; present for contributions and implications.

---

### Chapter 10 — Recommendations

**Key question**: "What should be done next?"

**Required content**:
- Recommendations for future work
- Suggestions for practitioners
- Areas for further research
- Technical improvements

**Tense**: Present and modal verbs (could, should, may).

**Example**: *"Future researchers could explore the use of deep learning models. It is recommended that the model be deployed as a web-based application."*

---

## 3. APA 7th Edition Tense Rules

### Tense by Situation

| Situation | Tense | Example |
|---|---|---|
| Specific procedures you performed | Past | *"The data was collected from..."* |
| Specific author findings | Past | *"Smith (2020) found that..."* |
| Body of research, ongoing trends | Present perfect | *"Researchers have shown that..."* / *"Several studies have demonstrated..."* |
| General truths, established knowledge | Present | *"Decision Trees are supervised algorithms."* |
| Referring to tables and figures | Present | *"Table 3 shows the distribution."* / *"Figure 2 presents the SHAP plot."* |
| Results and findings in your study | Past | *"The model achieved R² = 0.803."* |
| Interpretations and implications | Present | *"The results suggest that..."* |

### Tense Summary by Chapter

| Chapter | Tense |
|---|---|
| 1 Introduction | Present, Present Perfect, Past |
| 2 Related Works | Past, Present Perfect, Present |
| 3 Methodology | Past, Present Perfect |
| 4 Data Understanding | Past, Present (tables/figures) |
| 5 Data Preparation | Past |
| 6 Modeling | Past |
| 7 Evaluation | Past, Present (tables/figures) |
| 8 Results & Discussion | Past, Present |
| 9 Conclusions | Past, Present |
| 10 Recommendations | Present, Modal Verbs |

### Common Proposal Language Errors

These are incorrect in a final paper and must not appear in any chapter:

| Wrong (Proposal) | Correct (Final Paper) |
|---|---|
| "The data *will be* collected from..." | "The data *was* collected from..." |
| "SMOTE *will be* applied to..." | "SMOTE *was* applied to..." |
| "This study *aims* to develop..." | "This study *aimed* to develop..." |
| "Our target is to beat 48% MAPE" | "The XGBoost model achieved 43.93% MAPE, below the 48% benchmark." |

**Rule**: If the final paper reads like a proposal, it needs revision. Timeline sections, target tables, and future-tense method descriptions are proposal artifacts and must be removed or rewritten.

---

## 4. APA 7th Formatting Specifications

### Page Layout

| Setting | Value |
|---|---|
| Font | 12pt Times New Roman |
| Left margin | 1.5 inches |
| Right, top, bottom margins | 1 inch |
| Spacing | Double-spaced throughout |
| Alignment | Left-aligned (not justified) |
| Paragraph indent | 0.5 inch first line |
| Page numbers | Top right corner |

### Numbers

- Spell out numbers below 10: *one, two, three...*
- Use numerals for 10 and above: *10, 25, 100*

### In-Text Citations

- Parenthetical: `(Author, Year)` — e.g., *(Rosen, 1974)*
- Narrative: `Author (Year)` — e.g., *Rosen (1974) proposed...*
- Three or more authors: `(Smith et al., Year)`

### Tables and Figures — Numbering

Tables and figures are numbered **consecutively throughout the entire manuscript** — not per chapter.

- Correct: Table 1, Table 2, Table 3... (regardless of which chapter they appear in)
- Incorrect: Table 3.1, Table 4.2 (chapter-prefixed numbering is not used in this program)
- Table captions appear **above** the table
- Figure captions appear **below** the figure

### References

- Hanging indent, double-spaced, alphabetical order by author last name
- APA 7th edition format throughout
- Three or more authors: list all up to 20, then "et al." for 21+

---

## 5. LaTeX Conventions for This Manuscript

### Document Class and Core Packages

```latex
\documentclass[man, 12pt, letterpaper, floatsintext]{apa7}
\usepackage{booktabs}          % \toprule, \midrule, \bottomrule in tables
\usepackage[style=apa, backend=biber]{biblatex}  % citations
\addbibresource{biblio.bib}
```

Margins are set in main.tex: `\geometry{left=1.5in,right=1in,top=1in,bottom=1in}`
Paragraph indent is set in main.tex: `\setlength{\parindent}{0.5in}`

### Section Hierarchy

```latex
\section{Chapter Title}\label{chapterN}                          % Chapter heading
\subsection{\texorpdfstring{\textbf{N.N Title}}{N.N Title}}     % Numbered section
\label{section-slug}
\subsubsection{\texorpdfstring{\textbf{N.N.N Title}}{N.N.N Title}}  % Sub-section
\label{subsection-slug}
```

Use `\texorpdfstring{\textbf{...}}{...}` for all numbered subsections so the PDF bookmarks don't contain bold markup.

### Section Separators

Use a horizontal rule between major subsections:

```latex
\begin{center}\rule{0.5\linewidth}{0.5pt}\end{center}
```

### Tables — Required Format

All tables **must** use the `table` float environment with a `\caption{}` so they appear in the List of Tables and get a continuous number. Never use a bare `tabular` inside `\begin{center}` without a caption.

```latex
\begin{table}[htbp]
\caption{Title of the Table}   % Caption ABOVE the table for APA
\label{tab:descriptive-slug}
\begin{center}
\begin{tabular}{p{0.25\textwidth} p{0.35\textwidth} p{0.25\textwidth}}
\toprule
Column A & Column B & Column C \\
\midrule
Row 1 & ... & ... \\
Row 2 & ... & ... \\
\bottomrule
\end{tabular}
\end{center}
\end{table}
```

Use `p{width}` column specifiers for text-heavy columns. Use `booktabs` rules only — never `\hline`.

### Figures — Required Format

```latex
\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/filename}
\caption{Description of the Figure}   % Caption BELOW the figure for APA
\label{fig:descriptive-slug}
\end{figure}
```

### Equations

Use display math for all model equations:

```latex
\[
\ln(\text{Price}) = \alpha + \beta_1 \ln(\text{Area}) + \beta_2(\text{Bedrooms}) + \epsilon
\]
```

For multi-line equations:

```latex
\[
\begin{aligned}
\text{MCRAI}_{i,c} &= \sum_{j=1}^{N_c} \frac{1}{d_{ij}^{\beta}} \quad \text{for } d_{ij} \leq r_c \\
\text{MCRAI\_composite}_i &= \sum_{c \in C^+} w_c \cdot \text{MCRAI}_{i,c}
\end{aligned}
\]
```

### In-Text Citations (biblatex/APA)

```latex
\parencite{rosen1974}            % → (Rosen, 1974)
\textcite{rosen1974}             % → Rosen (1974)
\parencite[p.~416]{tiebout1956}  % → (Tiebout, 1956, p. 416)
\parencites{rosen1974}{breiman2001}  % → (Rosen, 1974; Breiman, 2001)
```

Do not use manual `(Author, Year)` text for citations — always use biblatex commands so the bibliography compiles correctly.

### Itemize and Enumerate

```latex
\begin{itemize}
  \item \textbf{Key term}: Explanation text.
\end{itemize}

\begin{enumerate}
  \item First step.
  \item Second step.
\end{enumerate}
```

---

## 6. Thesis-Specific Terminology

### Terminology Rules

| Always use | Never use |
|---|---|
| Metro Cebu Residential Accessibility Index (MCRAI) — full name on first reference, then MCRAI | Hansen scores, amenity scores, OSM_Amenity_Score |
| `mcrai_composite` | weighted amenity index, combined score |
| osmnx network distance | Haversine-only distance (for MCRAI) |
| open_market segment | Lamudi-only model |
| price per square meter (`price_per_sqm`) | price/sqm, price per sqm |
| `valuation_gap` | gap, BIR gap |
| six LGUs: Cebu City, Mandaue City, Lapu-Lapu City, Talisay City, Minglanilla, Consolacion | Metro Cebu cities (Naga City is a CBD anchor only, not in training data) |
| XGBoost (capital B) | xgboost, XGboost |
| OLS as "interpretive baseline" | OLS as the deployed model |

### Key Numbers (Production Models — as of 2026-05-07)

| Model | R² | MAPE | MAE | RMSE |
|---|---|---|---|---|
| OLS (baseline) | — | — | — | — |
| Random Forest | 0.783 | 54.76% | PHP 6.54M | PHP 31.6M |
| XGBoost (deployed) | 0.803 | 43.93% | PHP 6.24M | PHP 30.1M |

Training subset: 1,647 open_market rows from ABT (2,075 total rows, 50 columns).

### CBD Nodes (8 nodes — Giuliano & Small 1991 + JICA Roadmap 2050)

Cebu Business Park (CBP), Mandaue CBD, Mactan/Lapu-Lapu CBD, South Road Properties (SRP), Talisay Tabunok, Consolacion, Naga City (industrial anchor), Mactan-Cebu International Airport.

### MCRAI Categories and Radii

| Category | Radius | Composite Weight |
|---|---|---|
| education | 0.8 km | 0.401 |
| grocery | 2.0 km | 0.310 |
| recreation | 1.5 km | 0.199 |
| transport | 3.0 km | 0.102 |
| health | 2.0 km | excluded (negative OLS coef) |
| finance | 1.5 km | excluded (negative OLS coef) |
| security | 2.0 km | excluded (negative OLS coef) |
| tourism | 3.0 km | excluded (negative OLS coef) |
| retail_density | 1.0 km | excluded (negative OLS coef) |

Decay parameter β = 2.0. Floor distance = 0.5 km. Network distances via osmnx (Dijkstra), Haversine fallback.

---

## 7. Writing Style Rules

### Voice and Register

- Write in academic prose — clear, direct, and specific.
- Preserve local specificity: Metro Cebu, barangays, BIR zonal values, CBRT, LGUs, osmnx, property type — do not generalize these into generic terms.
- Preferred: one clear sentence over a dense paragraph.
- Prefer defensible phrasing over ambitious phrasing when discussing model performance.

### What to Avoid

**Filler transitions** — use these only when genuinely needed, not as habit:
- moreover, furthermore, thus, hence, thereby, in addition, additionally

**AI/template phrasing** — never use:
- underscores, leverages, highlights, demonstrates (as a verb for findings), showcases
- plays a crucial role, it is worth noting, it is important to note
- this study seeks to, this research endeavors to

**Structural over-formatting** — do not:
- Convert nuanced paragraphs into bullet lists unless the content is genuinely enumerable
- Write multi-paragraph section intros that repeat what the subsection headings already say
- Add a "Chapter Summary" paragraph that only restates the section titles

**Hedging excess** — do not qualify every claim with "it may be argued," "it could be suggested." State findings directly.

### What Makes a Good Paragraph in This Thesis

1. One clear function per paragraph (define, cite, explain, compare, or interpret — not all at once)
2. Citations appear where the specific claim is made, not bunched at the end
3. Quantitative claims include the actual numbers (not just "significantly higher")
4. Metro Cebu context is present where relevant — not a generic global claim

### Discussion and Interpretation Paragraphs

When interpreting model outputs or coefficients:
- State the finding first (past tense)
- Then interpret it (present tense)
- Then cite the literature that supports the interpretation

*Example: "The OLS coefficient for `mcrai_security` was negative (−0.093). This is consistent with spatial sorting theory: security infrastructure is more densely deployed in lower-income neighborhoods, reflecting population need rather than property value generation (Tiebout, 1956; Bayer & McMillan, 2012). Physical proximity to police substations and barangay halls is further associated with noise and institutional externalities that offset service benefits at very close range (Dronyk-Trosper, 2017)."*

---

## 8. Citation and Evidence Rules

- Never invent citations, author names, publication years, or empirical findings.
- Never claim a source supports a statement unless the source text clearly supports it.
- Separate verified from unverified sources explicitly when reviewing literature.
- Gemini Deep Research and AI-generated literature summaries are starting points only — verify each paper via DOI before citing.
- ResearchGate links alone are not citable — confirm journal name and DOI first.
- If evidence is missing for a claim, explicitly flag it rather than citing an approximate source.

### Specific Citations That Are Verified (as of 2026-05-07)

For the spatial sorting interpretation of negative MCRAI coefficients:
- Tiebout (1956) — security/sorting mechanism
- Bayer & McMillan (2012) — empirical Tiebout sorting
- Dronyk-Trosper (2017) — nonlinear proximity effect for police/fire stations
- Brasington & Parent (2024) — service quality vs. proximity
- Yang et al. (2016) — retail density threshold disamenity (Seoul)
- Song & Knaap (2004) — mixed land use and residential values (Portland)
- Chen & Jim (2010) — Shenzhen urban landscape disamenities (limited scope — urban villages, NOT theme parks)

**Do not cite**: The "Shenzhen theme park study" (ref 20 in Polycentric Urbanism POI Analysis file) — ResearchGate URL identified but journal/DOI unverified as of 2026-05-07. See `lit_decision20_spatial_sorting.md` for status.

---

## 9. Checklist Before Submitting Any Chapter Draft

- [ ] Tense matches the chapter rule (see Section 3)
- [ ] No proposal language ("will be," "aims to," "our target is")
- [ ] No timeline/milestones section (proposal artifact)
- [ ] All tables use `\begin{table}...\caption{...}...\end{table}` — not bare `tabular`
- [ ] Table numbers are continuous across the manuscript (not per-chapter)
- [ ] All citations use `\textcite{}` or `\parencite{}` — no manual `(Author, Year)` text
- [ ] All cited sources have a corresponding entry in `biblio.bib`
- [ ] Content matches the actual implemented system (not an earlier design)
- [ ] No forbidden phrases (see Section 7)
- [ ] Quantitative claims include the actual numbers
- [ ] Metro Cebu specificity is preserved throughout

---

*Last updated: 2026-05-07*
*Source documents: Capstone Project Writing Guide (PDF, 5pp) + Manuscript FORMAT DOCX (AY2025-26)*
*Thesis title: Predicting Residential Property Values in Metro Cebu Using Machine Learning with GIS-Derived Spatial Features*
*Author: Chris Dominic Estreba | University of Asia and the Pacific*

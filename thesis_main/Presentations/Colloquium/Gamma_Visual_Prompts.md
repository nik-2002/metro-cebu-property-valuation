# Gamma Visual Prompt Pack

## How to Use This in Gamma

Use this as a companion to [Gamma_Deck_Script.md](/Users/nicoestreba/Library/CloudStorage/GoogleDrive-nico.estreba@gmail.com/My%20Drive/UA&P/classes/Data%20Science/16%20Thesis/thesis_main/Presentations/Colloquium/Gamma_Deck_Script.md).

Recommended workflow:

1. Paste the slide outline from [Gamma_Deck_Script.md](/Users/nicoestreba/Library/CloudStorage/GoogleDrive-nico.estreba@gmail.com/My%20Drive/UA&P/classes/Data%20Science/16%20Thesis/thesis_main/Presentations/Colloquium/Gamma_Deck_Script.md) into Gamma as the main deck content.
2. Paste the overall visual direction and the slide-specific prompts below into Gamma's prompt or generation instructions.
3. Upload your local images and tell Gamma exactly which slides should use them.
4. If Gamma turns any prompt text into literal slide content, keep the prompts in the instruction box only and leave the slide script clean.

Recommended local images to upload:

- [MetroCebu.png](/Users/nicoestreba/Library/CloudStorage/GoogleDrive-nico.estreba@gmail.com/My%20Drive/UA&P/classes/Data%20Science/16%20Thesis/thesis_main/Presentations/Colloquium/MetroCebu.png)
- [qgis_fullscreen.png](/Users/nicoestreba/Library/CloudStorage/GoogleDrive-nico.estreba@gmail.com/My%20Drive/UA&P/classes/Data%20Science/16%20Thesis/thesis_main/Presentations/Colloquium/qgis_fullscreen.png)

---

## Overall Visual Direction for Gamma

Create an academic, data-driven presentation for a thesis colloquium. The look should be clean, map-centric, and credible rather than corporate or startup-like. Use a restrained palette based on deep navy, muted teal, slate gray, and off-white. Favor diagrams, map fragments, clean number cards, and structured layouts over stock photos. Avoid generic skyline images, fake dashboards, purple gradients, or overly polished business visuals. When maps are used, make them feel grounded in Metro Cebu and geospatial analysis. When possible, prioritize uploaded project images over generated imagery.

---

## Per-Slide Visual Prompts

### Slide 1

Use a strong academic title slide with a Metro Cebu map or cropped spatial background. Keep the title clear and prominent. Use a subtle grid or contour texture in the background. If possible, use [MetroCebu.png](/Users/nicoestreba/Library/CloudStorage/GoogleDrive-nico.estreba@gmail.com/My%20Drive/UA&P/classes/Data%20Science/16%20Thesis/thesis_main/Presentations/Colloquium/MetroCebu.png) as the main visual.

### Slide 2

Use a clean three-part conceptual layout showing study objective, approved direction, and intended output. Prefer icons for data, model, and map rather than decorative imagery. This should feel like a quick systems overview.

### Slide 3

Use a progress dashboard layout with three to four status cards. Each card should correspond to a major accomplishment area. Use progress labels such as completed, ongoing, or in progress with restrained color accents.

### Slide 4

Use a data-progress slide with strong number cards. Highlight the Pag-IBIG count and the geocoding completion figure. Pair the metrics with a simple flow from floor-price data and listings toward geocoded records.

### Slide 5

Use a split visual showing structured extraction on one side and ABT assembly on the other. The left side should suggest messy BIR source material becoming clean tables, while the right side should show multiple sources merging into one analytic base table.

### Slide 6

Use a full-width or dominant QGIS screenshot with minimal overlay text. Prioritize [qgis_fullscreen.png](/Users/nicoestreba/Library/CloudStorage/GoogleDrive-nico.estreba@gmail.com/My%20Drive/UA&P/classes/Data%20Science/16%20Thesis/thesis_main/Presentations/Colloquium/qgis_fullscreen.png) if possible. The point of this slide is to show visible, tangible progress, so avoid replacing this with a generic generated map.

### Slide 7

Use a four-box refinement layout in a clean 2 by 2 grid. Each box should represent one methodological refinement: floor-price strategy, geocoding and spatial value drivers, Project OHANA accessibility logic, and QGIS decision-support framing. This slide should feel like refinement, not accomplishment metrics.

### Slide 8

Use a structured checklist or grouped task board. Separate the remaining work into data, feature engineering, and modeling. Keep it operational and realistic.

### Slide 9

Use a combined roadmap and timeline layout. Show immediate next steps at the top and a short horizontal timeline beneath them. Make the dates legible and the sequence realistic.

### Slide 10

Use a restrained closing slide with a faint map background or soft QGIS-inspired texture. Keep the final takeaway prominent and leave enough whitespace for a calm ending.

---

## Extra Guardrails for Gamma

- Do not generate fake quantitative charts with made-up values beyond the numbers already stated in the slide script.
- Do not use generic city skyline photos that do not look like Cebu or do not support the thesis topic.
- Prefer maps, diagrams, tables, number cards, and project screenshots over stock photography.
- Keep layouts readable and formal enough for a university colloquium.
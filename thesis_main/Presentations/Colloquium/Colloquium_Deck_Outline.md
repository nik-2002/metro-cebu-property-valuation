# Colloquium Deck Outline

> Thesis: Data-Driven Property Valuation Model for Metro Cebu  
> Format: Progress Report with a short methodology-refinement section  
> Target Length: 10 slides, about 9 to 11 minutes of speaking time

## Core Strategy

This colloquium deck should feel different from the topic proposal deck.

- The proposal deck answered: What is the study and why does it matter?
- The colloquium deck should answer: What has been accomplished since proposal, what became methodologically stronger, and what remains to be completed?

Recommended emphasis:

- `75-80%` progress update
- `20-25%` methodology refinement and work plan

---

## Methodology Refinements Since Proposal

Use these as the exact talking points for a dedicated refinement slide.

### 1. Floor-price strategy became more robust

"Since the proposal, the floor-price component has been strengthened from a mostly single-institution base toward a more diversified institutional dataset, beginning with Pag-IBIG and other verified acquired-asset sources. This reduces source bias and gives the lower-bound market signal broader coverage."

### 2. Location is now operationalized more rigorously

"The study no longer treats location as a simple address field. Through geocoding, distance-based features, and spatial context variables, location is now represented as measurable geospatial value drivers that can enter the model directly."

### 3. Amenity measurement became more defensible through Project OHANA

"The amenity component was refined through Project OHANA and related literature, which introduced a more rigorous accessibility-scoring perspective. Instead of relying only on raw amenity counts, the study can now frame amenity access in terms of distance-weighted accessibility."

### 4. The applied output is now clearer

"The thesis is now framed not only as a predictive pricing model, but as a QGIS-based spatial decision-support tool. This makes the output more practical for brokers and better aligned with the panel's request for a tangible, map-based deliverable."

---

## 10-Slide Deck Flow

### Slide 1 - Title and Thesis Status

- **Purpose:** Open as a progress report, not a re-proposal.
- **Key message:** The thesis has moved from approved concept to active data-building and spatial implementation.
- **Visual:** Clean title slide with a small Metro Cebu map or the QGIS screenshot.
- **Speaker note:** In one sentence, say that this talk focuses on progress since proposal, current methodological refinements, and the remaining work plan.

### Slide 2 - Study Recap and Approved Direction

- **Purpose:** Re-ground the panel quickly and establish the approved baseline.
- **Key message:** The study aims to build a residential property valuation model for Metro Cebu using hybrid pricing data, model comparison, and GIS augmentation.
- **Visual:** One-slide study frame with objective, approved direction, and intended output.
- **Speaker note:** Keep this concise and avoid repeating the full proposal argument.

### Slide 3 - Progress Overview Since Proposal

- **Purpose:** Show the update at a glance.
- **Key message:** The major accomplishments are expanded floor-price collection, geocoding progress, BIR extraction, ABT assembly, and QGIS exploration.
- **Visual:** Three to five progress cards with restrained status labels.
- **Speaker note:** This is the roadmap for the rest of the talk.

### Slide 4 - Data Acquisition and Geocoding Progress

- **Purpose:** Combine the strongest data-preparation accomplishments into one efficient slide.
- **Key message:** The floor-price side has expanded through Pag-IBIG data, and the current listing batches are now overwhelmingly geocoded.
- **Visual:** Number cards plus a short source-to-geocode flow.
- **Speaker note:** Use the concrete counts here and keep the emphasis on readiness for spatial work.

### Slide 5 - BIR Extraction and ABT Build

- **Purpose:** Show administrative-data preparation and current integration work.
- **Key message:** BIR zonal schedules have been structured into machine-readable form, and the current center of work is assembling the analytic base table.
- **Visual:** Before-and-after extraction concept paired with an ABT merge diagram.
- **Speaker note:** Stress that this is the bridge from raw files to the first modeling-ready dataset.

### Slide 6 - QGIS Exploration and Spatial Validation

- **Purpose:** Show visible progress and tangible output.
- **Key message:** Property points and amenity layers are already being explored in QGIS, which supports both spatial validation and the final decision-support output.
- **Visual:** Use [qgis_fullscreen.png](/Users/nicoestreba/Library/CloudStorage/GoogleDrive-nico.estreba@gmail.com/My%20Drive/UA&P/classes/Data%20Science/16%20Thesis/thesis_main/Presentations/Colloquium/qgis_fullscreen.png) or [MetroCebu.png](/Users/nicoestreba/Library/CloudStorage/GoogleDrive-nico.estreba@gmail.com/My%20Drive/UA&P/classes/Data%20Science/16%20Thesis/thesis_main/Presentations/Colloquium/MetroCebu.png).
- **Speaker note:** This is the most tangible accomplishment slide and should visually reassure the panel that the project is moving.

### Slide 7 - Methodology Refinements Since Proposal

- **Purpose:** Show that the thesis improved, not just progressed.
- **Key message:** As implementation advanced, the methodology became more defensible in four ways.
- **Visual:** Four-box layout using the exact refinement points listed above.
- **Speaker note:** Keep this to about one minute. Do not let it become a second proposal defense.

### Slide 8 - Current Remaining Work

- **Purpose:** Show what is still unfinished.
- **Key message:** The remaining major tasks are ABT completion, full feature engineering, model training, and first-pass evaluation.
- **Visual:** Checklist grouped into data, feature engineering, and modeling.
- **Speaker note:** Be direct here. The panel will want to know what is still pending.

### Slide 9 - Immediate Next Steps and Timeline

- **Purpose:** Combine the work plan and timeline into one efficient slide.
- **Key message:** The next phase is ABT completion, feature engineering, model training, and QGIS output refinement on a manageable schedule.
- **Visual:** Short roadmap plus a simple horizontal timeline.
- **Speaker note:** This should communicate control and realism, not overconfidence.

### Slide 10 - Closing and Q&A

- **Purpose:** End with a concise synthesis.
- **Key message:** Since the proposal, the thesis has made real progress in data building and GIS integration, and the next phase is to turn that foundation into the first full valuation results.
- **Visual:** One-sentence takeaway plus `Thank you`.
- **Speaker note:** Close in 20 to 30 seconds.

---

## Suggested Timing

- Slides 1 to 2: `1.5 to 2 minutes`
- Slides 3 to 6: `4.5 to 5.5 minutes`
- Slide 7: `1 minute`
- Slides 8 to 9: `2 to 2.5 minutes`
- Slide 10: `30 seconds`

This keeps the talk within a comfortable 9.5 to 10.5 minute range and leaves buffer for pacing and transitions.

---

## Presenter Reminders

- Do not re-explain the full literature review.
- Do not over-discuss model theory unless asked.
- Lead with concrete accomplishments and visible artifacts.
- Make QGIS and geospatial augmentation feel like the distinct value of the thesis.
- Be candid about what is still ongoing, especially the ABT and modeling stages.
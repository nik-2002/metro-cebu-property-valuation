"""
plot_sensitivity_mcrai.py
=========================
Visualizes the MCRAI composite-weight sensitivity (Decision 56). Recomputes the
named variants and the +/-25% weight perturbation draws (reusing the evaluation
functions in sensitivity_mcrai_weights.py), then renders a two-panel figure:

  (A) Change in typical error (MdAPE) from baseline for each weighting variant,
      for Condominium and Houses, against a shaded "negligible (<1 pp)" band.
  (B) Distribution of typical error under 50 random +/-25% weight perturbations,
      with the deployed-baseline MdAPE marked.

Output: EDA/plots/10_stratified_models/sensitivity_mcrai_weights.png
"""

import os
import json

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from finalize_stratified_groupcv import PROCESSED_DIR, MODELS_DIR, STRATA
from sensitivity_mcrai_weights import (
    composite_from_weights, evaluate, BASELINE, POSITIVE_CATS, ALL_CATS,
    N_PERTURB, PERTURB_PCT, RANDOM_STATE,
)

OUT = os.path.join(os.path.dirname(os.path.dirname(MODELS_DIR)), "EDA", "plots",
                   "10_stratified_models", "sensitivity_mcrai_weights.png")
STRATA_KEYS = ["condo", "houses"]
COLORS = {"condo": "#2c6fbb", "houses": "#c2562a"}

NAMED = {
    "Equal weights\n(3 positive cats)": {c: 1 / 3 for c in POSITIVE_CATS},
    "All 8 categories, equal\n(keep-positives off)": {c: 1 / 8 for c in ALL_CATS},
    "No composite\n(MCRAI removed)": {c: 0.0 for c in POSITIVE_CATS},
}


def main():
    manifest = json.load(open(os.path.join(MODELS_DIR, "deployment_manifest.json")))
    base, deltas, perturb = {}, {key: {} for key in NAMED}, {}

    for key in STRATA_KEYS:
        df0 = pd.read_csv(os.path.join(PROCESSED_DIR, STRATA[key]["csv"])).reset_index(drop=True)
        bp = manifest["strata"][key]["best_params"]

        df = df0.copy(); df["mcrai_composite"] = composite_from_weights(df, BASELINE)
        base[key] = evaluate(df, bp, key)["MdAPE"]

        for name, w in NAMED.items():
            df = df0.copy(); df["mcrai_composite"] = composite_from_weights(df, w)
            deltas[name][key] = evaluate(df, bp, key)["MdAPE"] - base[key]

        rng = np.random.default_rng(RANDOM_STATE)
        vals = []
        for _ in range(N_PERTURB):
            factors = 1 + rng.uniform(-PERTURB_PCT, PERTURB_PCT, size=len(POSITIVE_CATS))
            raw = np.array([BASELINE[c] for c in POSITIVE_CATS]) * factors
            w = dict(zip(POSITIVE_CATS, raw / raw.sum()))
            df = df0.copy(); df["mcrai_composite"] = composite_from_weights(df, w)
            vals.append(evaluate(df, bp, key)["MdAPE"])
        perturb[key] = np.array(vals)
        print(f"{key}: baseline MdAPE={base[key]:.2f}  perturb range "
              f"[{perturb[key].min():.2f}, {perturb[key].max():.2f}]")

    # ---- figure ----
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(12.5, 5.2))

    # Panel A: signed change in MdAPE per variant
    names = list(NAMED.keys())
    y = np.arange(len(names))
    h = 0.36
    axA.axvspan(-1, 1, color="0.88", zorder=0, label="negligible (<1 pp)")
    axA.axvline(0, color="0.4", lw=1)
    for i, key in enumerate(STRATA_KEYS):
        d = [deltas[n][key] for n in names]
        bars = axA.barh(y + (h/2 if i else -h/2), d, height=h,
                        color=COLORS[key], label=f"{STRATA[key]['label']} (base {base[key]:.1f}%)")
        for b, v in zip(bars, d):
            axA.text(v + (0.03 if v >= 0 else -0.03), b.get_y() + b.get_height()/2,
                     f"{v:+.2f}", va="center", ha="left" if v >= 0 else "right", fontsize=9)
    axA.set_yticks(y); axA.set_yticklabels(names, fontsize=10)
    axA.set_xlim(-1.5, 1.5)
    axA.set_xlabel("Change in typical error (MdAPE) from deployed baseline, pp", fontsize=10)
    axA.set_title("Re-weighting barely changes accuracy", fontsize=12)
    axA.legend(fontsize=9, loc="lower right")
    axA.invert_yaxis()

    # Panel B: perturbation distribution
    for key in STRATA_KEYS:
        axB.hist(perturb[key], bins=12, alpha=0.55, color=COLORS[key],
                 label=f"{STRATA[key]['label']}")
        axB.axvline(base[key], color=COLORS[key], lw=2, ls="--")
    axB.set_xlabel("Typical error (MdAPE, %) under 50 random ±25% weight perturbations", fontsize=10)
    axB.set_ylabel("Count of draws", fontsize=10)
    axB.set_title("Random weight noise: error stays put\n(dashed = deployed baseline)", fontsize=12)
    axB.legend(fontsize=9)

    fig.suptitle("Sensitivity of the deployed models to the MCRAI composite weighting",
                 fontsize=13, fontweight="bold")
    fig.text(0.5, 0.015,
             "Vacant-lot model omitted: it uses the individual MCRAI categories, not the "
             "composite, so it is unaffected by these weights by construction.",
             ha="center", fontsize=8.5, style="italic", color="0.35")
    fig.tight_layout(rect=[0, 0.045, 1, 0.95])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.savefig(OUT, dpi=150, bbox_inches="tight")
    print(f"Saved -> {OUT}")


if __name__ == "__main__":
    main()

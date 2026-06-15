"""Re-render the 8 hyperparameter elbow plots from cached hpo_sweeps.csv (no recompute).
Fixes the title glyph and keeps the project plot style."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

THESIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SW = pd.read_csv(os.path.join(THESIS, "EDA", "tables", "hpo_sweeps.csv"))
OUT = os.path.join(THESIS, "EDA", "plots", "11_hyperparameter_tuning")
COLORS = {"Condominium": "#3b6fb6", "Houses": "#4f9d5d", "Vacant Lot": "#c89a2b"}
PREFIX = {"Random Forest": "rf", "XGBoost": "xgb"}
DEP = {
    "Random Forest": {
        "Condominium": {"n_estimators": "400", "max_depth": "None", "max_features": "0.9", "min_samples_leaf": "2"},
        "Houses": {"n_estimators": "300", "max_depth": "20", "max_features": "1.0", "min_samples_leaf": "2"},
        "Vacant Lot": {"n_estimators": "400", "max_depth": "None", "max_features": "1.0", "min_samples_leaf": "1"},
    },
    "XGBoost": {
        "Condominium": {"n_estimators": "300", "max_depth": "3", "learning_rate": "0.05", "subsample": "0.9"},
        "Houses": {"n_estimators": "500", "max_depth": "3", "learning_rate": "0.05", "subsample": "0.9"},
        "Vacant Lot": {"n_estimators": "300", "max_depth": "5", "learning_rate": "0.05", "subsample": "0.9"},
    },
}

plt.style.use("seaborn-v0_8-whitegrid")
for (model, param), g in SW.groupby(["model", "param"], sort=False):
    values = list(dict.fromkeys(g["value"]))  # preserve order
    fig, ax = plt.subplots(figsize=(7, 4.2))
    for strat in ["Condominium", "Houses", "Vacant Lot"]:
        sub = g[g["stratum"] == strat].set_index("value").reindex(values)
        ys = sub["MdAPE"].tolist()
        xs = list(range(len(values)))
        ax.plot(xs, ys, marker="o", ms=5, lw=1.8, color=COLORS[strat], label=strat)
        dv = DEP[model][strat].get(param)
        if dv in values:
            i = values.index(dv)
            ax.scatter([i], [ys[i]], s=160, marker="*", color=COLORS[strat],
                       edgecolor="black", linewidth=0.6, zorder=5)
    ax.set_xticks(range(len(values)))
    ax.set_xticklabels([str(v) for v in values])
    ax.set_xlabel(param)
    ax.set_ylabel("MdAPE (%)  — lower is better")
    ax.set_title(f"{model}: MdAPE vs {param}   (deployed = starred point; other params at best)", fontsize=11)
    ax.legend(frameon=False, fontsize=9)
    sns.despine(ax=ax)
    fig.tight_layout()
    out = os.path.join(OUT, f"{PREFIX[model]}_{param}.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print("re-rendered", out)

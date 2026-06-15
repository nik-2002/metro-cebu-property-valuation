"""
investigate_mcrai_lot_2026-06-15.py
===================================
EDA on the 8 individual MCRAI features for the VACANT LOT stratum, to decide which
categories earn their place and whether `security` (and any others) should be dropped.

Context: the lot model currently carries all 8 individual MCRAI + mcrai_composite.
The composite is an EXACT linear blend of education/grocery/recreation (compute_hansen_scores.py)
-> perfect collinearity with those individuals -> drop composite from lot (decided).
This script then asks, of the 8 individuals: zero-rates, mutual collinearity (VIF), OLS sign +
significance (HC3) against log(price_per_sqm), and RF importance. Read-only.
"""
import os, sys, warnings
import numpy as np, pandas as pd
import statsmodels.api as sm
from sklearn.ensemble import RandomForestRegressor
warnings.filterwarnings("ignore")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
THESIS_DIR = os.path.dirname(SCRIPT_DIR)
PROCESSED = os.path.join(THESIS_DIR, "Data", "processed")

MCRAI = ["mcrai_education","mcrai_grocery","mcrai_health","mcrai_hospitals",
         "mcrai_recreation","mcrai_security","mcrai_tourism","mcrai_retail_density"]

df = pd.read_csv(os.path.join(PROCESSED, "abt_lot.csv"))
y = np.log(df["price_per_sqm"].astype(float))
X = df[MCRAI].fillna(0.0).astype(float)
n = len(df)
print(f"VACANT LOT stratum — n={n}\n")

# 1. Zero-rate overall + by LGU
print("=== 1. ZERO-RATE (share of lots with score == 0) ===")
zr = (X == 0).mean().sort_values(ascending=False)
for c, v in zr.items():
    print(f"  {c:24s} {v*100:5.1f}%  zero")
print("\n  Zero-rate by LGU (security, tourism — the suspect ones):")
for c in ["mcrai_security","mcrai_tourism","mcrai_hospitals"]:
    by = df.assign(z=(X[c]==0)).groupby("city")["z"].mean()*100
    print(f"  {c}: " + ", ".join(f"{k}={v:.0f}%" for k,v in by.items()))

# 2. Correlation among the 8
print("\n=== 2. CORRELATION MATRIX (Pearson) among the 8 individuals ===")
corr = X.corr()
print(corr.round(2).to_string())

# 3. VIF among the 8 (composite excluded)
print("\n=== 3. VIF among the 8 individuals (composite NOT included) ===")
from sklearn.linear_model import LinearRegression
for c in MCRAI:
    others = [x for x in MCRAI if x != c]
    r2 = LinearRegression().fit(X[others], X[c]).score(X[others], X[c])
    vif = 1/(1-r2) if r2 < 1 else float("inf")
    print(f"  {c:24s} VIF = {vif:7.2f}")

# 4. OLS sign + significance (standardized X, HC3 robust SE)
print("\n=== 4. OLS: log(price_per_sqm) ~ 8 MCRAI (standardized), HC3 robust SE ===")
Xz = (X - X.mean()) / X.std(ddof=0)
Xc = sm.add_constant(Xz)
res = sm.OLS(y, Xc).fit(cov_type="HC3")
tab = pd.DataFrame({"coef": res.params, "p": res.pvalues}).drop("const")
tab["sig"] = tab["p"].apply(lambda p: "***" if p<0.01 else "**" if p<0.05 else "*" if p<0.10 else "")
tab["sign"] = np.where(tab["coef"]>0, "+", "-")
print(tab.round(4).to_string())
print(f"  (model R^2 = {res.rsquared:.3f})")

# 5. RF importance for the 8 within a lot RF (deployed-ish: 8 MCRAI + CBD + area + BIR + lag)
print("\n=== 5. RF importance (lot model, MCRAI share of total) ===")
extra = [c for c in ["area_sqm","dist_cebu_business_park_m","dist_mandaue_cbd_m","dist_mactan_cbd_m",
         "dist_srp_m","dist_talisay_tabunok_m","dist_consolacion_m","dist_naga_city_m","dist_airport_m",
         "bir_zonal_rr_median","spatial_lag_price"] if c in df.columns]
Xrf = pd.concat([X, df[extra].fillna(df[extra].median())], axis=1)
rf = RandomForestRegressor(n_estimators=300, max_features=1.0, min_samples_leaf=1,
                           max_depth=20, random_state=42, n_jobs=-1).fit(Xrf, y)
imp = pd.Series(rf.feature_importances_, index=Xrf.columns).sort_values(ascending=False)
mcrai_imp = imp[MCRAI].sort_values(ascending=False)
print(f"  MCRAI block = {imp[MCRAI].sum()*100:.1f}% of total RF importance")
for c, v in mcrai_imp.items():
    print(f"    {c:24s} {v*100:5.2f}%")

# 6. Univariate corr with target
print("\n=== 6. Pearson corr of each MCRAI with log(price_per_sqm) ===")
for c in MCRAI:
    print(f"  {c:24s} r = {np.corrcoef(X[c], y)[0,1]:+.3f}")

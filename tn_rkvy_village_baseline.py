import pandas as pd
import numpy as np

src = "tn_rkvy_village_records.csv"
out = "tn_rkvy_village_baseline.csv"

df = pd.read_csv(src)

def pct(a, total):
    return np.where(total > 0, (a / total) * 100, np.nan)

# Nutrients with Low / Medium / High classifications
for n in ["n", "p", "k", "OC"]:
    low = pd.to_numeric(df.get(f"{n}_Low", 0), errors="coerce").fillna(0)
    med = pd.to_numeric(df.get(f"{n}_Medium", 0), errors="coerce").fillna(0)
    high = pd.to_numeric(df.get(f"{n}_High", 0), errors="coerce").fillna(0)
    total = low + med + high

    df[f"{n}_sample_count"] = total
    df[f"{n}_low_pct"] = pct(low, total)
    df[f"{n}_medium_pct"] = pct(med, total)
    df[f"{n}_high_pct"] = pct(high, total)

# Sulfur / micronutrients: sufficient vs deficient
for n in ["S", "Fe", "Zn", "Cu", "B", "Mn"]:
    suff = pd.to_numeric(df.get(f"{n}_Sufficient", 0), errors="coerce").fillna(0)
    deficiency = pd.to_numeric(df.get(f"{n}_Deficient", 0), errors="coerce").fillna(0)
    total = suff + deficiency

    df[f"{n}_sample_count"] = total
    df[f"{n}_sufficient_pct"] = pct(suff, total)
    df[f"{n}_deficient_pct"] = pct(deficiency, total)

# pH: Acidic / Neutral / Alkaline
acid = pd.to_numeric(df.get("pH_Acidic", 0), errors="coerce").fillna(0)
neutral = pd.to_numeric(df.get("pH_Neutral", 0), errors="coerce").fillna(0)
alk = pd.to_numeric(df.get("pH_Alkaline", 0), errors="coerce").fillna(0)
total = acid + neutral + alk

df["pH_sample_count"] = total
df["pH_acidic_pct"] = pct(acid, total)
df["pH_neutral_pct"] = pct(neutral, total)
df["pH_alkaline_pct"] = pct(alk, total)

# EC: Saline / Non-saline
saline = pd.to_numeric(df.get("EC_Saline", 0), errors="coerce").fillna(0)
nonsaline = pd.to_numeric(df.get("EC_NonSaline", 0), errors="coerce").fillna(0)
total = saline + nonsaline

df["EC_sample_count"] = total
df["EC_saline_pct"] = pct(saline, total)
df["EC_nonsaline_pct"] = pct(nonsaline, total)

# One common soil-sample count for the village.
# Most parameters should share the same underlying sample count,
# but we use the maximum available count rather than assuming.
count_cols = [
    "n_sample_count", "p_sample_count", "k_sample_count",
    "OC_sample_count", "S_sample_count", "pH_sample_count",
    "EC_sample_count", "Fe_sample_count", "Zn_sample_count",
    "Cu_sample_count", "B_sample_count", "Mn_sample_count"
]

df["village_total_samples"] = df[count_cols].max(axis=1)

# Dominant category for quick ML / analytics features
def dominant(cols):
    values = df[cols].fillna(0)
    return values.idxmax(axis=1).str.replace("_pct", "", regex=False)

df["N_dominant"] = dominant(["n_low_pct", "n_medium_pct", "n_high_pct"])
df["P_dominant"] = dominant(["p_low_pct", "p_medium_pct", "p_high_pct"])
df["K_dominant"] = dominant(["k_low_pct", "k_medium_pct", "k_high_pct"])
df["OC_dominant"] = dominant(["OC_low_pct", "OC_medium_pct", "OC_high_pct"])
df["pH_dominant"] = dominant(["pH_acidic_pct", "pH_neutral_pct", "pH_alkaline_pct"])

# Simple data-quality flag
df["data_quality"] = np.where(
    df["village_total_samples"] >= 5,
    "GOOD",
    np.where(df["village_total_samples"] >= 2, "LIMITED", "VERY_LIMITED")
)

df.to_csv(out, index=False)

print("======================================")
print("VILLAGE BASELINE CREATED")
print("======================================")
print("Input rows :", len(df))
print("Output file:", out)
print("Columns    :", len(df.columns))
print("Villages   :", df["village"].nunique())
print("Blocks     :", df["block"].nunique())
print("Districts  :", df["district"].nunique())
print()
print("Data quality:")
print(df["data_quality"].value_counts().to_string())
print()
print("Example columns:")
print([
    "village",
    "district",
    "block",
    "village_total_samples",
    "n_low_pct",
    "n_medium_pct",
    "n_high_pct",
    "p_low_pct",
    "k_low_pct",
    "S_deficient_pct",
    "Fe_deficient_pct",
    "Zn_deficient_pct",
    "pH_neutral_pct",
    "EC_saline_pct"
])

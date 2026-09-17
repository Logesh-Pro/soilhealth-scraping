import pandas as pd
import numpy as np

src = "tn_rkvy_village_baseline.csv"
out = "tn_rkvy_village_ml_ready.csv"

df = pd.read_csv(src)

# Parameter groups
ordered_params = ["N","P","K","OC","S","pH","EC","Fe","Zn","Cu","B","Mn"]

count_map = {
    "N": "n_sample_count",
    "P": "p_sample_count",
    "K": "k_sample_count",
    "OC": "OC_sample_count",
    "S": "S_sample_count",
    "pH": "pH_sample_count",
    "EC": "EC_sample_count",
    "Fe": "Fe_sample_count",
    "Zn": "Zn_sample_count",
    "Cu": "Cu_sample_count",
    "B": "B_sample_count",
    "Mn": "Mn_sample_count"
}

# Actual maximum sample population observed in the village.
df["max_observed_samples"] = df[
    list(count_map.values())
].max(axis=1)

# Minimum parameter coverage.
df["min_observed_samples"] = df[
    list(count_map.values())
].min(axis=1)

# Number of parameters having full coverage.
full_count = pd.Series(0, index=df.index)

for p in ordered_params:
    c = count_map[p]

    df[f"{p}_coverage_pct"] = np.where(
        df["max_observed_samples"] > 0,
        (df[c] / df["max_observed_samples"]) * 100,
        np.nan
    )

    df[f"{p}_complete"] = (
        df[c] == df["max_observed_samples"]
    )

    full_count += df[f"{p}_complete"].astype(int)

df["parameters_complete"] = full_count
df["parameter_completeness_pct"] = (
    df["parameters_complete"] / len(ordered_params) * 100
)

# Overall classification
df["coverage_class"] = np.select(
    [
        df["parameter_completeness_pct"] == 100,
        df["parameter_completeness_pct"] >= 90,
        df["parameter_completeness_pct"] >= 75
    ],
    [
        "COMPLETE",
        "MINOR_MISSING",
        "PARTIAL"
    ],
    default="LOW_COVERAGE"
)

# Parameter-specific deficiency / category percentages
# N / P / K / OC
for p in ["N","P","K","OC"]:
    prefix = p.lower() if p != "OC" else "OC"

    low = pd.to_numeric(
        df.get(f"{prefix}_Low", 0),
        errors="coerce"
    ).fillna(0)

    med = pd.to_numeric(
        df.get(f"{prefix}_Medium", 0),
        errors="coerce"
    ).fillna(0)

    high = pd.to_numeric(
        df.get(f"{prefix}_High", 0),
        errors="coerce"
    ).fillna(0)

    total = low + med + high

    df[f"{p}_low_pct"] = np.where(total > 0, low / total * 100, np.nan)
    df[f"{p}_medium_pct"] = np.where(total > 0, med / total * 100, np.nan)
    df[f"{p}_high_pct"] = np.where(total > 0, high / total * 100, np.nan)

# S / Fe / Zn / Cu / B / Mn
for p in ["S","Fe","Zn","Cu","B","Mn"]:
    suff = pd.to_numeric(
        df.get(f"{p}_Sufficient", 0),
        errors="coerce"
    ).fillna(0)

    deficient = pd.to_numeric(
        df.get(f"{p}_Deficient", 0),
        errors="coerce"
    ).fillna(0)

    total = suff + deficient

    df[f"{p}_sufficient_pct"] = np.where(
        total > 0,
        suff / total * 100,
        np.nan
    )

    df[f"{p}_deficient_pct"] = np.where(
        total > 0,
        deficient / total * 100,
        np.nan
    )

# pH
acid = pd.to_numeric(
    df.get("pH_Acidic", 0),
    errors="coerce"
).fillna(0)

neutral = pd.to_numeric(
    df.get("pH_Neutral", 0),
    errors="coerce"
).fillna(0)

alk = pd.to_numeric(
    df.get("pH_Alkaline", 0),
    errors="coerce"
).fillna(0)

total = acid + neutral + alk

df["pH_acidic_pct"] = np.where(total > 0, acid / total * 100, np.nan)
df["pH_neutral_pct"] = np.where(total > 0, neutral / total * 100, np.nan)
df["pH_alkaline_pct"] = np.where(total > 0, alk / total * 100, np.nan)

# EC
saline = pd.to_numeric(
    df.get("EC_Saline", 0),
    errors="coerce"
).fillna(0)

nonsaline = pd.to_numeric(
    df.get("EC_NonSaline", 0),
    errors="coerce"
).fillna(0)

total = saline + nonsaline

df["EC_saline_pct"] = np.where(
    total > 0,
    saline / total * 100,
    np.nan
)

df["EC_nonsaline_pct"] = np.where(
    total > 0,
    nonsaline / total * 100,
    np.nan
)

df.to_csv(out, index=False)

print("======================================")
print("ML-READY VILLAGE DATASET")
print("======================================")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print()

print("Coverage class:")
print(df["coverage_class"].value_counts().to_string())
print()

print("Parameter completeness:")
print(
    df["parameter_completeness_pct"]
    .describe()
    .to_string()
)
print()

print("Villages with complete parameter coverage:",
      int((df["coverage_class"] == "COMPLETE").sum()))

print("Villages with any missing parameter coverage:",
      int((df["coverage_class"] != "COMPLETE").sum()))

print()
print("Most incomplete villages:")
print(
    df[
        [
            "district",
            "block",
            "village",
            "max_observed_samples",
            "min_observed_samples",
            "parameters_complete",
            "parameter_completeness_pct",
            "coverage_class"
        ]
    ]
    .sort_values("parameter_completeness_pct")
    .head(15)
    .to_string(index=False)
)

print()
print("OUTPUT:", out)

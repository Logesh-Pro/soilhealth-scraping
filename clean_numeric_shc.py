import pandas as pd

df = pd.read_csv("numeric_shc_master.csv")

# Remove accidental Test ID leakage from address.
df["address"] = (
    df["address"]
    .astype(str)
    .str.replace(
        r"\s+Test ID\s*:\s*SHC\d{4}-\d+-\d+-[A-Za-z0-9_-]+$",
        "",
        regex=True
    )
    .str.strip()
)

# Keep only the useful numeric + metadata fields.
columns = [
    "test_id",
    "sample_date",
    "testing_date",
    "plot_area_hectare",
    "soil_type",
    "address",
    "gps_lat",
    "gps_lon",
    "N_kg_ha",
    "P_kg_ha",
    "K_kg_ha",
    "OC_percent",
    "pH",
    "EC_dS_m",
    "S_ppm",
    "Fe_ppm",
    "Zn_ppm",
    "Cu_ppm",
    "B_ppm",
    "Mn_ppm",
    "parameters_found",
    "complete_numeric_record"
]

columns = [c for c in columns if c in df.columns]

df = df[columns]

df.to_csv(
    "numeric_shc_clean.csv",
    index=False
)

print("=" * 60)
print("CLEAN NUMERIC SHC DATASET")
print("=" * 60)
print("Rows:", len(df))
print("Columns:", len(df.columns))
print()

print(df.to_string(index=False))
print()
print("Saved: numeric_shc_clean.csv")

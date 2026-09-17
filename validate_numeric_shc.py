import pandas as pd

df = pd.read_csv("numeric_shc_clean.csv")

required = [
    "test_id",
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
    "Mn_ppm"
]

print("=" * 70)
print("NUMERIC SHC VALIDATION")
print("=" * 70)

print("Records:", len(df))
print()

missing_columns = [c for c in required if c not in df.columns]

if missing_columns:
    print("MISSING COLUMNS:")
    for c in missing_columns:
        print(" -", c)
else:
    print("Required columns: OK")

print()

for _, r in df.iterrows():
    missing_values = [
        c for c in required
        if pd.isna(r.get(c))
    ]

    print("Test ID:", r["test_id"])
    print("State/location:", r.get("address", ""))
    print("Complete:", len(missing_values) == 0)
    print("Missing:", missing_values if missing_values else "None")
    print()

print("STATE / LOCATION CHECK")
print("-" * 70)

for _, r in df.iterrows():
    address = str(r.get("address", ""))
    print(address)

print()
print("=" * 70)
print("VALIDATION COMPLETE")
print("=" * 70)

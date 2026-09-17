import os
import re
import csv
import glob
import html

INPUT_DIR = "reports"
OUTPUT = "numeric_shc_master.csv"

files = glob.glob(os.path.join(INPUT_DIR, "*.html"))

if os.path.exists("sample_soil_health_report.html"):
    files.append("sample_soil_health_report.html")

numeric_patterns = {
    "N_kg_ha": r"Available Nitrogen\s*\(N\)\s*([\d.]+)\s*kg/ha",
    "P_kg_ha": r"Available Phosphorus\s*\(P\)\s*([\d.]+)\s*kg/ha",
    "K_kg_ha": r"Available Potassium\s*\(K\)\s*([\d.]+)\s*kg/ha",
    "pH": r"pH\s*\(pH\)\s*([\d.]+)",
    "EC_dS_m": r"EC\s*\(EC\)\s*([\d.]+)\s*dS/m",
    "OC_percent": r"Organic Carbon\s*\(OC\)\s*([\d.]+)\s*w%",
    "S_ppm": r"Available Sulphur\s*\(S\)\s*([\d.]+)\s*ppm",
    "Zn_ppm": r"Available Zinc\s*\(Zn\)\s*([\d.]+)\s*ppm",
    "B_ppm": r"Available Boron\s*\(B\)\s*([\d.]+)\s*ppm",
    "Fe_ppm": r"Available Iron\s*\(Fe\)\s*([\d.]+)\s*ppm",
    "Mn_ppm": r"Available Manganese\s*\(Mn\)\s*([\d.]+)\s*ppm",
    "Cu_ppm": r"Available Copper\s*\(Cu\)\s*([\d.]+)\s*ppm",
}

meta_patterns = {
    "test_id": r"\b(SHC\d{4}-\d+-\d+-[A-Za-z0-9_-]+)\b",
    "sample_date": r"Sampling Date\s*:\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})",
    "testing_date": r"Testing Date\s*:\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})",
    "plot_area_hectare": r"Plot Size Area\s*:\s*([\d.]+)\s*Hectare",
    "soil_type": r"Soil Type\s*:\s*(.*?)(?:\s+Soil Sample Details|\s+Available Nitrogen)",
    "gps_lat": r"geo position\(GPS\)\s*:\s*([-\d.]+)\s*,",
    "gps_lon": r"geo position\(GPS\)\s*:\s*[-\d.]+\s*,\s*([-\d.]+)",
    "state": r"Address\s*:\s*(?:.*?,\s*)+([^,]+)\s*$",
}

rows = []

for path in files:
    raw = open(path, encoding="utf-8").read()
    raw = html.unescape(raw)

    text = re.sub(r"<script.*?</script>", " ", raw, flags=re.I | re.S)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    row = {
        "source_file": os.path.basename(path)
    }

    for name, pattern in meta_patterns.items():
        m = re.search(pattern, text, re.I)
        row[name] = m.group(1).strip() if m else ""

    # Extract address separately so we can inspect its components.
    address_match = re.search(
        r"Address\s*:\s*(.*?)\s+Testing Date\s*:",
        text,
        re.I
    )

    row["address"] = (
        address_match.group(1).strip()
        if address_match else ""
    )

    # Extract numeric measurements.
    for name, pattern in numeric_patterns.items():
        m = re.search(pattern, text, re.I)
        row[name] = float(m.group(1)) if m else None

    # Calculate completeness.
    row["parameters_found"] = sum(
        row[k] is not None
        for k in numeric_patterns
    )

    row["parameters_expected"] = len(numeric_patterns)

    row["complete_numeric_record"] = (
        row["parameters_found"] == row["parameters_expected"]
    )

    rows.append(row)

fields = list(rows[0].keys())

with open(
    OUTPUT,
    "w",
    newline="",
    encoding="utf-8"
) as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print("=" * 70)
print("ENRICHED NUMERIC SHC DATASET")
print("=" * 70)
print("Reports:", len(rows))
print("Output :", OUTPUT)
print()

for r in rows:
    print("Test ID :", r["test_id"])
    print("Sample  :", r["sample_date"])
    print("Testing :", r["testing_date"])
    print("GPS     :", r["gps_lat"], r["gps_lon"])
    print("Address :", r["address"])
    print("Soil    :", r["soil_type"])
    print("Values  :", r["parameters_found"], "/", r["parameters_expected"])

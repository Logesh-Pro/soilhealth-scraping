import re
import csv

html = open("sample_soil_health_report.html", encoding="utf-8").read()

text = re.sub(r"<script.*?</script>", " ", html, flags=re.I | re.S)
text = re.sub(r"<style.*?</style>", " ", text, flags=re.I | re.S)
text = re.sub(r"<[^>]+>", " ", text)
text = re.sub(r"\s+", " ", text).strip()

patterns = {
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

result = {}

for name, pattern in patterns.items():
    m = re.search(pattern, text, re.I)
    result[name] = float(m.group(1)) if m else None

print("NUMERIC SOIL MEASUREMENTS")
print("=" * 50)

for k, v in result.items():
    print(f"{k:15} = {v}")

with open("numeric_soil_measurements.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=result.keys())
    writer.writeheader()
    writer.writerow(result)

print()
print("Saved: numeric_soil_measurements.csv")

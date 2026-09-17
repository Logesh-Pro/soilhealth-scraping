import re

s = open("site_bundle.js", encoding="utf-8").read()

terms = [
    "nitrogen",
    "phosphorus",
    "potassium",
    "organicCarbon",
    "organic_carbon",
    "electricalConductivity",
    "conductivity",
    "sampleValue",
    "sample_value",
    "soilTest",
    "soil_test",
    "nutrientValue",
    "nutrient_value"
]

print("SEARCHING BUNDLE...")
print()

for term in terms:
    matches = list(re.finditer(term, s, re.I))

    if not matches:
        continue

    print("=" * 70)
    print(term, "FOUND:", len(matches))
    print("=" * 70)

    for m in matches[:3]:
        start = max(0, m.start() - 350)
        end = min(len(s), m.end() + 700)

        snippet = s[start:end].replace("\n", " ")
        print(snippet)
        print()

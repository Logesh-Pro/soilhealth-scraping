import re
import html
import requests

API = "https://soilhealth4.dac.gov.in/"

QUERY = """
query GetTestForPortal($locale: String, $computedId: String) {
  getTestForPortal(computedID: $computedId) {
    html(locale: $locale)
  }
}
"""

HEADERS = {
    "Content-Type": "application/json",
    "x-client-type": "portal",
    "Origin": "https://soilhealth.dac.gov.in",
    "Referer": "https://soilhealth.dac.gov.in/school",
    "User-Agent": "Mozilla/5.0"
}

computed_id = input("Enter a legitimate Soil Health Card Test ID: ").strip()

if not computed_id:
    raise SystemExit("No Test ID supplied.")

variables = {
    "computedId": computed_id,
    "locale": "en"
}

r = requests.post(
    API,
    json={
        "operationName": "GetTestForPortal",
        "variables": variables,
        "query": QUERY
    },
    headers=HEADERS,
    timeout=60
)

print()
print("HTTP STATUS:", r.status_code)

data = r.json()

if data.get("errors"):
    print("GRAPHQL ERRORS:")
    print(data["errors"])
    raise SystemExit

records = (
    data.get("data", {})
        .get("getTestForPortal", [])
)

print("REPORT RECORDS:", len(records))

if not records:
    raise SystemExit("No report returned for this Test ID.")

report = records[0].get("html")

if not report:
    raise SystemExit("Report HTML is empty.")

report = html.unescape(report)

with open("sample_soil_health_report.html", "w", encoding="utf-8") as f:
    f.write(report)

# Strip HTML for easier inspection
text = re.sub(r"<script.*?</script>", " ", report, flags=re.I | re.S)
text = re.sub(r"<style.*?</style>", " ", text, flags=re.I | re.S)
text = re.sub(r"<[^>]+>", " ", text)
text = re.sub(r"\s+", " ", text).strip()

print()
print("REPORT HTML LENGTH:", len(report))
print("TEXT LENGTH:", len(text))
print()

keywords = [
    "Nitrogen",
    "Phosphorus",
    "Potassium",
    "Organic Carbon",
    "Organic Matter",
    "pH",
    "Electrical Conductivity",
    "Sulfur",
    "Iron",
    "Zinc",
    "Copper",
    "Boron",
    "Manganese",
    "kg/ha",
    "mg/kg"
]

print("SOIL VALUE REFERENCES FOUND:")
print("=" * 70)

lower = text.lower()

for keyword in keywords:
    pos = lower.find(keyword.lower())

    if pos >= 0:
        start = max(0, pos - 150)
        end = min(len(text), pos + 500)
        print()
        print(keyword + ":")
        print(text[start:end])

print()
print("=" * 70)
print("Saved: sample_soil_health_report.html")

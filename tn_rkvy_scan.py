import json
import time
import csv
import requests

API = "https://soilhealth4.dac.gov.in/"
STATE_ID = "63f9be9f519359b7438d08bb"
CYCLE = "2026-27"
SCHEME_ID = "660f941a5c8405ca8375c7c6"
SCHEME_NAME = "Soil Health Card RKVY"

d = chr(36)

QUERY = """
query GetNutrientDashboardForPortal(
  $state: ID,
  $district: ID,
  $block: ID,
  $village: ID,
  $cycle: String,
  $count: Boolean,
  $scheme: String
) {
  getNutrientDashboardForPortal(
    state: $state
    district: $district
    block: $block
    village: $village
    cycle: $cycle
    count: $count
    scheme: $scheme
  )
}
"""

HEADERS = {
    "Content-Type": "application/json",
    "x-client-type": "portal",
    "Origin": "https://soilhealth.dac.gov.in",
    "Referer": "https://soilhealth.dac.gov.in/school",
    "User-Agent": "Mozilla/5.0"
}

with open("tn_districts.json", encoding="utf-8") as f:
    districts = json.load(f)["data"]["getdistrictAndSubdistrictBystate"]

session = requests.Session()
session.headers.update(HEADERS)

rows = []

print(f"Scanning {len(districts)} Tamil Nadu districts...")
print(f"Scheme: {SCHEME_NAME}")
print(f"Cycle: {CYCLE}")
print()

for i, district in enumerate(districts, 1):
    district_id = district["_id"]
    district_name = district["name"]

    variables = {
        "state": STATE_ID,
        "district": district_id,
        "cycle": CYCLE,
        "count": False,
        "scheme": SCHEME_ID
    }

    try:
        r = session.post(
            API,
            json={
                "operationName": "GetNutrientDashboardForPortal",
                "variables": variables,
                "query": QUERY
            },
            timeout=60
        )

        if r.status_code != 200:
            print(f"[{i}/{len(districts)}] {district_name}: HTTP {r.status_code}")
            continue

        payload = r.json()
        results = payload.get("data", {}).get("getNutrientDashboardForPortal") or []

        if results:
            for item in results:
                row = {
                    "district": district_name,
                    "district_id": district_id,
                    "scheme": SCHEME_NAME,
                    "scheme_id": SCHEME_ID,
                    "cycle": CYCLE,
                    "record_id": item.get("_id"),
                }

                for nutrient, values in (item.get("results") or {}).items():
                    for level, value in values.items():
                        row[f"{nutrient}_{level}"] = value

                rows.append(row)

            print(f"[{i}/{len(districts)}] {district_name}: FOUND {len(results)} record(s)")
        else:
            print(f"[{i}/{len(districts)}] {district_name}: no data")

    except Exception as e:
        print(f"[{i}/{len(districts)}] {district_name}: ERROR {e}")

    time.sleep(0.35)

with open("tn_rkvy_district_nutrients.csv", "w", newline="", encoding="utf-8") as f:
    if rows:
        fields = sorted({k for row in rows for k in row.keys()})
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

with open("tn_rkvy_district_nutrients.json", "w", encoding="utf-8") as f:
    json.dump(rows, f, indent=2, ensure_ascii=False)

print()
print("======================================")
print("SCAN COMPLETE")
print("Non-empty district records:", len(rows))
print("CSV:", "tn_rkvy_district_nutrients.csv")
print("JSON:", "tn_rkvy_district_nutrients.json")
print("======================================")

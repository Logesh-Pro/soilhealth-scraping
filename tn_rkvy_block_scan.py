import json
import time
import csv
import requests

API = "https://soilhealth4.dac.gov.in/"
STATE_ID = "63f9be9f519359b7438d08bb"
CYCLE = "2026-27"
SCHEME_ID = "660f941a5c8405ca8375c7c6"
SCHEME_NAME = "Soil Health Card RKVY"

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

all_records = []
seen_ids = set()

print(f"Scanning {len(districts)} Tamil Nadu districts for block-level records...")
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
            print(f"[{i}/38] {district_name}: HTTP {r.status_code}")
            continue

        payload = r.json()
        records = payload.get("data", {}).get(
            "getNutrientDashboardForPortal"
        ) or []

        found = 0

        for rec in records:
            record_id = rec.get("_id")

            if record_id in seen_ids:
                continue

            seen_ids.add(record_id)

            block = rec.get("block") or {}
            village = rec.get("village") or {}
            state = rec.get("state") or {}
            district_obj = rec.get("district") or {}

            row = {
                "record_id": record_id,
                "state": state.get("name", "TAMIL NADU"),
                "state_id": state.get("_id", STATE_ID),
                "district": district_obj.get("name", district_name),
                "district_id": district_obj.get("_id", district_id),

                "block": block.get("name"),
                "block_id": block.get("_id"),
                "block_code": block.get("code"),

                "village": village.get("name"),
                "village_id": village.get("_id"),
                "village_code": village.get("code"),

                "scheme": SCHEME_NAME,
                "scheme_id": rec.get("scheme", SCHEME_ID),
                "cycle": rec.get("cycle", CYCLE),

                "createdAt": rec.get("createdAt"),
                "lastProcessedAt": rec.get("lastProcessedAt"),
                "updatedAt": rec.get("updatedAt"),
            }

            for nutrient, values in (rec.get("results") or {}).items():
                for level, value in (values or {}).items():
                    row[f"{nutrient}_{level}"] = value

            all_records.append(row)
            found += 1

        print(
            f"[{i}/38] {district_name}: "
            f"{found} record(s)"
        )

    except Exception as e:
        print(f"[{i}/38] {district_name}: ERROR {e}")

    time.sleep(0.35)

# Save complete raw records
with open(
    "tn_rkvy_block_records.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(all_records, f, indent=2, ensure_ascii=False)

# Save CSV
if all_records:
    fields = sorted({
        key
        for row in all_records
        for key in row.keys()
    })

    with open(
        "tn_rkvy_block_records.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(all_records)

# Statistics
block_ids = {
    r["block_id"]
    for r in all_records
    if r.get("block_id")
}

village_ids = {
    r["village_id"]
    for r in all_records
    if r.get("village_id")
}

district_ids = {
    r["district_id"]
    for r in all_records
    if r.get("district_id")
}

print()
print("======================================")
print("BLOCK-LEVEL SCAN COMPLETE")
print("======================================")
print("Unique districts:", len(district_ids))
print("Unique blocks:", len(block_ids))
print("Unique villages:", len(village_ids))
print("Nutrient records:", len(all_records))
print()
print("JSON: tn_rkvy_block_records.json")
print("CSV : tn_rkvy_block_records.csv")

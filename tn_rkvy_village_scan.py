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

with open("tn_rkvy_block_records.json", encoding="utf-8") as f:
    block_records = json.load(f)

blocks = {}
for r in block_records:
    block_id = r.get("block_id")
    if block_id:
        blocks[block_id] = {
            "block_id": block_id,
            "block": r.get("block"),
            "district_id": r.get("district_id"),
            "district": r.get("district")
        }

print("Unique blocks to scan:", len(blocks))
print()

session = requests.Session()
session.headers.update(HEADERS)

all_records = []
seen = set()

for i, info in enumerate(blocks.values(), 1):

    variables = {
        "state": STATE_ID,
        "district": info["district_id"],
        "block": info["block_id"],
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
            print(
                f"[{i}/{len(blocks)}] "
                f"{info['district']} / {info['block']}: "
                f"HTTP {r.status_code}"
            )
            continue

        payload = r.json()
        records = payload.get("data", {}).get(
            "getNutrientDashboardForPortal"
        ) or []

        new_count = 0

        for rec in records:

            record_id = rec.get("_id")

            if record_id and record_id in seen:
                continue

            if record_id:
                seen.add(record_id)

            state = rec.get("state") or {}
            district = rec.get("district") or {}
            block = rec.get("block") or {}
            village = rec.get("village") or {}

            row = {
                "record_id": record_id,

                "state": state.get("name"),
                "state_id": state.get("_id"),

                "district": district.get("name"),
                "district_id": district.get("_id"),

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
            new_count += 1

        print(
            f"[{i}/{len(blocks)}] "
            f"{info['district']} / {info['block']}: "
            f"{new_count} village record(s)"
        )

    except Exception as e:
        print(
            f"[{i}/{len(blocks)}] "
            f"{info['district']} / {info['block']}: ERROR {e}"
        )

    time.sleep(0.35)

with open(
    "tn_rkvy_village_records.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        all_records,
        f,
        indent=2,
        ensure_ascii=False
    )

if all_records:
    fields = sorted({
        key
        for row in all_records
        for key in row
    })

    with open(
        "tn_rkvy_village_records.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(all_records)

print()
print("======================================")
print("VILLAGE-LEVEL SCAN COMPLETE")
print("======================================")

print(
    "Districts:",
    len({
        r["district_id"]
        for r in all_records
        if r.get("district_id")
    })
)

print(
    "Blocks:",
    len({
        r["block_id"]
        for r in all_records
        if r.get("block_id")
    })
)

print(
    "Villages:",
    len({
        r["village_id"]
        for r in all_records
        if r.get("village_id")
    })
)

print(
    "Records:",
    len(all_records)
)

print()
print("JSON: tn_rkvy_village_records.json")
print("CSV : tn_rkvy_village_records.csv")

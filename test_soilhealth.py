import requests
import json

url = "https://soilhealth4.dac.gov.in/"

query = """
query GetSchoolProgressReport($state: String, $district: String, $cycle: String, $scheme: String, $type: String) {
  getSchoolProgressReport(
    state: $state
    district: $district
    cycle: $cycle
    scheme: $scheme
    type: $type
  )
}
"""

payload = {
    "operationName": "GetSchoolProgressReport",
    "variables": {
        "cycle": "2026-27"
    },
    "query": query
}

headers = {
    "Content-Type": "application/json",
    "x-client-type": "portal",
    "Origin": "https://soilhealth.dac.gov.in",
    "Referer": "https://soilhealth.dac.gov.in/"
}

print("Requesting Soil Health Card data...")

response = requests.post(
    url,
    json=payload,
    headers=headers,
    timeout=30
)

response.raise_for_status()

data = response.json()

with open("school_progress_2026-27.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

records = data["data"]["getSchoolProgressReport"]

print("HTTP Status:", response.status_code)
print("Records:", len(records))
print("Saved: school_progress_2026-27.json")

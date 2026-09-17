import re

s = open("site_bundle.js", encoding="utf-8").read()

for name in ["GetTestForPortal", "GetProgressReportForPortal", "GetTestForPortalForSchool"]:
    print()
    print("=" * 80)
    print(name)
    print("=" * 80)

    matches = list(re.finditer(
        r"query\s+" + re.escape(name) + r"\b",
        s
    ))

    print("Occurrences:", len(matches))

    for i, m in enumerate(matches[:10], 1):
        start = max(0, m.start() - 200)
        end = min(len(s), m.start() + 2200)

        text = s[start:end].replace("\n", " ")
        print()
        print(f"--- occurrence {i} ---")
        print(text)

import re

s = open("site_bundle.js", encoding="utf-8").read()

patterns = [
    r'query\s+([A-Za-z0-9_]+)',
    r'mutation\s+([A-Za-z0-9_]+)',
    r'fragment\s+([A-Za-z0-9_]+)'
]

found = set()

for pattern in patterns:
    for m in re.finditer(pattern, s):
        found.add(m.group(1))

print("GRAPHQL OPERATIONS / FRAGMENTS")
print("=" * 60)

for name in sorted(found):
    print(name)

print()
print("TOTAL UNIQUE NAMES:", len(found))

from lxml import etree
from collections import defaultdict

tree = etree.parse("../../data/nsw/raw_data/act-2005-028_2025-12-16.xml")

root = tree.getroot()

tags = set()
for elem in root.iter():
    tags.add(elem.tag)

# for t in sorted(tags):
#     print(t)

tags_attrs = defaultdict(set)

WHITELIST_ATTRS = {"type", "title", "number", "no", "heading", "year.passed", "year.assent", "enact.or.made.date", "first.valid.date"}
 # Uncomment this to see the levels , subdivision etc all that stuff
# for elem in root.iter():
#     relevant_attrs = {k: v for k, v in elem.attrib.items() if k in WHITELIST_ATTRS}
#     if relevant_attrs:
#         print(elem.tag, relevant_attrs)

from collections import Counter

level_types = Counter()
tier_types = Counter()
content_types = Counter()
defterm_types = Counter()
legref_types = Counter()

for elem in root.iter():
    if elem.tag == "level":
        level_types[elem.get("type")] += 1
    elif elem.tag == "tier":
        tier_types[elem.get("type")] += 1
    elif elem.tag == "content":
        content_types[elem.get("type")] += 1
    elif elem.tag == "defterm":
        defterm_types[elem.get("type")] += 1
    elif elem.tag == "legref":
        legref_types[elem.get("type")] += 1

print("LEVEL types:", level_types)
print("TIER types:", tier_types)
print("CONTENT types:", content_types)
print("DEFTYPES:", defterm_types)
print("LEGREF types:", legref_types)


from collections import defaultdict
import requests
import json
from lxml import etree
import re
# -----------------------------------
# Fetch agency metadata from the eCFR API
# and build a mapping of (title, chapter) → agency name
# -----------------------------------
def build_agency_mapping():
    url = "https://www.ecfr.gov/api/admin/v1/agencies.json"
    response = requests.get(url)
    agency_map = {}

    if response.status_code == 200:
        data = response.json()
        for agency in data.get("agencies", []):
            name = agency["name"]
            for ref in agency.get("cfr_references", []):
                title = ref.get("title")
                chapter = ref.get("chapter")
                if title and chapter:
                    agency_map[(str(title), chapter)] = name
            for child in agency.get("children", []):
                name = child["name"]
                for ref in child.get("cfr_references", []):
                    title = ref.get("title")
                    chapter = ref.get("chapter")
                    if title and chapter:
                        agency_map[(str(title), chapter)] = name
    else:
        print("❌ Failed to fetch agency metadata")
    return agency_map

# -----------------------------------
# Count words in each paragraph (<P>) for a specific title and issue date.
# Detects which chapter each paragraph belongs to using regex, and attributes word counts to agencies.
# -----------------------------------

def count_words_by_chapter(title_number, issue_date, agency_map):
    url = f"https://www.ecfr.gov/api/versioner/v1/full/{issue_date}/title-{title_number}.xml"
    response = requests.get(url)
    word_counts = defaultdict(int)

    if response.status_code == 200:
        parser = etree.XMLParser(recover=True)
        tree = etree.fromstring(response.content, parser)
        p_tags = tree.findall(".//P")

        for p in p_tags:
            parent = p.getparent()
            chapter = None

            while parent is not None:
                if parent.tag.startswith("DIV"):
                    head = parent.find("HEAD")
                    if head is not None and head.text:
                        match = re.search(r"CHAPTER\s+([A-Z0-9]+)", head.text.upper())
                        if match:
                            chapter = match.group(1)
                            break
                parent = parent.getparent()

            if not chapter:
                continue

            text = p.text
            if text:
                word_count = len(text.strip().split())
                agency = agency_map.get((str(title_number), chapter))
                if agency:
                    word_counts[agency] += word_count

    return word_counts
# -----------------------------------
# Get the latest issue date for every title available from the API
# Returns a list of (title_number, issue_date) pairs
# -----------------------------------
def get_latest_issue_dates():
    url = "https://www.ecfr.gov/api/versioner/v1/titles.json"
    response = requests.get(url)
    if response.status_code == 200:
        return [(str(t["number"]), t["latest_issue_date"]) for t in response.json().get("titles", [])]
    return []


# -----------------------------------
# loop over all titles and count words by agency
# Saves the results to word_counts.json
# -----------------------------------
agency_map = build_agency_mapping()
final_counts = defaultdict(int)
title_dates = get_latest_issue_dates()

for title_number, issue_date in title_dates:
    print(f"🔍 Processing Title {title_number} ({issue_date})...")
    counts = count_words_by_chapter(title_number, issue_date, agency_map)
    for agency, count in counts.items():
        final_counts[agency] += count

# Save to JSON
with open("word_counts.json", "w") as f:
    json.dump(final_counts, f, indent=4)

print("✅ All agency word counts saved to word_counts.json")

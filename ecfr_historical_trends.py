# import requests
# from lxml import etree
# from collections import defaultdict
# import json
# from time import sleep

# def build_agency_mapping():
#     url = "https://www.ecfr.gov/api/admin/v1/agencies.json"
#     response = requests.get(url)
#     agency_map = {}

#     if response.status_code == 200:
#         data = response.json()
#         for agency in data.get("agencies", []):
#             name = agency["name"]
#             for ref in agency.get("cfr_references", []):
#                 title = str(ref.get("title"))
#                 chapter = ref.get("chapter")
#                 if title and chapter:
#                     agency_map[(title, chapter)] = name
#             for child in agency.get("children", []):
#                 name = child["name"]
#                 for ref in child.get("cfr_references", []):
#                     title = str(ref.get("title"))
#                     chapter = ref.get("chapter")
#                     if title and chapter:
#                         agency_map[(title, chapter)] = name
#     return agency_map

# def count_words_by_agency(title_number, issue_date, agency_map):
#     url = f"https://www.ecfr.gov/api/versioner/v1/full/{issue_date}/title-{title_number}.xml"
#     response = requests.get(url)
#     word_counts = defaultdict(int)

#     if response.status_code == 200:
#         parser = etree.XMLParser(recover=True)
#         tree = etree.fromstring(response.content, parser)

#         chapter_nodes = tree.findall(".//DIV3")
#         for chapter in chapter_nodes:
#             chapter_num = chapter.get("N")
#             if not chapter_num:
#                 continue

#             p_tags = chapter.findall(".//P")
#             words = sum(len(p.text.strip().split()) for p in p_tags if p.text)
#             agency = agency_map.get((str(title_number), chapter_num))
#             if agency:
#                 word_counts[agency] += words
#     return word_counts

# def build_historical_dataset():
#     agency_map = build_agency_mapping()

#     title_num = 2
#     issue_dates = get_issue_dates(title_num)
#     if not issue_dates:
#         return {}

#     selected_date = issue_dates[0]  # Most recent date
#     print(f"📘 Processing Title {title_num}, Date: {selected_date}")

#     counts = count_words_by_agency(title_num, selected_date, agency_map)

#     historical_data = defaultdict(dict)
#     for agency, count in counts.items():
#         historical_data[agency][selected_date] = count

#     return historical_data

# def get_issue_dates(title_number):
#     url = f"https://www.ecfr.gov/api/versioner/v1/versions/title-{title_number}.json"
#     response = requests.get(url)
#     if response.status_code == 200:
#         versions = response.json().get("content_versions", [])
#         return sorted({v["issue_date"] for v in versions}, reverse=True)
#     return []

# if __name__ == "__main__":
#     results = build_historical_dataset()
#     print(json.dumps(results, indent=2))
#     with open("historical_word_counts.json", "w") as f:
#         json.dump(results, f, indent=2)
#     print("✅ Saved to historical_word_counts.json")


import requests
from lxml import etree
from collections import defaultdict
import json
from time import sleep

# 🔧 Build a (title, chapter) → agency name mapping
def build_agency_mapping():
    url = "https://www.ecfr.gov/api/admin/v1/agencies.json"
    response = requests.get(url)
    agency_map = {}

    if response.status_code == 200:
        data = response.json()
        for agency in data.get("agencies", []):
            name = agency["name"]
            for ref in agency.get("cfr_references", []):
                title = str(ref.get("title"))
                chapter = ref.get("chapter")
                if title and chapter:
                    agency_map[(title, chapter)] = name
            for child in agency.get("children", []):
                name = child["name"]
                for ref in child.get("cfr_references", []):
                    title = str(ref.get("title"))
                    chapter = ref.get("chapter")
                    if title and chapter:
                        agency_map[(title, chapter)] = name
    return agency_map

# Count words by agency for a given title and issue date
def count_words_by_agency(title_number, issue_date, agency_map):
    url = f"https://www.ecfr.gov/api/versioner/v1/full/{issue_date}/title-{title_number}.xml"
    response = requests.get(url)
    word_counts = defaultdict(int)

    if response.status_code == 200:
        parser = etree.XMLParser(recover=True)
        tree = etree.fromstring(response.content, parser)

        chapter_nodes = tree.findall(".//DIV3")
        for chapter in chapter_nodes:
            chapter_num = chapter.get("N")
            if not chapter_num:
                continue

            p_tags = chapter.findall(".//P")
            words = sum(len(p.text.strip().split()) for p in p_tags if p.text)
            agency = agency_map.get((str(title_number), chapter_num))
            if agency:
                word_counts[agency] += words
    return word_counts

# Get the latest issue dates for a title
def get_issue_dates(title_number):
    url = f"https://www.ecfr.gov/api/versioner/v1/versions/title-{title_number}.json"
    response = requests.get(url)
    if response.status_code == 200:
        versions = response.json().get("content_versions", [])
        return sorted({v["issue_date"] for v in versions}, reverse=True)
    return []

# Loop through all titles + latest 3 issue dates
def build_historical_dataset():
    agency_map = build_agency_mapping()
    historical_data = defaultdict(dict)

    # 🔎 Get all titles from metadata
    titles_url = "https://www.ecfr.gov/api/versioner/v1/titles.json"
    titles_response = requests.get(titles_url)
    if titles_response.status_code != 200:
        print("❌ Failed to fetch titles.")
        return {}

    all_titles = titles_response.json().get("titles", [])
    for title in all_titles:
        title_num = str(title["number"])
        print(f"\n📘 Processing Title {title_num}...")

        issue_dates = get_issue_dates(title_num)[:3] # 3 most recent
        for date in issue_dates:
            print(f"  ⏳ {date}")
            counts = count_words_by_agency(title_num, date, agency_map)
            for agency, count in counts.items():
                historical_data[agency][date] = historical_data[agency].get(date, 0) + count
            sleep(0.5) 

    return historical_data

# Save to file
if __name__ == "__main__":
    results = build_historical_dataset()
    with open("historical_word_counts.json", "w") as f:
        json.dump(results, f, indent=2)
    print("✅ Saved to historical_word_counts.json")

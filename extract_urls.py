import requests
from bs4 import BeautifulSoup
import re
import os
import json
import time

BASE_URL = "https://utopiastories.com/"
TAG_CLOUD_URL = f"{BASE_URL}tagcloud.html"

def get_tag_urls():
    print(f"Fetching tag cloud from {TAG_CLOUD_URL}")
    response = requests.get(TAG_CLOUD_URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    tag_urls = []
    # Tags are in <div id="tagcloud"> as <a> elements
    tagcloud_div = soup.find(id="tagcloud")
    if tagcloud_div:
        for a in tagcloud_div.find_all('a'):
            href = a.get('href')
            if href:
                # Relative URL from tagcloud.html
                tag_urls.append(BASE_URL + href)

    return list(set(tag_urls))

def get_story_urls_from_tag(tag_url):
    print(f"Fetching stories from tag: {tag_url}")
    response = requests.get(tag_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    story_links = []
    # Stories are in a table, linked with ../../code/show_story.asp/recid/XXXXX.html
    for a in soup.find_all('a', href=re.compile(r'show_story\.asp/recid/(\d+)\.html')):
        href = a.get('href')
        # href is like ../../code/show_story.asp/recid/60120.html
        # We want the absolute URL
        match = re.search(r'recid/(\d+)\.html', href)
        if match:
            recid = match.group(1)
            story_links.append(f"{BASE_URL}code/show_story.asp/recid/{recid}.html")

    return list(set(story_links))

def main():
    tag_urls = get_tag_urls()
    print(f"Found {len(tag_urls)} tags.")

    all_story_urls = set()
    for tag_url in tag_urls:
        try:
            story_urls = get_story_urls_from_tag(tag_url)
            print(f"  Found {len(story_urls)} stories.")
            all_story_urls.update(story_urls)
            time.sleep(0.5) # Be nice to the server
        except Exception as e:
            print(f"  Error fetching {tag_url}: {e}")

    print(f"Total unique stories found: {len(all_story_urls)}")

    with open("story_urls.json", "w") as f:
        json.dump(list(all_story_urls), f, indent=2)
    print("Saved story URLs to story_urls.json")

if __name__ == "__main__":
    main()

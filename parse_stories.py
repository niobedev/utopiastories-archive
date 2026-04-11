import requests
from bs4 import BeautifulSoup
import re
import os
import json
import yaml
from markdownify import markdownify as md
import time
import argparse

BASE_URL = "https://utopiastories.com/"

def parse_story_page(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Extracting title - usually in the first <td> with class="titlebar"
    # Actually, title is often inside a table row with bold link
    # But on the story page itself, it's just in a <td>
    # Let's look for the title from the metadata table or titlebar

    # Metadata extraction
    metadata = {}

    # Finding metadata - there is a table with Author, Rating, Site Rank, Story Codes, Post Date
    # Looking for 'Author' string
    author_elem = soup.find(string=re.compile(r'Author'))
    if author_elem:
        # Structure is usually: Author - [tiedguy](../../show_result3e6c.html?search=basic&author=tiedguy)
        # It's in a <li> or just text
        parent = author_elem.parent
        if parent.name == 'b' or parent.name == 'strong':
             parent = parent.parent

        # Get author name
        author_link = parent.find('a')
        if author_link:
            metadata['author'] = author_link.get_text(strip=True)
        else:
            # Fallback if no link
            metadata['author'] = parent.get_text(strip=True).split('-', 1)[-1].strip()

    # Story Codes (metadata)
    codes_elem = soup.find(string=re.compile(r'Story Codes'))
    if codes_elem:
        parent = codes_elem.parent
        if parent.name == 'b' or parent.name == 'strong':
             parent = parent.parent
        codes_text = parent.get_text(strip=True).split('-', 1)[-1].strip()
        metadata['story_codes'] = [c.strip() for c in codes_text.split(',')]

    # Post Date (metadata)
    date_elem = soup.find(string=re.compile(r'Post Date'))
    if date_elem:
        parent = date_elem.parent
        if parent.name == 'b' or parent.name == 'strong':
             parent = parent.parent
        metadata['post_date'] = parent.get_text(strip=True).split('-', 1)[-1].strip()

    # Title - usually in the page title or a header
    title = soup.title.string.split('::')[0].strip() if soup.title else "Untitled"
    metadata['title'] = title

    # Story content - it's between metadata and footer
    # Usually it starts after Author's Note or in a specific <td>
    # Looking for Author's Note
    authors_note_elem = soup.find(string=re.compile(r"Author's Note:"))
    content_html = ""

    # Let's find the main content <td>. It usually contains the metadata table and then the story.
    # The metadata table has "Author" in it.
    metadata_table = soup.find('table', border="0", width="100%")
    if metadata_table and "Author" in metadata_table.get_text():
        # The content is usually in the parent or following the table
        # Based on the structure, it's often in a <td> that contains this metadata table.
        content_container = metadata_table.find_parent('td')
        if content_container:
            # Clone it to avoid modifying the original soup
            import copy
            content_copy = copy.copy(content_container)

            # Remove the metadata table from the copy
            mt = content_copy.find('table', border="0", width="100%")
            if mt:
                mt.decompose()

            # Remove the footer table (navigation)
            ft = content_copy.find('table', class_='footmenu')
            if ft:
                ft.decompose()

            # Remove images (headers/banners)
            for img in content_copy.find_all('img'):
                img.decompose()

            # Remove links that are part of navigation
            for a in content_copy.find_all('a', href=re.compile(r'home|faq|stories|links|tagcloud|forum|contact')):
                a.decompose()

            content_html = str(content_copy)

    if not content_html:
         # Fallback search for content
         # It's usually after the metadata table.
         # Let's try to get the <div> with margin: 10px 15px 10px 15px;
         main_div = soup.find('div', style=re.compile(r'margin:\s*10px 15px 10px 15px;'))
         if main_div:
             # Remove similar elements from main_div
             import copy
             content_copy = copy.copy(main_div)
             for t in content_copy.find_all('table'):
                 if "Author" in t.get_text() or "Home" in t.get_text():
                     t.decompose()
             for img in content_copy.find_all('img'):
                 img.decompose()
             content_html = str(content_copy)

    # Convert to Markdown
    story_markdown = md(content_html, heading_style="ATX")

    # Post-process markdown
    # Fix the issue with ***Author's Note:** where it's bold inside italic
    # We want it to be _**Author's Note:** ..._
    story_markdown = re.sub(r'(\n|^)_+(\s*)\*\*Author\'s Note:\*\*', r'\1_**Author\'s Note:**', story_markdown)
    story_markdown = re.sub(r'\*\*\*([^*]+)\*\*(.+?)\*', r'_**\1**\2_', story_markdown, flags=re.DOTALL)

    # Post-process markdown to remove empty table rows and excessive whitespace
    story_markdown = re.sub(r'\|[\s\|-]*\n', '', story_markdown)
    story_markdown = re.sub(r'\n{3,}', '\n\n', story_markdown)
    story_markdown = story_markdown.strip()

    return metadata, story_markdown

def save_story(metadata, content, recid):
    filename = f"stories/{recid}.md"
    os.makedirs("stories", exist_ok=True)

    # Clean up content a bit - remove metadata from content if it was captured
    # (Basic cleaning, can be improved)

    yaml_header = yaml.dump(metadata, sort_keys=False)

    with open(filename, "w") as f:
        f.write("---\n")
        f.write(yaml_header)
        f.write("---\n\n")
        f.write(content)

def main():
    parser = argparse.ArgumentParser(description="Parse stories from UtopiaStories.")
    parser.add_argument("--retry-failed", action="store_true", help="Retry URLs that previously returned 404.")
    args = parser.parse_args()

    if not os.path.exists("story_urls.json"):
        print("story_urls.json not found. Run extract_urls.py first.")
        return

    with open("story_urls.json", "r") as f:
        urls = json.load(f)

    failed_urls_file = "failed_urls.json"
    failed_urls = []
    if os.path.exists(failed_urls_file):
        with open(failed_urls_file, "r") as f:
            failed_urls = json.load(f)

    to_process = []
    for url in urls:
        recid = url.split('/')[-1].replace('.html', '')
        if not os.path.exists(f"stories/{recid}.md"):
            if url in failed_urls and not args.retry_failed:
                continue
            to_process.append((url, recid))

    total = len(to_process)
    if total == 0:
        print("All stories already parsed or marked as failed (use --retry-failed to retry).")
        return

    print(f"Processing {total} stories.")

    new_failed_urls = []

    try:
        for i, (url, recid) in enumerate(to_process, 1):
            try:
                print(f"[{i}/{total}] Processing {url}...", end="\r", flush=True)
                response = requests.get(url)

                if response.status_code == 404:
                    print(f"\n[404] {url} not found. Marking as failed.")
                    if url not in failed_urls:
                        failed_urls.append(url)
                        new_failed_urls.append(url)
                    continue

                response.raise_for_status()

                # Fix encoding - site often reports UTF-8 but uses Latin-1
                # and might contain null bytes
                response.encoding = response.apparent_encoding
                html_content = response.text.replace('\x00', '')

                metadata, content = parse_story_page(html_content)
                metadata['url'] = url
                save_story(metadata, content, recid)

                # If it was in failed_urls and we successfully parsed it, remove it
                if url in failed_urls:
                    failed_urls.remove(url)

                time.sleep(0.25) # Be nice
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    print(f"\n[404] {url} not found. Marking as failed.")
                    if url not in failed_urls:
                        failed_urls.append(url)
                        new_failed_urls.append(url)
                else:
                    print(f"\nHTTP Error processing {url}: {e}")
            except Exception as e:
                print(f"\nError processing {url}: {e}")
    finally:
        # Save failed URLs even if interrupted
        with open(failed_urls_file, "w") as f:
            json.dump(failed_urls, f, indent=2)

    print(f"\nFinished processing. Total failed: {len(failed_urls)}")

if __name__ == "__main__":
    main()

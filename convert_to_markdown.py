import os
import re
import yaml
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import glob
import argparse

def parse_story_html(html, url):
    # Detect encoding and handle null bytes
    # BeautifulSoup handles most encoding issues if we give it the bytes or a decoded string
    soup = BeautifulSoup(html, 'html.parser')

    metadata = {}
    metadata['original_url'] = url

    # Author
    author_elem = soup.find(string=re.compile(r'Author'))
    if author_elem:
        parent = author_elem.parent
        if parent.name in ['b', 'strong']:
             parent = parent.parent
        author_link = parent.find('a')
        if author_link:
            author_name = author_link.get_text(strip=True)
        else:
            author_name = parent.get_text(strip=True).split('-', 1)[-1].strip()
        metadata['authors'] = [author_name]

    # Story Codes
    codes_elem = soup.find(string=re.compile(r'Story Codes'))
    if codes_elem:
        parent = codes_elem.parent
        if parent.name in ['b', 'strong']:
             parent = parent.parent
        codes_text = parent.get_text(strip=True).split('-', 1)[-1].strip()
        metadata['tags'] = [c.strip() for c in codes_text.split(',')]

    # Post Date
    date_elem = soup.find(string=re.compile(r'Post Date'))
    if date_elem:
        parent = date_elem.parent
        if parent.name in ['b', 'strong']:
             parent = parent.parent
        metadata['post_date'] = parent.get_text(strip=True).split('-', 1)[-1].strip()

    # Title
    title = soup.title.string.split('::')[0].strip() if soup.title else "Untitled"
    metadata['title'] = title

    # Content extraction
    content_html = ""
    metadata_table = soup.find('table', border="0", width="100%")
    if metadata_table and "Author" in metadata_table.get_text():
        content_container = metadata_table.find_parent('td')
        if content_container:
            import copy
            content_copy = copy.copy(content_container)
            mt = content_copy.find('table', border="0", width="100%")
            if mt: mt.decompose()
            ft = content_copy.find('table', class_='footmenu')
            if ft: ft.decompose()
            for img in content_copy.find_all('img'): img.decompose()
            for a in content_copy.find_all('a', href=re.compile(r'home|faq|stories|links|tagcloud|forum|contact')):
                a.decompose()
            content_html = str(content_copy)

    if not content_html:
         main_div = soup.find('div', style=re.compile(r'margin:\s*10px 15px 10px 15px;'))
         if main_div:
             import copy
             content_copy = copy.copy(main_div)
             for t in content_copy.find_all('table'):
                 if "Author" in t.get_text() or "Home" in t.get_text():
                     t.decompose()
             for img in content_copy.find_all('img'): img.decompose()
             content_html = str(content_copy)

    # Convert to Markdown
    story_markdown = md(content_html, heading_style="ATX")

    # Post-process
    story_markdown = re.sub(r'(\n|^)[\*_]*(\s*)\*\*Author\'s Note:?\*\*\s*', r'\1_**Author\'s Note:** _', story_markdown)
    story_markdown = re.sub(r'\*\*\*([^*]+)\*\*(.+?)\*', r'_**\1**\2_', story_markdown, flags=re.DOTALL)
    story_markdown = re.sub(r'[ \t]+$', '', story_markdown, flags=re.MULTILINE)

    def fix_italics(match):
        content = match.group(1)
        content = content.strip()
        if '\n\n' in content:
            paragraphs = content.split('\n\n')
            return '\n\n'.join([f'_{p.strip()}_' for p in paragraphs if p.strip()])
        return f'_{content}_'

    story_markdown = re.sub(r'_(.+?)_', fix_italics, story_markdown, flags=re.DOTALL)
    story_markdown = re.sub(r'\|[\s\|-]*\n', '', story_markdown)
    story_markdown = re.sub(r'\n{3,}', '\n\n', story_markdown)
    story_markdown = re.sub(r'[ \t]+$', '', story_markdown, flags=re.MULTILINE)
    story_markdown = story_markdown.strip()

    return metadata, story_markdown

def convert_all_stories():
    source_dir = "stories"
    target_dir = "website/content/stories"
    os.makedirs(target_dir, exist_ok=True)

    # Load mapping of recid to URL if available, or just use placeholders
    import json
    url_map = {}
    if os.path.exists("story_urls.json"):
        with open("story_urls.json", "r") as f:
            urls = json.load(f)
            for u in urls:
                recid = u.split('/')[-1].replace('.html', '')
                url_map[recid] = u

    html_files = glob.glob(os.path.join(source_dir, "*.html"))
    print(f"Converting {len(html_files)} HTML stories to Markdown...")

    for i, filepath in enumerate(html_files, 1):
        filename = os.path.basename(filepath)
        recid = filename.replace(".html", "")
        target_path = os.path.join(target_dir, recid + ".md")

        print(f"[{i}/{len(html_files)}] Converting {filename}...", end="\r", flush=True)

        try:
            with open(filepath, "rb") as f:
                raw_html = f.read()

            # Detect encoding and handle null bytes
            from bs4 import UnicodeDammit
            dammit = UnicodeDammit(raw_html, is_html=True)
            encoding = dammit.original_encoding

            # Map iso-8859-1 to cp1252 to better handle smart quotes/apostrophes in the \x80-\x9F range
            if encoding and encoding.lower() in ['iso-8859-1', 'latin-1']:
                 encoding = 'cp1252'

            try:
                html_text = raw_html.decode(encoding or 'utf-8', errors='replace').replace('\x00', '')
            except (UnicodeDecodeError, LookupError):
                html_text = raw_html.decode('utf-8', errors='replace').replace('\x00', '')

            url = url_map.get(recid, f"https://utopiastories.com/story/{recid}.html")
            metadata, content = parse_story_html(html_text, url)

            yaml_header = yaml.dump(metadata, sort_keys=False, allow_unicode=True)

            with open(target_path, "w", encoding="utf-8") as f:
                f.write("---\n")
                f.write(yaml_header)
                f.write("---\n\n")
                f.write(content)
                f.write("\n") # Ensure trailing newline

        except Exception as e:
            print(f"\nError converting {filename}: {e}")

    print(f"\nFinished converting {len(html_files)} stories.")

if __name__ == "__main__":
    convert_all_stories()

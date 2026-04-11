import requests
import os
import json
import time
import argparse

def download_stories(retry_failed=False):
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

    stories_dir = "stories"
    os.makedirs(stories_dir, exist_ok=True)

    to_process = []
    for url in urls:
        recid = url.split('/')[-1].replace('.html', '')
        if not os.path.exists(os.path.join(stories_dir, f"{recid}.html")):
            if url in failed_urls and not retry_failed:
                continue
            to_process.append((url, recid))

    total = len(to_process)
    if total == 0:
        print("All stories already downloaded or marked as failed (use --retry-failed to retry).")
        return

    print(f"Downloading {total} stories...")

    new_failed_urls = []
    try:
        for i, (url, recid) in enumerate(to_process, 1):
            try:
                print(f"[{i}/{total}] Downloading {url}...", end="\r", flush=True)
                response = requests.get(url)

                if response.status_code == 404:
                    print(f"\n[404] {url} not found. Marking as failed.")
                    if url not in failed_urls:
                        failed_urls.append(url)
                        new_failed_urls.append(url)
                    continue

                response.raise_for_status()

                # Save raw HTML
                filepath = os.path.join(stories_dir, f"{recid}.html")
                with open(filepath, "wb") as f:
                    f.write(response.content)

                # If it was in failed_urls and we successfully downloaded it, remove it
                if url in failed_urls:
                    failed_urls.remove(url)

                time.sleep(0.1) # Be nice
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

    print(f"\nFinished downloading. Total failed: {len(failed_urls)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download raw HTML stories from UtopiaStories.")
    parser.add_argument("--retry-failed", action="store_true", help="Retry URLs that previously returned 404.")
    args = parser.parse_args()
    download_stories(args.retry_failed)

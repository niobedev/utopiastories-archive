import os
import yaml
import glob

def convert_stories():
    source_dir = "stories"
    target_dir = "website/content/stories"
    os.makedirs(target_dir, exist_ok=True)

    story_files = glob.glob(os.path.join(source_dir, "*.md"))
    print(f"Converting {len(story_files)} stories...")

    for i, filepath in enumerate(story_files, 1):
        filename = os.path.basename(filepath)
        target_path = os.path.join(target_dir, filename)

        print(f"[{i}/{len(story_files)}] Converting {filename}...", end="\r", flush=True)

        with open(filepath, "r") as f:
            content = f.read()

        if not content.startswith("---"):
            continue

        parts = content.split("---", 2)
        if len(parts) < 3:
            continue

        front_matter = yaml.safe_load(parts[1])
        body = parts[2]

        # Map metadata
        new_front_matter = {}
        if 'author' in front_matter:
            new_front_matter['authors'] = front_matter['author']
        if 'story_codes' in front_matter:
            new_front_matter['tags'] = front_matter['story_codes']
        if 'post_date' in front_matter:
            new_front_matter['post_date'] = front_matter['post_date']
        if 'title' in front_matter:
            new_front_matter['title'] = front_matter['title']
        if 'url' in front_matter:
            new_front_matter['original_url'] = front_matter['url']

        # Preserve any other fields
        for key, value in front_matter.items():
            if key not in ['author', 'story_codes', 'post_date', 'title', 'url']:
                new_front_matter[key] = value

        new_content = "---\n" + yaml.dump(new_front_matter, sort_keys=False) + "---" + body

        with open(target_path, "w") as f:
            f.write(new_content)

    print(f"\nFinished converting {len(story_files)} stories.")

if __name__ == "__main__":
    convert_stories()

import os
import re
import argparse

def is_broken(content):
    # Pattern 1: Italics that span across multiple paragraphs (blank lines)
    # Goldmark doesn't handle _\n\n_ well.
    # Example: _Para 1\n\nPara 2_
    # The fix in parse_stories.py now splits these into _Para 1_\n\n_Para 2_
    if re.search(r'_[^_\n]+?\n\n[^_]+?_', content):
        return True, "Multiline italics with blank lines"

    # Pattern 2: Italics with trailing spaces before the closing underscore
    # This was identified as a cause for extra underscores being rendered
    if re.search(r'_[^_\n]+? \s*_', content):
        return True, "Italics with trailing spaces before closing underscore"

    # Pattern 5: Italics that start with a space
    if re.search(r'_\s+[^_\n]+?_', content):
        return True, "Italics with leading spaces after opening underscore"

    # Pattern 3: Triple underscores or triple asterisks that might be poorly converted
    if '***' in content or '___' in content:
        # Though *** is valid for bold-italic, sometimes it's a sign of a bad conversion
        # if it was meant to be separate. But let's be careful.
        # The specific issue reported was extra underscores around Author's Note.
        pass

    # Pattern 4: The specific "Author's Note" issue where it's not correctly italicized
    # or has extra underscores.
    # If we see things like _ **Author's Note:** ... _ (with spaces)
    if re.search(r'_\s+\*\*Author\'s Note:\*\*', content) or re.search(r'\*\*Author\'s Note:\*\*\s+_', content):
         return True, "Broken Author's Note formatting"

    return False, ""

def main():
    parser = argparse.ArgumentParser(description="Detect and delete stories with broken markdown.")
    parser.add_argument("--delete", action="store_true", help="Delete the broken stories after detection.")
    args = parser.parse_args()

    stories_dir = "stories"
    website_stories_dir = "website/content/stories"

    if not os.path.exists(stories_dir):
        print(f"Directory {stories_dir} not found.")
        return

    broken_files = []

    files = [f for f in os.listdir(stories_dir) if f.endswith(".md")]
    print(f"Scanning {len(files)} files in {stories_dir}...")

    for filename in files:
        filepath = os.path.join(stories_dir, filename)
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        broken, reason = is_broken(content)
        if broken:
            broken_files.append((filename, reason))

    if not broken_files:
        print("No broken stories detected.")
        return

    print(f"\nDetected {len(broken_files)} broken stories:")
    for filename, reason in broken_files:
        print(f" - {filename}: {reason}")

    if args.delete:
        confirm = input(f"\nAre you sure you want to delete these {len(broken_files)} files? (y/N): ")
        if confirm.lower() == 'y':
            for filename, _ in broken_files:
                # Delete from stories/
                p1 = os.path.join(stories_dir, filename)
                if os.path.exists(p1):
                    os.remove(p1)

                # Delete from website/content/stories/
                p2 = os.path.join(website_stories_dir, filename)
                if os.path.exists(p2):
                    os.remove(p2)

            print(f"\nDeleted {len(broken_files)} files. Now you can run parse_stories.py and then convert_stories.py.")
        else:
            print("\nDeletion cancelled.")
    else:
        print(f"\nRun with --delete to delete these {len(broken_files)} files.")

if __name__ == "__main__":
    main()

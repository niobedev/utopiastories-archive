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

    # Pattern 5: Italics that start or end with a space
    # Example: _ Author's Note: Hello_ or _Author's Note: Hello _
    if re.search(r'_\s+[^_\n]+?_', content) or re.search(r'_[^_\n]+?\s+_', content):
        return True, "Italics with leading or trailing spaces"

    # Pattern 3: Triple underscores or triple asterisks that might be poorly converted
    # Often a sign of nested formatting that went wrong or extra underscores
    if '___' in content:
        return True, "Triple underscores detected"

    # Pattern 4: The specific "Author's Note" issue where it's not correctly italicized
    # or has extra underscores.
    # If we see things like _ **Author's Note:** ... _ (with spaces)
    if re.search(r'_\s+\*\*Author\'s Note:\*\*', content) or re.search(r'\*\*Author\'s Note:\*\*\s+_', content):
         return True, "Broken Author's Note formatting"

    # Pattern 6: Missing trailing newline
    if content and not content.endswith('\n'):
        return True, "Missing trailing newline"

    return False, ""

def main():
    parser = argparse.ArgumentParser(description="Detect and delete stories with broken markdown.")
    parser.add_argument("--delete", action="store_true", help="Delete the broken stories after detection.")
    parser.add_argument("--force", action="store_true", help="Force deletion without confirmation.")
    args = parser.parse_args()

    # Scan website/content/stories/ for converted stories
    stories_dir = "website/content/stories"

    if not os.path.exists(stories_dir):
        print(f"Directory {stories_dir} not found. Run 'make convert' first.")
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
        if args.force:
            confirm = 'y'
        else:
            confirm = input(f"\nAre you sure you want to delete these {len(broken_files)} files? (y/N): ")

        if confirm.lower() == 'y':
            for filename, _ in broken_files:
                # Delete from website/content/stories/
                p = os.path.join(stories_dir, filename)
                if os.path.exists(p):
                    os.remove(p)

            print(f"\nDeleted {len(broken_files)} files. Now you can run 'make convert' to re-convert them.")
        else:
            print("\nDeletion cancelled.")
    else:
        print(f"\nRun with --delete to delete these {len(broken_files)} files.")

if __name__ == "__main__":
    main()

# UtopiaStories Archive Parser

A clean, searchable archive of stories parsed from UtopiaStories. This project exists to preserve a collection of stories after the original website temporarily went down in 2022.

## Purpose

The original website [UtopiaStories](https://utopiastories.com) temporarily went down in 2022. During that time, the maintainer lost access to their favorite stories used for bedtime reading. This project was created to keep a copy of those stories, ensuring they remain accessible for personal reading and preservation.

All credits and original rights belong to the author of UtopiaStories (webmaster@utopiastories.com). This project is an archival effort to preserve content that is important to its readers.

**Adult Content Warning:** This site contains adult/explicit content intended for mature audiences.

## Project Structure

- `stories/`: Contains the raw parsed stories in Markdown format (committed to the repository).
- `website/`: A Hugo-based website that displays the stories in a clean, searchable format.
- `parse_stories.py`: Script to fetch and parse stories from the original website.
- `convert_stories.py`: Script to convert raw stories into the Hugo-compatible format for the website.
- `extract_urls.py`: Script to extract story URLs from the main site.
- `Makefile`: Automates the parsing, conversion, and building process.

## How to Deploy Your Own Copy

### Prerequisites

- Python 3.x
- [Hugo](https://gohugo.io/) (extended version recommended)
- `pip` (Python package manager)

### Installation

1. Clone the repository and initialize submodules (for the website theme):
   ```bash
   git clone <repository-url>
   cd utopiastories-parser
   git submodule update --init --recursive
   ```

2. Set up the environment and install dependencies:
   ```bash
   make venv
   ```

### Parsing and Building

1. **Parse Stories:** To fetch new stories from the original site (if available):
   ```bash
   make parse
   ```
   Note: This uses `parse_stories.py` and respects a delay between requests to be polite to the server.

2. **Convert for Website:** Convert the raw `stories/*.md` files into `website/content/stories/*.md`:
   ```bash
   make convert
   ```

3. **Build the Website:** Generate the static site files:
   ```bash
   make build
   ```
   The output will be in `website/public/`.

4. **Local Preview:** You can run a local Hugo server to preview the site:
   ```bash
   cd website
   hugo server
   ```

## License and Copyright

Stories are copyrighted by the respective authors. Duplication of any kind is prohibited without consent. The code in this repository is provided for archival and educational purposes.

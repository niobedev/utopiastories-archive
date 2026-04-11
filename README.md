# 🌌 UtopiaStories Archive Parser

[![Build and Release Archive](https://github.com/victoria-shayner/utopiastories-parser/actions/workflows/release.yml/badge.svg)](https://github.com/victoria-shayner/utopiastories-parser/actions/workflows/release.yml)

> A high-performance parser and modern web archive for preserving adult stories from UtopiaStories.

## 📜 Purpose

In 2022, the original website **[UtopiaStories](https://utopiastories.com)** temporarily went offline. This project was born from a desire to preserve a curated collection of bedtime stories that were nearly lost. 

This repository contains the tools to scrape, clean, and re-host these stories in a modern, searchable, and responsive archive. All credits and original rights belong to the webmaster of UtopiaStories (webmaster@utopiastories.com).

> 🔞 **Adult Content Warning:** This site contains adult/explicit content intended for mature audiences only.

## ✨ Features

- ⚡ **High-Speed Parsing:** Efficient Python-based scraper with failure tracking and polite request delays.
- 🔍 **Fast Search:** Integrated search functionality with debounced input and minimum character requirements for performance.
- 📱 **Responsive Design:** Based on the clean and minimalist `PaperMod` Hugo theme.
- 🎨 **Smart Markdown Correction:** Automatic detection and fixing of common formatting issues (broken italics, malformed author's notes).
- 🏷️ **Rich Metadata:** Stories include author tags, original publication dates, and links to the original source.
- 🚀 **One-Click Deployment:** GitHub Actions workflow automatically builds the site and creates a deployable archive on every push.

## 📂 Project Structure

- `stories/` - Raw Markdown files parsed from the original site (committed).
- `website/` - The Hugo-based web frontend.
- `parse_stories.py` - The main scraping engine with 404 tracking.
- `convert_stories.py` - Bridge script to move raw data into the web directory.
- `detect_broken_markdown.py` - Quality control utility for fixing formatting.
- `Makefile` - The automation hub for all common tasks.

## 🛠️ Quick Start

### 1. Prerequisites
- **Python 3.x** & `pip`
- **[Hugo Extended](https://gohugo.io/installation/)** (v0.120+ recommended)
- **Make** (optional, but highly recommended)

### 2. Installation
```bash
# Clone the repository and its theme submodule
git clone https://github.com/victoria-shayner/utopiastories-parser.git
cd utopiastories-parser
git submodule update --init --recursive

# Set up the Python virtual environment
make venv
```

## ⚙️ Usage Workflow

The project is designed to be managed via `make` commands:

### Step 1: Parsing
Fetch new stories that aren't already in your `stories/` folder:
```bash
make parse
```
*Failed URLs (404s) are tracked in `failed_urls.json` to avoid redundant requests.*

### Step 2: Quality Control
Before publishing, check if any stories have rendering issues:
```bash
# Detect broken formatting
python3 detect_broken_markdown.py

# Delete identified broken files (optional, allows re-parsing)
python3 detect_broken_markdown.py --delete
```

### Step 3: Conversion & Build
Prepare the data for Hugo and generate the static site:
```bash
# Sync stories to the website directory
make convert

# Build the site and create a .tar.gz archive
make build
```

### Step 4: Local Preview
```bash
cd website
hugo server
```

## 🚢 Deployment

1. **GitHub Actions:** Every push to `master` automatically creates a new GitHub Release with a `website-archive.tar.gz` asset.
2. **Manual:** Run `make build` and upload the contents of the generated `website-archive.tar.gz` to your web server's root.

## ⚖️ License & Copyright

**Stories are copyrighted by their respective authors.** Duplication of any kind is prohibited without express consent from the original creators. This software is provided for archival and educational purposes.

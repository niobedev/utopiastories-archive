# 🌌 UtopiaStories Archive

[![Build and Publish](https://github.com/niobedev/utopiastories-archive/actions/workflows/build-and-publish.yml/badge.svg)](https://github.com/niobedev/utopiastories-archive/actions/workflows/build-and-publish.yml)
![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)

A serverless web archive of stories preserved from [UtopiaStories](https://utopiastories.com/).

**Live Website:** https://utopiastories.housetoral.uk

> 🔞 This site contains adult content intended for mature audiences only.

## 📜 Purpose

In 2022 the original **[UtopiaStories](https://utopiastories.com)** website temporarily went offline. This project was born from a desire to preserve a curated collection of stories that were nearly lost.

This repository contains the tools that scraped, cleaned, and re-host these stories in a modern, searchable, responsive archive. All credits and original rights belong to the webmaster of UtopiaStories (webmaster@utopiastories.com).

> **This is a frozen archive.** The original site is no longer updated, so there is no automatic sync — the content set is fixed. The site is rebuilt and redeployed only when the templates or configuration change.

## ✨ Features

- 🔍 **Fast Search** — Client-side Fuse.js search across all story titles, authors, and tags.
- 📱 **Responsive** — Clean, mobile-friendly design based on the `PaperMod` Hugo theme.
- 🏷️ **Rich Metadata** — Browse by tags or authors; each story links back to its original source.
- 🚀 **Serverless** — Builds and deploys entirely on GitHub's infrastructure (GitHub Pages).
- 📦 **Versioned Releases** — Every build publishes a downloadable archive.

## 📂 Project Structure

```
stories/                # Raw HTML from utopiastories.com (committed)
website/                # Hugo static site
  content/stories/      # Markdown stories
  layouts/              # Custom templates
  assets/               # Custom CSS/JS (search, tag styling)
  static/CNAME          # Custom domain for GitHub Pages
download_stories.py     # Scraping engine with 404 tracking
convert_to_markdown.py  # Bridge: raw HTML → Hugo markdown
detect_broken_markdown.py # Quality-control utility
extract_urls.py         # URL discovery (manual operation)
story_urls.json         # Story URL database
failed_urls.json        # Tracks 404s to avoid redundant requests
Makefile                # Automation hub for common tasks
.github/workflows/
  build-and-publish.yml # Runs on push to main: build → deploy to Pages → release
```

## 🛠️ Development

### Prerequisites
- **Python 3.x** & `pip`
- **[Hugo Extended](https://gohugo.io/installation/)** 0.146+
- **Make** (optional, recommended)

### Setup
```bash
# Clone with the theme submodule
git clone --recurse-submodules https://github.com/niobedev/utopiastories-archive.git
cd utopiastories-archive

# Set up the Python virtual environment
make venv
```

### Common tasks
```bash
# Download any stories not already in stories/ (404s tracked in failed_urls.json)
make download

# Quality control: detect (and optionally delete) broken markdown for re-parsing
python3 detect_broken_markdown.py
python3 detect_broken_markdown.py --delete

# Convert raw HTML into the website content directory
make convert

# Build the static site (also creates website-archive.tar.gz)
make build

# Local preview
cd website && hugo server
```

## 🚢 Deployment

### GitHub Pages (default)
The site deploys automatically to https://utopiastories.housetoral.uk on every push to `main`
via [`build-and-publish.yml`](.github/workflows/build-and-publish.yml): Hugo builds the site,
deploys it to GitHub Pages, and publishes a release archive. No server required.

### Manual / VPS
Download `website-archive.tar.gz` from the latest release and extract it to your web root:
```bash
wget <release-asset-url> -O website-archive.tar.gz
tar -xzf website-archive.tar.gz
cp -r public/* /var/www/utopia/
```

## ⚖️ License & Copyright

This project (the parser and tooling) is licensed under the [BSD-3-Clause License](LICENSE).

**Stories are copyrighted by their respective authors.** This software is provided for archival
purposes only. All rights belong to the original authors and UtopiaStories.

# Web Resource Manager

A simple web-based resource management tool built with HTML, CSS, and JavaScript.

## Features

- Clean and responsive user interface
- Dynamic content loading
- Easy configuration via JSON files
- SEO-friendly with sitemap and robots.txt support
- GitHub Pages deployment ready

## Tech Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Backend**: Python (for data processing)
- **Deployment**: GitHub Actions + GitHub Pages
- **Data Format**: JSON

## Project Structure

```
/
├── index.html          # Main page
├── config.json         # Configuration file
├── data.json           # Data storage
├── sitemap.xml         # Site map for search engines
├── robots.txt          # Crawling rules
├── collector.py        # Data processor
└── .github/workflows/  # CI/CD configuration
```

## Setup

1. Clone the repository
2. Edit `config.json` to customize settings
3. Push changes to trigger automatic deployment

## Configuration

The main configuration is stored in `config.json`. Modify this file to adjust:
- Site domain and protocol
- Data sources (if applicable)
- Update intervals
- Display preferences

## Deployment

This project uses GitHub Actions for automatic deployment. Changes to configuration files will automatically trigger updates.

## License

MIT License
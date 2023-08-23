# Manga Panel Scraping API

This FastAPI-based API lets you retrieve manga panel links by providing manga name, chapter number, and page number. It uses web scraping to fetch data from `https://batocomic.com`.

## Setup

1. Clone the repo: `git clone https://github.com/your-username/manga-panel-scraping-api.git`
2. Install packages: `pip install -r requirements.txt`
3. Run the server: `uvicorn main:app --host 0.0.0.0 --port 8000`

For testing: `uvicorn main:app --reload`

## Usage

Make requests to available endpoints:

-   `/get_series_link`: Retrieve series link by search query.
-   `/get_chapters`: Get available chapters info by series URL.
-   `/get_image_link`: Get image link by chapter URL and page number.
-   `/get_manga_panel_link`: Get image link by manga name, chapter, and page number.

There are also separated scripts in the `scripts` folder.

## Dependencies

-   FastAPI
-   requests
-   beautifulsoup4

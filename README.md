# Manga Panel Scraping API

This FastAPI-based API lets you retrieve manga panel links by providing manga name, chapter number, and page number. It uses web scraping to fetch data from `https://batocomic.com`.

## Setup

1. Clone the repo: `git clone https://github.com/LuizBudeu/manga-panel-scraper.git`
2. Install packages: `pip install -r requirements.txt`
3. Run the server: `uvicorn main:app`

For testing: `uvicorn main:app --reload`

## Usage

Make requests to available endpoints:

-   `/get_series_link`: Retrieve series link by search query.

    -   Method: GET
    -   Parameters:
        -   `search_query`: Manga name search query
    -   Example request:
        ```
        GET /get_series_link?search_query=skip and loafer
        ```

-   `/get_chapters`: Get chapter info by series URL (link).

    -   Method: GET
    -   Parameters:
        -   `series_url`: Series URL (link)
    -   Example request:
        ```
        GET /get_chapters?series_url=/series/86788/skip-to-loafer
        ```

-   `/get_images_links`: Get images links by chapter URL and page numbers.

    -   Method: GET
    -   Parameters:
        -   `chapter_url`: Chapter URL
        -   `page_nums`: Page numbers
    -   Example request:
        ```
        GET /get_images_links?chapter_url=/chapter/1683038&page_nums=5,6,7
        ```

-   `/get_manga_panels_links`: Get images links by manga name, chapter, and page numbers. This endpoint takes ~25 seconds (uses selenium to launch headless browser)
    -   Method: GET
    -   Parameters:
        -   `manga_name`: Manga name search query
        -   `chapter`: Chapter number
        -   `page_nums`: Page numbers
    -   Example request:
        ```
        GET /get_manga_panels_links?manga_name=skip and loafer&chapter=37&page_nums=5,6,7
        ```

There are also separated scripts in the `scripts` folder.

## Dependencies

-   FastAPI
-   requests
-   beautifulsoup4
-   selenium

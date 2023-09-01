from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import time
import os
import asyncio
import re
from dotenv import load_dotenv


app = FastAPI()
BATO_URL = "https://batocomic.com"

load_dotenv()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add the origin of your React app
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to your FastAPI app!"}


@app.get("/get_series_link")
def get_series_link(search_query: str):
    search_url = f"{BATO_URL}/search?word={search_query.replace(' ', '+')}"
    
    response = requests.get(search_url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        series_list_div = soup.find("div", class_="series-list")
        
        if series_list_div:
            # Find all results that match the search query
            matching_results = series_list_div.find_all("div", class_="item-text") # type: ignore
            
            for result in matching_results:
                manga_name_anchor = result.find("a")
                if manga_name_anchor and manga_name_anchor.text.strip().lower() == search_query.lower():
                    series_link = result.find("a")["href"]

                    return {"search_query": search_query, "series_link": series_link}
            
            # If no exact match, get the first result
            first_result = series_list_div.find("div", class_="col item line-b no-flag") # type: ignore
            if first_result:
                series_link = first_result.find("a")["href"] # type: ignore
                return {"search_query": search_query, "series_link": series_link}
    
    return {"error": f"No search result found for {search_query}"}
    

@app.get("/get_chapters")
async def get_chapters(series_url: str):
    search_url = f"{BATO_URL}{series_url}"
    response = requests.get(search_url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        chapter_tags = soup.find_all("a", class_="visited chapt")
        
        chapters = []
        for chapter in chapter_tags:
            chapter_title = chapter.text
            chapter_link = chapter["href"]
            chapters.append({"title": chapter_title, "link": chapter_link})
        
        return {"series_url": series_url, "chapters": chapters}
    else:
        return {"error": f"Failed to fetch the manga page for {series_url}"}
    
    
@app.get("/get_images_links")
async def get_images_links(chapter_url: str, page_nums: str): # type: ignore
    async def download_panel(panel, index):
        img_element = panel.find_element(By.TAG_NAME, "img")
        img_url = img_element.get_attribute("src")

        if index + 1 in page_nums:
            return {"image_link": img_url, "page_num": index + 1}
        else:
            return None
        
    search_url = f"{BATO_URL}{chapter_url}"
        
    page_nums: list[int] = [int(num) for num in page_nums.split(",")]
    
    # Configure Selenium to use the Chrome WebDriver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.headless = True  # Run Chrome in headless mode (no UI)
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(search_url)
        
        # Find the main container of manga panels
        panel_container = driver.find_element(By.ID, "viewer")
    
        # Find all div tags with class 'item invisible' within the panel container
        panel_elements = panel_container.find_elements(By.CSS_SELECTOR, "div.item.invisible")
    
        # Use asyncio to concurrently get image links
        tasks = []
        for index, panel in enumerate(panel_elements):
            if index + 1 in page_nums:
                task = asyncio.create_task(download_panel(panel, index)) # type: ignore
                tasks.append(task)
    
        image_links = await asyncio.gather(*tasks)
    
        return {"chapter_url": chapter_url, "image_links": image_links}
    
    finally:
        driver.quit()


@app.get("/get_manga_panels_links")
def get_manga_panels_links(manga_name: str, chapter: int, page_nums: str):
    
    # Get the series link based on the manga name
    series_response = requests.get(f"http://127.0.0.1:8000/get_series_link?search_query={manga_name}")
    
    if series_response.status_code != 200:
        return {"error": f"Failed to retrieve series link, code: {series_response.status_code}. Args: {manga_name=}"}
    
    series_data = series_response.json()
    series_link = series_data["series_link"]
    
    # Get the chapters for the series
    chapters_response = requests.get(f"http://127.0.0.1:8000/get_chapters?series_url={series_link}")
    
    if chapters_response.status_code != 200:
        return {"error": f"Failed to retrieve chapters, code: {chapters_response.status_code}. Args: {series_link=}"}
    
    chapters_data = chapters_response.json()
    
    # Filter the chapter data to find the desired chapter
    chapter_pattern = re.compile(rf"Chapter 0*{chapter}\b", re.IGNORECASE)
    target_chapter = next((ch for ch in chapters_data["chapters"] if re.search(chapter_pattern, ch["title"])), None)

    if not target_chapter:
        return {"error": f"Chapter {chapter} not found. Available chapters: {', '.join(ch['title'] for ch in chapters_data['chapters'])}"}
    
    chapter_url = target_chapter["link"]
    
    # Get the image link for the specified page number
    image_link_response = requests.get(f"http://127.0.0.1:8000/get_images_links?chapter_url={chapter_url}&page_nums={page_nums}")
    
    if image_link_response.status_code != 200:
        return {"error": f"Failed to retrieve manga panel link, code: {image_link_response.status_code}. Args: {chapter_url=}, {page_nums=}"}
    
    image_link_data = image_link_response.json()

    return {
        "manga_name": manga_name,
        "series_link": series_link,
        "chapter": chapter,
        "chapter_url": chapter_url,
        "page_nums": page_nums,
        "image_links": image_link_data["image_links"],
    }
    
    
@app.get("/proxy_mal")
def proxy_mal(user_name: str):
    mal_url = f"https://api.myanimelist.net/v2/users/{user_name}/mangalist?fields=list_status&limit=10" # todo make limit bigger

    response = requests.get(mal_url, headers={"X-MAL-CLIENT-ID": f"{os.environ.get('MAL_CLIENT_ID')}"})
    
    return response.json()

from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import time
import os
import asyncio
import re


app = FastAPI()
BATO_URL = "https://batocomic.com"


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
            first_result = series_list_div.find("div", class_="col item line-b no-flag") # type: ignore
            if first_result:
                series_link = first_result.find("a")["href"] # type: ignore
                return {"search_query": search_query, "series_link": series_link}
    
    return {"error": "No search result found"}


@app.get("/get_chapters")
async def get_chapters(url: str):
    search_url = f"{BATO_URL}{url}"
    response = requests.get(search_url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        chapter_tags = soup.find_all("a", class_="visited chapt")
        
        chapters = []
        for chapter in chapter_tags:
            chapter_title = chapter.text
            chapter_link = chapter["href"]
            chapters.append({"title": chapter_title, "link": chapter_link})
        
        return {"url": url, "chapters": chapters}
    else:
        return {"error": "Failed to fetch the manga page"}
    
    
@app.get("/get_image_link")
async def get_image_link(chapter_url: str, page_nums: str): # type: ignore
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


@app.get("/get_manga_panel_link")
def get_manga_panel_link(manga_name: str, chapter: int, page_nums: str):
    # Get the series link based on the manga name
    series_response = requests.get(f"http://127.0.0.1:8000/get_series_link?search_query={manga_name}")
    
    if series_response.status_code != 200:
        return {"error": f"Failed to retrieve series link, code: {series_response.status_code}. Args: {manga_name=}"}
    
    series_data = series_response.json()
    series_link = series_data["series_link"]
    
    # Get the chapters for the series
    chapters_response = requests.get(f"http://127.0.0.1:8000/get_chapters?url={series_link}")
    
    if chapters_response.status_code != 200:
        return {"error": f"Failed to retrieve chapters, code: {chapters_response.status_code}. Args: {series_link=}"}
    
    chapters_data = chapters_response.json()
    
    # Filter the chapter data to find the desired chapter
    chapter_pattern = re.compile(rf"Chapter {chapter}\b", re.IGNORECASE)
    target_chapter = next((ch for ch in chapters_data["chapters"] if re.search(chapter_pattern, ch["title"])), None)
                
    if not target_chapter:
        return {"error": f"Chapter {chapter} not found. Available chapters: {', '.join(ch['title'] for ch in chapters_data['chapters'])}"}
    
    chapter_url = target_chapter["link"]
    
    # Get the image link for the specified page number
    image_link_response = requests.get(f"http://127.0.0.1:8000/get_image_link?chapter_url={chapter_url}&page_nums={page_nums}")
    
    if image_link_response.status_code != 200:
        return {"error": f"Failed to retrieve manga panel link, code: {image_link_response.status_code}. Args: {chapter_url=}, {page_nums=}"}
    
    image_link_data = image_link_response.json()

    return {
        "manga_name_search_query": manga_name,
        "series_link": series_link,
        "chapter": chapter,
        "chapter_url": chapter_url,
        "page_nums": page_nums,
        "image_links": image_link_data["image_links"],
    }
    
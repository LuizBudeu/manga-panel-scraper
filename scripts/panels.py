from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import time
import os
import asyncio

# URL of the manga chapter page
chapter_url = "https://batocomic.com/chapter/2314765"

# Create a directory to store the downloaded manga panels
output_directory = "imgs"
os.makedirs(output_directory, exist_ok=True)


async def download_panel(panel, index, page_num):
    img_element = panel.find_element(By.TAG_NAME, "img")
    img_url = img_element.get_attribute("src")

    img_response = requests.get(img_url)

    if img_response.status_code == 200:
        if index + 1 == page_num:
            # Save the image to the output directory
            img_filename = f"panel_{index + 1}.jpg"
            img_path = os.path.join(output_directory, img_filename)

            with open(img_path, "wb") as img_file:
                img_file.write(img_response.content)
            print(f"Downloaded panel {index + 1}")
        else:
            print(f"Skipping panel {index + 1}")
    else:
        print(f"Failed to download panel {index + 1}")


async def main(page_num):
    # Configure Selenium to use the Chrome WebDriver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.headless = True  # Run Chrome in headless mode (no UI)
    driver = webdriver.Chrome(options=chrome_options)

    # Load the chapter page
    driver.get(chapter_url)

    # Find the main container of manga panels
    panel_container = driver.find_element(By.ID, "viewer")

    # Find all div tags with class 'item invisible' within the panel container
    panel_elements = panel_container.find_elements(By.CSS_SELECTOR, "div.item.invisible")

    # Use asyncio to concurrently download manga panels
    tasks = []
    for index, panel in enumerate(panel_elements):
        if index + 1 == page_num:
            task = asyncio.create_task(download_panel(panel, index, page_num))
            tasks.append(task)

    await asyncio.gather(*tasks)

    # Close the WebDriver
    driver.quit()

if __name__ == "__main__":
    page_to_download = 5  # Change this to the desired page number
    asyncio.run(main(page_to_download))
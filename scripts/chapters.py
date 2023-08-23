import requests
from bs4 import BeautifulSoup

# URL of the manga page
url = "https://batocomic.com/series/86788/skip-to-loafer"

# Send an HTTP GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content of the page using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all anchor tags with class 'visited chapt'
    chapter_tags = soup.find_all("a", class_="visited chapt")

    # Print the chapter titles and links
    for chapter in chapter_tags:
        chapter_title = chapter.text
        chapter_link = chapter["href"]
        print(f"Chapter: {chapter_title} - Link: {chapter_link}")

else:
    print("Failed to fetch the manga page")

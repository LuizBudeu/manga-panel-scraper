import asyncio
import requests
from bs4 import BeautifulSoup

async def get_series_link(search_query: str):
    search_url = f"https://batocomic.com/search?word={search_query.replace(' ', '+')}"
    
    response = requests.get(search_url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        series_list_div = soup.find("div", class_="series-list")
        
        if series_list_div:
            first_result = series_list_div.find("div", class_="col item line-b no-flag")
            if first_result:
                series_link = first_result.find("a")["href"]
                return series_link
    
    return None

async def main():
    search_query = "skip and loafer"
    series_link = await get_series_link(search_query)
    
    if series_link:
        print(f"Series Link: {series_link}")
    else:
        print("No search result found.")

if __name__ == "__main__":
    asyncio.run(main())

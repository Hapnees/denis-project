from bs4 import BeautifulSoup, Tag
from typing import TypedDict, List
import requests

class Book(TypedDict):
    title: str
    price: int
    link: str
    img_link: str
    
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
    'Referer': 'https://google.com',
    'Accept-Language': 'ru-RU,ru;q=0.9'
}

async def parse(bookName: str):
    books: List[Book] = []

    url = 'https://book24.ru/search/?q={}'.format(bookName)

    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')

    books_container_element = soup.find('div', {"class": "search-result"})

    if not books_container_element or not isinstance(books_container_element, Tag):
        return []

    books_elements = books_container_element.find_all('div', {"class": "product-card"})

    if not books_elements:
        return []

    for book in books_elements:
        if not isinstance(book, Tag):
           continue
        
        title: str = str(book.get('data-name'))
        price: int = int(str(book.get('data-price')))
        book_id: str = str(book.get('data-product-id'))
        link: str = 'https://www.labirint.ru/books/{}/'.format(book_id)

        img_element = book.find("img")
        img_link: str = ''

        if img_element and isinstance(img_element, Tag):
            img_link = str(img_element.get("src"))

        books.append({
           "title": title,
           "price": price,
           "link": link,
           "img_link": img_link
       })

    return books

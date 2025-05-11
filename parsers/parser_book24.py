from bs4 import BeautifulSoup, Tag
from typing import TypedDict, List
import requests

class Book(TypedDict):
    title: str
    link: str
    price: int
    img_link: str

async def parse(book_name: str) -> List[Book]:
    books: List[Book] = []

    url = 'https://book24.ru/search/?q={}'.format(book_name)

    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    books_container_element = soup.find('div', {"class": "product-list"})

    if not books_container_element or not isinstance(books_container_element, Tag):
        return []

    books_elements = books_container_element.find_all('article', {"class": "product-card"})

    if not books_elements:
        return []

    for book in books_elements:
        if not isinstance(book, Tag):
            continue
        
        
        title: str = str(book.get('data-b24-name'))
        price: int = int(str(book.get('data-b24-price')))

        link_element = book.find('a')

        href = ''
        if isinstance(link_element, Tag):
            href: str = str(link_element.get('href'))

        link: str = "https://book24.ru" + href

        img_link: str = ''
        img_element = book.find("img")

        if img_element and isinstance(img_element, Tag):
            img_element_link = str(img_element.get("src", ""))
            if 'not-image' in img_element_link or 'no-product':
                img_element_link = ''

            img_link = "https:" + str(img_element.get("src", "")) if img_element_link else ''
        
        books.append({
           "title": title,
           "price": price,
           "link": link,
           "img_link": img_link
       })

    return books

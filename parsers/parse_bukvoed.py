
from bs4 import BeautifulSoup, Tag
from typing import TypedDict, List
import requests

class Book(TypedDict):
    title: str
    link: str
    price: int
    img_link: str

async def parse(bookName: str) -> List[Book]:
    books: List[Book] = []

    url = 'https://www.bookvoed.ru/search?q={}'.format(bookName)

    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')


    books_container_element = soup.find('div', {"class": "app-catalog__products"})

    if not books_container_element or not isinstance(books_container_element, Tag):
        return []

    books_elements = books_container_element.find_all('div', {"class": "product-card"})

    if not books_elements:
        return []

    for book in books_elements:
       if not isinstance(book, Tag):
           continue


       title: str = str(book.get('data-product-name', ''))

       price_discounted = str(book.get('data-product-price-discounted', ''))
       price_total = str(book.get('data-product-price-total', ''))
       price: int = int(price_discounted) if price_discounted else int(price_total)


       link_element = book.find('a')
       href = ''
       
       if isinstance(link_element, Tag):
        href = str(link_element.get('href'))
       
       link: str = "https://www.bookvoed.ru" + href 

       img_element = book.find('img')
       img_link = ''

       if img_element and isinstance(img_element, Tag):
          img_element_link = str(img_element.get("src"))
          if 'no-product' in img_element_link:
             img_element_link = ''
          img_link = img_element_link

       books.append({
           "title": title,
           "price": price,
           "link": link,
           "img_link": img_link
       })

    return books

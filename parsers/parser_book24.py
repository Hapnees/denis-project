# Импортируем BeautifulSoup для разбора HTML и Tag для проверки типа элементов
from bs4 import BeautifulSoup, Tag
# Импортируем типы для создания структуры данных книги
from typing import TypedDict, List
# Импортируем requests для отправки HTTP-запросов
import requests

# Определяем структуру данных для книги
class Book(TypedDict):
    title: str    # Название книги
    link: str     # Ссылка на страницу книги
    price: int    # Цена книги
    img_link: str # Ссылка на обложку
    external_id: str

class Options(TypedDict):
    sort: str | None

async def parse(book_name: str, options: Options) -> List[Book]:
    """
    Функция ищет книги на сайте Book24 по названию и возвращает список найденных книг.
    
    Что делает функция:
    1. Отправляет запрос на сайт Book24 с названием книги
    2. Получает HTML-страницу с результатами поиска
    3. Разбирает HTML и находит все карточки книг
    4. Из каждой карточки извлекает название, цену, ссылку и обложку
    5. Возвращает список всех найденных книг
    
    Аргументы:
        book_name (str): Название книги, которую ищем
            Например: "Война+и+мир" или "Гарри+Поттер"
            
    Возвращает:
        List[Book]: Список словарей с данными о книгах
            Каждый словарь содержит:
            - title: название книги
            - price: цена в рублях
            - link: ссылка на страницу книги
            - img_link: ссылка на изображение обложки
    """
    # Создаём пустой список для хранения найденных книг
    books: List[Book] = []

    sort = options['sort']
    # Формируем URL для поиска на сайте Book24
    url = 'https://book24.ru/search/?q={}'.format(book_name)

    if sort:
        url += '&' + sort

    # Отправляем GET-запрос на сайт и получаем HTML-страницу
    page = requests.get(url)
    # Создаём объект BeautifulSoup для разбора HTML
    soup = BeautifulSoup(page.text, 'html.parser')

    # Ищем контейнер, в котором находятся все карточки книг
    books_container_element = soup.find('div', {"class": "product-list"})

    # Если контейнер не найден или это не HTML-тег, возвращаем пустой список
    if not books_container_element or not isinstance(books_container_element, Tag):
        return []

    # Ищем все карточки книг внутри контейнера
    # На сайте Book24 карточки находятся в тегах <article>
    books_elements = books_container_element.find_all('article', {"class": "product-card"})

    # Если карточек не найдено, возвращаем пустой список
    if not books_elements:
        return []

    # Перебираем каждую карточку книги
    for book in books_elements:
        # Пропускаем элемент, если это не HTML-тег
        if not isinstance(book, Tag):
            continue
        
        # Получаем название книги из атрибута data-b24-name
        title: str = str(book.get('data-b24-name'))
        # Получаем цену из атрибута data-b24-price
        price: int = int(str(book.get('data-b24-price')))

        # Ищем ссылку на книгу (тег <a>)
        link_element = book.find('a')
        href = ''  # По умолчанию ссылка пустая
        external_id: str = str(book.get('data-b24-id'))
        
        # Если нашли тег <a>, берём из него ссылку
        if isinstance(link_element, Tag):
            href: str = str(link_element.get('href'))

        # Формируем полную ссылку, добавляя домен сайта
        link: str = "https://book24.ru" + href

        # Ищем изображение обложки (тег <img>)
        img_link: str = ''  # По умолчанию ссылка пустая
        img_element = book.find("img")


        # Если нашли тег <img>
        if img_element and isinstance(img_element, Tag):
            # Получаем ссылку на изображение
            img_element_link = str(img_element.get("data-src", ""))
            # Если это заглушка (нет изображения), используем пустую строку
            if 'not-image' in img_element_link or 'no-product':
                img_element_link = ''

            # Формируем полную ссылку на изображение, добавляя https:
            # Некоторые ссылки на изображения начинаются с //, поэтому добавляем https:
            img_link = ''
            if img_element_link:
                img_link = "https:" + img_element_link
        
        # Добавляем информацию о книге в список
        books.append({
           "title": title,      # Название книги
           "price": price,      # Цена
           "link": link,        # Ссылка на страницу
           "img_link": img_link, # Ссылка на обложку
           "external_id": external_id
       })

    # Возвращаем список всех найденных книг
    print('book24 books PARSED')
    return books
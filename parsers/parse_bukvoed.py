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

async def parse(bookName: str, options: Options) -> List[Book]:
    """
    Функция ищет книги на сайте Буквоед по названию и возвращает список найденных книг.
    
    Что делает функция:
    1. Отправляет запрос на сайт Буквоед с названием книги
    2. Получает HTML-страницу с результатами поиска
    3. Разбирает HTML и находит все карточки книг
    4. Из каждой карточки извлекает название, цену, ссылку и обложку
    5. Возвращает список всех найденных книг
    
    Аргументы:
        bookName (str): Название книги, которую ищем
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

    # Формируем URL для поиска на сайте Буквоед
    url = 'https://www.bookvoed.ru/search?q={}'.format(bookName)

    sort = options['sort']

    if sort:
        url += '&' + sort

    # Отправляем GET-запрос на сайт и получаем HTML-страницу
    page = requests.get(url)
    # Создаём объект BeautifulSoup для разбора HTML
    soup = BeautifulSoup(page.text, 'html.parser')

    # Ищем контейнер, в котором находятся все карточки книг
    books_container_element = soup.find('div', {"class": "app-catalog__products"})

    # Если контейнер не найден или это не HTML-тег, возвращаем пустой список
    if not books_container_element or not isinstance(books_container_element, Tag):
        return []

    # Ищем все карточки книг внутри контейнера
    books_elements = books_container_element.find_all('div', {"class": "product-card"})

    # Если карточек не найдено, возвращаем пустой список
    if not books_elements:
        return []

    # Перебираем каждую карточку книги
    for book in books_elements:
        # Пропускаем элемент, если это не HTML-тег
        if not isinstance(book, Tag):
            continue

        # Получаем название книги из атрибута data-product-name
        title: str = str(book.get('data-product-name', ''))

        # Получаем цену со скидкой (если есть)
        price_discounted = str(book.get('data-product-price-discounted', ''))
        # Получаем обычную цену
        price_total = str(book.get('data-product-price-total', ''))
        # Используем цену со скидкой, если она есть, иначе обычную цену
        price: int = int(price_discounted) if price_discounted else int(price_total)
        external_id: str = str(book.get('data-product-item-id'))

        # Ищем ссылку на книгу (тег <a>)
        link_element = book.find('a')
        href = ''  # По умолчанию ссылка пустая
        
        # Если нашли тег <a>, берём из него ссылку
        if isinstance(link_element, Tag):
            href = str(link_element.get('href'))
        
        # Формируем полную ссылку, добавляя домен сайта
        link: str = "https://www.bookvoed.ru" + href 

        # Ищем изображение обложки (тег <img>)
        img_element = book.find('img')
        img_link = ''  # По умолчанию ссылка пустая

        # Если нашли тег <img>
        if img_element and isinstance(img_element, Tag):
            # Получаем ссылку на изображение
            img_element_link = str(img_element.get("src"))
            # Если это заглушка (нет изображения), используем пустую строку
            if 'no-product' in img_element_link:
                img_element_link = ''
            img_link = img_element_link

        # Добавляем информацию о книге в список
        books.append({
            "title": title,      # Название книги
            "price": price,      # Цена
            "link": link,        # Ссылка на страницу
            "img_link": img_link, # Ссылка на обложку
            "external_id": external_id
        })

    # Возвращаем список всех найденных книг
    print('bukvoed books PARSED')
    return books
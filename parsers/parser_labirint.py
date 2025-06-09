# Импортируем BeautifulSoup для разбора HTML и Tag для проверки типа элементов
from bs4 import BeautifulSoup, Tag
# Импортируем типы для создания структуры данных книги
from typing import TypedDict, List
# Импортируем requests для отправки HTTP-запросов
import requests

# Определяем структуру данных для книги
class Book(TypedDict):
    title: str    # Название книги
    price: int    # Цена книги
    link: str     # Ссылка на страницу книги
    img_link: str # Ссылка на обложку
    external_id: str

class Options(TypedDict):
    sort: str | None

# Заголовки для HTTP-запроса, чтобы сайт думал, что запрос идёт от браузера
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
    'Referer': 'https://google.com',
    'Accept-Language': 'ru-RU,ru;q=0.9'
}

async def parse(book_name: str, options: Options) -> List[Book]:
    """
    Функция ищет книги на сайте Лабиринт по названию и возвращает список найденных книг.
    
    Что делает функция:
    1. Отправляет запрос на сайт Лабиринт с названием книги
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

    # Формируем URL для поиска на сайте Лабиринт
    url = 'https://www.labirint.ru/search/{}/'.format(book_name)

    if sort:
        url += '&' + sort

    # Отправляем GET-запрос на сайт и получаем HTML-страницу
    # Передаём заголовки, чтобы сайт думал, что запрос идёт от браузера
    try:
        page = requests.get(url, timeout=10)
        # Создаём объект BeautifulSoup для разбора HTML
        soup = BeautifulSoup(page.text, 'html.parser')

        # Ищем контейнер, в котором находятся все карточки книг
        books_container_element = soup.find('div', {"class": "search-result"})

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
            
            # Ищем название книги (тег <a> с классом product-title)
            title_element = book.find('a', {"class": "product-title"})
            title: str = ''  # По умолчанию название пустое
            
            # Если нашли тег с названием и это действительно тег
            if title_element and isinstance(title_element, Tag):
                # Получаем текст из тега, убираем лишние пробелы
                title = title_element.text.strip()
            
            # Ищем цену книги (тег <span> с классом price)
            price_element = book.find('span', {"class": "price"})
            price: int = 0  # По умолчанию цена 0
            
            # Если нашли тег с ценой и это действительно тег
            if price_element and isinstance(price_element, Tag):
                # Получаем текст из тега, убираем лишние пробелы и символы
                # Заменяем '₽' на пустую строку и убираем пробелы
                price_text = price_element.text.strip().replace('₽', '').strip()
                # Преобразуем текст цены в целое число
                price = int(price_text) if price_text else 0

            # Ищем ссылку на книгу (тег <a> с классом product-title)
            link_element = book.find('a', {"class": "product-title"})
            href: str = ''  # По умолчанию ссылка пустая
            external_id: str = str(book.get('data-product-id'))
            
            # Если нашли тег с ссылкой и это действительно тег
            if link_element and isinstance(link_element, Tag):
                # Получаем атрибут href из тега
                href = str(link_element.get('href', ''))
            
            # Формируем полную ссылку на книгу, добавляя домен
            # Например: https://www.labirint.ru/books/123456
            link: str = "https://www.labirint.ru" + href

            # Ищем изображение обложки (тег <img>)
            img_link: str = ''  # По умолчанию ссылка пустая
            img_element = book.find("img")

            # Если тег <img> найден и это действительно тег
            if img_element and isinstance(img_element, Tag):
                # Получаем ссылку на изображение из атрибута src
                img_link = str(img_element.get("data-src", ""))
            
            # Добавляем всю собранную информацию о книге в список
            books.append({
            "title": title,      # Название книги
            "price": price,      # Цена
            "link": link,        # Ссылка на страницу
            "img_link": img_link, # Ссылка на обложку
            "external_id": external_id
        })

        # Возвращаем список всех найденных книг
        print('labirint books PARSED')
        return books
    except:
        return []
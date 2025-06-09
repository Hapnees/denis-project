# Импорт модуля asyncio для асинхронного выполнения операций
# asyncio позволяет выполнять несколько задач одновременно без блокировки основного потока
import asyncio

import yaml

# Импорт парсеров для различных книжных магазинов
# parse_bukvoed - парсер для магазина Буквоед
# parser_labirint - парсер для магазина Лабиринт
# parser_book24 - парсер для магазина Book24
# parse_book_name - утилита для подготовки названий книг к поиску
from parsers import parse_bukvoed, parser_labirint, parser_book24, parse_book_name

# Импорт основных компонентов FastAPI
# FastAPI - основной класс для создания веб-приложения
# Request - класс для обработки HTTP-запросов
from fastapi import FastAPI, Request, Depends

# Импорт компонента для работы с HTML-шаблонами
# Jinja2Templates позволяет рендерить HTML-страницы с использованием шаблонов
from fastapi.templating import Jinja2Templates

# Импорт компонента для работы со статическими файлами
# StaticFiles позволяет обслуживать статические файлы (CSS, JavaScript, изображения)
from fastapi.staticfiles import StaticFiles

# Импорт функции reduce из модуля functools
# reduce используется для последовательного применения функции к элементам списка
from functools import reduce 

# Импорт роутера для аутентификации
# router2 содержит все маршруты, связанные с авторизацией и регистрацией
from auth.router import router as user_router
from books.router import router as book_router

# Импорт функции инициализации базы данных
# init_db создает необходимые таблицы при запуске приложения
from database.database import init_db
from database import database

from auth.models import UserModel
from auth.service import get_current_user
from books.models import BookModel
from books.dto import BookStatus

from sqlalchemy import select
from parsers.adapters import BOOK24_MAPPINGS, BUKVOED_MAPPINGS, LABIRINT_MAPPIGNS
from parsers.parse_query_params import parse_query_sort

with open("config.yaml") as file:
    config = yaml.safe_load(file)

API_URL = config['api-url']

# Создание экземпляра шаблонизатора
# directory="templates" указывает путь к директории с HTML-шаблонами
templates = Jinja2Templates(directory="templates")

# Создание экземпляра FastAPI приложения
# app будет основным объектом для определения маршрутов и middleware
app = FastAPI()

# Декоратор для обработки события запуска приложения
# Функция startup выполняется при старте сервера
@app.on_event("startup")
async def startup():
    # Инициализация базы данных при запуске
    # await используется для асинхронного вызова функции
    await init_db()

# Подключение роутера аутентификации к основному приложению
app.include_router(user_router)
app.include_router(book_router)

# Монтирование статических файлов
# Все файлы из директории "static" будут доступны по URL /static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Обработчик GET-запроса для главной страницы
# request: Request - объект запроса, содержащий информацию о HTTP-запросе
@app.get("/")
async def home(request: Request):
    # Рендеринг шаблона index.html
    # {"request": request} - контекст для шаблона, необходимый для генерации URL
    return templates.TemplateResponse("index.html", {"request": request, "api_url": API_URL})

# Обработчик GET-запроса для страницы аутентификации
# Возвращает страницу с формами входа и регистрации
@app.get("/auth")
async def auth_page(request: Request):
    # Рендеринг шаблона auth.html
    return templates.TemplateResponse("auth.html", {"request": request, "api_url": API_URL})

# Обработчик GET-запроса для поиска книг
# Принимает параметр query из URL и выполняет поиск по всем магазинам
@app.get("/search")
async def find_books(request: Request):
    # Получение параметра query из URL
    # Если параметр отсутствует, используется пустая строка
    query = request.query_params.get("query") or ""
    sort = request.query_params.get("sort") or None
    resources = request.query_params.getlist("resources") or None

    if not resources or len(resources) == 0:
        resources = ['bukvoed', 'book24', 'labirint']
    
    # Подготовка запроса для поиска
    # parse_book_name обрабатывает название книги для использования в URL
    parsed_query = parse_book_name.parse_book_name(query)

    bukvoed_sort = BUKVOED_MAPPINGS[sort] if sort else None
    book24_sort = BOOK24_MAPPINGS[sort] if sort else None
    labirint_sort = LABIRINT_MAPPIGNS[sort] if sort else None

    # Параллельный запуск парсеров для всех магазинов
    # asyncio.gather выполняет все парсеры одновременно

    requests = []

    if resources:
        if 'bukvoed' in resources:
            requests.append(parse_bukvoed.parse(parsed_query, {"sort": bukvoed_sort }))
        if 'book24' in resources:
            requests.append(parser_book24.parse(parsed_query, {"sort": book24_sort }))
        if 'labirint' in resources:
            requests.append(parser_labirint.parse(parsed_query, {"sort": labirint_sort }))

    books = await asyncio.gather(*requests)

    # Объединение результатов всех парсеров в один список
    # reduce последовательно объединяет списки книг
    flatten_books = reduce(lambda a, b: a+b, books)
    filtered_books = filter(lambda book: book['price'], flatten_books)

    sort_param = parse_query_sort(sort)

    sorted_books = sorted(filtered_books, key=lambda book: book[sort_param['value']], reverse=sort_param['direction'] == 'desc') if sort_param else filtered_books


    # Рендеринг шаблона с результатами поиска
    # Передаем список книг и исходный запрос в контекст шаблона
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "books": sorted_books, 
            "query": query,
            "sort": sort or "",
            "resources": resources or "",
            "api_url": API_URL
        }
    )

@app.get('/account')
async def account_page(session: database.SessionDep, request: Request, user: UserModel = Depends(get_current_user)):
    tab_param = request.query_params.get("tab")

    status: str | None = None
    if tab_param and "-" in tab_param:
        status = tab_param.split("-")[1]

    where_clauses = []
    where_clauses.append(BookModel.user_id == user.id)

    if status:
        where_clauses.append(BookModel.status == BookStatus[status.upper()])

    books_query = await session.execute(select(BookModel).where(*where_clauses))
    books = books_query.scalars().all()

    serialized_books = [ {
        "id": book.id,
        "title": book.title,
        "link": book.link,
        "price": book.price,
        "img_link": book.img_link,
        "external_id": book.external_id,
        "status": book.status.value,
    } for book in books]

    return templates.TemplateResponse("account.html", {"request": request, "books": serialized_books, "api_url": API_URL})
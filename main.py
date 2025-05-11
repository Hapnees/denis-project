import asyncio
from parsers import parse_bukvoed, parser_labirint, parser_book24, parse_book_name
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from functools import reduce 

templates = Jinja2Templates(directory="templates")


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/results")
async def find_books(request: Request):
    query = request._query_params.get("query") or ""
    parsed_query = parse_book_name.parse_book_name(query)

    books = await asyncio.gather(parse_bukvoed.parse(parsed_query), parser_book24.parse(parsed_query), parser_labirint.parse(parsed_query))

    flatten_books = reduce(lambda a, b: a+b, books)

    #flatten_books = [
    #    {"title": "Колобок", "price": 179, "link": "www.google.com"},
    #    {"title": "Колобок. Русская народная сказка. Книжка-панорама с движущимися фигурками", "price": 180, "link": "www.google.com"},
    #    {"title": "Колобок", "price": 179, "link": "www.google.com"},
    #    {"title": "Колобок", "price": 179, "link": "www.google.com"},
    #    {"title": "Колобок", "price": 179, "link": "www.google.com"},
    #    {"title": "Колобок", "price": 179, "link": "www.google.com"},
    #    {"title": "Колобок", "price": 179, "link": "www.google.com"},
    #    {"title": "Колобок", "price": 179, "link": "www.google.com"},
    #    {"title": "Колобок", "price": 179, "link": "www.google.com"},
    #    {"title": "Колобок", "price": 179, "link": "www.google.com"},
    #    {"title": "Колобок", "price": 179, "link": "www.google.com"},
    #    {"title": "Колобок", "price": 179, "link": "www.google.com"},
    #    {"title": "Колобок", "price": 179, "link": "www.google.com"},
    #    {"title": "Колобок", "price": 179, "link": "www.google.com"},
    #    {"title": "Колобок", "price": 179, "link": "www.google.com"},
    #    {"title": "Колобок", "price": 179, "link": "www.google.com"},
    #    {"title": "Колобок", "price": 179, "link": "www.google.com"},
    #    {"title": "Колобок", "price": 179, "link": "www.google.com"},
    #    {"title": "Колобок", "price": 179, "link": "www.google.com"},
    #    {"title": "Колобок", "price": 179, "link": "www.google.com"},
    #]

    return templates.TemplateResponse("results.html", {"request": request, "books": flatten_books, "query": query})

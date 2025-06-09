# Импортируем необходимые компоненты из FastAPI
from fastapi import APIRouter, Response, Depends, Request
# Импортируем сервисный слой с бизнес-логикой
from . import service
# Импортируем модуль с настройками базы данных
from database import database
from auth.models import UserModel
from auth.service import get_current_user
from sqlalchemy import select, insert, delete, update
from .models import BookModel
from .dto import BookCreateDto, BookUpdateStatusDto, BookStatus

# Создаём роутер для обработки запросов, связанных с пользователями
# prefix="/user" - все маршруты будут начинаться с /user
# tags=["user"] - для группировки в документации API
router = APIRouter(
    prefix="/book",
    tags=["book"]
)

@router.post("/add-favorite")
async def addFavoriteBook(session: database.SessionDep, body: BookCreateDto, user: UserModel = Depends(get_current_user)):
	await session.execute(insert(BookModel).values(
		title=body['title'],
		link=body['link'],
		price=body['price'],
		img_link=body['img_link'],
		external_id=body['external_id'],
		user_id=user.id
    ))
	await session.commit()
	
	return {"success": True}

@router.delete("/remove-favorite/{id}")
async def removeFavoriteBook(session: database.SessionDep, id: int, user: UserModel = Depends(get_current_user)):
	await session.execute(delete(BookModel).where(BookModel.id == id))
	await session.commit()

	return {"success": True}

@router.get("/get-favorites")
async def getFavorites(session: database.SessionDep, status: BookStatus | None = None, user: UserModel = Depends(get_current_user)):
	where_clauses = []

	where_clauses.append(BookModel.user_id == user.id)
	if status:
		where_clauses.append(BookModel.status == "planned")

	books_query = await session.execute(select(BookModel).where(*where_clauses))
	books = books_query.scalars().all()
	return books

@router.put("/status/{id}")
async def updateStatus(session: database.SessionDep, id: int, body: BookUpdateStatusDto, user: UserModel = Depends(get_current_user)):
	await session.execute(update(BookModel).where(BookModel.id == id, BookModel.user_id == user.id).values(
		status=body['status']
	))
	await session.commit()

	return {"Success": True}
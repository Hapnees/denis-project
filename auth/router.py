# Импортируем необходимые компоненты из FastAPI
from fastapi import APIRouter, Response, Depends, Request
# Импортируем схемы данных для валидации и сериализации
from .schemas import UserSchema, UserRegisterSchema, UserLoginSchema
# Импортируем модель пользователя
from .models import UserModel
# Импортируем сервисный слой с бизнес-логикой
from . import service
# Импортируем модуль с настройками базы данных
from database import database

from sqlalchemy import update

# Создаём роутер для обработки запросов, связанных с пользователями
# prefix="/user" - все маршруты будут начинаться с /user
# tags=["user"] - для группировки в документации API
router = APIRouter(
    prefix="/user",
    tags=["user"]
)

# Обработчик GET-запроса для получения списка всех пользователей
# response_model=list[UserSchema] - указывает формат ответа
@router.get('/all', response_model=list[UserSchema])
async def get_all_users(
    session: database.SessionDep,  # Зависимость для получения сессии БД
    user: UserModel = Depends(service.get_current_user)  # Зависимость для проверки авторизации
):
    # Выводим имя текущего пользователя в консоль
    # Возвращаем список всех пользователей через сервисный слой
    return await service.get_all_users(session)

# Обработчик POST-запроса для регистрации нового пользователя
@router.post('/register')
async def register(
    response: Response,  # Объект ответа для установки cookies
    body: UserRegisterSchema,
    session: database.SessionDep  # Зависимость для получения сессии БД
):
    # Передаём данные в сервисный слой для регистрации
    return await service.register(response, body, session)

# Обработчик POST-запроса для авторизации пользователя
@router.post('/login')
async def login(
    body: UserLoginSchema,
    response: Response,  # Объект ответа для установки cookies
    session: database.SessionDep  # Зависимость для получения сессии БД
):
    # Передаём данные в сервисный слой для авторизации
    return await service.login(response, body, session)

@router.post('/logout')
async def logout(session: database.SessionDep, response: Response, user: UserModel = Depends(service.get_current_user)):
    await session.execute(update(UserModel).where(UserModel.id == user.id).values(rt_hash=None))
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    await session.commit()
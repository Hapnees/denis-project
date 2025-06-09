# Импортируем AsyncSession для работы с асинхронными сессиями базы данных
from sqlalchemy.ext.asyncio import AsyncSession
# Импортируем необходимые компоненты из FastAPI
from fastapi import status, HTTPException, Response, Cookie, Depends
from fastapi.responses import RedirectResponse
# Импортируем компоненты для работы с датами и временем
from datetime import datetime, timedelta, timezone
# Импортируем библиотеку для работы с JWT токенами
import jwt

# Импортируем функции для работы с базой данных
from sqlalchemy import select, insert
# Импортируем модуль с настройками базы данных
from database import database

# Импортируем библиотеку для хеширования паролей
import bcrypt

# Импортируем модели и схемы данных
from .models import UserModel
from .schemas import UserRegisterSchema, UserLoginSchema

# Функция для получения access token из cookie
def get_access_token_from_cookie(access_token = Cookie(default=None, alias="access_token")):
    return access_token

# Функция для получения текущего пользователя по токену
async def get_current_user(session: database.SessionDep, access_token: str = Depends(get_access_token_from_cookie)):
    try:
        # Декодируем JWT токен
        access_token_decoded = jwt.decode(access_token, "access_secret", algorithms=["HS256"])
        # Ищем пользователя в базе данных по id из токена
        found_user_result = await session.execute(select(UserModel).where(UserModel.id == access_token_decoded['id']))
        # Получаем результат запроса
        found_user = found_user_result.scalar_one_or_none()

        # Если пользователь не найден, возвращаем ошибку авторизации
        if not found_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Не авторизован")
    except:
        # При любой ошибке возвращаем ошибку авторизации
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Не авторизован")

    return found_user

# Функция для создания access и refresh токенов
def create_tokens(data: dict):
    # Получаем текущее время в UTC
    now = datetime.now(timezone.utc)

    # Создаём access token со сроком действия 2 дня
    access_expire = now + timedelta(days=2)
    access_payload = data.copy()
    access_payload.update({"exp": int(access_expire.timestamp())})
    access_token = jwt.encode(
        access_payload,
        "access_secret",
        algorithm="HS256"
    )

    # Создаём refresh token со сроком действия 7 дней
    refresh_expire = now + timedelta(days=7)
    refresh_payload = data.copy()
    refresh_payload.update({"exp": int(refresh_expire.timestamp())})
    refresh_token = jwt.encode(
        refresh_payload,
        "refresh_secret",
        algorithm="HS256"
    )

    return {"access_token": access_token, "refresh_token": refresh_token}

# Функция для проверки пароля
def verify_password(password: str, hash_password: str) -> bool:
    # Сравниваем хеш введённого пароля с хешем из базы данных
    return bcrypt.checkpw(password.encode(), hash_password.encode())

# Функция для хеширования пароля
def hash_password(password: str) -> str:
    # Генерируем соль с 5 раундами
    salt = bcrypt.gensalt(5)
    # Хешируем пароль с солью и возвращаем строку
    return bcrypt.hashpw(str.encode(password), salt).decode()

# Функция для хеширования refresh token
def hash_rt(rt: str) -> str:
    # Генерируем соль с 7 раундами
    salt = bcrypt.gensalt(7)
    # Хешируем токен с солью и возвращаем строку
    return bcrypt.hashpw(str.encode(rt), salt).decode()

# Функция для получения всех пользователей
async def get_all_users(session: database.SessionDep):
    # Выполняем запрос на получение всех пользователей
    users = await session.execute(select(UserModel))
    # Возвращаем список всех пользователей
    return users.scalars().all()

# Функция для регистрации нового пользователя
async def register(data: UserRegisterSchema, session: database.SessionDep):
    # Хешируем пароль
    hash = hash_password(data.password)

    # Добавляем нового пользователя в базу данных
    await session.execute(insert(UserModel).values(
        name=data.name,
        email=data.email,
        hash=hash,
        rt_hash="test_hash",
    ))
    # Сохраняем изменения
    await session.commit()

    return RedirectResponse(url="/", status_code=303)

# Функция для авторизации пользователя
async def login(response: Response, data: UserLoginSchema, session: database.SessionDep):
    # Ищем пользователя по email
    user_result = await session.execute(select(UserModel).where(UserModel.email == data.email))
    user = user_result.scalar_one_or_none()

    # Если пользователь не найден, возвращаем ошибку
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль")

    # Проверяем пароль
    if not verify_password(data.password, str(user.hash)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль")

    # Создаём access token
    access_token = create_tokens({"id": user.id})['access_token']
    # Устанавливаем токен в cookie
    response.set_cookie(key="access_token", value=access_token, httponly=True)

    return {"success": True}

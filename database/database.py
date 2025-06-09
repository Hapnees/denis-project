# Импортируем Depends из FastAPI для внедрения зависимостей
from fastapi import Depends
# Импортируем DeclarativeBase для создания базового класса моделей
from sqlalchemy.orm import DeclarativeBase
# Импортируем необходимые компоненты для асинхронной работы с базой данных
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
# Импортируем Annotated для типизации зависимостей
from typing import Annotated

# Создаём асинхронный движок для работы с SQLite базой данных
# sqlite+aiosqlite:///test.db - это URL для подключения к базе данных
# aiosqlite - это асинхронный драйвер для SQLite
engine = create_async_engine('sqlite+aiosqlite:///test.db')

# Создаём фабрику сессий для работы с базой данных
# expire_on_commit=False означает, что объекты не будут автоматически обновляться после коммита
new_session = async_sessionmaker(engine, expire_on_commit=False)

# Создаём базовый класс для всех моделей базы данных
# DeclarativeBase предоставляет базовую функциональность для ORM моделей
class Base(DeclarativeBase):
    pass

# Функция для инициализации базы данных
async def init_db():
    # Создаём соединение с базой данных
    async with engine.begin() as conn:
        # Создаём все таблицы, определённые в моделях
        # Base.metadata.create_all создаёт таблицы на основе определений моделей
        await conn.run_sync(Base.metadata.create_all)

# Функция для получения сессии базы данных
async def get_session():
    # Создаём новую сессию
    async with new_session() as session:
        # Возвращаем сессию через yield
        # Это позволяет использовать сессию в контексте FastAPI
        yield session

# Создаём тип для внедрения зависимости сессии
# Annotated используется для добавления метаданных к типу
# Depends(get_session) указывает, что значение будет получено из функции get_session
SessionDep = Annotated[AsyncSession, Depends(get_session)]
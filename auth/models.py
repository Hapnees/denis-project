from database.database import Base
# Импортируем необходимые компоненты из SQLAlchemy для создания моделей
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
# Импортируем базовый класс для моделей из нашего модуля database

# Создаём модель пользователя, наследуясь от Base
class UserModel(Base):
    # Указываем имя таблицы в базе данных
    __tablename__ = "users"

    # Создаём поле id:
    # - Integer: тип данных - целое число
    # - primary_key=True: это первичный ключ таблицы
    # - index=True: создаём индекс для ускорения поиска
    id = Column(Integer, primary_key=True, index=True)

    # Создаём поле name:
    # - String: тип данных - строка
    # - хранит имя пользователя
    name = Column(String)

    # Создаём поле email:
    # - String: тип данных - строка
    # - unique=True: значение должно быть уникальным
    # - хранит email пользователя
    email = Column(String, unique=True)

    # Создаём поле hash:
    # - String: тип данных - строка
    # - хранит хеш пароля пользователя
    hash = Column(String)

    # Создаём поле rt_hash:
    # - String: тип данных - строка
    # - хранит хеш refresh token'а пользователя
    rt_hash = Column(String)

    books_favorite = relationship("BookModel", back_populates="user")

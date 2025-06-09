from database.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import relationship
from enum import Enum

class BookStatus(Enum):
	READING = "reading"
	READ = "read"
	POSTPONED = "postponed"
	PLANNED = "planned"

class BookModel(Base):
	__tablename__ = "books"
	id = Column(Integer, primary_key=True, index=True)
	external_id = Column(String, index=True)
	title = Column(String)
	link = Column(String)
	price = Column(Integer)
	img_link = Column(String)
	status = Column(SqlEnum(BookStatus), default=BookStatus.PLANNED)

	user = relationship("UserModel", back_populates="books_favorite")
	user_id = Column(Integer, ForeignKey("users.id"))

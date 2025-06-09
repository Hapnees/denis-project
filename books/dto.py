from typing import TypedDict
from .models import BookStatus

class BookCreateDto(TypedDict):
	title: str
	link: str
	price: int
	img_link: str
	external_id: str

class BookUpdateStatusDto(TypedDict):
	status: BookStatus
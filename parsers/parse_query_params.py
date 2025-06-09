from typing import TypedDict

class Result(TypedDict):
	value: str
	direction: str

def parse_query_sort(sort: str | None) -> Result | None:
	if not sort:
		return None
	
	splitted_sort = sort.split("_")
	
	return {"value": splitted_sort[0], "direction": splitted_sort[1]}
BUKVOED_MAPPINGS = {
	"price_asc": "sort=priceAsc",
	"price_desc": "sort=priceDesc"
}

BOOK24_MAPPINGS = {
	"price_asc": "sort=price_asc",
	"price_desc": "sort=price_desc"
}

LABIRINT_MAPPIGNS = {
	"price_desc": "order=price&way=back",
	"price_asc": "order=price&way=forward",
}

def bukvoedSortAdapt(sort: str | None):
	if not sort:
		return None

	return BUKVOED_MAPPINGS[sort]
	

def book24SortAdapt(sort: str | None):
	if not sort:
		return None
	
	return BOOK24_MAPPINGS[sort]

def labirintSortAdapt(sort: str | None):
	if not sort:
		return None
	
	return LABIRINT_MAPPIGNS[sort]
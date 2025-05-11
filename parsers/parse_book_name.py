import urllib.parse

def parse_book_name(bookName: str) -> str:
    parsed_payload = urllib.parse.quote_plus(bookName)
    return parsed_payload
import re

def validate_phone(phone: str) -> bool:
    """Проверяем корректность номера телефона."""
    return bool(re.fullmatch(r'\+?\d{10,15}', phone))

def validate_city(city: str) -> bool:
    """Проверяем корректность города (только буквы и пробелы)."""
    return bool(re.fullmatch(r"[A-Za-zА-Яа-яЁё\s\-]+", city.strip()))
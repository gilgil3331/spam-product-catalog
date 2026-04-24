import re

# Whitelist: letters, digits, spaces only. 1–100 chars. (INP-1)
_NAME_RE = re.compile(r'^[A-Za-z0-9 ]{1,100}$')
_MAX_PRICE = 999_999.99


def validate_product_name(value):
    if not isinstance(value, str):
        return False, "Invalid product name."
    value = value.strip()
    if not _NAME_RE.match(value):
        return False, "Product name must be 1–100 characters: letters, digits, and spaces only."
    return True, value


def validate_price(value):
    try:
        price = float(value)
    except (TypeError, ValueError):
        return False, "Price must be a number."
    if price <= 0:                          # range check (INP-3)
        return False, "Price must be greater than zero."
    if price > _MAX_PRICE:                  # upper bound (INP-3)
        return False, "Price exceeds the maximum allowed value."
    return True, round(price, 2)


def validate_search_query(value):
    if not isinstance(value, str):
        return False, "Invalid search query."
    value = value.strip()
    if not value:
        return False, "Search query cannot be empty."
    if not _NAME_RE.match(value):
        return False, "Search query must be 1–100 characters: letters, digits, and spaces only."
    return True, value

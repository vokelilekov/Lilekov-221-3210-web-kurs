import hmac
from urllib.parse import urlencode

def safe_str_cmp(a, b):
    """
    Safely compare two strings, intended to replace Werkzeug's safe_str_cmp.
    """
    return hmac.compare_digest(a.encode('utf-8'), b.encode('utf-8'))

def url_encode(obj):
    """
    Encode a dictionary or list of tuples into a URL query string.
    """
    return urlencode(obj)
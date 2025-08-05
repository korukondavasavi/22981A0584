import random
import string
import re

def generate_shortcode(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def is_valid_url(url):
    regex = re.compile(
        r'^(http|https)://[^\s/$.?#].[^\s]*$', re.IGNORECASE
    )
    return re.match(regex, url) is not None
import re

def is_valid_filename(filename):
    return not bool(re.search(r'[<>:"/\\|?*]', filename))

def is_valid_color_hex(hex_code):
    return bool(re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', hex_code))

def validate_timer_input(minutes):
    try:
        val = int(minutes)
        return val > 0
    except ValueError:
        return False

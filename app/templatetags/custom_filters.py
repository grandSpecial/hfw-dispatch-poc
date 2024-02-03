from django import template
from datetime import datetime 

register = template.Library()

@register.filter(name='format_iso_datetime')
def format_iso_datetime(value, fmt='%b. %d, %Y, %I:%M %p'):
    """
    Converts an ISO formatted datetime string to a formatted date string.

    Args:
        value (str): The ISO format datetime string.
        fmt (str): The format string.

    Returns:
        str: The formatted datetime string.
    """
    try:
        # Parse the ISO format string to a datetime object
        date_obj = datetime.fromisoformat(value)
        # Return the formatted date string
        return date_obj.strftime(fmt)
    except ValueError:
        # In case of a formatting error, return the original value
        return value
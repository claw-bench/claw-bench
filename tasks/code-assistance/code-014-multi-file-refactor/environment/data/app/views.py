"""View handlers with duplicated response formatting."""


def _format_response(data, status="ok"):
    """Format a response dict -- duplicated helper."""
    return {
        "status": status,
        "data": data,
    }


def _format_error(message):
    """Format an error response -- duplicated helper."""
    return {
        "status": "error",
        "data": None,
        "message": message,
    }


def render_user(user):
    """Render a user as a response."""
    try:
        data = user.to_dict()
        # Duplicated response formatting
        return _format_response(data)
    except Exception as e:
        # Duplicated error handling
        return _format_error(str(e))


def render_product(product):
    """Render a product as a response."""
    try:
        data = product.to_dict()
        # Duplicated response formatting
        return _format_response(data)
    except Exception as e:
        # Duplicated error handling
        return _format_error(str(e))

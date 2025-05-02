import re
from datetime import datetime
from flask import jsonify
from functools import wraps


def format_datetime(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None


def handle_errors(f):
    """Decorator untuk menangani error secara konsisten"""

    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({"success": False, "message": str(e)}), 400
        except Exception as e:
            return (
                jsonify({"success": False, "message": f"Terjadi kesalahan: {str(e)}"}),
                500,
            )

    return decorated

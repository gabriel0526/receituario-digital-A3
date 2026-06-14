from datetime import datetime
from functools import wraps

from flask import abort, flash, redirect, url_for
from flask_login import current_user


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            if current_user.role not in roles:
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator


def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


def parse_datetime_local(value):
    return datetime.strptime(value, "%Y-%m-%dT%H:%M")


def flash_form_error(error):
    flash(f"Não foi possível salvar: {error}", "danger")

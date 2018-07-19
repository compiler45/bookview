""" Global app decorators"""
from functools import wraps
from flask_login import current_user
from flask import abort, request, redirect, url_for


def attach_request_hooks(app):
    @app.before_request
    def is_confirmed():
        if current_user.is_authenticated:
            if not current_user.confirmed and not \
             request.endpoint.startswith('static') and request.endpoint not in \
             ['auth.confirm', 'auth.resend_confirmation_email', 'auth.logout']:
                return redirect(url_for('auth.confirm'))


def has_permission(f, permission):
    @wraps(f)
    def check_if_has_permission(*args, **kwargs):
        if not current_user.role.has_permission(permission):
            abort(404)
        return f(*args, **kwargs)

    return check_if_has_permission

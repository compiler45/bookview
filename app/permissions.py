from flask import abort
from flask_login import current_user


class Permission:
    VIEW_ARTICLE = 1
    WRITE_ARTICLE = 2
    SUBMIT_SUGGESTIONS = 4
    ADMIN = 8

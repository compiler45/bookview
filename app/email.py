from threading import Thread
from flask import current_app, render_template
from flask_mail import Message

from . import mail


def send_async_email(app, msg):
    with app.app_context():
        app.logger.info('Sending emails to {}'.format(msg.recipients))
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message('{} {}'.format(app.config['MAIL_SUBJECT_PREFIX'], subject), recipients=[to])
    msg.html = render_template(template, **kwargs)
    thread = Thread(target=send_async_email, args=[app, msg])
    thread.start()
    return thread

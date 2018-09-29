from flask import render_template, flash, request, redirect, url_for, abort, \
    current_app
from flask_login import login_user, logout_user, current_user, login_required

from . import auth
from .forms import LoginForm, RegistrationForm
from ..models import User, db
from ..email import send_email


@auth.before_request
def before_request():
    if current_user.is_authenticated and request.endpoint == 'auth.login':
        return redirect(url_for('main.index'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).one_or_none()

        if user and user.check_password(password):
            remember_me = form.remember_me.data
            login_user(user, remember=remember_me)
            next = request.args.get('next')
            if not next or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)

        flash('Invalid account details', 'danger')
    return render_template('auth/login.html', form=form)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password1.data
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        # TODO: move to an email module for god sake
        # send confirmation email
        token = user.generate_confirmation_token()
        send_email(to=email, subject='Please confirm your Bookview account',
                   template='email/confirm.html', token=token, user=user)
        flash("Thank you! An email has been sent to your address with "
              "instructions to confirm your account.", 'success')

    return render_template('auth/register.html', form=form)


@auth.route('/confirm')
@login_required
def confirm():
    if current_user.confirmed:
        return redirect(url_for('main.index'))

    token = request.args.get('t')
    # we want to use the actual User instance
    user = current_user._get_current_object()
    if token:
        if user.verify_confirmation_token(token):
            user.confirmed = True
            db.session.commit()

            flash('Thank you for confirming your account.', 'success')
            return redirect(url_for('main.index'))

        flash('Token is invalid or expired', 'danger')

    return render_template('auth/confirm_account.html', user=user)


@auth.route('/resend-confirmation')
@login_required
def resend_confirmation_email():
    if current_user.confirmed:
        return redirect(url_for('main.index'))

    token = current_user.generate_confirmation_token()
    current_app.logger.debug('Email {}'.format(current_user.email))
    # TODO: move to sendemail module, this view doesn't need to know all these details
    send_email(to=current_user.email, subject='Please confirm your Bookview account',
               template='email/confirm.html', token=token, user=current_user)

    flash('A new token has been sent to your email', 'warning')
    return redirect(url_for('auth.confirm'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('auth/logout.html')

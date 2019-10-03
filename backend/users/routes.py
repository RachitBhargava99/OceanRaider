from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import login_user, current_user, logout_user
from backend.users.forms import RegistrationForm, LoginForm
from backend.models import User, LoggedInUser
from backend import db, bcrypt
import json
from backend.users.utils import send_reset_email

users = Blueprint('users', __name__)


# End-point to enable a user to log in to the website
@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('events.show_game'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            logged_in_user = LoggedInUser(id=user.id, name=user.name, email=user.email, auth_token=user.get_auth_token())
            db.session.add(logged_in_user)
            db.session.commit()
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('events.show_game'))
        else:
            flash("Authentication Failed", 'danger')
    return render_template('login.html', title='Login', form=form)


# End-point to enable a user to register on the website
@users.route('/register', methods=['GET', 'POST'])
def normal_register():
    if current_user.is_authenticated:
        return redirect(url_for('events.generate'))

    form = RegistrationForm()

    if User.query.filter_by(email=form.email.data).first():
        flash("User Already Exists", 'danger')
    else:
        if form.validate_on_submit():
            email = form.email.data
            hashed_pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            name = form.name.data
            user = User(email=email, password=hashed_pwd, name=name, isAdmin=False)
            db.session.add(user)
            db.session.commit()
            flash(f'Account created for {user.name}.', 'success')
            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


# End-point to enable a user to change their access level to administrator
@users.route('/admin/add', methods=['GET', 'POST'])
def master_add():
    request_json = request.get_json()
    user = User.query.filter_by(email=request_json['email']).first()
    user.isAdmin = True
    db.session.commit()
    return json.dumps({'status': 1})


# End-point to enable a user to request a new password
@users.route('/password/request_reset', methods=['GET', 'POST'])
def request_reset_password():
    request_json = request.get_json()
    user = User.query.filter_by(email=request_json['email']).first()
    if user:
        send_reset_email(user)
        return json.dumps({'status': 1})
    else:
        return json.dumps({'status': 0, 'error': "User Not Found"})


# End-point to enable a user to verify their password reset request
@users.route('/backend/password/verify_token', methods=['GET', 'POST'])
def verify_reset_token():
    request_json = request.get_json()
    user = User.verify_reset_token(request_json['token'])
    if user is None:
        return json.dumps({'status': 0, 'error': "Sorry, the link is invalid or has expired. Please submit password reset request again."})
    else:
        return json.dumps({'status': 1})


# End-point to enable a user to set up a new password
@users.route('/backend/password/reset', methods=['GET', 'POST'])
def reset_password():
    request_json = request.get_json()
    user = User.verify_reset_token(request_json['token'])
    if user is None:
        return json.dumps({'status': 0,
                           'error': "Sorry, the link is invalid or has expired. Please submit password reset request again."})
    else:
        hashed_pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pwd
        db.session.commit()
        return json.dumps({'status': 1})


# Checker to see if the server is up and running
@users.route('/test', methods=['GET'])
def test():
    return "Hello World"

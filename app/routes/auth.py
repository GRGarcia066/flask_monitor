from app.forms import RegistrationForm, LoginForm, UserUpdateForm
from app.models import User, db, Project

from flask import render_template, redirect, flash, Blueprint, g
from flask_login import current_user, login_user, logout_user, login_required
from flask_api import status
import requests


# Define the blueprint: 'auth', set its url prefix: app.url/auth
bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """
    The registration page.
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        if current_user.is_authenticated:
            return redirect('/auth/profile/{}'.format(current_user.username))
        else:
            flash('¡Felicitaciones, ahora eres un usuario registrado!', 'success') 
            return redirect('/')
    return render_template('auth/register.html', title='Registro', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Nombre de usuario o contraseña incorrectos.', 'error')
            return redirect('/auth/login')
        login_user(user, remember=form.remember_me.data)
        return redirect('/')
    return render_template('auth/login.html', form=form)


@bp.route('/profile/<string:username>', methods=['GET'])
@login_required
def profile(username):
    form = UserUpdateForm()
    if username != current_user.username:
        return render_template('404.html')
    return render_template('auth/profile.html', form=form)


@bp.route('/user/<string:username>', methods=['GET', 'POST'])
@login_required
def edit_user(username):
    form = UserUpdateForm()
    g.current_user = current_user
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is not None:
            if form.username.data and user.username != form.username.data:
                user.username = form.username.data
            if form.newpassword.data and form.oldpassword.data:
                if user.check_password(form.oldpassword.data):
                    user.set_password(form.newpassword.data)
                else:
                    flash('Contraseña incorrecta.', 'error')
        else:
            flash('El nombre de usuario no existe.', 'error')

    if form.errors:
        return render_template('auth/edit.html', form=form), status.HTTP_303_SEE_OTHER

    db.session.commit()
    return render_template('auth/edit.html', form=form)
        

@bp.route('/logout')
def logout():
    logout_user()
    return redirect('/')

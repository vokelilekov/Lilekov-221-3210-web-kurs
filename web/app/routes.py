from flask import Blueprint, render_template, url_for, flash, redirect, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app import db, login_manager
from app.forms import RegistrationForm, LoginForm, CardForm, UserForm, SearchForm, UpdateProfileForm, ChangePasswordForm
from flask_login import login_user, current_user, logout_user, login_required
from app.models import User, Card, UserCard
import os

main = Blueprint('main', __name__)

@main.route("/", methods=['GET'])
def index():
    query = request.args.get('query', '')
    artist = request.args.get('artist', '')
    album = request.args.get('album', '')

    form = SearchForm(query=query, artist_selected=artist, album_selected=album)
    cards = []

    learned_cards = {card.card_id for card in UserCard.get_user_cards(current_user.id)} if current_user.is_authenticated else set()

    if query or artist or album:
        cards = Card.search(query, artist, album)
    else:
        cards = Card.get_all()

    return render_template('index.html', title='Home', form=form, cards=cards, learned_cards=learned_cards)

@main.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        avatar_filename = None
        if form.avatar.data:
            if hasattr(form.avatar.data, 'filename'):
                avatar_filename = secure_filename(form.avatar.data.filename)
                avatar_path = os.path.join(current_app.config['UPLOADED_PHOTOS_DEST'], avatar_filename)
                os.makedirs(current_app.config['UPLOADED_PHOTOS_DEST'], exist_ok=True)
                form.avatar.data.save(avatar_path)
            else:
                flash('Ошибка загрузки аватара. Пожалуйста, выберите файл изображения.', 'danger')
                return redirect(url_for('main.register'))

        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            middle_name=form.middle_name.data,
            phone_number=form.phone_number.data,
            email=form.email.data,
            role_id=2,
            avatar=avatar_filename
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()
        flash('Ваш аккаунт создан! Теперь вы можете войти.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Регистрация', form=form)


@main.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    update_form = UpdateProfileForm(obj=current_user)
    password_form = ChangePasswordForm()
    if update_form.validate_on_submit() and 'submit' in request.form:
        current_user.first_name = update_form.first_name.data
        current_user.last_name = update_form.last_name.data
        current_user.middle_name = update_form.middle_name.data
        current_user.phone_number = update_form.phone_number.data
        current_user.email = update_form.email.data
        if update_form.avatar.data:
            avatar_filename = secure_filename(update_form.avatar.data.filename)
            avatar_path = os.path.join(current_app.config['UPLOADED_PHOTOS_DEST'], avatar_filename)
            update_form.avatar.data.save(avatar_path)
            current_user.avatar = avatar_filename
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.profile'))
    elif password_form.validate_on_submit() and 'submit_password' in request.form:
        if current_user.check_password(password_form.current_password.data):
            current_user.update_password(password_form.new_password.data)
            flash('Your password has been updated!', 'success')
            return redirect(url_for('main.profile'))
        else:
            flash('Current password is incorrect', 'danger')

    learned_cards_count = UserCard.count_user_cards(current_user.id)
    learned_cards = UserCard.get_user_cards_with_details(current_user.id)
    return render_template('profile.html', title='Profile', update_form=update_form, password_form=password_form, learned_cards_count=learned_cards_count, learned_cards=learned_cards)

@main.route("/profile/update", methods=['GET', 'POST'])
@login_required
def update_profile():
    update_form = UpdateProfileForm(obj=current_user)
    if update_form.validate_on_submit():
        current_user.first_name = update_form.first_name.data
        current_user.last_name = update_form.last_name.data
        current_user.middle_name = update_form.middle_name.data
        current_user.phone_number = update_form.phone_number.data
        current_user.email = update_form.email.data
        if update_form.avatar.data:
            avatar_filename = secure_filename(update_form.avatar.data.filename)
            avatar_path = os.path.join(current_app.config['UPLOADED_PHOTOS_DEST'], avatar_filename)
            update_form.avatar.data.save(avatar_path)
            current_user.avatar = avatar_filename
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.profile'))
    return render_template('update_profile.html', title='Update Profile', form=update_form)

@main.route("/profile/change_password", methods=['GET', 'POST'])
@login_required
def change_password():
    password_form = ChangePasswordForm()
    if password_form.validate_on_submit() and 'submit_password' in request.form:
        if current_user.check_password(password_form.current_password.data):
            current_user.update_password(password_form.new_password.data)
            flash('Ваш пароль был обновлен!', 'success')
            return redirect(url_for('main.profile'))
        else:
            flash('Текущий пароль неверен', 'danger')
    return render_template('change_password.html', title='Смена пароля', form=password_form)

@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('main.index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route("/admin/cards", methods=['GET'])
@login_required
def admin_cards():
    if current_user.role_id != 1:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    per_page = 10
    cards = Card.query.paginate(page=page, per_page=per_page)
    return render_template('admin_cards.html', title='Manage Cards', cards=cards)


@main.route("/admin/cards/create", methods=['GET', 'POST'])
@login_required
def admin_create_card():
    if current_user.role_id != 1:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    form = CardForm()
    if form.validate_on_submit():
        album_id = form.album_id.data
        Card.create(form.word.data, form.translate.data, form.line.data, form.translate_line.data, album_id)
        flash('Card created successfully!', 'success')
        return redirect(url_for('main.admin_cards'))
    return render_template('admin_create_card.html', title='Create Card', form=form)

@main.route("/admin/cards/<int:card_id>/edit", methods=['GET', 'POST'])
@login_required
def admin_edit_card(card_id):
    if current_user.role_id != 1:
        return redirect(url_for('main.index'))
    card = Card.get(card_id)
    if not card:
        flash('Card not found.', 'danger')
        return redirect(url_for('main.admin_cards'))
    form = CardForm(obj=card)
    if form.validate_on_submit():
        album_id = form.album_id.data
        Card.update(card_id, form.word.data, form.translate.data, form.line.data, form.translate_line.data, album_id)
        flash('Card updated successfully!', 'success')
        return redirect(url_for('main.admin_cards'))
    elif request.method == 'GET':
        form.album_id.data = card.album_id
    return render_template('admin_edit_card.html', title='Edit Card', form=form, card=card)


@main.route("/admin/cards/<int:card_id>/delete", methods=['POST'])
@login_required
def admin_delete_card(card_id):
    if current_user.role_id != 1:
        return redirect(url_for('main.index'))
    Card.delete(card_id)
    flash('Card deleted successfully!', 'success')
    return redirect(url_for('main.admin_cards'))

@main.route("/learned_card", methods=['POST'])
@login_required
def learned_card():
    card_id = request.form.get('card_id')
    action = request.form.get('action')
    if card_id and action:
        if action == 'add':
            UserCard.create(user_id=current_user.id, card_id=card_id)
        elif action == 'remove':
            UserCard.delete(user_id=current_user.id, card_id=card_id)
        learned_words_count = UserCard.count_user_cards(current_user.id)
        return jsonify(success=True, learned_words=learned_words_count)
    return jsonify(success=False)

@main.route("/admin/users")
@login_required
def admin_users():
    if current_user.role_id != 1:
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    per_page = 10
    users = User.query.paginate(page=page, per_page=per_page)
    return render_template('admin_users.html', title='Manage Users', users=users)

@main.route("/admin/users/<int:user_id>/edit", methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
    if current_user.role_id != 1:
        return redirect(url_for('main.index'))

    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)  # передаем объект user в форму

    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.middle_name = form.middle_name.data
        user.phone_number = form.phone_number.data
        user.email = form.email.data
        user.role_id = form.role_id.data
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('main.admin_users'))
    elif request.method == 'GET':
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.middle_name.data = user.middle_name
        form.phone_number.data = user.phone_number
        form.email.data = user.email
        form.role_id.data = user.role_id

    return render_template('admin_edit_user.html', title='Edit User', form=form)

@main.route("/admin/users/<int:user_id>/delete", methods=['POST'])
@login_required
def admin_delete_user(user_id):
    if current_user.role_id != 1:
        return redirect(url_for('main.index'))
    User.delete(user_id)
    flash('User deleted successfully!', 'success')
    return redirect(url_for('main.admin_users'))

@main.route("/admin/cards/<int:card_id>/view")
@login_required
def admin_view_card(card_id):
    if current_user.role_id != 1:
        return redirect(url_for('main.index'))
    card = Card.get(card_id)
    return render_template('admin_view_card.html', title='View Card', card=card)

@main.route("/admin/users/<int:user_id>/view")
@login_required
def admin_view_user(user_id):
    if current_user.role_id != 1:
        return redirect(url_for('main.index'))
    user = User.get(user_id)
    return render_template('admin_view_user.html', title='View User', user=user)

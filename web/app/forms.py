from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField, FileField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional
from app.models import Card, Album, Role
from flask_wtf.file import FileAllowed
from .validators import password_validator

class RegistrationForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired()])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    middle_name = StringField('Отчество')
    phone_number = StringField('Телефон', validators=[DataRequired()])
    email = StringField('Почта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), password_validator])
    confirm_password = PasswordField('Подтверждение пароля', validators=[DataRequired(), EqualTo('password', message='Пароли должны совпадать.')])
    avatar = FileField('Аватар')
    submit = SubmitField('Зарегистрироваться')

class LoginForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class CardForm(FlaskForm):
    word = StringField('Слово', validators=[DataRequired(), Length(min=1, max=100)])
    translate = StringField('Перевод слова', validators=[DataRequired(), Length(min=1, max=100)])
    line = TextAreaField('Строчки песни', validators=[DataRequired()])
    translate_line = TextAreaField('Перевод строчек', validators=[DataRequired()])
    album_id = SelectField('Альбом', choices=[], coerce=int)
    submit = SubmitField('Сохранить')

    def __init__(self, *args, **kwargs):
        super(CardForm, self).__init__(*args, **kwargs)
        self.album_id.choices = [(album.id, album.album_name) for album in Album.query.all()]

class UserForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired(), Length(min=1, max=50)])
    last_name = StringField('Фамилия', validators=[Length(max=50)])
    middle_name = StringField('Отчество', validators=[Length(max=50)])
    phone_number = StringField('Номер телефона', validators=[DataRequired(), Length(min=10, max=20)])
    email = StringField('Почта', validators=[DataRequired(), Email()])
    role_id = SelectField('Роль', choices=[], coerce=int)
    submit = SubmitField('Сохранить')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.role_id.choices = [(role.id, role.role_name) for role in Role.query.all()]

def get_unique_artists():
    albums = Album.get_all()
    artists = set(album.artist for album in albums)
    return sorted(artists)

def get_albums_by_artist(artist):
    if artist:
        return Album.query.filter_by(artist=artist).all()
    return Album.get_all()

class SearchForm(FlaskForm):
    query = StringField('Поиск', validators=[Optional()])
    artist = SelectField('По артисту', choices=[], coerce=str, validators=[Optional()])
    album = SelectField('По альбому', choices=[], coerce=str, validators=[Optional()])
    submit = SubmitField('Найти')

    def __init__(self, *args, **kwargs):
        artist_selected = kwargs.pop('artist_selected', '')
        album_selected = kwargs.pop('album_selected', '')
        super(SearchForm, self).__init__(*args, **kwargs)
        self.artist.choices = [('', 'Выберите артиста')] + [(artist, artist) for artist in get_unique_artists()]
        self.album.choices = [('', 'Выберите альбом')] + [(album.album_name, album.album_name) for album in get_albums_by_artist(artist_selected)]
        self.artist.data = artist_selected
        self.album.data = album_selected

class UpdateProfileForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired(), Length(min=1, max=50)])
    last_name = StringField('Фамилия', validators=[Length(max=50)])
    middle_name = StringField('Отчество', validators=[Length(max=50)])
    phone_number = StringField('Номер телефона', validators=[DataRequired(), Length(min=10, max=20)])
    email = StringField('Почта', validators=[DataRequired(), Email()])
    avatar = FileField('Обновить аватар', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Сохранить изменения')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Текущий пароль', validators=[DataRequired()])
    new_password = PasswordField('Новый пароль', validators=[DataRequired(), password_validator])
    confirm_new_password = PasswordField('Подтверждение нового пароля', validators=[DataRequired(), EqualTo('new_password', message='Пароли должны совпадать.')])
    submit_password = SubmitField('Сменить пароль')

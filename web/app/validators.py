import re
from wtforms import ValidationError

def password_validator(form, field):
    password = field.data
    if len(password) < 8 or len(password) > 128:
        raise ValidationError('Пароль должен быть не менее 8 и не более 128 символов.')
    
    if not re.search(r'[A-ZА-Я]', password):
        raise ValidationError('Пароль должен содержать как минимум одну заглавную букву.')
    
    if not re.search(r'[a-zа-я]', password):
        raise ValidationError('Пароль должен содержать как минимум одну строчную букву.')
    
    if not re.search(r'\d', password):
        raise ValidationError('Пароль должен содержать как минимум одну цифру.')
    
    if re.search(r'\s', password):
        raise ValidationError('Пароль не должен содержать пробелы.')
    
    if not re.search(r'[~!?@#$%^&*_\-+()\[\]{}><\/\\|"\',.:;]', password):
        raise ValidationError('Пароль должен содержать как минимум один специальный символ: ~ ! ? @ # $ % ^ & * _ - + ( ) [ ] { } > < / \\ | " \'. , : ;')
    
    if re.search(r'[^\w~!?@#$%^&*_\-+()\[\]{}><\/\\|"\',.:;]', password):
        raise ValidationError('Пароль содержит недопустимые символы.')

import os

class Config:
    SECRET_KEY = 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://std_2472_kurs:TaySwiFan1989.dat@std-mysql.ist.mospolytech.ru/std_2472_kurs'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOADED_PHOTOS_DEST = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'media', 'images')

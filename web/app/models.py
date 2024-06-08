from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import joinedload

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'Users'

    id: Mapped[int] = mapped_column('UserID', Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column('FirstName', String(50), nullable=False)
    last_name: Mapped[str] = mapped_column('LastName', String(50), nullable=False)
    middle_name: Mapped[Optional[str]] = mapped_column('MiddleName', String(50), nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column('PhoneNumber', String(20), nullable=True)
    email: Mapped[str] = mapped_column('Email', String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column('Password', String(100), nullable=False)
    role_id: Mapped[int] = mapped_column('RoleID', Integer, ForeignKey('Roles.RoleID'), nullable=False)
    avatar: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    learned_words: Mapped[Optional[int]] = mapped_column('LearnedWords', Integer, nullable=True)
    cards: Mapped[List["UserCard"]] = relationship('UserCard', back_populates='user', lazy=True)

    role = relationship('Role', backref='users')

    def set_password(self, password: str) -> None:
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    @staticmethod
    def get(user_id: int) -> Optional["User"]:
        return User.query.get(user_id)

    @staticmethod
    def get_by_email(email: str) -> Optional["User"]:
        return User.query.filter_by(email=email).first()

    @staticmethod
    def create(first_name: str, last_name: str, middle_name: Optional[str], phone_number: Optional[str], email: str, password: str, role_id: int, avatar: Optional[str] = None) -> "User":
        user = User(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            phone_number=phone_number,
            email=email,
            role_id=role_id,
            avatar=avatar
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    def update_profile(self) -> None:
        db.session.commit()

    def update_password(self, password: str) -> None:
        self.set_password(password)
        db.session.commit()

    @staticmethod
    def delete(user_id: int) -> None:
        user = User.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()

class Card(db.Model):
    __tablename__ = 'Cards'

    id: Mapped[int] = mapped_column('CardID', Integer, primary_key=True, autoincrement=True)
    album_id: Mapped[int] = mapped_column('AlbumID', Integer, ForeignKey('Albums.AlbumID'), nullable=False)
    word: Mapped[str] = mapped_column('Word', String(100), nullable=False)
    translate: Mapped[str] = mapped_column('Translate', String(100), nullable=False)
    line: Mapped[str] = mapped_column('Line', String(200), nullable=False)
    translate_line: Mapped[str] = mapped_column('TranslateLine', String(200), nullable=False)

    album: Mapped["Album"] = relationship('Album')

    @staticmethod
    def get_all() -> List["Card"]:
        return Card.query.all()

    @staticmethod
    def get(card_id: int) -> Optional["Card"]:
        return Card.query.get(card_id)

    @staticmethod
    def get_albums() -> List["Album"]:
        return Album.query.all()

    @staticmethod
    def get(card_id: int) -> Optional["Card"]:
        return Card.query.get(card_id)

    @staticmethod
    def search(query: Optional[str] = None, artist: Optional[str] = None, album: Optional[str] = None) -> List["Card"]:
        query_filter = []
        if query:
            query_filter.append((Card.word.contains(query)) | 
                                (Card.translate.contains(query)) | 
                                (Card.line.contains(query)))
        if artist or album:
            album_ids = [album.id for album in Album.query.filter((Album.artist == artist) | 
                                                                  (Album.album_name == album)).all()]
            if album_ids:
                query_filter.append(Card.album_id.in_(album_ids))
        
        return Card.query.filter(*query_filter).all()

    @staticmethod
    def delete(card_id: int) -> None:
        card = Card.get(card_id)
        if card:
            db.session.delete(card)
            db.session.commit()

    @staticmethod
    def create(word: str, translate: str, line: str, translate_line: str, album_id: int) -> "Card":
        card = Card(
            word=word,
            translate=translate,
            line=line,
            translate_line=translate_line,
            album_id=album_id
        )
        db.session.add(card)
        db.session.commit()
        return card

    @staticmethod
    def update(card_id: int, word: str, translate: str, line: str, translate_line: str, album_id: int) -> None:
        card = Card.get(card_id)
        if card:
            card.word = word
            card.translate = translate
            card.line = line
            card.translate_line = translate_line
            card.album_id = album_id
            db.session.commit()

    @staticmethod
    def get_artists() -> List[str]:
        artists = db.session.query(Album.artist).distinct().all()
        return [artist[0] for artist in artists]

    @staticmethod
    def get_album_id_by_name(album_name: str) -> Optional[int]:
        album = Album.query.filter_by(album_name=album_name).first()
        return album.id if album else None

    @staticmethod
    def get_album_name_by_id(album_id: int) -> Optional[str]:
        album = Album.query.get(album_id)
        return album.album_name if album else None

class Album(db.Model):
    __tablename__ = 'Albums'

    id: Mapped[int] = mapped_column('AlbumID', Integer, primary_key=True, autoincrement=True)
    album_name: Mapped[str] = mapped_column('AlbumName', String(100), nullable=False)
    artist: Mapped[str] = mapped_column('Artist', String(100), nullable=False)

    @staticmethod
    def get_all() -> List["Album"]:
        return Album.query.all()

class Role(db.Model):
    __tablename__ = 'Roles'

    id: Mapped[int] = mapped_column('RoleID', Integer, primary_key=True, autoincrement=True)
    role_name: Mapped[str] = mapped_column('RoleName', String(50), nullable=False)

class UserCard(db.Model):
    __tablename__ = 'UserCards'

    id: Mapped[int] = mapped_column('UserCardID', Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column('UserID', Integer, ForeignKey('Users.UserID'), nullable=False)
    card_id: Mapped[int] = mapped_column('CardID', Integer, ForeignKey('Cards.CardID'), nullable=False)

    user: Mapped["User"] = relationship('User', back_populates='cards')
    card: Mapped["Card"] = relationship('Card')

    @staticmethod
    def create(user_id: int, card_id: int) -> None:
        if not UserCard.exists(user_id, card_id):
            user_card = UserCard(user_id=user_id, card_id=card_id)
            db.session.add(user_card)
            db.session.commit()

    @staticmethod
    def delete(user_id: int, card_id: int) -> None:
        user_card = UserCard.query.filter_by(user_id=user_id, card_id=card_id).first()
        if user_card:
            db.session.delete(user_card)
            db.session.commit()

    @staticmethod
    def exists(user_id: int, card_id: int) -> bool:
        return db.session.query(UserCard.query.filter_by(user_id=user_id, card_id=card_id).exists()).scalar()

    @staticmethod
    def get_user_cards(user_id: int) -> List["UserCard"]:
        return db.session.query(UserCard).join(Card).filter(UserCard.user_id == user_id).all()
    
    @staticmethod
    def get_user_cards_with_details(user_id: int) -> List["UserCard"]:
        return UserCard.query.options(joinedload(UserCard.card)).filter_by(user_id=user_id).all()
    
    @staticmethod
    def count_user_cards(user_id: int) -> int:
        return UserCard.query.filter_by(user_id=user_id).count()

    @staticmethod
    def is_card_learned(user_id: int, card_id: int) -> bool:
        return db.session.query(UserCard.query.filter_by(user_id=user_id, card_id=card_id).exists()).scalar()

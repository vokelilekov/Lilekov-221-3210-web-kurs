from flask import Flask, send_from_directory
from flask_login import LoginManager
from flask_migrate import Migrate
from app.models import db, User
from config import Config

login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    Migrate(app, db)
    login_manager.init_app(app)

    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    @app.route('/media/<path:filename>')
    def media(filename):
        return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename)

    return app

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


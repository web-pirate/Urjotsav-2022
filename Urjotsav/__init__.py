from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from Urjotsav.config import Config
from flask_mail import Mail


db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    login_manager.init_app(app)
    mail.init_app(app)

    from Urjotsav.main.views import main
    app.register_blueprint(main)

    return app

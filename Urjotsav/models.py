from flask import current_app
from Urjotsav import db, login_manager
from datetime import datetime
from flask_login import UserMixin
import pytz
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

tz = pytz.timezone("Asia/Calcutta")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    enrollment_number = db.Column(db.String(128))
    email = db.Column(db.String(140), unique=True, nullable=False)
    password = db.Column(db.String(1000), nullable=False)
    dept_name = db.Column(db.String(1000), nullable=False)
    branch = db.Column(db.String(1000), nullable=False)
    role = db.Column(db.String(1000), nullable=False)
    reward_points = db.Column(db.Integer, nullable=False, default=0)

    def get_reset_token(self, expires_sec=600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)


class Events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(1000), nullable=False)
    co_cordinators = db.Column(db.String(1000), nullable=False)
    event_date = db.Column(db.DateTime, default=datetime.now(tz), nullable=False)
    venue = db.Column(db.String(1000), nullable=False)
    in_entry_fess = db.Column(db.String(1000), nullable=False)
    out_entry_fess = db.Column(db.String(1000), nullable=False)
    price = db.Column(db.Text, nullable=False)

# class EventRegistration(db.Model):
#     pass

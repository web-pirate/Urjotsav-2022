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
    name = db.Column(db.String(128))
    enrollment_number = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(140), unique=True, nullable=False)
    mobile_number = db.Column(db.String(140), unique=True, nullable=False)
    password = db.Column(db.String(1000), nullable=False)
    dept_name = db.Column(db.String(1000), nullable=False)
    role = db.Column(db.String(1000), nullable=False)
    reward_points = db.Column(db.Integer, nullable=False, default=0)
    is_piemr = db.Column(db.Boolean, default=False)
    college = db.Column(db.String(1000), nullable=False)
    registered_events = db.relationship('EventRegistration', backref='user', lazy='dynamic')
    main_co_ordinators = db.relationship('Events', backref='user', lazy='dynamic')
    payments = db.relationship('Payments', backref='user', lazy='dynamic')


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
    event_type = db.Column(db.String(1000), nullable=False)
    event_name = db.Column(db.String(1000), nullable=False)
    co_cordinators = db.Column(db.Text, nullable=False)
    event_date = db.Column(db.DateTime, default=datetime.now(tz), nullable=False)
    venue = db.Column(db.String(1000), nullable=False)
    in_entry_fees = db.Column(db.String(1000), nullable=False)
    out_entry_fees = db.Column(db.String(1000), nullable=False)
    reward_points = db.Column(db.Integer, nullable=False, default=0)
    prize = db.Column(db.Text, nullable=False)
    main_co_ordinator = db.Column(db.Integer, db.ForeignKey('user.id'))


class EventRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(1000), nullable=False)
    event_name = db.Column(db.String(1000), nullable=False)
    fees = db.Column(db.String(1000), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now(tz))
    venue = db.Column(db.String(1000), nullable=False)
    team_leader = db.Column(db.String(1000), nullable=False)
    mobile_number = db.Column(db.String(1000), nullable=False)
    team_size = db.Column(db.Integer, nullable=False)
    team_members = db.Column(db.String(1000), nullable=False)
    team_members_id = db.Column(db.String(1000), nullable=False)
    paid = db.Column(db.Boolean)
    pay_id = db.Column(db.String(100))
    first_no = db.Column(db.Boolean, default=True)
    second_no = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dept_name = db.Column(db.String(1000), nullable=False)
    reward_points = db.Column(db.Integer, nullable=False)


class Payments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.String(100))
    payment_id = db.Column(db.String(100))
    date = db.Column(db.DateTime, default=datetime.now(tz))
    status = db.Column(db.String(10))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Counter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer)

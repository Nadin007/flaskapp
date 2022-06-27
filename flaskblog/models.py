from datetime import datetime as dt

from flask import current_app, jsonify
from flask_jwt_extended import create_access_token, decode_token
from flask_login import UserMixin
from jwt import ExpiredSignatureError, InvalidTokenError

from flaskblog import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        reset_token = create_access_token(identity=str(self.id), expires_delta=expires_sec)
        return reset_token.decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        """
        Validates the auth token
        :param auth_token:
        :return: user_id:integer
        """
        try:
            data = decode_token(token, current_app.config.get('SECRET_KEY'), allow_expired=False)
            person = User.query.filter_by(user_id=data["identity"]).first()
            if person:
                return person
            return None
        except ExpiredSignatureError:
            return jsonify({'message': 'Token expired, log in again'}), 403
        except InvalidTokenError:
            return jsonify({'message': 'Invalid token. Please log in again.'}), 403

    def __repr__(self) -> str:
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self) -> str:
        return f"Post('{self.title}', '{self.date_posted}')"

import os
import secrets
from http.client import INTERNAL_SERVER_ERROR

from flask import url_for, current_app
from flask_mail import Message
from PIL import Image

from flaskblog import mail


def save_picture(file_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(file_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pict', picture_fn)
    output_size = (125, 125)
    i = Image.open(file_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


def send_email(user):
    token = user.get_token()
    msg = Message(
        subject='Password Reset Request', sender='noreply@myflaskdemo.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did no make this request then simply ignore this email and no changes will make!'''
    try:
        mail.send(msg)
    except ConnectionRefusedError:
        raise INTERNAL_SERVER_ERROR("[MAIL SERVER] not working")

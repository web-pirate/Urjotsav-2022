from flask import Blueprint, render_template, request, flash, redirect, url_for
# from Urjotsav.main.forms import BecomePartnerForm, ContactsForm
from Urjotsav.models import User
from flask_login import current_user, logout_user, login_user, login_required
from Urjotsav import db
from datetime import datetime, timedelta

main = Blueprint('main', __name__)

@main.route('/')
def home():
  """Home Page"""
  return render_template('index.html')

@main.route('/')
def about():
  """Home Page"""
  return render_template('about.html')


@main.route('/register/')
def register():
    return render_template('registration.html')


@main.route('/login/', methods=['GET', 'POST'])
def login():
  # if request
  return render_template('login.html')


@main.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

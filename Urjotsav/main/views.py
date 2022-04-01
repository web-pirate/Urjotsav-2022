from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
# from Urjotsav.main.forms import BecomePartnerForm, ContactsForm
from Urjotsav.models import User
from flask_login import current_user
from Urjotsav import db
from datetime import datetime, timedelta

main = Blueprint('main', __name__)

@main.route('/')
def home():
  """Home Page"""
  return render_template('index.html')

@main.route('/login/', methods=['GET', 'POST'])
def login():
  # if request
  return render_template('login.html')

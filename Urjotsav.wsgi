#!/usr/bin/python3
activate_this = '/var/www/Urjotsav/Urjotsav/venv/bin/activate_this.py'
exec(open(activate_this).read(), dict(__file__=activate_this))
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/Urjotsav/")

from Urjotsav import create_app
from Urjotsav.main.views import *
from Urjotsav.models import *

application = create_app()

with application.app_context():
    db.create_all()

application.secret_key = '2f14f2997d0cb0ac2fd939f11c8d38f074139fde1fcaa84c86d2c29199669d4976bb0ac05e48ec817c10c7637930af700a6a'

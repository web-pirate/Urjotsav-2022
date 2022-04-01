from Urjotsav import create_app
from tejearning.main.views import *
from tejearning.models import *

app = create_app()

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    website_url = 'tejearning.in:5000'
    app.config['SERVER_NAME'] = website_url
    app.run(debug=True)

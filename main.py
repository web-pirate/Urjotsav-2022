from Urjotsav import create_app
from Urjotsav.main.views import *
from Urjotsav.models import *

app = create_app()

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

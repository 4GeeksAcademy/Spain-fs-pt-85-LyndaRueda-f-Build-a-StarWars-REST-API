import os
from flask_admin import Admin
from models import db, User
from flask_admin.contrib.sqla import ModelView
from models import db, User, Character, Episode, Location, Favorite


# Clase personalizada para la vista de Favorite en Flask-Admin
class View_Favorite(ModelView):
    form_columns = ['user_id', 'character_id', 'episode_id', 'location_id']
    column_list = ('user_id', 'character_id', 'episode_id', 'location_id')

# Confi admin
def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='Rick and Morty Admin', template_mode='bootstrap3')

    # Modelos al panel de adminin con vistas personalizadas para c/u
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Character, db.session))
    admin.add_view(ModelView(Episode, db.session))
    admin.add_view(ModelView(Location, db.session))
    admin.add_view(View_Favorite(Favorite, db.session))

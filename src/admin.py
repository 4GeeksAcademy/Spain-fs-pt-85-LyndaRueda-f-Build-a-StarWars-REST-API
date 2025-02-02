import os
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, validators
from models import db, User, Character, Episode, Location, Favorite

# Clase personalizada para UserForm
class UserForm(FlaskForm):
    email = StringField('Email', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', [validators.DataRequired()])
    is_active = BooleanField('Is Active')

# Clase personalizada para la vista de usuarios en Flask-Admin
class UserAdmin(ModelView):
    form = UserForm
    column_list = ('email', 'password', 'is_active')
    column_labels = {
        'email': 'Correo Electrónico',
        'password': 'Contraseña',
        'is_active': 'Activo'
    }
    form_columns = ['email', 'password', 'is_active']

# Clase personalizada para la vista de Favoritos en Flask-Admin
class ViewFavorite(ModelView):
    column_list = ('user.email', 'character.name', 'character.episode.name', 'character.location.name')
    column_labels = {
        'user.email': 'Usuario',
        'character.name': 'Personaje',
        'character.episode.name': 'Episodio',
        'character.location.name': 'Ubicación'
    }
    form_columns = ['user', 'character']

    # Búsqueda por usuario y personaje
    column_searchable_list = ['user.email', 'character.name']

    # Hacer que la interfaz muestre las relaciones en lugar de IDs
    column_sortable_list = ['user.email', 'character.name']

    # filtros para la búsqueda en fav de cada user
    column_filters = ['user.email', 'character.name']

# Configuración de Flask-Admin
def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample_key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='Rick and Morty Admin', template_mode='bootstrap3')
    
    # Modelos de Admin
    admin.add_view(UserAdmin(User, db.session))
    admin.add_view(ModelView(Character, db.session))
    admin.add_view(ModelView(Episode, db.session))
    admin.add_view(ModelView(Location, db.session))
    admin.add_view(ViewFavorite(Favorite, db.session))

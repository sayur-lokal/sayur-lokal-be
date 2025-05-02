from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from supabase import create_client, Client

# Inisialisasi extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
supabase: Client = None


def init_app(app):
    jwt.init_app(app)
    cors.init_app(app)


def init_db(app):
    db.init_app(app)
    migrate.init_app(app, db)

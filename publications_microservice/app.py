"""Flask api."""
import logging
from pathlib import Path

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.event import listen
from sqlalchemy.sql import func, select
from werkzeug.middleware.proxy_fix import ProxyFix

from publications_microservice.api import api
from publications_microservice.cfg import config
from publications_microservice.models import db

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def fix_dialect(s):
    if s.startswith("postgres://"):
        s = s.replace("postgres://", "postgresql://")
    s = s.replace("postgresql://", "postgresql+psycopg2://")
    return s


def load_spatialite(sqlite, _connection_rec):
    logger.info("======== loading spatialite ========")
    sqlite.enable_load_extension(True)
    sqlite.load_extension('/usr/lib64/mod_spatialite.so')


def create_app():
    """creates a new app instance"""
    new_app = Flask(__name__)
    new_app.config["SQLALCHEMY_DATABASE_URI"] = config.database.url(
        default="sqlite:///{curr_loc}/publications_microservice.db".format(
            curr_loc=Path(__file__).parent
        ),
        cast=fix_dialect,
    )
    new_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(new_app)
    api.init_app(new_app)
    Migrate(new_app, db, directory=Path(__file__).parent / "migrations")
    new_app.wsgi_app = ProxyFix(
        new_app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1
    )  # remove after flask-restx > 0.2.0 is released
    # https://github.com/python-restx/flask-restx/issues/230
    CORS(new_app)

    if new_app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite"):
        listen(Engine, 'connect', load_spatialite)
        listen(Engine, 'first_connect', load_spatialite)
        engine = create_engine(new_app.config["SQLALCHEMY_DATABASE_URI"], echo=True)
        conn = engine.connect()
        conn.execute(select([func.InitSpatialMetaData()]))
        conn.close()

    return new_app

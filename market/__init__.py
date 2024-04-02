from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_apscheduler import APScheduler
from flask_login import LoginManager


app = Flask(__name__)
schedule = APScheduler()
schedule.init_app(app)
schedule.start()
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///excorpse.db"
app.config["SECRET_KEY"] = "d41929e43c407e753fde725f"
db = SQLAlchemy(app)

from market import routes

import os
from flask import Flask
from .config import Config
from .extensions import db, login_manager
from .models import User, Category


def create_app() -> Flask:
	app = Flask(__name__, template_folder="templates", static_folder="static")

	# Config
	app.config.from_object(Config())

	# Extensions
	db.init_app(app)
	login_manager.init_app(app)
	login_manager.login_view = "auth.login"
	login_manager.login_message_category = "info"

	@login_manager.user_loader
	def load_user(user_id: str):
		return User.query.get(int(user_id))

	# Blueprints
	from .main.routes import main_bp
	from .auth.routes import auth_bp
	from .posts.routes import posts_bp

	app.register_blueprint(main_bp)
	app.register_blueprint(auth_bp, url_prefix="/auth")
	app.register_blueprint(posts_bp, url_prefix="/posts")

	# Create tables in dev mode and seed categories
	with app.app_context():
		os.makedirs(os.path.dirname(Config.SQLITE_PATH), exist_ok=True) if Config.SQLALCHEMY_DATABASE_URI.startswith("sqlite") else None
		db.create_all()
		default_categories = ["Backtest", "Journal", "Strategy", "Psychology", "Education"]
		for cat_name in default_categories:
			if not Category.query.filter_by(name=cat_name).first():
				db.session.add(Category(name=cat_name))
		db.session.commit()

	return app
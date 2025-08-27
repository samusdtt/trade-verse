import os


class Config:
	APP_NAME = "TradeVerse"

	# Core
	SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
	SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT", "dev-salt")

	# Database
	SQLITE_PATH = os.getenv("SQLITE_PATH", "/workspace/tradeverse.db")
	DATABASE_URL = os.getenv("DATABASE_URL")
	SQLALCHEMY_DATABASE_URI = DATABASE_URL or f"sqlite:///{SQLITE_PATH}"
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	# Mail (optional in dev)
	MAIL_SERVER = os.getenv("MAIL_SERVER", "localhost")
	MAIL_PORT = int(os.getenv("MAIL_PORT", "25"))
	MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "false").lower() == "true"
	MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() == "true"
	MAIL_USERNAME = os.getenv("MAIL_USERNAME")
	MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
	MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "TradeVerse <no-reply@localhost>")
	ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@localhost")
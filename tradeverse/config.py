import os


class Config:
	APP_NAME = "TradeVerse"

	# Core
	SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
	SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT", "dev-salt")

	# Database
	SQLITE_PATH = os.getenv("SQLITE_PATH", "/workspace/tradeverse.db")
	DATABASE_URL = os.getenv("DATABASE_URL")
	# Convert postgresql:// to postgresql+psycopg2:// for psycopg2-binary
	if DATABASE_URL and DATABASE_URL.startswith('postgresql://'):
		DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg2://')
	SQLALCHEMY_DATABASE_URI = DATABASE_URL or f"sqlite:///{SQLITE_PATH}"
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	# Uploads (relative paths under app.static_folder)
	UPLOAD_FOLDER = "uploads"
	UPLOAD_THUMBNAILS = "uploads/thumbnails"
	UPLOAD_PDFS = "uploads/pdfs"
	UPLOAD_CONTENT_IMAGES = "uploads/content-images"
	MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "50000000"))  # 50MB
	ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}
	ALLOWED_PDF_EXTENSIONS = {"pdf"}

	# Mail (optional in prod)
	MAIL_SERVER = os.getenv("MAIL_SERVER", "localhost")
	MAIL_PORT = int(os.getenv("MAIL_PORT", "25"))
	MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "false").lower() == "true"
	MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() == "true"
	MAIL_USERNAME = os.getenv("MAIL_USERNAME")
	MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
	MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "TradeVerse <no-reply@localhost>")
	ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@localhost")
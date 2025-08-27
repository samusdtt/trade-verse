from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db


class Category(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50), unique=True, nullable=False)
	posts = db.relationship("Post", backref="category", lazy=True)

	def __repr__(self) -> str:
		return f"<Category {self.name}>"


class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	name = db.Column(db.String(120), nullable=True)  # Display Name
	password_hash = db.Column(db.String(255), nullable=False)
	bio = db.Column(db.Text, nullable=True)
	is_admin = db.Column(db.Boolean, default=False)
	created_at = db.Column(db.DateTime, default=datetime.utcnow)
	posts = db.relationship("Post", backref="author", lazy=True)

	def set_password(self, password: str) -> None:
		self.password_hash = generate_password_hash(password)

	def check_password(self, password: str) -> bool:
		return check_password_hash(self.password_hash, password)

	def __repr__(self) -> str:
		return f"<User {self.username}>"


class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(200), nullable=False)
	content = db.Column(db.Text, nullable=False)
	created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
	category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)

	def __repr__(self) -> str:
		return f"<Post {self.title[:20]}>"
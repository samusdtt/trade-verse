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
	email_verified = db.Column(db.Boolean, default=False)
	email_verification_token = db.Column(db.String(100), nullable=True)
	created_at = db.Column(db.DateTime, default=datetime.utcnow)
	posts = db.relationship("Post", backref="author", lazy=True)
	
	# Follow relationships will be handled in a separate table

	def set_password(self, password: str) -> None:
		self.password_hash = generate_password_hash(password)

	def check_password(self, password: str) -> bool:
		return check_password_hash(self.password_hash, password)

	def __repr__(self) -> str:
		return f"<User {self.username}>"


class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(200), nullable=False)
	content = db.Column(db.Text, nullable=False)  # HTML allowed
	excerpt = db.Column(db.String(300), nullable=True)
	cover_image = db.Column(db.String(512), nullable=True)  # kept for backward-compat
	thumbnail_path = db.Column(db.String(512), nullable=True)
	pdf_path = db.Column(db.String(512), nullable=True)
	status = db.Column(db.String(20), default="published")  # draft, published, scheduled
	likes_count = db.Column(db.Integer, default=0)
	created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
	category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)

	def __repr__(self) -> str:
		return f"<Post {self.title[:20]}>"


class Comment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	content = db.Column(db.Text, nullable=False)
	created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
	post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
	
	# Relationships
	user = db.relationship("User", backref="comments")
	post = db.relationship("Post", backref="comments")
	
	def __repr__(self) -> str:
		return f"<Comment {self.content[:20]}>"


class Like(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
	post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
	created_at = db.Column(db.DateTime, default=datetime.utcnow)
	
	# Ensure user can only like a post once
	__table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),)
	
	def __repr__(self) -> str:
		return f"<Like user:{self.user_id} post:{self.post_id}>"


class Bookmark(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
	post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
	created_at = db.Column(db.DateTime, default=datetime.utcnow)
	
	# Ensure user can only bookmark a post once
	__table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_bookmark'),)
	
	def __repr__(self) -> str:
		return f"<Bookmark user:{self.user_id} post:{self.post_id}>"


class Follow(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	follower_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
	followed_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
	created_at = db.Column(db.DateTime, default=datetime.utcnow)
	
	# Ensure user can only follow another user once
	__table_args__ = (db.UniqueConstraint('follower_id', 'followed_id', name='unique_follow'),)
	
	def __repr__(self) -> str:
		return f"<Follow {self.follower_id} -> {self.followed_id}>"
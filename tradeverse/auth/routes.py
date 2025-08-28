from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from ..extensions import db
from ..models import User
from flask_mail import Message
from .. import mail
import secrets
import string

auth_bp = Blueprint("auth", __name__, template_folder="../templates/auth")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
	if request.method == "POST":
		full_name = request.form.get("name", "").strip()
		username = request.form.get("username", "").strip().lower()
		email = request.form.get("email", "").strip().lower()
		password = request.form.get("password", "")

		if not username or not email or not password:
			flash("Please fill all required fields.", "danger")
			return render_template("auth/signup.html")

		if User.query.filter((User.username == username) | (User.email == email)).first():
			flash("Username or email already exists.", "warning")
			return render_template("auth/signup.html")

		user = User(username=username, email=email, name=full_name)
		user.set_password(password)
		db.session.add(user)
		db.session.commit()
		flash("Account created. Please log in.", "success")
		return redirect(url_for("auth.login"))

	return render_template("auth/signup.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		identifier = request.form.get("identifier", "").strip().lower()
		password = request.form.get("password", "")

		user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()
		if not user or not user.check_password(password):
			flash("Invalid credentials.", "danger")
			return render_template("auth/login.html")

		login_user(user)
		flash(f"Welcome, {user.name or user.username}!", "success")
		return redirect(url_for("main.index"))

	return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
	logout_user()
	flash("Logged out.", "info")
	return redirect(url_for("main.index"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
	if request.method == "POST":
		name = request.form.get("name", "").strip()
		bio = request.form.get("bio", "").strip()
		email = request.form.get("email", "").strip().lower()

		if email and email != current_user.email:
			# Ensure email uniqueness
			if User.query.filter(User.email == email, User.id != current_user.id).first():
				flash("Email already in use.", "warning")
				return render_template("auth/profile.html", user=current_user)
			current_user.email = email
		if name:
			current_user.name = name
		current_user.bio = bio
		db.session.commit()
		flash("Profile updated.", "success")
		return redirect(url_for("auth.profile"))

	return render_template("auth/profile.html", user=current_user)


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
	if request.method == "POST":
		email = request.form.get("email", "").strip().lower()
		
		if not email:
			flash("Please enter your email address.", "danger")
			return render_template("auth/forgot_password.html")
		
		user = User.query.filter_by(email=email).first()
		if user:
			# Generate a random password
			alphabet = string.ascii_letters + string.digits
			new_password = ''.join(secrets.choice(alphabet) for i in range(12))
			user.set_password(new_password)
			db.session.commit()
			
			# Send email with new password
			try:
				msg = Message(
					"Password Reset - TradeVerse",
					sender=current_app.config['MAIL_DEFAULT_SENDER'],
					recipients=[email]
				)
				msg.body = f"""
Hello {user.name or user.username},

Your password has been reset.

New Password: {new_password}

Please log in with this password and change it immediately.

Best regards,
TradeVerse Team
"""
				mail.send(msg)
				flash("New password sent to your email. Please check your inbox.", "success")
			except Exception as e:
				flash("Password reset failed. Please try again or contact support.", "danger")
		else:
			flash("Email not found.", "warning")
		
		return render_template("auth/forgot_password.html")
	
	return render_template("auth/forgot_password.html")
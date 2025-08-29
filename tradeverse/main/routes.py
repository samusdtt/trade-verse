from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from ..models import Category, Post
from ..extensions import db

main_bp = Blueprint("main", __name__, template_folder="../templates")


@main_bp.route("/")
def index():
	selected_category = request.args.get("category")
	search_query = request.args.get("q", "").strip()
	
	query = Post.query.options(joinedload(Post.category), joinedload(Post.author))
	
	# Show published posts and scheduled posts that are due (only public posts)
	from datetime import datetime
	query = query.filter(
		((Post.status == "published") | 
		((Post.status == "scheduled") & (Post.scheduled_at <= datetime.utcnow()))) &
		(Post.is_public == True)
	)
	
	# Get categories for filter (only public categories)
	categories = Category.query.filter_by(is_public=True).all()
	
	if selected_category:
		query = query.join(Category).filter(Category.name == selected_category)
	if search_query:
		query = query.filter(or_(
			Post.title.ilike(f"%{search_query}%"), 
			Post.content.ilike(f"%{search_query}%"),
			Post.tags.ilike(f"%{search_query}%")
		))
	query = query.order_by(Post.created_at.desc())
	posts = query.all()
	return render_template("index.html", categories=categories, selected_category=selected_category, q=search_query, posts=posts)


@main_bp.route("/private")
@login_required
def private_section():
	selected_category = request.args.get("category")
	search_query = request.args.get("q", "").strip()
	
	query = Post.query.options(joinedload(Post.category), joinedload(Post.author))
	
	# Show user's private posts and private categories
	from datetime import datetime
	query = query.filter(
		((Post.status == "published") | 
		((Post.status == "scheduled") & (Post.scheduled_at <= datetime.utcnow()))) &
		((Post.is_public == False) & (Post.user_id == current_user.id))
	)
	
	# Get user's private categories
	private_categories = Category.query.filter(
		(Category.is_public == False) & (Category.created_by == current_user.id)
	).all()
	
	if selected_category:
		query = query.join(Category).filter(Category.name == selected_category)
	if search_query:
		query = query.filter(or_(
			Post.title.ilike(f"%{search_query}%"), 
			Post.content.ilike(f"%{search_query}%"),
			Post.tags.ilike(f"%{search_query}%")
		))
	query = query.order_by(Post.created_at.desc())
	posts = query.all()
	return render_template("private.html", categories=private_categories, selected_category=selected_category, q=search_query, posts=posts)


@main_bp.route("/about")
def about():
	return render_template("about.html")


@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
	if request.method == "POST":
		# Handle contact form submission
		pass
	return render_template("contact.html")
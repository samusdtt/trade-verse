from flask import Blueprint, render_template, request
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from ..models import Category, Post

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
	selected_category = request.args.get("category")
	search_query = request.args.get("q", "").strip()

	categories = Category.query.order_by(Category.name.asc()).all()
	query = Post.query.options(joinedload(Post.category), joinedload(Post.author))
	
	# Only show published posts
	# Show published posts and scheduled posts that are due (only public posts)
	from datetime import datetime
	query = query.filter(
		((Post.status == "published") | 
		((Post.status == "scheduled") & (Post.scheduled_at <= datetime.utcnow()))) &
		(Post.is_public == True)
	)
	
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


@main_bp.route("/about")
def about():
	return render_template("about.html")


@main_bp.route("/contact")
def contact():
	return render_template("contact.html")
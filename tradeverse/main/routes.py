from flask import Blueprint, render_template, request
from ..models import Category, Post

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
	selected_category = request.args.get("category")
	search_query = request.args.get("q", "").strip()

	categories = Category.query.order_by(Category.name.asc()).all()
	# Placeholder: posts list not implemented yet; pass empty.
	posts = []
	return render_template("index.html", categories=categories, selected_category=selected_category, q=search_query, posts=posts)


@main_bp.route("/about")
def about():
	return render_template("about.html")


@main_bp.route("/contact")
def contact():
	return render_template("contact.html")
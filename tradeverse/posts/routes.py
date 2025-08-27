from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from ..extensions import db
from ..models import Post, Category

posts_bp = Blueprint("posts", __name__, template_folder="../templates/posts")


def _user_can_edit(post: Post) -> bool:
	return current_user.is_authenticated and (current_user.is_admin or current_user.id == post.user_id)


@posts_bp.route("/new", methods=["GET", "POST"])
@login_required
def create_post():
	categories = Category.query.order_by(Category.name.asc()).all()
	if request.method == "POST":
		title = request.form.get("title", "").strip()
		content = request.form.get("content", "").strip()
		category_id = request.form.get("category_id")
		if not title or not content or not category_id:
			flash("Please fill all fields.", "warning")
			return render_template("posts/new.html", categories=categories)
		category = Category.query.get(int(category_id))
		if not category:
			flash("Invalid category.", "danger")
			return render_template("posts/new.html", categories=categories)
		post = Post(title=title, content=content, category_id=category.id, user_id=current_user.id)
		db.session.add(post)
		db.session.commit()
		flash("Post created.", "success")
		return redirect(url_for("main.index", category=category.name))
	return render_template("posts/new.html", categories=categories)


@posts_bp.route("/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id: int):
	post = Post.query.get_or_404(post_id)
	if not _user_can_edit(post):
		abort(403)
	categories = Category.query.order_by(Category.name.asc()).all()
	if request.method == "POST":
		post.title = request.form.get("title", post.title).strip()
		post.content = request.form.get("content", post.content).strip()
		category_id = request.form.get("category_id")
		if category_id:
			category = Category.query.get(int(category_id))
			if category:
				post.category_id = category.id
		db.session.commit()
		flash("Post updated.", "success")
		return redirect(url_for("main.index"))
	return render_template("posts/edit.html", post=post, categories=categories)


@posts_bp.route("/<int:post_id>/delete", methods=["POST"]) 
@login_required
def delete_post(post_id: int):
	post = Post.query.get_or_404(post_id)
	if not _user_can_edit(post):
		abort(403)
	db.session.delete(post)
	db.session.commit()
	flash("Post deleted.", "info")
	return redirect(url_for("main.index"))
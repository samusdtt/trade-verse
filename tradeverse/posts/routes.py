from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os, uuid
from ..extensions import db
from ..models import Post, Category
from ..config import Config

posts_bp = Blueprint("posts", __name__, template_folder="../templates/posts")


def _user_can_edit(post: Post) -> bool:
	return current_user.is_authenticated and (current_user.is_admin or current_user.id == post.user_id)


def _allowed(filename: str, allowed: set) -> bool:
	return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


def _save_file(file_storage, folder: str) -> str | None:
	if not file_storage or file_storage.filename == "":
		return None
	filename = secure_filename(file_storage.filename)
	ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
	unique = f"{uuid.uuid4().hex}.{ext}"
	# Save to static folder
	full_path = os.path.join(Config.STATIC_ROOT, folder, unique)
	file_storage.save(full_path)
	# Return relative path for url_for
	return f"{folder}/{unique}"


@posts_bp.post("/upload-image")
@login_required
def upload_image():
	file = request.files.get("image")
	if not file or not _allowed(file.filename, Config.ALLOWED_IMAGE_EXTENSIONS):
		return jsonify({"error": "Invalid image"}), 400
	rel_path = _save_file(file, Config.UPLOAD_FOLDER)
	return jsonify({"url": url_for('static', filename=rel_path, _external=False)})


@posts_bp.route("/<int:post_id>")
def detail(post_id: int):
	post = Post.query.get_or_404(post_id)
	return render_template("posts/detail.html", post=post)


@posts_bp.route("/new", methods=["GET", "POST"])
@login_required
def create_post():
	categories = Category.query.order_by(Category.name.asc()).all()
	if request.method == "POST":
		title = request.form.get("title", "").strip()
		content = request.form.get("content", "").strip()
		excerpt = request.form.get("excerpt", "").strip()
		category_id = request.form.get("category_id")
		thumb_file = request.files.get("thumbnail")
		pdf_file = request.files.get("pdf")

		# Debug logging
		print(f"Thumbnail file: {thumb_file}")
		if thumb_file:
			print(f"Thumbnail filename: {thumb_file.filename}")
			print(f"Thumbnail allowed: {_allowed(thumb_file.filename, Config.ALLOWED_IMAGE_EXTENSIONS)}")

		if not title or not content or not category_id:
			flash("Please fill all required fields.", "warning")
			return render_template("posts/new.html", categories=categories)

		thumb_rel = None
		if thumb_file and _allowed(thumb_file.filename, Config.ALLOWED_IMAGE_EXTENSIONS):
			thumb_rel = _save_file(thumb_file, Config.UPLOAD_THUMBNAILS)
			print(f"Saved thumbnail to: {thumb_rel}")
		elif thumb_file and thumb_file.filename:
			flash("Unsupported thumbnail format.", "warning")

		pdf_rel = None
		if pdf_file and _allowed(pdf_file.filename, Config.ALLOWED_PDF_EXTENSIONS):
			pdf_rel = _save_file(pdf_file, Config.UPLOAD_PDFS)
		elif pdf_file and pdf_file.filename:
			flash("Unsupported PDF format.", "warning")

		post = Post(
			title=title,
			content=content,
			excerpt=excerpt or (content[:280] if content else None),
			thumbnail_path=thumb_rel,
			pdf_path=pdf_rel,
			category_id=int(category_id),
			user_id=current_user.id,
		)
		db.session.add(post)
		db.session.commit()
		flash("Post created.", "success")
		return redirect(url_for("posts.detail", post_id=post.id))
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
		post.excerpt = request.form.get("excerpt", post.excerpt).strip()
		category_id = request.form.get("category_id")

		thumb_file = request.files.get("thumbnail")
		pdf_file = request.files.get("pdf")

		if category_id:
			category = Category.query.get(int(category_id))
			if category:
				post.category_id = category.id

		if thumb_file and thumb_file.filename:
			if _allowed(thumb_file.filename, Config.ALLOWED_IMAGE_EXTENSIONS):
				post.thumbnail_path = _save_file(thumb_file, Config.UPLOAD_THUMBNAILS)
			else:
				flash("Unsupported thumbnail format.", "warning")

		if pdf_file and pdf_file.filename:
			if _allowed(pdf_file.filename, Config.ALLOWED_PDF_EXTENSIONS):
				post.pdf_path = _save_file(pdf_file, Config.UPLOAD_PDFS)
			else:
				flash("Unsupported PDF format.", "warning")

		db.session.commit()
		flash("Post updated.", "success")
		return redirect(url_for("posts.detail", post_id=post.id))
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
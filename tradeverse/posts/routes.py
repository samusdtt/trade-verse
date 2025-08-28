from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from ..extensions import db
from ..models import Post, Category, Comment, Like, Bookmark, Follow, User, PostTemplate
import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime

posts_bp = Blueprint("posts", __name__, template_folder="../templates/posts")


@posts_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_post():
	if request.method == "POST":
		title = request.form.get("title", "").strip()
		content = request.form.get("content", "").strip()
		category_id = request.form.get("category_id")
		excerpt = request.form.get("excerpt", "").strip()
		tags = request.form.get("tags", "").strip()
		status = request.form.get("status", "published")
		series_name = request.form.get("series_name", "").strip()
		series_order = request.form.get("series_order")
		scheduled_at = request.form.get("scheduled_at")

		if not title or not content or not category_id:
			flash("Please fill all required fields.", "danger")
			return render_template("posts/new.html", categories=Category.query.all())

		# Handle scheduling
		if status == "scheduled" and scheduled_at:
			try:
				scheduled_datetime = datetime.fromisoformat(scheduled_at.replace('T', ' '))
				if scheduled_datetime <= datetime.now():
					flash("Scheduled time must be in the future.", "danger")
					return render_template("posts/new.html", categories=Category.query.all())
			except ValueError:
				flash("Invalid scheduled date format.", "danger")
				return render_template("posts/new.html", categories=Category.query.all())
		else:
			scheduled_datetime = None

		# Handle thumbnail upload
		thumbnail_path = None
		if "thumbnail" in request.files:
			thumbnail_file = request.files["thumbnail"]
			if thumbnail_file.filename:
				thumbnail_path = _save_file(thumbnail_file, current_app.config["UPLOAD_THUMBNAILS"])

		# Handle PDF upload
		pdf_path = None
		if "pdf" in request.files:
			pdf_file = request.files["pdf"]
			if pdf_file.filename:
				pdf_path = _save_file(pdf_file, current_app.config["UPLOAD_PDFS"])

		post = Post(
			title=title,
			content=content,
			category_id=category_id,
			excerpt=excerpt,
			tags=tags,
			thumbnail_path=thumbnail_path,
			pdf_path=pdf_path,
			user_id=current_user.id,
			status=status,
			series_name=series_name if series_name else None,
			series_order=int(series_order) if series_order else None,
			scheduled_at=scheduled_datetime
		)
		db.session.add(post)
		db.session.commit()
		
		# Update user post count and achievements
		current_user.post_count = Post.query.filter_by(user_id=current_user.id, status="published").count()
		
		# Award achievement points
		achievement_points = 0
		if current_user.post_count == 1:
			achievement_points += 10  # First post
		elif current_user.post_count == 5:
			achievement_points += 25  # 5 posts
		elif current_user.post_count == 10:
			achievement_points += 50  # 10 posts
		elif current_user.post_count == 25:
			achievement_points += 100  # 25 posts
		
		if achievement_points > 0:
			current_user.achievement_points += achievement_points
			# Add badges
			badges = current_user.badges.split(',') if current_user.badges else []
			if current_user.post_count == 1 and 'First Post' not in badges:
				badges.append('First Post')
			elif current_user.post_count == 5 and 'Regular Writer' not in badges:
				badges.append('Regular Writer')
			elif current_user.post_count == 10 and 'Pro Blogger' not in badges:
				badges.append('Pro Blogger')
			elif current_user.post_count == 25 and 'Master Author' not in badges:
				badges.append('Master Author')
			current_user.badges = ','.join(badges)
		
		db.session.commit()
		
		flash("Post created successfully!", "success")
		return redirect(url_for("posts.detail", post_id=post.id))

	return render_template("posts/new.html", categories=Category.query.all())


@posts_bp.route("/templates")
@login_required
def templates():
	# Get public templates and user's private templates
	templates = PostTemplate.query.filter(
		(PostTemplate.is_public == True) | (PostTemplate.created_by == current_user.id)
	).order_by(PostTemplate.created_at.desc()).all()
	
	return render_template("posts/templates.html", templates=templates)


@posts_bp.route("/templates/new", methods=["GET", "POST"])
@login_required
def new_template():
	if request.method == "POST":
		name = request.form.get("name", "").strip()
		description = request.form.get("description", "").strip()
		title_template = request.form.get("title_template", "").strip()
		content_template = request.form.get("content_template", "").strip()
		category_id = request.form.get("category_id")
		tags_template = request.form.get("tags_template", "").strip()
		is_public = request.form.get("is_public") == "on"

		if not name:
			flash("Template name is required.", "danger")
			return render_template("posts/new_template.html", categories=Category.query.all())

		template = PostTemplate(
			name=name,
			description=description,
			title_template=title_template,
			content_template=content_template,
			category_id=category_id if category_id else None,
			tags_template=tags_template,
			created_by=current_user.id,
			is_public=is_public
		)
		db.session.add(template)
		db.session.commit()
		
		flash("Template created successfully!", "success")
		return redirect(url_for("posts.templates"))

	return render_template("posts/new_template.html", categories=Category.query.all())


@posts_bp.route("/templates/<int:template_id>/use")
@login_required
def use_template(template_id):
	template = PostTemplate.query.get_or_404(template_id)
	
	# Check if user can use this template
	if not template.is_public and template.created_by != current_user.id:
		flash("You don't have permission to use this template.", "danger")
		return redirect(url_for("posts.templates"))
	
	return render_template("posts/new.html", 
		categories=Category.query.all(),
		template=template
	)


@posts_bp.route("/<int:post_id>")
def detail(post_id):
	post = Post.query.get_or_404(post_id)
	
	# Increment view count (only for published posts)
	if post.status == "published":
		post.views_count += 1
		db.session.commit()
	
	# Get related posts (same series or same author)
	related_posts = []
	if post.series_name:
		related_posts = Post.query.filter(
			Post.series_name == post.series_name,
			Post.id != post.id,
			Post.status == "published"
		).order_by(Post.series_order).limit(3).all()
	elif post.author.posts:
		related_posts = Post.query.filter(
			Post.user_id == post.author.id,
			Post.id != post.id,
			Post.status == "published"
		).order_by(Post.created_at.desc()).limit(3).all()
	
	return render_template("posts/detail.html", post=post, related_posts=related_posts)


@posts_bp.route("/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
	post = Post.query.get_or_404(post_id)
	
	# Check if user can edit this post
	if post.user_id != current_user.id and not current_user.is_admin:
		flash("You can only edit your own posts.", "danger")
		return redirect(url_for("posts.detail", post_id=post.id))

	if request.method == "POST":
		title = request.form.get("title", "").strip()
		content = request.form.get("content", "").strip()
		category_id = request.form.get("category_id")
		excerpt = request.form.get("excerpt", "").strip()
		tags = request.form.get("tags", "").strip()
		status = request.form.get("status", "published")
		series_name = request.form.get("series_name", "").strip()
		series_order = request.form.get("series_order")
		scheduled_at = request.form.get("scheduled_at")

		if not title or not content or not category_id:
			flash("Please fill all required fields.", "danger")
			return render_template("posts/edit.html", post=post, categories=Category.query.all())

		# Handle scheduling
		if status == "scheduled" and scheduled_at:
			try:
				scheduled_datetime = datetime.fromisoformat(scheduled_at.replace('T', ' '))
				if scheduled_datetime <= datetime.now():
					flash("Scheduled time must be in the future.", "danger")
					return render_template("posts/edit.html", post=post, categories=Category.query.all())
			except ValueError:
				flash("Invalid scheduled date format.", "danger")
				return render_template("posts/edit.html", post=post, categories=Category.query.all())
		else:
			scheduled_datetime = None

		# Handle thumbnail upload
		if "thumbnail" in request.files:
			thumbnail_file = request.files["thumbnail"]
			if thumbnail_file.filename:
				post.thumbnail_path = _save_file(thumbnail_file, current_app.config["UPLOAD_THUMBNAILS"])

		# Handle PDF upload
		if "pdf" in request.files:
			pdf_file = request.files["pdf"]
			if pdf_file.filename:
				post.pdf_path = _save_file(pdf_file, current_app.config["UPLOAD_PDFS"])

		post.title = title
		post.content = content
		post.category_id = category_id
		post.excerpt = excerpt
		post.tags = tags
		post.status = status
		post.series_name = series_name if series_name else None
		post.series_order = int(series_order) if series_order else None
		post.scheduled_at = scheduled_datetime
		db.session.commit()
		flash("Post updated successfully!", "success")
		return redirect(url_for("posts.detail", post_id=post.id))

	return render_template("posts/edit.html", post=post, categories=Category.query.all())


@posts_bp.route("/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	
	# Check if user can delete this post
	if post.user_id != current_user.id and not current_user.is_admin:
		flash("You can only delete your own posts.", "danger")
		return redirect(url_for("posts.detail", post_id=post.id))

	db.session.delete(post)
	db.session.commit()
	flash("Post deleted successfully!", "success")
	return redirect(url_for("main.index"))


@posts_bp.route("/upload-image", methods=["POST"])
@login_required
def upload_image():
	if "image" not in request.files:
		return jsonify({"error": "No image provided"}), 400
	
	file = request.files["image"]
	if file.filename == "":
		return jsonify({"error": "No file selected"}), 400
	
	if file:
		filename = _save_file(file, current_app.config["UPLOAD_CONTENT_IMAGES"])
		image_url = url_for("static", filename=filename, _external=True)
		return jsonify({"url": image_url})
	
	return jsonify({"error": "Upload failed"}), 400


def _save_file(file_storage, upload_folder):
	"""Save uploaded file and return the relative path"""
	if file_storage.filename == "":
		return None
	
	# Secure the filename
	filename = secure_filename(file_storage.filename)
	
	# Generate unique filename to avoid conflicts
	file_ext = os.path.splitext(filename)[1]
	unique_filename = f"{uuid.uuid4().hex}{file_ext}"
	
	# Save file
	file_path = os.path.join(current_app.static_folder, upload_folder, unique_filename)
	file_storage.save(file_path)
	
	# Return relative path for database
	return os.path.join(upload_folder, unique_filename)


# Comment routes
@posts_bp.route("/<int:post_id>/comment", methods=["POST"])
@login_required
def add_comment(post_id):
	post = Post.query.get_or_404(post_id)
	content = request.form.get("content", "").strip()
	
	if not content:
		flash("Comment cannot be empty.", "danger")
		return redirect(url_for("posts.detail", post_id=post_id))
	
	comment = Comment(
		content=content,
		user_id=current_user.id,
		post_id=post_id
	)
	db.session.add(comment)
	db.session.commit()
	
	flash("Comment added successfully!", "success")
	return redirect(url_for("posts.detail", post_id=post_id))


@posts_bp.route("/comment/<int:comment_id>/delete", methods=["POST"])
@login_required
def delete_comment(comment_id):
	comment = Comment.query.get_or_404(comment_id)
	
	# Check if user can delete this comment
	if comment.user_id != current_user.id and not current_user.is_admin:
		flash("You can only delete your own comments.", "danger")
		return redirect(url_for("posts.detail", post_id=comment.post_id))
	
	post_id = comment.post_id
	db.session.delete(comment)
	db.session.commit()
	
	flash("Comment deleted successfully!", "success")
	return redirect(url_for("posts.detail", post_id=post_id))


# Like routes
@posts_bp.route("/<int:post_id>/like", methods=["POST"])
@login_required
def like_post(post_id):
	post = Post.query.get_or_404(post_id)
	
	# Check if already liked
	existing_like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
	
	if existing_like:
		# Unlike
		db.session.delete(existing_like)
		post.likes_count -= 1
		action = "unliked"
	else:
		# Like
		like = Like(user_id=current_user.id, post_id=post_id)
		db.session.add(like)
		post.likes_count += 1
		action = "liked"
	
	db.session.commit()
	
	if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
		return jsonify({
			"action": action,
			"likes_count": post.likes_count,
			"is_liked": action == "liked"
		})
	
	flash(f"Post {action}!", "success")
	return redirect(url_for("posts.detail", post_id=post_id))


# Bookmark routes
@posts_bp.route("/<int:post_id>/bookmark", methods=["POST"])
@login_required
def bookmark_post(post_id):
	post = Post.query.get_or_404(post_id)
	
	# Check if already bookmarked
	existing_bookmark = Bookmark.query.filter_by(user_id=current_user.id, post_id=post_id).first()
	
	if existing_bookmark:
		# Remove bookmark
		db.session.delete(existing_bookmark)
		action = "removed from bookmarks"
	else:
		# Add bookmark
		bookmark = Bookmark(user_id=current_user.id, post_id=post_id)
		db.session.add(bookmark)
		action = "added to bookmarks"
	
	db.session.commit()
	
	if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
		return jsonify({
			"action": action,
			"is_bookmarked": action == "added to bookmarks"
		})
	
	flash(f"Post {action}!", "success")
	return redirect(url_for("posts.detail", post_id=post_id))


# Follow routes
@posts_bp.route("/user/<int:user_id>/follow", methods=["POST"])
@login_required
def follow_user(user_id):
	if user_id == current_user.id:
		flash("You cannot follow yourself.", "danger")
		return redirect(url_for("main.index"))
	
	user_to_follow = User.query.get_or_404(user_id)
	
	# Check if already following
	existing_follow = Follow.query.filter_by(follower_id=current_user.id, followed_id=user_id).first()
	
	if existing_follow:
		# Unfollow
		db.session.delete(existing_follow)
		action = "unfollowed"
	else:
		# Follow
		follow = Follow(follower_id=current_user.id, followed_id=user_id)
		db.session.add(follow)
		action = "followed"
	
	db.session.commit()
	
	if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
		return jsonify({
			"action": action,
			"is_following": action == "followed"
		})
	
	flash(f"You {action} {user_to_follow.name or user_to_follow.username}!", "success")
	return redirect(url_for("main.index"))
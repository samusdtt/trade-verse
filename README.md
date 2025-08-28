# 🚀 TradeVerse - Trading Community Blog

A modern, feature-rich blogging platform for the trading community, built with Flask and PostgreSQL.

## ✨ Features

### 🎯 Core Features
- **User Authentication** - Signup, login, password reset, email verification
- **Rich Blog Posts** - Rich text editor, images, PDFs, YouTube embeds
- **Social Features** - Comments, likes, bookmarks, user follows
- **Post Management** - Drafts, scheduling, templates, series
- **Dark Mode** - Toggle between light and dark themes

### 📊 Analytics & Insights
- **Post Analytics** - Views, likes, comments tracking
- **User Dashboard** - Personal statistics and achievements
- **Activity Feed** - Real-time user activities
- **Recommendations** - AI-like post suggestions

### 🎨 Advanced Features
- **Post Export** - Download as HTML or PDF
- **Reading Lists** - Curate and share post collections
- **User Badges** - Achievement system with points
- **Post Tags** - Categorize and search posts
- **Reading Time** - Automatic calculation
- **Related Posts** - Smart post suggestions

### 🔧 Technical Features
- **Responsive Design** - Works on all devices
- **PostgreSQL Database** - Reliable data storage
- **File Uploads** - Images, PDFs, thumbnails
- **Search & Filter** - Find posts by category, tags, date
- **Email Integration** - Notifications and password reset

## 🛠️ Tech Stack

- **Backend**: Flask 3.0.3
- **Database**: PostgreSQL (Neon/Render)
- **Authentication**: Flask-Login
- **Email**: Flask-Mail (Gmail SMTP)
- **Frontend**: Bootstrap 5.3.3, Bootstrap Icons
- **Rich Text**: Quill Editor
- **PDF Export**: WeasyPrint
- **Deployment**: Render (Free Tier)

## 🚀 Quick Deploy

### Option 1: One-Click Deploy (Recommended)

1. **Fork this repository** to your GitHub account
2. **Go to [Render.com](https://render.com)** and sign up
3. **Click "New +"** → "Web Service"
4. **Connect your GitHub** and select this repository
5. **Configure the service**:
   - **Name**: `tradeverse`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app`
6. **Add Environment Variables**:
   - `SECRET_KEY`: (auto-generated)
   - `SECURITY_PASSWORD_SALT`: (auto-generated)
   - `DATABASE_URL`: (from Render PostgreSQL)
   - `MAIL_USERNAME`: Your Gmail
   - `MAIL_PASSWORD`: Your Gmail app password
   - `MAIL_DEFAULT_SENDER`: Your email
   - `ADMIN_EMAIL`: Admin email
7. **Click "Create Web Service"**

### Option 2: Manual Deploy

```bash
# Clone the repository
git clone https://github.com/yourusername/trade-verse.git
cd trade-verse

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export SECRET_KEY="your-secret-key"
export DATABASE_URL="your-postgresql-url"
export MAIL_USERNAME="your-gmail"
export MAIL_PASSWORD="your-app-password"

# Run the application
python run.py
```

## 📧 Email Setup

For email features (password reset, notifications), you need Gmail:

1. **Enable 2-Factor Authentication** on your Gmail
2. **Generate App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. **Set Environment Variables**:
   - `MAIL_USERNAME`: your-gmail@gmail.com
   - `MAIL_PASSWORD`: your-app-password
   - `MAIL_DEFAULT_SENDER`: your-gmail@gmail.com

## 🎯 Usage

### For Users
1. **Sign up** with email and username
2. **Verify email** (check spam folder)
3. **Create posts** with rich content
4. **Engage** with likes, comments, bookmarks
5. **Follow** other users
6. **Create reading lists** to organize content

### For Admins
1. **Set `is_admin=True`** in database for admin user
2. **Access admin features** - edit/delete any post
3. **Manage users** and content
4. **View analytics** and reports

## 🔧 Configuration

### Environment Variables

```bash
# Required
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host:port/db

# Email (optional)
MAIL_USERNAME=your-gmail@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-gmail@gmail.com
ADMIN_EMAIL=admin@example.com

# Optional
SECURITY_PASSWORD_SALT=your-salt
MAX_CONTENT_LENGTH=50000000
```

### Database Setup

The app automatically:
- Creates all tables on first run
- Adds default categories (Backtest, Journal, Strategy, Psychology, Education)
- Handles database migrations

## 🎨 Customization

### Themes
- Edit `tradeverse/static/css/styles.css` for custom styling
- Dark mode variables are in CSS custom properties

### Categories
- Default categories are set in `tradeverse/__init__.py`
- Add/remove categories in the database

### Features
- All features are modular and can be enabled/disabled
- Check individual route files for customization

## 📊 Performance

- **Database**: PostgreSQL with connection pooling
- **Static Files**: Served directly by Flask
- **Images**: Optimized thumbnails and responsive images
- **Caching**: Browser caching for static assets

## 🔒 Security

- **Password Hashing**: bcrypt with salt
- **CSRF Protection**: Flask-WTF
- **SQL Injection**: SQLAlchemy ORM
- **File Uploads**: Secure filename validation
- **Session Management**: Flask-Login

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check `DATABASE_URL` format
   - Ensure PostgreSQL is running

2. **Email Not Working**
   - Verify Gmail app password
   - Check spam folder
   - Enable "Less secure apps" (if needed)

3. **File Upload Issues**
   - Check file size limits
   - Verify upload directory permissions
   - Ensure allowed file types

4. **Deployment Issues**
   - Check Render logs
   - Verify environment variables
   - Ensure all dependencies are in `requirements.txt`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **Flask** - Web framework
- **Bootstrap** - UI components
- **Quill** - Rich text editor
- **Render** - Free hosting
- **Neon** - PostgreSQL hosting

---

**Made with ❤️ for the trading community**
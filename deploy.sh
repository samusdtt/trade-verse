#!/bin/bash

echo "🚀 Deploying TradeVerse to Render..."

# Check if we're in the right directory
if [ ! -f "run.py" ]; then
    echo "❌ Error: run.py not found. Make sure you're in the project root."
    exit 1
fi

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Error: Git repository not found. Please initialize git first."
    exit 1
fi

# Check if we have uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Warning: You have uncommitted changes. Committing them..."
    git add .
    git commit -m "Auto-commit before deployment"
fi

# Push to GitHub
echo "📤 Pushing to GitHub..."
git push origin main

echo "✅ Deployment initiated!"
echo ""
echo "🌐 Your TradeVerse blog will be available at:"
echo "   https://tradeverse.onrender.com"
echo ""
echo "📧 Don't forget to set up your email settings in Render dashboard:"
echo "   - MAIL_USERNAME (your Gmail)"
echo "   - MAIL_PASSWORD (your app password)"
echo "   - MAIL_DEFAULT_SENDER (your email)"
echo "   - ADMIN_EMAIL (admin email)"
echo ""
echo "🎉 Deployment complete! Check Render dashboard for status."
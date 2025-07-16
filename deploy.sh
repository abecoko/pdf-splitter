#!/bin/bash
set -e

echo "🚀 Starting automatic deployment..."

# Check if required tools are installed
check_tool() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 is not installed. Please install it first."
        return 1
    fi
    echo "✅ $1 is available"
}

echo "📋 Checking required tools..."
check_tool "git" || exit 1
check_tool "npm" || exit 1

# Get backend URL from user
echo ""
read -p "🔗 Enter your deployed backend URL (e.g., https://your-app.onrender.com): " BACKEND_URL

if [ -z "$BACKEND_URL" ]; then
    echo "❌ Backend URL is required. Exiting."
    exit 1
fi

# Validate URL format
if [[ ! $BACKEND_URL =~ ^https?:// ]]; then
    echo "❌ Invalid URL format. Please include http:// or https://"
    exit 1
fi

echo "🔧 Configuring frontend environment..."

# Update .env.production
cat > .env.production << EOF
# Vercel Production Environment Variables (Frontend)
VITE_API_URL=$BACKEND_URL
VITE_MAX_FILE_SIZE=130
EOF

echo "✅ Updated .env.production with backend URL: $BACKEND_URL"

# Commit changes
echo "📝 Committing configuration changes..."
git add .env.production
git commit -m "Update backend URL for production deployment

Backend URL: $BACKEND_URL

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>" || echo "No changes to commit"

git push origin main

echo "🌐 Deploying frontend to Vercel..."

# Check if vercel is installed, if not install it
if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
fi

# Deploy to Vercel
cd frontend
vercel --prod --yes
cd ..

echo ""
echo "🎉 Deployment completed!"
echo "✅ Backend: $BACKEND_URL"
echo "✅ Frontend: Check the Vercel output above for the URL"
echo ""
echo "🧪 Test your application:"
echo "1. Open the frontend URL"
echo "2. Upload a PDF file"
echo "3. Specify page ranges (e.g., 1-5,8,10-12)"
echo "4. Download the split PDF as ZIP"
echo ""
echo "🐛 If there are issues:"
echo "1. Check that backend is responding: curl $BACKEND_URL/health"
echo "2. Verify CORS settings allow your frontend domain"
echo "3. Check Vercel environment variables are set correctly"
#!/bin/bash

echo "🧪 Testing JAR-VET Deployment Readiness..."
echo ""

# Test frontend build
echo "📦 Testing frontend build..."
cd frontend
npm run build
if [ $? -eq 0 ]; then
    echo "✅ Frontend build successful"
else
    echo "❌ Frontend build failed"
    exit 1
fi
echo ""

# Test backend
echo "🔧 Testing backend..."
cd ../backend
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

python -c "import fastapi; import uvicorn; print('✅ Backend dependencies OK')"
if [ $? -ne 0 ]; then
    echo "❌ Backend dependencies missing"
    exit 1
fi
echo ""

# Check for API key
if [ -f ".env" ]; then
    if grep -q "GEMINI_API_KEY" .env; then
        echo "✅ .env file exists with API key"
    else
        echo "⚠️  .env file exists but GEMINI_API_KEY not found"
    fi
else
    echo "⚠️  .env file not found - create one before deploying"
fi
echo ""

echo "🎉 Deployment readiness check complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Deploy backend to Railway: https://railway.app/"
echo "2. Deploy frontend to Vercel: https://vercel.com/"
echo "3. See DEPLOY_NOW.md for detailed instructions"

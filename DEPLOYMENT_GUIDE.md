# JAR-VET Deployment Guide

## Important Note About Vercel

⚠️ **Vercel Limitation**: Vercel **does NOT support WebSockets** in serverless functions. Since JAR-VET uses WebSocket for real-time communication between frontend and backend, you have two options:

## Option 1: Split Deployment (RECOMMENDED)

### Frontend → Vercel (Static)
### Backend → Railway/Render/Heroku (WebSocket Support)

---

## 🚀 **Option 1: Recommended Deployment**

### **A. Deploy Frontend to Vercel**

1. **Install Vercel CLI**
```bash
npm install -g vercel
```

2. **Navigate to Frontend**
```bash
cd /mnt/d/projects/experiment/jarvis/frontend
```

3. **Login to Vercel**
```bash
vercel login
```

4. **Deploy Frontend**
```bash
vercel --prod
```

5. **Note your frontend URL** (e.g., `https://jar-vet.vercel.app`)

### **B. Deploy Backend to Railway (Free Tier)**

1. **Create Railway Account**: https://railway.app/

2. **Install Railway CLI**
```bash
npm install -g @railway/cli
```

3. **Login to Railway**
```bash
railway login
```

4. **Navigate to Backend**
```bash
cd /mnt/d/projects/experiment/jarvis/backend
```

5. **Initialize Railway Project**
```bash
railway init
```

6. **Add Environment Variables**
```bash
railway variables set GEMINI_API_KEY=your_api_key_here
railway variables set USE_SEARCH_GROUNDING=true
```

7. **Deploy Backend**
```bash
railway up
```

8. **Get Backend URL** (e.g., `https://jar-vet-backend.up.railway.app`)

### **C. Connect Frontend to Backend**

Update the WebSocket URL in frontend:

**File**: `/frontend/src/websocket-client.js`

Change line 2:
```javascript
constructor(url = 'wss://jar-vet-backend.up.railway.app/ws') {
```

Then redeploy frontend:
```bash
cd /mnt/d/projects/experiment/jarvis/frontend
vercel --prod
```

---

## 🔄 **Option 2: Alternative Platforms**

### **Deploy Both to Railway**

Railway supports both static sites and WebSocket backends.

```bash
# Deploy frontend
cd /mnt/d/projects/experiment/jarvis/frontend
railway init
railway up

# Deploy backend
cd /mnt/d/projects/experiment/jarvis/backend
railway init
railway variables set GEMINI_API_KEY=your_key
railway up
```

### **Deploy Both to Render**

Render.com offers free tier with WebSocket support.

1. Create account at https://render.com
2. Create **Web Service** for backend
3. Create **Static Site** for frontend
4. Set environment variables
5. Deploy

### **Deploy Both to Heroku**

```bash
# Install Heroku CLI
npm install -g heroku

# Deploy backend
cd /mnt/d/projects/experiment/jarvis/backend
heroku create jar-vet-backend
git init
git add .
git commit -m "Initial commit"
git push heroku main

# Deploy frontend
cd /mnt/d/projects/experiment/jarvis/frontend
heroku create jar-vet-frontend
git init
git add .
git commit -m "Initial commit"
git push heroku main
```

---

## 📱 **Android Compatibility**

### **Already Implemented:**

✅ Responsive viewport meta tags
✅ Touch-optimized UI elements
✅ Mobile-friendly sizing
✅ Safe area insets for notched devices
✅ Tap highlight removal
✅ Touch gesture support
✅ PWA-ready meta tags

### **Testing on Android:**

1. Open Chrome on Android
2. Visit your deployed URL
3. Test touch interactions:
   - Tap orb for voice input
   - Type in input field
   - Drag orb to rotate
   - Toggle speaker
   - View results card

### **Install as PWA (Optional):**

Add to home screen:
1. Open site in Chrome
2. Menu → "Add to Home Screen"
3. App icon appears on home screen

---

## 🔧 **Configuration Files Created**

### Frontend (`/frontend/vercel.json`)
- Vite build configuration
- SPA routing support
- Security headers

### Backend (`/backend/vercel.json`)
- Python runtime configuration
- Environment variables setup
- API routing

---

## 🌐 **Environment Variables**

### Backend Needs:
- `GEMINI_API_KEY` - Your Google Gemini API key
- `USE_SEARCH_GROUNDING` - Set to "true"

### Frontend Needs:
- Update WebSocket URL to production backend

---

## 📋 **Pre-Deployment Checklist**

- [ ] Gemini API key is valid
- [ ] Backend requirements.txt is complete
- [ ] Frontend builds successfully (`npm run build`)
- [ ] WebSocket URL updated for production
- [ ] Environment variables set on hosting platform
- [ ] CORS configured for production domains
- [ ] Test on Android device after deployment

---

## 🚨 **Known Issues & Solutions**

### Issue: WebSocket connection fails
**Solution**: Ensure backend is on a platform that supports WebSockets (Railway, Render, Heroku - NOT Vercel serverless)

### Issue: Voice recognition doesn't work on Android
**Solution**: Voice recognition requires HTTPS. Ensure your deployment uses HTTPS (all mentioned platforms provide this)

### Issue: Mobile layout broken
**Solution**: Clear browser cache and hard refresh

---

## 💡 **Recommended Setup**

**Best Free Option:**
- Frontend: **Vercel** (unlimited bandwidth, fast CDN)
- Backend: **Railway** (free tier, WebSocket support, easy setup)

**Why?**
- Both have generous free tiers
- Easy deployment process
- Automatic HTTPS
- Good performance
- WebSocket support on Railway

---

## 📞 **Support**

After deployment, test these features:
1. Voice input (requires microphone permission)
2. Text input and send
3. Speaker toggle
4. Orb interaction
5. Results card display
6. Mobile responsiveness

---

**Status**: Ready for deployment
**Platforms**: Railway (backend) + Vercel (frontend)
**Mobile**: Fully compatible with Android

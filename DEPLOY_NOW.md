# 🚀 Deploy JAR-VET Now - Step by Step

## ⚠️ IMPORTANT: Vercel + WebSocket Issue

**Vercel does NOT support WebSockets in serverless functions.**

You must use:
- **Frontend**: Vercel ✅
- **Backend**: Railway/Render/Heroku (NOT Vercel) ✅

---

## 🎯 Quick Deploy (Choose One Method)

### **Method 1: Railway (Recommended - Easiest)**

#### **A. Deploy Backend**

1. **Go to**: https://railway.app/new
2. **Sign up** with GitHub
3. Click **"Deploy from GitHub repo"**
4. Select your repository or click **"Deploy from local"**
5. **Set Root Directory**: `backend`
6. **Add Environment Variables**:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   USE_SEARCH_GROUNDING=true
   ```
7. **Deploy** - Railway will auto-detect Python and deploy
8. **Copy URL**: e.g., `jar-vet-backend.up.railway.app`

#### **B. Deploy Frontend**

1. **Go to**: https://vercel.com/new
2. **Import** your repository
3. **Configure**:
   - Framework: **Vite**
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. **Deploy**
5. **Done!** Your site is live

---

### **Method 2: Using CLI (For Developers)**

#### **Install CLIs**
```bash
npm install -g vercel @railway/cli
```

#### **Deploy Backend to Railway**
```bash
cd /mnt/d/projects/experiment/jarvis/backend
railway login
railway init
railway variables set GEMINI_API_KEY=your_key
railway variables set USE_SEARCH_GROUNDING=true
railway up
railway domain
```

#### **Deploy Frontend to Vercel**
```bash
cd /mnt/d/projects/experiment/jarvis/frontend
vercel login
vercel --prod
```

---

### **Method 3: All on Railway**

Deploy both frontend and backend to Railway:

```bash
# Backend
cd /mnt/d/projects/experiment/jarvis/backend
railway init
railway variables set GEMINI_API_KEY=your_key
railway up

# Frontend
cd /mnt/d/projects/experiment/jarvis/frontend
railway init
railway up
```

---

## 📱 **Android Compatibility - Already Done! ✅**

Your UI is now Android-ready with:
- ✅ Touch-optimized controls
- ✅ Responsive layout for all screen sizes
- ✅ Safe area support for notched devices
- ✅ PWA-ready (can install as app)
- ✅ Optimized tap targets
- ✅ Mobile-friendly animations

---

## 🔑 **Before You Deploy**

### **Get Your Gemini API Key**

1. Go to: https://makersuite.google.com/app/apikey
2. Click **"Create API Key"**
3. Copy the key
4. Add it to your backend environment variables

---

## 📋 **Deployment Checklist**

- [ ] Have Gemini API key ready
- [ ] Backend deployed to Railway/Render
- [ ] Backend URL copied
- [ ] Frontend deployed to Vercel
- [ ] Test on desktop browser
- [ ] Test on Android Chrome
- [ ] Verify voice input works (HTTPS required)
- [ ] Check WebSocket connection

---

## 🧪 **Test Your Deployment**

### **Desktop Test**
1. Open your Vercel URL
2. Click orb or mic icon
3. Ask: "What vaccinations does a puppy need?"
4. Verify response appears

### **Android Test**
1. Open Chrome on Android
2. Visit your Vercel URL
3. Allow microphone permission
4. Test voice input
5. Test text input
6. Try rotating orb
7. Check results card display

---

## 🎨 **Your Deployed URLs**

After deployment, you'll have:

- **Frontend**: `https://jar-vet.vercel.app` (or your custom domain)
- **Backend**: `https://jar-vet-backend.up.railway.app`
- **API Health**: `https://jar-vet-backend.up.railway.app/health`

---

## 💡 **Pro Tips**

### **Custom Domain (Optional)**
- Vercel: Project Settings → Domains → Add Domain
- Railway: Project Settings → Networking → Custom Domain

### **Install as App on Android**
1. Open site in Chrome
2. Menu (⋮) → "Add to Home Screen"
3. Icon appears on home screen
4. Opens like a native app!

### **Monitor Usage**
- Railway Dashboard: View logs, metrics, usage
- Vercel Dashboard: View analytics, bandwidth

---

## 🆘 **Common Issues**

### **"WebSocket connection failed"**
- Backend must be on Railway/Render (NOT Vercel)
- Check backend URL is correct
- Verify backend is running

### **"Voice recognition not working"**
- Requires HTTPS (automatic on Vercel/Railway)
- Allow microphone permission
- Use Chrome/Edge/Safari browser

### **"API Key Invalid"**
- Check environment variable is set correctly
- Verify API key at https://makersuite.google.com/app/apikey
- No quotes around the key value

---

## 📊 **Free Tier Limits**

### **Railway**
- $5 credit/month (renews monthly)
- ~500 hours of usage
- Perfect for JAR-VET

### **Vercel**
- Unlimited bandwidth
- 100GB bandwidth/month
- More than enough for JAR-VET

### **Gemini API**
- 15 requests/minute (free tier)
- 1,500 requests/day
- Sufficient for testing and moderate use

---

## 🎉 **You're Ready!**

Everything is configured and ready to deploy. Choose your method above and follow the steps!

**Estimated Time**: 5-10 minutes
**Cost**: $0 (free tiers)
**Difficulty**: Easy

---

**Questions?** Check the full `DEPLOYMENT_GUIDE.md` for detailed information.

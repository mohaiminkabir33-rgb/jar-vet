# JAR-VET Quick Deployment Guide

## 🚀 Fastest Way to Deploy (5 Minutes)

### **Step 1: Deploy Backend to Railway**

1. Go to https://railway.app/ and sign up (free)

2. Click **"New Project"** → **"Deploy from GitHub repo"**
   - Or use **"Empty Project"** and upload manually

3. **Add Environment Variables:**
   - Click your project → **Variables** tab
   - Add: `GEMINI_API_KEY` = `your_gemini_api_key`
   - Add: `USE_SEARCH_GROUNDING` = `true`

4. **Configure Service:**
   - Root Directory: `/backend`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

5. **Copy your backend URL** (e.g., `jar-vet-backend.up.railway.app`)

---

### **Step 2: Update Frontend WebSocket URL**

The frontend is already configured to auto-detect production URLs!

Just make sure your Railway backend domain follows this pattern:
- Frontend: `jar-vet.vercel.app`
- Backend: `jar-vet-backend.up.railway.app`

Or manually set it in `/frontend/src/websocket-client.js` line 10.

---

### **Step 3: Deploy Frontend to Vercel**

1. Go to https://vercel.com/ and sign up (free)

2. Click **"Add New Project"** → **"Import Git Repository"**
   - Or use Vercel CLI:

```bash
cd /mnt/d/projects/experiment/jarvis/frontend
npm install -g vercel
vercel login
vercel --prod
```

3. **Configure:**
   - Framework Preset: **Vite**
   - Root Directory: `/frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`

4. **Deploy!** Your site will be live at `https://your-project.vercel.app`

---

## ✅ **Done!**

Your JAR-VET is now live:
- 🌐 **Frontend**: `https://jar-vet.vercel.app`
- 🔌 **Backend**: `https://jar-vet-backend.up.railway.app`

---

## 📱 **Android Testing**

1. Open Chrome on Android
2. Visit your Vercel URL
3. Allow microphone permission when prompted
4. Test all features:
   - ✅ Voice input
   - ✅ Text input
   - ✅ Orb interaction
   - ✅ Results display
   - ✅ Speaker toggle

---

## 🔧 **Alternative: One-Click Deploy**

### **Deploy to Render (Both Frontend + Backend)**

1. Go to https://render.com/
2. Create **Web Service** for backend:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Add environment variables

3. Create **Static Site** for frontend:
   - Build Command: `npm run build`
   - Publish Directory: `dist`

---

## 💰 **Cost Comparison**

| Platform | Frontend | Backend | WebSocket | Free Tier |
|----------|----------|---------|-----------|-----------|
| **Vercel** | ✅ Best | ❌ No WS | ❌ | Unlimited |
| **Railway** | ✅ Good | ✅ Best | ✅ | $5 credit/month |
| **Render** | ✅ Good | ✅ Good | ✅ | 750 hours/month |
| **Heroku** | ✅ Good | ✅ Good | ✅ | Limited |

**Recommendation**: Vercel (frontend) + Railway (backend)

---

## 🐛 **Troubleshooting**

### WebSocket Connection Failed
- Check backend URL is correct
- Ensure backend is running
- Check CORS settings
- Verify HTTPS/WSS protocol

### Voice Recognition Not Working
- Requires HTTPS (all platforms provide this)
- Check microphone permissions
- Only works on Chrome/Edge/Safari

### Mobile UI Issues
- Hard refresh (Ctrl+Shift+R)
- Clear browser cache
- Check viewport meta tags

---

## 📚 **Additional Resources**

- Railway Docs: https://docs.railway.app/
- Vercel Docs: https://vercel.com/docs
- Render Docs: https://render.com/docs

---

**Ready to deploy!** Follow the steps above and your JAR-VET will be live in minutes! 🚀🐾

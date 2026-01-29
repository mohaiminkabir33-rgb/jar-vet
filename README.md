# JAR-VET - Veterinary AI Assistant 🐾

A specialized AI assistant for veterinary medicine with a beautiful liquid orb interface.

## ✨ Features

- 🤖 **Specialized Veterinary AI** - Expert knowledge across all animal species
- 🎤 **Voice Input** - Click orb or mic icon to speak
- ⌨️ **Text Input** - Type your questions
- 🔊 **Voice Output** - Toggle AI voice responses
- 🌊 **Interactive Liquid Orb** - Click to activate, drag to rotate
- 💎 **Premium Glassmorphism UI** - Modern, professional design
- 📱 **Mobile Optimized** - Fully responsive, Android compatible
- 🔒 **Real-time Search** - Google Search grounding for up-to-date info

## 🚀 Quick Start (Local)

### Prerequisites
- Node.js 16+
- Python 3.11+
- Gemini API Key

### Installation

1. **Clone and Install**
```bash
# Install frontend
cd frontend
npm install

# Install backend
cd ../backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
cd backend
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

3. **Run**
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
python main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

4. **Access**: http://localhost:3000

## 🌐 Deployment

### **Recommended Setup**
- **Frontend**: Vercel (free, fast CDN)
- **Backend**: Railway (free tier, WebSocket support)

### **Quick Deploy**

See `DEPLOY_NOW.md` for detailed step-by-step instructions.

**TL;DR:**
1. Deploy backend to Railway with Gemini API key
2. Deploy frontend to Vercel
3. WebSocket URL auto-configures for production

## 📱 Android Compatibility

✅ **Fully Compatible**
- Responsive design for all screen sizes
- Touch-optimized controls
- Safe area support for notched devices
- PWA-ready (installable as app)
- Works on Chrome, Edge, Samsung Internet

**To Install as App:**
1. Open in Chrome on Android
2. Menu → "Add to Home Screen"
3. Launch from home screen

## 🎯 Usage

### **Voice Input**
- Click the liquid orb
- OR click the microphone icon
- Speak your veterinary question
- AI responds with expert guidance

### **Text Input**
- Type in the bottom input field
- Press Enter or click send button
- Get instant veterinary advice

### **Example Queries**
- "What vaccinations does a puppy need?"
- "My cat is vomiting, what should I do?"
- "Signs of colic in horses?"
- "How to care for a bearded dragon?"
- "My dog ate chocolate, is this dangerous?"

## 🏗️ Tech Stack

### **Frontend**
- Vite
- Three.js (3D orb rendering)
- GSAP (animations)
- Web Speech API (voice recognition)
- WebSocket client

### **Backend**
- FastAPI
- Google Gemini 2.5 Flash
- WebSocket server
- Python 3.11

## 📂 Project Structure

```
jarvis/
├── frontend/
│   ├── src/
│   │   ├── main-liquid.js       # Main UI controller
│   │   ├── liquid-orb.js        # 3D orb rendering
│   │   ├── websocket-client.js  # WebSocket connection
│   │   └── speech-synthesis.js  # Text-to-speech
│   ├── index.html               # Main HTML
│   ├── package.json
│   └── vercel.json              # Vercel config
├── backend/
│   ├── ai/
│   │   ├── gemini_ai.py         # Veterinary AI brain
│   │   └── nlp_engine.py        # Intent processing
│   ├── main.py                  # FastAPI server
│   ├── requirements.txt
│   ├── railway.json             # Railway config
│   └── Procfile                 # Process config
└── README.md
```

## 🔧 Configuration

### **Environment Variables**

**Backend (.env)**
```env
GEMINI_API_KEY=your_gemini_api_key
USE_SEARCH_GROUNDING=true
```

**Frontend**
- Auto-detects production vs development
- WebSocket URL configures automatically

## 🎨 Customization

### **Change Orb Color**
Edit `/frontend/src/liquid-orb.js` line 26:
```javascript
uColor: { value: new THREE.Color(0x5E87FF) }
```

### **Change AI Personality**
Edit `/backend/ai/gemini_ai.py` lines 42-90 (system prompt)

### **Adjust Orb Size**
Edit `/frontend/src/liquid-orb.js` line 21:
```javascript
const geometry = new THREE.SphereGeometry(1.7, 256, 256);
```

## 📊 Performance

- **Frontend**: ~560KB gzipped
- **Backend**: <50MB memory
- **Response Time**: 1-3 seconds
- **WebSocket**: Real-time, low latency

## 🔒 Security

- HTTPS enforced in production
- API keys stored as environment variables
- CORS configured for production domains
- No data persistence (privacy-first)

## 📄 License

MIT License - Free to use and modify

## 🤝 Contributing

This is a personal project. Feel free to fork and customize for your needs.

## 📞 Support

For deployment issues, check:
- `DEPLOYMENT_GUIDE.md` - Detailed deployment info
- `DEPLOY_NOW.md` - Quick start guide
- `VETERINARY_SPECIALIZATION.md` - AI specialization details

---

## 🎯 Quick Links

- **Gemini API**: https://makersuite.google.com/app/apikey
- **Railway**: https://railway.app/
- **Vercel**: https://vercel.com/
- **Render**: https://render.com/

---

**Built with ❤️ for veterinary professionals and animal lovers**

**Version**: 1.0.0
**Last Updated**: January 29, 2026

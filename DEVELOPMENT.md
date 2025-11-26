# 🎯 Development Workflow Guide

## 📂 Project Overview

**BadDebtGuard AI** is a full-stack application with:
- **Backend**: FastAPI (Python) - AI-powered loan risk analysis
- **Frontend**: React + Vite - User interface for loan assessment

---

## 🛠️ Development Setup

### First Time Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Cerebral-cortex
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.template .env
   # Edit .env and add your HF_TOKEN
   ```

3. **Frontend Setup**
   ```bash
   cd ../frontend
   npm install
   ```

### Daily Development

**Quick Start (Both Servers):**
```bash
# Windows
start.bat

# Linux/Mac
./start.sh
```

**Manual Start:**
```bash
# Terminal 1: Backend
cd backend
python -m app.main

# Terminal 2: Frontend
cd frontend
npm run dev
```

---

## 📁 Project Structure Guide

### Backend Architecture

```
backend/
├── app/                    # Application package
│   ├── __init__.py        # Package marker
│   ├── main.py            # FastAPI routes & LLM logic
│   ├── extractor.py       # Document text extraction
│   └── config.py          # Environment configuration
├── uploads/               # Temporary file uploads
├── .venv/                 # Virtual environment (gitignored)
├── requirements.txt       # Python dependencies
└── pyproject.toml        # Project metadata
```

**Key Files:**
- `main.py`: API endpoints, LLM prompts, analysis logic
- `extractor.py`: PDF/DOCX/TXT/Image text extraction
- `config.py`: Environment variables, HuggingFace token

### Frontend Architecture

```
frontend/
├── src/
│   ├── App.jsx           # Main component (entire UI)
│   ├── App.css           # All styling
│   ├── main.jsx          # React entry point
│   └── assets/           # Images, icons
├── public/               # Static files
├── index.html            # HTML template
├── vite.config.js        # Vite configuration
└── package.json          # Dependencies
```

**Key Files:**
- `App.jsx`: Entire application UI and logic
- `App.css`: All custom styles (TailwindCSS included)

---

## 🔧 Common Development Tasks

### Adding a New Backend Feature

1. **Add new endpoint in `backend/app/main.py`:**
   ```python
   @app.post("/api/new-feature")
   async def new_feature():
       return {"message": "Hello"}
   ```

2. **Test the endpoint:**
   ```bash
   # Backend auto-reloads
   # Visit: http://localhost:8000/docs
   ```

### Adding a New Frontend Feature

1. **Edit `frontend/src/App.jsx`:**
   ```jsx
   function NewComponent() {
     return <div>New Feature</div>;
   }
   ```

2. **Frontend auto-reloads** - Check http://localhost:5173

### Adding Dependencies

**Backend (Python):**
```bash
cd backend
pip install new-package
pip freeze > requirements.txt
```

**Frontend (Node):**
```bash
cd frontend
npm install new-package
```

### Document Processing

**Supported formats** (handled in `extractor.py`):
- PDF: `pdfplumber`
- DOCX: `python-docx`
- TXT: Built-in Python
- Images: Would need OCR (pytesseract)

**Add new format:**
```python
# In backend/app/extractor.py
def extract_text(file_path):
    # Add new extension handling
    if extension == ".new_format":
        # Your extraction logic
        pass
```

---

## 🧪 Testing

### Manual Testing

1. Start both servers
2. Open http://localhost:5173
3. Upload test documents
4. Verify analysis results

### Test Documents
Create sample documents in a `test-data/` folder:
- `sample-payslip.pdf`
- `sample-bank-statement.docx`
- `sample-id.txt`

### API Testing
Use FastAPI's built-in docs:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

---

## 🐛 Debugging

### Backend Debugging

**Check logs:**
```bash
# Terminal shows FastAPI logs
# Look for errors in console
```

**Common issues:**
- `ModuleNotFoundError`: Check imports use `app.module` format
- `FileNotFoundError`: Ensure `uploads/` directory exists
- `Invalid HF_TOKEN`: Check `.env` file

**Debug mode:**
```python
# In main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Frontend Debugging

**Browser console:**
- Right-click → Inspect → Console tab
- Look for network errors (failed API calls)

**Common issues:**
- `CORS error`: Backend must allow `http://localhost:5173`
- `Network error`: Ensure backend is running on port 8000
- `Component not updating`: Check state management

---

## 📦 Building for Production

### Backend Production

```bash
cd backend
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend Production

```bash
cd frontend
npm run build
# Output in frontend/dist/
```

**Serve built frontend:**
```bash
npm run preview
# Or use any static file server
```

---

## 🔒 Security Best Practices

1. **Never commit `.env` files**
   - Always in `.gitignore`
   - Use `.env.template` for documentation

2. **Validate file uploads**
   - Check file types
   - Limit file sizes
   - Scan for malware in production

3. **API Security**
   - Add authentication (JWT tokens)
   - Rate limiting
   - Input validation

4. **Environment Variables**
   ```bash
   # Development
   HF_TOKEN=dev_token
   
   # Production
   HF_TOKEN=prod_token_from_secrets_manager
   ```

---

## 📊 Performance Tips

### Backend Optimization

1. **Async processing:**
   ```python
   # Use async/await for I/O operations
   async def process_file(file):
       await asyncio.to_thread(extract_text, file)
   ```

2. **Caching:**
   - Cache LLM responses for identical documents
   - Use Redis for session storage

3. **File cleanup:**
   - Auto-delete old uploads
   - Implement scheduled cleanup task

### Frontend Optimization

1. **Code splitting:**
   ```jsx
   const HeavyComponent = lazy(() => import('./HeavyComponent'));
   ```

2. **Memoization:**
   ```jsx
   const memoizedValue = useMemo(() => expensiveCalc(), [deps]);
   ```

3. **Image optimization:**
   - Use WebP format
   - Lazy load images

---

## 🚀 Deployment

### Backend Deployment Options

1. **Railway / Render / Fly.io** (Easiest)
2. **AWS EC2 / DigitalOcean** (More control)
3. **Docker** (Containerized)

### Frontend Deployment Options

1. **Vercel / Netlify** (Easiest - auto deploy)
2. **GitHub Pages** (Free static hosting)
3. **Cloudflare Pages** (CDN included)

### Environment Variables in Production

**Backend:**
```bash
# Set in hosting platform
HF_TOKEN=your_production_token
CORS_ORIGINS=https://your-frontend.com
```

**Frontend:**
```bash
# In vite.config.js or .env
VITE_API_URL=https://your-backend-api.com
```

---

## 📚 Learning Resources

### FastAPI
- [Official Docs](https://fastapi.tiangolo.com/)
- [Tutorial](https://fastapi.tiangolo.com/tutorial/)

### React
- [Official Docs](https://react.dev/)
- [React Hooks](https://react.dev/reference/react)

### HuggingFace
- [Inference API](https://huggingface.co/docs/api-inference/index)
- [Models](https://huggingface.co/models)

---

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit pull request

### Code Style

**Python:**
- Follow PEP 8
- Use type hints
- Add docstrings

**JavaScript:**
- Use ESLint rules
- Consistent naming
- Add comments for complex logic

---

## 💡 Tips & Tricks

### Backend Tips

1. **Hot reload works** - Edit `main.py` and see changes instantly
2. **Use FastAPI docs** - Visit `/docs` for interactive API testing
3. **Print debugging** - Use `logger.info()` instead of `print()`

### Frontend Tips

1. **Vite is fast** - HMR updates in milliseconds
2. **React DevTools** - Install browser extension
3. **Console.log** - Use browser console for debugging

### Git Tips

```bash
# Create feature branch
git checkout -b feature/new-feature

# Commit with good messages
git commit -m "feat: add new loan type support"

# Push to remote
git push origin feature/new-feature
```

---

**Happy Coding! 🚀**

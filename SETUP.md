# 🚀 Quick Setup Guide

## Prerequisites

- **Python 3.8+** installed
- **Node.js 16+** and npm installed
- **HuggingFace Account** (for API token)

## Step-by-Step Setup

### 1️⃣ Backend Configuration

```bash
cd backend
```

#### Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Configure Environment Variables
Create a `.env` file in the `backend/` directory:
```env
HF_TOKEN=your_huggingface_token_here
```

To get your HuggingFace token:
1. Go to https://huggingface.co/settings/tokens
2. Create a new token with read access
3. Copy and paste it in the `.env` file

### 2️⃣ Frontend Configuration

```bash
cd ../frontend
```

#### Install Node Dependencies
```bash
npm install
```

### 3️⃣ Start the Application

#### Option A: Start Everything at Once (Recommended)

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

#### Option B: Start Manually

**Terminal 1 - Backend:**
```bash
cd backend
python -m app.main
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## 🌐 Access the Application

- **Frontend UI**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🧪 Testing

1. Open the frontend at http://localhost:5173
2. Select banking system (Conventional/Islamic)
3. Choose loan type (Home/Car/Personal/Business)
4. Select customer type
5. Upload sample documents (PDF, DOCX, TXT, images)
6. Click "Start AI-Powered Analysis"

## 📦 Supported Document Formats

- PDF (`.pdf`)
- Word Documents (`.docx`)
- Text Files (`.txt`)
- Images (`.png`, `.jpg`, `.jpeg`, `.bmp`, `.tiff`)

## ⚙️ Configuration

### Backend Port (default: 8000)
Edit `backend/app/main.py`:
```python
uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
```

### Frontend Port (default: 5173)
Edit `frontend/vite.config.js`:
```javascript
export default defineConfig({
  server: {
    port: 5173
  }
})
```

## 🐛 Troubleshooting

### Backend won't start
- Check if Python is installed: `python --version`
- Verify dependencies: `pip list`
- Check if port 8000 is available
- Ensure `.env` file exists with valid HF_TOKEN

### Frontend won't start
- Check if Node.js is installed: `node --version`
- Verify dependencies: `npm list`
- Clear node_modules: `rm -rf node_modules && npm install`
- Check if port 5173 is available

### API Connection Error
- Ensure backend is running on http://localhost:8000
- Check CORS settings in `backend/app/main.py`
- Verify frontend is making requests to correct URL

## 📝 Development Notes

- Backend auto-reloads on code changes (FastAPI reload mode)
- Frontend hot-reloads on code changes (Vite HMR)
- Uploaded files are stored temporarily in `backend/uploads/`
- All uploaded files are automatically cleaned up after analysis

## 🔒 Security Notes

- **Never commit `.env` file** to version control
- Keep your HuggingFace token private
- In production, use proper authentication and authorization
- Validate all file uploads before processing

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [HuggingFace Inference API](https://huggingface.co/docs/api-inference/index)

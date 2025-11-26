# BadDebtGuard AI - Intelligent Loan Assessment Platform

An AI-powered loan assessment system for Malaysian banking institutions, supporting both Conventional and Islamic banking models.

## 🏗️ Project Structure

```
Cerebral-cortex/
├── backend/          # FastAPI backend server
│   ├── app/          # Application code
│   │   ├── main.py       # API endpoints and LLM integration
│   │   ├── extractor.py  # Document text extraction
│   │   └── config.py     # Configuration settings
│   ├── uploads/      # Temporary file uploads
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── README.md
│
└── frontend/         # React + Vite frontend
    ├── src/          # React components
    │   ├── App.jsx       # Main application
    │   ├── App.css       # Styling
    │   ├── main.jsx      # Entry point
    │   └── assets/       # Static assets
    ├── public/       # Public assets
    ├── index.html
    ├── package.json
    └── vite.config.js
```

## 🚀 Getting Started

### Backend Setup

1. Navigate to backend directory:
   ```powershell
   cd backend
   ```

2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

3. Create `.env` file with your OpenAI API key:
   ```powershell
   Copy-Item .env.template .env
   # Then edit .env and add your OPENAI_API_KEY
   ```
   Example `.env` content:
   ```
   OPENAI_API_KEY=sk-proj-your_key_here
   ```

4. Start the server:
   ```powershell
   python -m app.main
   ```
   Or use the provided startup script:
   ```powershell
   .\start.bat
   ```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
   ```powershell
   cd ..\frontend
   ```

2. Install dependencies:
   ```powershell
   npm install
   ```

3. Start development server:
   ```powershell
   npm run dev
   ```

The frontend will be available at `http://localhost:5173`

## 🎯 Features

- **Multi-Banking Support**: Conventional and Islamic banking models
- **Loan Type Coverage**: Home, Car, Personal, and Business financing
- **Customer Segmentation**: Salaried, Rental Income, Small Business, Large Enterprise
- **AI-Powered Analysis**: OpenAI GPT-4o based document analysis and credit risk assessment
- **Bilingual Interface**: English and Malay language support
- **Document Processing**: PDF, DOCX, TXT, and image file support
- **Risk Metrics**: Credit scoring, default probability, and risk premium calculation
- **CCRIS Integration**: Bank Negara Malaysia credit reporting integration

## 🔧 Technology Stack

**Backend:**
- FastAPI
- Python 3.12+
- OpenAI GPT-4o API
- PDFPlumber, python-docx
- Pydantic

**Frontend:**
- React 19
- Vite 7
- TailwindCSS 4
- Lucide React Icons
- Bilingual Support (English/Malay)

## 📝 API Endpoints

- `GET /` - API information
- `GET /api/health` - Health check
- `POST /api/upload-documents` - Upload documents
- `POST /api/analyze-loan` - Analyze loan application
- `POST /api/cleanup` - Clean temporary files
- `GET /api/status` - System status

## 📄 License

This project is part of CodeFest25 - BadDebtGuard AI initiative.

## 👥 Contributors

- Team: Cerebral-Cortex
- Repository: touhidulai/Cerebral-Cortex_CodeFest25_BadDebtGuard-AI

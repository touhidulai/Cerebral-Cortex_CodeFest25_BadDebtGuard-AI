# 🏦 BadDebtGuard AI - Intelligent Loan Assessment Platform

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.12+-yellow)
![React](https://img.shields.io/badge/react-19.0-blue)

**An advanced AI-powered hybrid loan risk assessment system for Malaysian banking institutions**

Combining **XGBoost Machine Learning (70%)** and **OpenAI GPT-4o LLM with RAG (30%)** for comprehensive, BNM-compliant credit risk analysis.

</div>

---

## 📋 Table of Contents
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Technology Stack](#-technology-stack)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)

---

## 🎯 Key Features

### 🤖 Hybrid AI Architecture
- **✅ 70% XGBoost ML Model**: Trained on 24,000 historical Malaysian loan records with 99.79% accuracy
- **✅ 30% GPT-4o LLM**: RAG-enhanced natural language understanding for qualitative analysis
- **✅ Weighted Fusion**: Intelligent combination of quantitative and qualitative assessments
- **✅ ChromaDB RAG**: Vector database with 15 BNM banking guidelines for regulatory compliance

### 🛡️ Multi-Layer Risk Assessment
1. **Fraud Detection**: 6-point fraud signal detection system
2. **Credit Scoring**: Automated DSR/LTV calculation following BNM guidelines  
3. **Document Quality**: Comprehensive document authenticity and completeness checks
4. **XGBoost Prediction**: Quantitative ML-based risk assessment
5. **LLM Analysis**: Qualitative natural language document analysis
6. **Hybrid Fusion**: Weighted combination with model agreement validation

### 🏦 Banking Coverage
- **Conventional Banking**: Standard interest-based financing
- **Islamic Banking**: Shariah-compliant financing (Murabahah, Ijarah, Musharakah, Tawarruq)
- **Loan Types**: Housing, Car, Personal, Business financing
- **Customer Segments**: Salaried, Rental Income, Small Business, Large Enterprise

### 🌐 User Experience
- **Bilingual Interface**: Full English and Malay (Bahasa Malaysia) support
- **Real-time Analysis**: ~3 second processing time per application
- **Document Support**: PDF, DOCX, TXT, PNG, JPG
- **Interactive Dashboard**: Live statistics and assessment history tracking
- **Responsive Design**: Modern, intuitive UI with TailwindCSS

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React + Vite)                    │
│                  http://localhost:5173/5174                     │
│  • Document Upload  • Bilingual UI  • Real-time Dashboard      │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP REST API
┌────────────────────────────▼────────────────────────────────────┐
│                   BACKEND (FastAPI + Python)                    │
│                    http://localhost:8000                        │
├─────────────────────────────────────────────────────────────────┤
│  1. Document Extraction (PDFPlumber, python-docx)              │
│  2. Fraud Detection (6 fraud signals)                          │
│  3. Credit Scoring (DSR/LTV calculations)                      │
│  4. XGBoost Prediction (70% weight) ────────────────┐          │
│  5. ChromaDB RAG (BNM guidelines retrieval) ───┐    │          │
│  6. GPT-4o LLM Analysis (30% weight) ◄─────────┤    │          │
│  7. Hybrid Fusion (weighted combination) ◄──────────┤          │
└─────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
   ┌──────────┐      ┌──────────────┐    ┌────────────────┐
   │ XGBoost  │      │  ChromaDB    │    │   OpenAI API   │
   │  Model   │      │  Vector DB   │    │    GPT-4o      │
   │ 24K loans│      │ 15 BNM Rules │    │  LLM Service   │
   └──────────┘      └──────────────┘    └────────────────┘
```

### Processing Pipeline

1. **Document Upload** → User uploads loan documents (PDF, DOCX, etc.)
2. **Text Extraction** → Extract text from documents using PDFPlumber/python-docx
3. **Fraud Detection** → Scan for 6 fraud signals (inconsistencies, duplicates, etc.)
4. **Credit Scoring** → Calculate DSR, LTV, credit score based on extracted data
5. **XGBoost Prediction** → ML model predicts approval probability (70% weight)
6. **RAG Retrieval** → ChromaDB retrieves relevant BNM guidelines based on loan type
7. **LLM Analysis** → GPT-4o analyzes documents with BNM context (30% weight)
8. **Hybrid Fusion** → Weighted combination: `Final = 0.70 × XGBoost + 0.30 × LLM`
9. **Risk Classification** → LOW/MEDIUM/HIGH risk with recommendation
10. **Response** → Comprehensive JSON response with all metrics

### Project Structure

```
Cerebral-cortex/
│
├── 📂 backend/                     # FastAPI Backend
│   ├── 📂 app/                     # Application code
│   │   ├── main.py                 # FastAPI app with hybrid fusion (506 lines)
│   │   ├── xgboost_predictor.py    # XGBoost ML model (70% weight)
│   │   ├── openai_agent.py         # GPT-4o LLM (30% weight, RAG-enhanced)
│   │   ├── chromadb_rag.py         # ChromaDB RAG for BNM guidelines (338 lines)
│   │   ├── fraud_detector.py       # Fraud detection (6 checks)
│   │   ├── credit_scorer.py        # Credit scoring (DSR/LTV)
│   │   ├── extractor.py            # Document text extraction
│   │   ├── config.py               # Configuration settings
│   │   └── __init__.py
│   │
│   ├── 📂 chroma_db/               # ChromaDB vector database
│   │   └── (15 BNM banking guidelines)
│   │
│   ├── 📂 data/                    # Training data
│   │   └── loan-data.csv           # 24,000 loan records
│   │
│   ├── 📂 models/                  # Trained models
│   │   ├── xgboost_loan_model.pkl  # XGBoost model (99.79% accuracy)
│   │   └── label_encoders.pkl      # Feature encoders
│   │
│   ├── 📂 uploads/                 # Temporary file uploads
│   │
│   ├── test_chromadb_rag.py        # ChromaDB RAG tests
│   ├── test_hybrid_system.py       # Full system integration test
│   ├── requirements.txt            # Python dependencies
│   ├── .env                        # Environment variables (create this)
│   ├── start.bat                   # Windows startup script
│   └── start.sh                    # Linux/Mac startup script
│
├── 📂 frontend/                    # React Frontend
│   ├── 📂 src/
│   │   ├── App.jsx                 # Main React component (bilingual)
│   │   ├── App.css                 # Styling
│   │   ├── main.jsx                # Entry point
│   │   └── 📂 assets/              # Static assets
│   │
│   ├── 📂 public/                  # Public assets
│   ├── index.html                  # HTML template
│   ├── package.json                # npm dependencies
│   ├── vite.config.js              # Vite configuration
│   └── README.md                   # Frontend documentation
│
├── start.bat                       # Windows full-stack startup
├── start.sh                        # Linux/Mac full-stack startup
├── README.md                       # This file
└── .gitignore                      # Git ignore rules
```

---

## 💻 Installation

### Prerequisites
- **Python 3.12+** (Python 3.10+ compatible)
- **Node.js 18+** and npm
- **OpenAI API Key** (for GPT-4o access)

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/touhidulai/Cerebral-Cortex_CodeFest25_BadDebtGuard-AI.git
   cd Cerebral-Cortex_CodeFest25_BadDebtGuard-AI/backend
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   This installs:
   - FastAPI & Uvicorn (API framework)
   - XGBoost & scikit-learn (ML)
   - ChromaDB & sentence-transformers (RAG)
   - OpenAI (LLM)
   - PDFPlumber, python-docx (document processing)

3. **Configure OpenAI API Key**
   
   Create a `.env` file in the `backend/` directory:
   ```bash
   OPENAI_API_KEY=sk-proj-your_key_here
   ```

4. **Train XGBoost Model** (one-time setup)
   ```bash
   python -m app.xgboost_predictor
   ```
   
   Expected output:
   ```
   Loading loan data from data/loan-data.csv
   Training samples: 24000
   Accuracy: 99.79%
   Model saved to models/xgboost_loan_model.pkl
   ```

5. **Initialize ChromaDB** (automatic on first run)
   ```bash
   python test_chromadb_rag.py
   ```
   
   Expected output:
   ```
   ✓ All 6 tests passed
   ChromaDB initialized with 15 BNM guidelines
   ```

6. **Start the backend server**
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   
   Or use the startup script:
   ```bash
   # Windows
   .\start.bat
   
   # Linux/Mac
   ./start.sh
   ```

   Server will run at: **http://localhost:8000**
   
   API Documentation: **http://localhost:8000/docs**

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd ../frontend
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

   Frontend will run at: **http://localhost:5173** (or 5174 if 5173 is in use)

4. **Build for production** (optional)
   ```bash
   npm run build
   ```

---

## 🚀 Quick Start

### Option 1: Full Stack (Recommended)

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Then open **http://localhost:5173** in your browser.

### Option 2: Backend Only (API Testing)

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Test the API at **http://localhost:8000/docs** (Swagger UI)

### Quick Test

```bash
# Health check
curl http://localhost:8000/api/health

# Expected response
{
  "status": "healthy",
  "timestamp": "2025-11-27T...",
  "services": {
    "api": "operational",
    "extractor": "operational",
    "openai": "operational"
  }
}
```

---

## 🔧 Technology Stack

### Backend
| Technology | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.12+ | Core language |
| **FastAPI** | 0.115+ | Web framework |
| **Uvicorn** | 0.32+ | ASGI server |
| **XGBoost** | 2.0+ | Machine Learning model |
| **scikit-learn** | 1.5+ | ML utilities |
| **ChromaDB** | 0.4+ | Vector database for RAG |
| **sentence-transformers** | 5.1+ | Text embeddings |
| **OpenAI** | 1.54+ | GPT-4o LLM API |
| **PDFPlumber** | 0.11+ | PDF text extraction |
| **python-docx** | 1.1+ | DOCX text extraction |
| **Pydantic** | 2.0+ | Data validation |

### Frontend
| Technology | Version | Purpose |
|-----------|---------|---------|
| **React** | 19.0+ | UI framework |
| **Vite** | 7.2+ | Build tool |
| **TailwindCSS** | 4.1+ | Styling |
| **Lucide React** | 0.468+ | Icons |

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Health Check
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-27T...",
  "services": {
    "api": "operational",
    "extractor": "operational",
    "openai": "operational"
  }
}
```

#### 2. Analyze Loan Application
```http
POST /api/analyze-loan
Content-Type: multipart/form-data
```

**Request Parameters:**
- `banking_system` (string): "conventional" or "islamic"
- `loan_type` (string): "housing", "car", "personal", or "business"
- `customer_type` (string): "salaried", "rental", "small-business", or "large-business"
- `files` (array): Uploaded documents (PDF, DOCX, TXT, PNG, JPG)

**Response:**
```json
{
  "status": "success",
  "risk_analysis": {
    "risk_level": "LOW",
    "risk_category": "LOW RISK",
    "risk_premium": 2.45,
    "default_probability": 1.2,
    "credit_stability_score": 8.7,
    "repayment_capacity": "Strong",
    "ai_confidence": 94
  },
  "executive_summary": "Based on comprehensive analysis...",
  "findings": [
    {
      "category": "XGBOOST ML MODEL",
      "title": "LOW Risk - 99.98% approval probability",
      "description": "Machine learning model trained on 24,000 historical loans...",
      "keywords": ["XGBoost", "Machine Learning", "Predictive Model"],
      "status": "positive"
    }
  ],
  "fusion_metrics": {
    "xgboost_approval_probability": 99.98,
    "xgboost_risk_level": "LOW",
    "llm_approval_probability": 85,
    "llm_risk_level": "LOW",
    "fused_approval_probability": 84.99,
    "fused_risk_level": "LOW",
    "fusion_weights": "XGBoost: 70%, LLM: 30%",
    "model_agreement": true
  },
  "recommendation": "APPROVED - Strong candidate"
}
```

#### 3. Upload Documents
```http
POST /api/upload-documents
Content-Type: multipart/form-data
```

**Request Parameters:**
- `files` (array): Documents to upload

**Response:**
```json
{
  "status": "success",
  "message": "Successfully uploaded 3 documents",
  "files": [
    {
      "filename": "payslip.pdf",
      "saved_as": "20251127_123456_payslip.pdf",
      "size": 45678,
      "text_length": 1234,
      "extracted_successfully": true
    }
  ]
}
```

### Interactive API Docs
Visit **http://localhost:8000/docs** for Swagger UI with interactive API testing.

---

## 🧪 Testing

### Run All Tests
```bash
cd backend

# Test ChromaDB RAG integration
python test_chromadb_rag.py

# Test complete hybrid system
python test_hybrid_system.py
```

### Manual Testing

1. **Test with sample documents:**
   - Place test documents in `backend/data/test_documents/`
   - Use Swagger UI at `http://localhost:8000/docs`
   - Upload documents and test the `/api/analyze-loan` endpoint

2. **Test frontend:**
   - Open `http://localhost:5173`
   - Upload sample loan documents
   - Verify real-time analysis results
   - Check dashboard statistics

---

## 🎯 Usage Examples

### Example 1: Housing Loan Assessment (Conventional Banking)

**Input:**
- Banking System: Conventional
- Loan Type: Housing
- Customer Type: Salaried
- Documents: IC, 3 months payslips, bank statements, property valuation report

**Output:**
- Risk Level: LOW RISK
- Approval Probability: 84.99%
- Recommended Amount: RM 578,000
- Interest Rate: 5.20%
- Max Tenure: 35 years

### Example 2: Car Financing (Islamic Banking)

**Input:**
- Banking System: Islamic
- Loan Type: Car
- Customer Type: Salaried
- Documents: IC, employment letter, 6 months bank statements

**Output:**
- Risk Level: LOW-MEDIUM
- Approval Probability: 72.5%
- Financing Amount: RM 85,000
- Profit Rate: 4.8%
- Max Tenure: 9 years

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team & Acknowledgments

**Team Cerebral-Cortex**
- Project: BadDebtGuard AI - CodeFest25
- Repository: [Cerebral-Cortex_CodeFest25_BadDebtGuard-AI](https://github.com/touhidulai/Cerebral-Cortex_CodeFest25_BadDebtGuard-AI)

### Special Thanks
- **Bank Negara Malaysia (BNM)** for banking guidelines
- **OpenAI** for GPT-4o API access
- **XGBoost** and **ChromaDB** communities

---

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/touhidulai/Cerebral-Cortex_CodeFest25_BadDebtGuard-AI/issues)
- **Documentation**: [Wiki](https://github.com/touhidulai/Cerebral-Cortex_CodeFest25_BadDebtGuard-AI/wiki)

---

<div align="center">

**⭐ Star this repository if you found it helpful!**

Made with ❤️ by Team Cerebral-Cortex

</div>

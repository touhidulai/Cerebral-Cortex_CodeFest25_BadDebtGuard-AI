# 🔧 OpenAI Integration - Setup & Testing Guide

## ✅ What Was Changed

### Backend Updates:
1. **Replaced HuggingFace with OpenAI GPT-4**
   - New file: `backend/app/openai_agent.py` - OpenAI integration
   - Updated: `backend/app/main.py` - FastAPI endpoints with OpenAI
   - Updated: `backend/app/config.py` - Added OPENAI_API_KEY support

2. **Perfect Frontend Integration**
   - All API responses match frontend expectations exactly
   - Response structure: risk_analysis, findings, calculation_breakdown, etc.
   - Proper error handling and fallback responses

3. **Enhanced Analysis**
   - Uses structured JSON output from GPT-4
   - Validates and enhances results automatically
   - Generates Malaysian banking-specific assessments

---

## 🚀 Quick Setup

### Step 1: Get OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key (starts with `sk-...`)

### Step 2: Configure Backend

```powershell
cd backend
Copy-Item .env.template .env
notepad .env
```

Add your OpenAI API key in `.env`:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### Step 3: Install Dependencies

```powershell
pip install -r requirements.txt
```

New packages added:
- `openai>=1.0.0` - OpenAI Python client

### Step 4: Start Backend

```powershell
python -m app.main
```

You should see:
```
🚀 Starting BadDebtGuard AI - Loan Assessment API
   AI Engine: OpenAI GPT-4
```

### Step 5: Start Frontend

```powershell
cd ..\frontend
npm install   # If not done already
npm run dev
```

---

## 🧪 Testing the Integration

### Test 1: Health Check

```powershell
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "api": "operational",
    "extractor": "operational",
    "openai": "operational"
  }
}
```

### Test 2: System Status

```powershell
curl http://localhost:8000/api/status
```

Should show:
```json
{
  "ai_engine": "OpenAI GPT-4",
  "openai_configured": true,
  ...
}
```

### Test 3: Full Analysis (via Frontend)

1. Open http://localhost:5173
2. Select:
   - Banking System: Conventional
   - Loan Type: Home Loan
   - Customer Type: Salaried Employee
3. Upload sample documents (PDFs, DOCX, TXT)
4. Click "Start AI-Powered Analysis"

Expected flow:
1. ✅ Status changes to "analyzing" (spinner shows)
2. ✅ OpenAI processes documents (5-15 seconds)
3. ✅ Results display with:
   - Risk Assessment Cards
   - Executive Summary
   - Key Findings (4-5 items)
   - Risk Premium Breakdown
   - Confidence Metrics
   - Recommendation Details

---

## 📊 API Response Structure

The backend now returns this exact structure (matching frontend):

```json
{
  "status": "success",
  "risk_analysis": {
    "risk_category": "LOW RISK",
    "risk_level": "LOW RISK",
    "risk_premium": 2.45,
    "default_probability": 1.2,
    "credit_stability_score": 8.5,
    "repayment_capacity": "Strong",
    "ai_confidence": 94.0
  },
  "executive_summary": "Based on analysis...",
  "findings": [
    {
      "category": "INCOME VERIFICATION",
      "title": "Stable Employment & Income",
      "description": "Analysis shows consistent income...",
      "keywords": ["Stable", "Verified", "Consistent"],
      "status": "positive"
    }
  ],
  "calculation_breakdown": {
    "base_rate": 1.95,
    "credit_risk_premium": 0.45,
    "ltv_adjustment": 0.39,
    "employment_discount": -0.15,
    "income_discount": -0.10,
    "credit_history_discount": -0.20,
    "total": 2.34
  },
  "confidence_metrics": {
    "document_authenticity": 98.0,
    "income_stability": 95.0,
    "default_risk": 92.0,
    "overall_recommendation": 94.0
  },
  "recommendation": "Application recommended for approval...",
  "recommendation_details": {
    "approved_amount": "RM 578,000",
    "max_tenure": "35 years",
    "indicative_rate": "4.29%"
  },
  "documents_analyzed": [...],
  "analysis_timestamp": "2025-11-27T02:45:00"
}
```

---

## 🔍 How It Works

### 1. Document Upload & Extraction
```
Frontend → Backend → extractor.py
- PDFs: pdfplumber
- DOCX: python-docx
- TXT: built-in Python
```

### 2. OpenAI Analysis
```
main.py → openai_agent.py → OpenAI GPT-4
- Sends extracted text + context
- Requests structured JSON response
- Validates and enhances result
```

### 3. Response to Frontend
```
Structured JSON → Pydantic Models → FastAPI Response
- Type-safe response
- Matches frontend expectations
- Auto-documentation via Swagger
```

---

## 🐛 Troubleshooting

### Error: "OpenAI API key not configured"

**Solution:**
```powershell
cd backend
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

### Error: "No text could be extracted"

**Causes:**
- Unsupported file format
- Corrupted file
- Empty document

**Solution:**
- Use PDF, DOCX, or TXT files
- Ensure files contain text (not just images)

### Error: "Analysis failed: Rate limit exceeded"

**Cause:** Too many API calls to OpenAI

**Solution:**
- Wait a minute and try again
- Check your OpenAI usage limits
- Consider upgrading OpenAI plan

### Frontend shows "Sample Report" with warning

**Cause:** Backend is not running or OpenAI call failed

**Check:**
```powershell
# Is backend running?
curl http://localhost:8000/api/health

# Check backend logs for errors
# Look in terminal where you ran "python -m app.main"
```

---

## 💰 OpenAI Costs

Approximate costs per analysis:
- **Input tokens:** ~2,000-4,000 (documents)
- **Output tokens:** ~1,000-2,000 (response)
- **Model:** GPT-4o
- **Cost:** ~$0.01-0.05 per analysis

Tips to reduce costs:
1. Limit document text to 8,000 characters (done automatically)
2. Use shorter documents
3. Batch testing during development

---

## 🔧 Advanced Configuration

### Change OpenAI Model

Edit `backend/app/openai_agent.py`:
```python
response = await client.chat.completions.create(
    model="gpt-4o",  # or "gpt-4-turbo", "gpt-3.5-turbo"
    ...
)
```

Models:
- `gpt-4o`: Best quality, more expensive
- `gpt-4-turbo`: Fast, good quality
- `gpt-3.5-turbo`: Cheaper, lower quality

### Adjust Temperature

Lower temperature = more consistent results:
```python
temperature=0.3,  # 0.0 to 1.0
```

### Modify Prompts

Edit the prompt in `openai_agent.py` to:
- Change analysis focus
- Add new assessment criteria
- Adjust output format

---

## 📝 Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend connects to backend
- [ ] Health check returns "operational"
- [ ] Can upload documents
- [ ] Analysis starts (spinner shows)
- [ ] Results display correctly
- [ ] All risk cards show data
- [ ] Findings appear (4-5 items)
- [ ] Calculation breakdown shows
- [ ] No console errors

---

## 🎯 Next Steps

1. ✅ Test with real loan documents
2. ✅ Fine-tune prompts for better results
3. ✅ Add error notifications in frontend
4. ✅ Implement caching for repeated documents
5. ✅ Add user authentication
6. ✅ Deploy to production

---

**Integration Complete! 🎉**

Your backend now uses OpenAI GPT-4 and perfectly integrates with the frontend.

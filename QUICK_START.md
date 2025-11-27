# 🚀 QUICK START GUIDE

## ⚡ 3-Minute Setup

### Step 1: Configure OpenAI API Key (30 seconds)
```powershell
cd E:\Cerebral-cortex\backend
notepad .env
```
Replace `YOUR_OPENAI_API_KEY_HERE` with your actual key:
```
OPENAI_API_KEY=sk-proj-your_actual_key_here
```
Save and close.

### Step 2: Start Backend (30 seconds)
```powershell
# Stay in backend directory
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Wait for: `✅ Application startup complete`

### Step 3: Start Frontend (30 seconds)
Open **NEW terminal**:
```powershell
cd E:\Cerebral-cortex\frontend
npm run dev
```
Wait for: `Local: http://localhost:5173/`

### Step 4: Test Upload (90 seconds)
1. Open browser: `http://localhost:5173`
2. Click "New Assessment"
3. Select: Conventional → Home Loan → Salaried Employee
4. Upload 2-3 documents (any PDF, DOCX, or TXT files)
5. Click "Start AI-Powered Analysis"
6. Wait 3-5 seconds
7. ✅ See results!

---

## 🔍 Troubleshooting

### Backend won't start
```powershell
# Check if port 8000 is in use
Get-NetTCPConnection -LocalPort 8000

# Kill process if needed
Stop-Process -Id <PID>
```

### Frontend won't start
```powershell
# Check if port 5173 is in use
Get-NetTCPConnection -LocalPort 5173

# Use alternative port
npm run dev -- --port 5174
```

### OpenAI API errors
- Verify API key is correct (starts with `sk-proj-` or `sk-`)
- Check balance: https://platform.openai.com/usage
- Restart backend after changing `.env`

### ChromaDB errors
```powershell
# Rebuild ChromaDB
cd E:\Cerebral-cortex\backend
python test_chromadb_rag.py
```

---

## ✅ Health Check

Run before starting servers:
```powershell
cd E:\Cerebral-cortex\backend
python health_check.py
```

Should show 7/7 components ready.

---

## 📊 What to Expect

### With OpenAI API Key:
- ✅ Full AI analysis (XGBoost 70% + GPT-4o 30%)
- ✅ RAG-enhanced recommendations
- ✅ Detailed document findings
- ✅ Real-time risk assessment

### Without OpenAI API Key:
- ✅ XGBoost analysis works (70% weight)
- ⚠️ Fallback to sample LLM data
- ⚠️ Warning banner displayed
- ⏸️ Limited document insights

---

## 🎯 Sample Test Documents

Create a test document:
```
File: test_payslip.txt
Content:
---
PAYSLIP - NOVEMBER 2025
Employee: Ahmad bin Ali
IC: 900101-01-1234
Monthly Salary: RM 8,500
EPF Contribution: RM 935
SOCSO: RM 45
Net Pay: RM 7,520
---
```

Upload this and 1-2 more similar files.

---

## 📞 Support

If issues persist:
1. Check `CRITICAL_FIXES.md`
2. Check `PROJECT_ANALYSIS.md`
3. Run `python health_check.py`
4. Check browser DevTools console (F12)
5. Check backend terminal logs

---

**Last Updated:** November 27, 2025  
**Status:** ✅ Ready to use (after API key setup)

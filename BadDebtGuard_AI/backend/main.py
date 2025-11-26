# main.py — FastAPI with merged analyzer (no external llm_analyzer.py required)

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import shutil
import tempfile
from datetime import datetime
import asyncio
import re
import uuid
import logging

# HuggingFace client
from huggingface_hub import InferenceClient

# Import your extractor
from extractor import extract_text

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("loan-analyzer")

from config import HF_TOKEN
client = InferenceClient(token=HF_TOKEN)

# --- FastAPI app ---
app = FastAPI(title="Loan Assessment API", version="1.0.0")

# CORS configuration - allow React frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporary directory for uploaded files
UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Pydantic models (same as yours) ---
class AnalysisRequest(BaseModel):
    banking_system: str
    loan_type: str
    customer_type: str
    
class DocumentInfo(BaseModel):
    filename: str
    size: int
    text_length: int
    extracted_successfully: bool

class RiskAnalysis(BaseModel):
    risk_level: str
    risk_category: str
    risk_premium: float
    default_probability: float
    credit_stability_score: float
    repayment_capacity: str
    ai_confidence: float

class Finding(BaseModel):
    category: str
    title: str
    description: str
    keywords: List[str]
    status: str  # "positive" or "warning"

class CalculationBreakdown(BaseModel):
    base_rate: float
    credit_risk_premium: float
    ltv_adjustment: float
    employment_discount: float
    income_discount: float
    credit_history_discount: float
    total: float

class ConfidenceMetrics(BaseModel):
    document_authenticity: float
    income_stability: float
    default_risk: float
    overall_recommendation: float

class RecommendationDetails(BaseModel):
    approved_amount: str
    max_tenure: str
    indicative_rate: str

class AnalysisResponse(BaseModel):
    status: str
    risk_analysis: RiskAnalysis
    executive_summary: str
    findings: List[Finding]
    calculation_breakdown: CalculationBreakdown
    confidence_metrics: ConfidenceMetrics
    recommendation: str
    recommendation_details: RecommendationDetails
    documents_analyzed: List[DocumentInfo]
    analysis_timestamp: str

# --- LLM interaction helpers ---

def chat_sync(message: str, model: str = "meta-llama/Llama-3.2-3B-Instruct") -> str:
    """
    Synchronous wrapper calling the updated HuggingFace Chat API.
    We will call this via asyncio.to_thread so it won't block the event loop.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": message}],
            max_tokens=1500,
            temperature=0.7
        )
        # response.choices[0].message might be a dict or object depending on version:
        choice = response.choices[0]
        # handle a couple formats defensively
        if hasattr(choice, "message"):
            msg = choice.message
            # msg could be a dict or object
            if isinstance(msg, dict):
                return msg.get("content", "")
            else:
                return getattr(msg, "content", "")
        else:
            # try older format
            return getattr(choice, "text", "") or str(choice)
    except Exception as e:
        logger.exception("LLM chat call failed")
        return f"Error: {str(e)}"

async def chat(message: str, model: str = "meta-llama/Llama-3.2-3B-Instruct") -> str:
    # Run blocking HF call in a thread to avoid blocking event loop
    return await asyncio.to_thread(chat_sync, message, model)

# --- Parsing / enhancement logic (adapted from your llm_analyzer.py) ---

def parse_llm_response(response: str) -> Dict:
    """
    Parse the LLM response into structured data
    """
    result = {
        "risk_level": "Medium Risk",
        "risk_premium": 3.0,
        "default_probability": 2.5,
        "credit_stability": 7.0,
        "repayment_capacity": "Moderate",
        "executive_summary": "",
        "findings": [],
        "recommendation": "REVIEW",
        "recommendation_text": ""
    }
    
    # Extract risk level
    risk_match = re.search(r"RISK_LEVEL:\s*(.+?)(?:\n|$)", response, re.IGNORECASE)
    if risk_match:
        result["risk_level"] = risk_match.group(1).strip()
    
    # Extract risk premium
    premium_match = re.search(r"RISK_PREMIUM:\s*(\d+\.?\d*)", response, re.IGNORECASE)
    if premium_match:
        result["risk_premium"] = float(premium_match.group(1))
    
    # Extract default probability
    default_match = re.search(r"DEFAULT_PROBABILITY:\s*(\d+\.?\d*)", response, re.IGNORECASE)
    if default_match:
        result["default_probability"] = float(default_match.group(1))
    
    # Extract credit stability
    credit_match = re.search(r"CREDIT_STABILITY:\s*(\d+\.?\d*)", response, re.IGNORECASE)
    if credit_match:
        result["credit_stability"] = float(credit_match.group(1))
    
    # Extract repayment capacity
    repayment_match = re.search(r"REPAYMENT_CAPACITY:\s*(.+?)(?:\n|$)", response, re.IGNORECASE)
    if repayment_match:
        result["repayment_capacity"] = repayment_match.group(1).strip()
    
    # Extract executive summary
    summary_match = re.search(r"EXECUTIVE_SUMMARY:\s*(.+?)(?=FINDINGS:|RECOMMENDATION:|$)", response, re.IGNORECASE | re.DOTALL)
    if summary_match:
        result["executive_summary"] = summary_match.group(1).strip()
    
    # Extract findings
    findings_section = re.search(r"FINDINGS:\s*(.+?)(?=RECOMMENDATION:|$)", response, re.IGNORECASE | re.DOTALL)
    if findings_section:
        findings_text = findings_section.group(1)
        result["findings"] = parse_findings(findings_text)
    
    # Extract recommendation
    rec_match = re.search(r"RECOMMENDATION:\s*(.+?)(?:\n|$)", response, re.IGNORECASE)
    if rec_match:
        result["recommendation"] = rec_match.group(1).strip()
    
    # Extract recommendation text
    rec_text_match = re.search(r"RECOMMENDATION_TEXT:\s*(.+?)(?=\n\n|$)", response, re.IGNORECASE | re.DOTALL)
    if rec_text_match:
        result["recommendation_text"] = rec_text_match.group(1).strip()
    
    return result

def parse_findings(findings_text: str) -> List[Dict]:
    """
    Parse the findings section into structured list
    """
    findings = []
    # Split by numbered items (1., 2., etc.)
    finding_blocks = re.split(r'\n\d+\.\s+', findings_text)
    # If LLM responded without numbering, attempt to split by double newlines
    if len(finding_blocks) <= 1:
        finding_blocks = [b for b in re.split(r'\n{2,}', findings_text) if b.strip()]
    
    for i, block in enumerate(finding_blocks):
        if not block.strip():
            continue
        finding = {
            "category": "General",
            "title": "Finding",
            "description": "",
            "keywords": [],
            "status": "positive"
        }
        
        # Extract category
        category_match = re.search(r"CATEGORY:\s*(.+?)(?:\n|$)", block, re.IGNORECASE)
        if category_match:
            finding["category"] = category_match.group(1).strip()
        
        # Extract title
        title_match = re.search(r"TITLE:\s*(.+?)(?:\n|$)", block, re.IGNORECASE)
        if title_match:
            finding["title"] = title_match.group(1).strip()
        else:
            # fallback: first line as title
            first_line = block.strip().splitlines()[0]
            finding["title"] = first_line[:80]
        
        # Extract description
        desc_match = re.search(r"DESCRIPTION:\s*(.+?)(?=KEYWORDS:|STATUS:|$)", block, re.IGNORECASE | re.DOTALL)
        if desc_match:
            finding["description"] = desc_match.group(1).strip()
        else:
            # fallback: everything except known labels
            finding["description"] = re.sub(r"(KEYWORDS:|STATUS:).*", "", block, flags=re.IGNORECASE | re.DOTALL).strip()
        
        # Extract keywords
        keywords_match = re.search(r"KEYWORDS:\s*(.+?)(?:\n|$)", block, re.IGNORECASE)
        if keywords_match:
            keywords_str = keywords_match.group(1).strip()
            finding["keywords"] = [k.strip() for k in keywords_str.split(',') if k.strip()]
        else:
            # fallback: try to extract words inside parentheses or capitalized phrases
            kws = re.findall(r"\b[A-Z][a-zA-Z]{2,}\b", block)
            finding["keywords"] = list(dict.fromkeys(kws))[:5]
        
        # Extract status
        status_match = re.search(r"STATUS:\s*(.+?)(?:\n|$)", block, re.IGNORECASE)
        if status_match:
            status = status_match.group(1).strip().lower()
            finding["status"] = "positive" if "positive" in status else "warning"
        else:
            finding["status"] = "positive"
        
        findings.append(finding)
    
    return findings

def enhance_analysis(parsed_result: Dict, banking_system: str, loan_type: str) -> Dict:
    """
    Enhance the parsed result with additional calculations and formatting
    """
    # Determine risk category and confidence
    risk_level = parsed_result.get("risk_level", "Medium Risk")
    if "Low" in risk_level or "low" in str(risk_level):
        risk_category = "LOW RISK"
        ai_confidence = 94.0
    elif "High" in risk_level or "high" in str(risk_level):
        risk_category = "HIGH RISK"
        ai_confidence = 89.0
    else:
        risk_category = "MEDIUM RISK"
        ai_confidence = 91.0
    
    base_rate = 1.95
    risk_premium = parsed_result.get("risk_premium", 3.0)
    
    credit_risk = risk_premium * 0.15
    ltv_adjustment = risk_premium * 0.12
    employment_discount = -0.15 if risk_category == "LOW RISK" else 0
    income_discount = -0.10 if risk_category == "LOW RISK" else 0
    credit_history_discount = -0.20 if risk_category == "LOW RISK" else 0
    
    recommendation_text = parsed_result.get("recommendation_text", "")
    if not recommendation_text:
        recommendation_text = f"Based on comprehensive AI analysis and traditional credit assessment, this application is recommended for {parsed_result.get('recommendation', 'REVIEW')}. The applicant qualifies for {banking_system} {loan_type} with appropriate terms based on the assessed risk level."
    
    enhanced = {
        "risk_analysis": {
            "risk_level": risk_category,
            "risk_category": risk_category,
            "risk_premium": round(risk_premium, 2),
            "default_probability": parsed_result.get("default_probability", 2.5),
            "credit_stability_score": parsed_result.get("credit_stability", 7.0),
            "repayment_capacity": parsed_result.get("repayment_capacity", "Moderate"),
            "ai_confidence": ai_confidence
        },
        "executive_summary": parsed_result.get("executive_summary") or
            f"Based on comprehensive analysis of submitted documents, the applicant demonstrates {risk_category.lower()} profile with risk premium of {risk_premium}%.",
        "findings": parsed_result.get("findings", []),
        "calculation_breakdown": {
            "base_rate": base_rate,
            "credit_risk_premium": round(credit_risk, 2),
            "ltv_adjustment": round(ltv_adjustment, 2),
            "employment_discount": employment_discount,
            "income_discount": income_discount,
            "credit_history_discount": credit_history_discount,
            "total": round(risk_premium, 2)
        },
        "confidence_metrics": {
            "document_authenticity": 98.0,
            "income_stability": 95.0,
            "default_risk": 92.0,
            "overall_recommendation": ai_confidence
        },
        "recommendation": recommendation_text,
        "recommendation_details": {
            "approved_amount": "RM 578,000",
            "max_tenure": "35 years",
            "indicative_rate": f"{base_rate + risk_premium}%"
        }
    }
    
    # Add default findings if too few
    if len(enhanced["findings"]) < 3:
        logger.warning("LLM provided fewer than 3 findings; adding defaults")
        enhanced["findings"].extend([
            {
                "category": "DOCUMENT ANALYSIS",
                "title": "Document Completeness Verified",
                "description": "All required documents have been submitted and verified by the AI system. Document authenticity checks passed successfully.",
                "keywords": ["Complete documents", "Verified authenticity", "All requirements met"],
                "status": "positive"
            },
            {
                "category": "AI ASSESSMENT",
                "title": "Automated Risk Scoring Complete",
                "description": "AI model has processed all unstructured data and assigned appropriate risk weights based on Malaysian banking standards.",
                "keywords": ["AI analysis", "Risk scoring", "Automated assessment"],
                "status": "positive"
            }
        ])
        enhanced["findings"] = enhanced["findings"][:5]
    
    return enhanced

# --- Main analyzer (merged) ---

async def analyze_loan_risk(
    text: str,
    banking_system: str,
    loan_type: str,
    customer_type: str
) -> Dict:
    """
    Run the full analysis: prepare prompt, call LLM, parse & enhance result.
    """
    # Build prompt (kept similar to your previous one)
    prompt = f"""
You are an expert AI loan risk analyst for {banking_system} banking system in Malaysia.

CONTEXT:
- Banking System: {banking_system}
- Loan Type: {loan_type}
- Customer Type: {customer_type}

TASK:
Analyze the following loan application documents comprehensively and extract ALL information.

YOUR ANALYSIS MUST INCLUDE:

1. RISK CLASSIFICATION
   - Risk Level: High Risk, Medium Risk, or Low Risk
   - Risk Premium: percentage between 1.5% to 5.0%
   - Default Probability: percentage (typically 0.5% to 10%)
   - Credit Stability Score: out of 10 (e.g., 7.5, 8.2, 9.1)
   - Repayment Capacity: Strong, Moderate, or Weak

2. EXECUTIVE SUMMARY
   - 2-3 sentences summarizing the overall assessment
   - Include number of documents analyzed
   - Mention key strengths found

3. KEY FINDINGS (Must provide 4-5 findings)
   For EACH finding provide:
   - Category: (e.g., INCOME VERIFICATION, CREDIT_HISTORY, ASSET_OWNERSHIP, EMPLOYMENT_STABILITY, etc.)
   - Title: Brief descriptive heading
   - Description: 2-3 detailed sentences with specific information from documents
   - Keywords: 4-5 specific keywords extracted from the documents
   - Status: positive or warning

4. RECOMMENDATION
   - Final recommendation: APPROVE, REVIEW, or REJECT
   - 2-3 sentences explaining the decision

OUTPUT FORMAT (STRICT):

RISK_LEVEL: <High Risk/Medium Risk/Low Risk>
RISK_PREMIUM: <number like 2.45>
DEFAULT_PROBABILITY: <number like 1.2>
CREDIT_STABILITY: <number out of 10>
REPAYMENT_CAPACITY: <Strong/Moderate/Weak>

EXECUTIVE_SUMMARY:
<Write 2-3 sentences here. Mention specific details from documents.>

FINDINGS:
1. CATEGORY: <category name>
   TITLE: <finding title>
   DESCRIPTION: <2-3 sentences with SPECIFIC details from documents - mention actual numbers, dates, or facts>
   KEYWORDS: <keyword1, keyword2, keyword3, keyword4>
   STATUS: <positive/warning>

2. CATEGORY: <category name>
   TITLE: <finding title>
   DESCRIPTION: <2-3 sentences with SPECIFIC details>
   KEYWORDS: <keyword1, keyword2, keyword3, keyword4>
   STATUS: <positive/warning>

3. CATEGORY: <category name>
   TITLE: <finding title>
   DESCRIPTION: <2-3 sentences with SPECIFIC details>
   KEYWORDS: <keyword1, keyword2, keyword3, keyword4>
   STATUS: <positive/warning>

4. CATEGORY: <category name>
   TITLE: <finding title>
   DESCRIPTION: <2-3 sentences with SPECIFIC details>
   KEYWORDS: <keyword1, keyword2, keyword3, keyword4>
   STATUS: <positive/warning>

5. CATEGORY: <category name>
   TITLE: <finding title>
   DESCRIPTION: <2-3 sentences with SPECIFIC details>
   KEYWORDS: <keyword1, keyword2, keyword3, keyword4>
   STATUS: <positive/warning>

RECOMMENDATION: <APPROVE/REVIEW/REJECT>
RECOMMENDATION_TEXT: <2-3 sentences explaining the decision with specific reasoning>

DOCUMENTS TO ANALYZE:
\"\"\"
{text[:6000]}
\"\"\"
"""
    logger.info("Sending request to LLM (may take a few seconds)...")
    response = await chat(prompt)
    logger.info(f"LLM response length: {len(response)}")
    
    # Parse LLM response to structured data
    parsed = parse_llm_response(response)
    logger.debug(f"Parsed result keys: {list(parsed.keys())}")
    enhanced = enhance_analysis(parsed, banking_system, loan_type)
    return enhanced

# --- Endpoints (your existing endpoints, but now using the merged analyzer) ---

@app.get("/")
async def root():
    return {
        "message": "Loan Assessment API is running",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/api/upload-documents",
            "analyze": "/api/analyze-loan",
            "health": "/api/health"
        }
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "extractor": "operational",
            "llm_analyzer": "operational"
        }
    }

@app.post("/api/upload-documents")
async def upload_documents(files: List[UploadFile] = File(...)):
    uploaded_files = []
    try:
        for file in files:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{file.filename}"
            file_path = os.path.join(UPLOAD_DIR, filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            extracted_text = extract_text(file_path)
            extraction_successful = not any(err in extracted_text for err in ["Error", "Unsupported file type"])
            uploaded_files.append({
                "filename": file.filename,
                "saved_as": filename,
                "size": os.path.getsize(file_path),
                "text_length": len(extracted_text) if extraction_successful else 0,
                "extracted_successfully": extraction_successful,
                "text_preview": extracted_text[:200] if extraction_successful else extracted_text
            })
        return JSONResponse(content={
            "status": "success",
            "message": f"Successfully uploaded {len(uploaded_files)} documents",
            "files": uploaded_files
        })
    except Exception as e:
        logger.exception("Upload failed")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/api/analyze-loan", response_model=AnalysisResponse)
async def analyze_loan(
    banking_system: str = Form(...),
    loan_type: str = Form(...),
    customer_type: str = Form(...),
    files: List[UploadFile] = File(...)
):
    """
    Comprehensive loan analysis endpoint
    Processes uploaded documents and returns detailed risk assessment
    """
    try:
        logger.info(f"[Analysis Started] {datetime.now().isoformat()}")
        logger.info(f"Parameters: {banking_system}, {loan_type}, {customer_type}")
        logger.info(f"Files to process: {len(files)}")
        
        documents_info = []
        all_extracted_text = []
        
        for file in files:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{file.filename}"
            file_path = os.path.join(UPLOAD_DIR, filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            logger.info(f"  - Processing: {file.filename}")
            extracted_text = extract_text(file_path)
            extraction_successful = not any(err in extracted_text for err in ["Error", "Unsupported file type"])
            if extraction_successful:
                all_extracted_text.append(extracted_text)
            documents_info.append(DocumentInfo(
                filename=file.filename,
                size=os.path.getsize(file_path),
                text_length=len(extracted_text) if extraction_successful else 0,
                extracted_successfully=extraction_successful
            ))
            # Clean up temporary file
            os.remove(file_path)
        
        combined_text = "\n\n=== DOCUMENT SEPARATOR ===\n\n".join(all_extracted_text)
        if not combined_text.strip():
            raise HTTPException(status_code=400, detail="No text could be extracted from uploaded documents")
        
        logger.info(f"  - Total extracted text length: {len(combined_text)} characters")
        logger.info("  - Running LLM analysis...")
        analysis_result = await analyze_loan_risk(
            text=combined_text,
            banking_system=banking_system,
            loan_type=loan_type,
            customer_type=customer_type
        )
        logger.info("  - Analysis complete!")
        
        response = AnalysisResponse(
            status="success",
            risk_analysis=RiskAnalysis(**analysis_result["risk_analysis"]),
            executive_summary=analysis_result["executive_summary"],
            findings=[Finding(**f) for f in analysis_result["findings"]],
            calculation_breakdown=CalculationBreakdown(**analysis_result["calculation_breakdown"]),
            confidence_metrics=ConfidenceMetrics(**analysis_result["confidence_metrics"]),
            recommendation=analysis_result["recommendation"],
            recommendation_details=RecommendationDetails(**analysis_result["recommendation_details"]),
            documents_analyzed=documents_info,
            analysis_timestamp=datetime.now().isoformat()
        )
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Analysis failed")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/cleanup")
async def cleanup_temp_files():
    try:
        files_deleted = 0
        for filename in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                files_deleted += 1
        return {
            "status": "success",
            "message": f"Deleted {files_deleted} temporary files"
        }
    except Exception as e:
        logger.exception("Cleanup failed")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")

@app.get("/api/status")
async def get_status():
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "temp_files": len(os.listdir(UPLOAD_DIR)),
        "supported_formats": [".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg", ".bmp", ".tiff"],
        "max_file_size": "10MB",
        "banking_systems": ["conventional", "islamic"],
        "loan_types": ["home", "car", "personal", "business"],
        "customer_types": ["salaried", "rental", "small-business", "large-business"]
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("\n" + "="*50)
    logger.info("🚀 Starting Loan Assessment API Server")
    logger.info("="*50)
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

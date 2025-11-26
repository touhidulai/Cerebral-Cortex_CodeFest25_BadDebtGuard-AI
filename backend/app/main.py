"""
FastAPI Backend for BadDebtGuard AI - Loan Assessment System
Integrates OpenAI's GPT models for credit risk analysis
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import shutil
from datetime import datetime
import logging

# Import local modules
from app.extractor import extract_text
from app.openai_agent import analyze_with_openai
from app.config import OPENAI_API_KEY

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("loan-analyzer")

# --- FastAPI app ---
app = FastAPI(
    title="BadDebtGuard AI - Loan Assessment API",
    version="2.0.0",
    description="AI-powered loan risk assessment for Malaysian banking"
)

# CORS configuration - allow React frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Upload directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Pydantic Models ---
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


# --- API Endpoints ---

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "BadDebtGuard AI - Loan Assessment API",
        "version": "2.0.0",
        "status": "operational",
        "ai_engine": "OpenAI GPT-4",
        "endpoints": {
            "analyze": "/api/analyze-loan",
            "upload": "/api/upload-documents",
            "health": "/api/health",
            "status": "/api/status",
            "cleanup": "/api/cleanup"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    openai_status = "operational" if OPENAI_API_KEY else "not_configured"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "operational",
            "extractor": "operational",
            "openai": openai_status
        }
    }


@app.post("/api/upload-documents")
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload and extract text from documents
    """
    uploaded_files = []
    
    try:
        for file in files:
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{file.filename}"
            file_path = os.path.join(UPLOAD_DIR, filename)
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Extract text
            extracted_text = extract_text(file_path)
            extraction_successful = not any(
                err in extracted_text for err in ["Error", "Unsupported file type"]
            )
            
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
    Main loan analysis endpoint
    Processes uploaded documents and returns detailed risk assessment
    """
    try:
        logger.info(f"[Analysis Started] {datetime.now().isoformat()}")
        logger.info(f"Parameters: Banking={banking_system}, Loan={loan_type}, Customer={customer_type}")
        logger.info(f"Files to process: {len(files)}")
        
        # Check OpenAI API key
        if not OPENAI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key not configured. Please set OPENAI_API_KEY in .env file"
            )
        
        documents_info = []
        all_extracted_text = []
        
        # Process each uploaded file
        for file in files:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"{timestamp}_{file.filename}"
            file_path = os.path.join(UPLOAD_DIR, filename)
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            logger.info(f"  - Processing: {file.filename}")
            
            # Extract text
            extracted_text = extract_text(file_path)
            extraction_successful = not any(
                err in extracted_text for err in ["Error", "Unsupported file type"]
            )
            
            if extraction_successful:
                all_extracted_text.append(f"=== DOCUMENT: {file.filename} ===\n{extracted_text}")
            
            documents_info.append(DocumentInfo(
                filename=file.filename,
                size=os.path.getsize(file_path),
                text_length=len(extracted_text) if extraction_successful else 0,
                extracted_successfully=extraction_successful
            ))
            
            # Clean up temporary file
            try:
                os.remove(file_path)
            except:
                pass
        
        # Combine all extracted text
        combined_text = "\n\n".join(all_extracted_text)
        
        if not combined_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from uploaded documents"
            )
        
        logger.info(f"  - Total extracted text length: {len(combined_text)} characters")
        logger.info("  - Calling OpenAI for analysis...")
        
        # Call OpenAI agent for analysis
        analysis_result = await analyze_with_openai(
            extracted_text=combined_text,
            banking_system=banking_system,
            loan_type=loan_type,
            customer_type=customer_type
        )
        
        logger.info("  - Analysis complete!")
        
        # Build response matching frontend expectations
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
    """Clean up temporary uploaded files"""
    try:
        files_deleted = 0
        for filename in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, filename)
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                    files_deleted += 1
                except:
                    pass
        
        return {
            "status": "success",
            "message": f"Deleted {files_deleted} temporary files"
        }
    except Exception as e:
        logger.exception("Cleanup failed")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


@app.get("/api/status")
async def get_status():
    """Get system status and capabilities"""
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "ai_engine": "OpenAI GPT-4",
        "openai_configured": bool(OPENAI_API_KEY),
        "temp_files": len([f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))]),
        "supported_formats": [".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg", ".bmp", ".tiff"],
        "max_file_size": "10MB",
        "banking_systems": ["conventional", "islamic"],
        "loan_types": ["home", "car", "personal", "business"],
        "customer_types": ["salaried", "rental", "small-business", "large-business"]
    }


# Run the application
if __name__ == "__main__":
    import uvicorn
    logger.info("\n" + "="*50)
    logger.info("🚀 Starting BadDebtGuard AI - Loan Assessment API")
    logger.info("   AI Engine: OpenAI GPT-4")
    logger.info("="*50)
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

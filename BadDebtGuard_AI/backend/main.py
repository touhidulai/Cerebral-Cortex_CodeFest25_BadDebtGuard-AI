from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil
import tempfile
from datetime import datetime
import asyncio

# Import your existing modules
from extractor import extract_text
from llm_analyzer import analyze_loan_risk

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

# Pydantic models for request/response
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


# Root endpoint
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

# Health check endpoint
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

# Upload documents endpoint
@app.post("/api/upload-documents")
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload multiple documents for loan assessment
    Returns file information and extracted text preview
    """
    uploaded_files = []
    
    try:
        for file in files:
            # Create unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{file.filename}"
            file_path = os.path.join(UPLOAD_DIR, filename)
            
            # Save uploaded file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Extract text
            extracted_text = extract_text(file_path)
            
            # Check if extraction was successful
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
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


# Main analysis endpoint
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
        # Step 1: Save and extract text from all documents
        print(f"\n[Analysis Started] {datetime.now().isoformat()}")
        print(f"Parameters: {banking_system}, {loan_type}, {customer_type}")
        print(f"Files to process: {len(files)}")
        
        documents_info = []
        all_extracted_text = []
        
        for file in files:
            # Save file temporarily
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{file.filename}"
            file_path = os.path.join(UPLOAD_DIR, filename)
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            print(f"  - Processing: {file.filename}")
            
            # Extract text
            extracted_text = extract_text(file_path)
            extraction_successful = not any(
                err in extracted_text for err in ["Error", "Unsupported file type"]
            )
            
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
        
        # Step 2: Combine all text for analysis
        combined_text = "\n\n=== DOCUMENT SEPARATOR ===\n\n".join(all_extracted_text)
        
        if not combined_text.strip():
            raise HTTPException(
                status_code=400, 
                detail="No text could be extracted from uploaded documents"
            )
        
        print(f"  - Total extracted text length: {len(combined_text)} characters")
        
        # Step 3: Run LLM analysis
        print("  - Running LLM analysis...")
        analysis_result = await analyze_loan_risk(
            text=combined_text,
            banking_system=banking_system,
            loan_type=loan_type,
            customer_type=customer_type
        )
        
        print(f"  - Analysis complete!")
        print(f"  - Risk Level: {analysis_result['risk_analysis']['risk_level']}")
        
        # Step 4: Prepare response
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
        print(f"[ERROR] {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# Cleanup endpoint (optional - for maintenance)
@app.post("/api/cleanup")
async def cleanup_temp_files():
    """
    Clean up temporary uploaded files
    """
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
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


# Get system status
@app.get("/api/status")
async def get_status():
    """
    Get current system status and statistics
    """
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
    print("\n" + "="*50)
    print("🚀 Starting Loan Assessment API Server")
    print("="*50)
    print(f"📍 Server will run on: http://localhost:8000")
    print(f"📚 API Docs available at: http://localhost:8000/docs")
    print(f"📊 Alternative docs at: http://localhost:8000/redoc")
    print("="*50 + "\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

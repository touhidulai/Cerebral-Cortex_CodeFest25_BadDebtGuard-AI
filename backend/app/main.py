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
from app.fraud_detector import detect_fraud_signals, calculate_document_quality_score
from app.credit_scorer import CreditScoreCalculator
from app.xgboost_predictor import XGBoostLoanPredictor

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
        "http://localhost:5174",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174"
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
        
        # STEP 1: Fraud Detection (Rule-based ML)
        logger.info("  - Running fraud detection...")
        fraud_analysis = detect_fraud_signals(combined_text)
        logger.info(f"    Fraud Score: {fraud_analysis['fraud_score']}/100")
        logger.info(f"    Signals: {len(fraud_analysis['signals'])}")
        
        # STEP 2: Credit Scoring (Quantitative ML)
        logger.info("  - Calculating credit score...")
        credit_calculator = CreditScoreCalculator()
        credit_analysis = credit_calculator.analyze(combined_text)
        logger.info(f"    Credit Score: {credit_analysis['credit_score']}/850")
        logger.info(f"    DSR: {credit_analysis['dsr']}%, LTV: {credit_analysis['ltv']}%")
        
        # STEP 3: Document Quality Assessment
        logger.info("  - Assessing document quality...")
        quality_analysis = calculate_document_quality_score(combined_text)
        logger.info(f"    Quality Score: {quality_analysis['quality_score']}/100")
        
        # STEP 4: XGBoost Prediction (Quantitative ML Model)
        logger.info("  - Running XGBoost risk prediction...")
        try:
            xgb_predictor = XGBoostLoanPredictor()
            xgb_predictor.load_model()
            xgb_prediction = xgb_predictor.predict_from_document_data(credit_analysis['extracted_data'])
            logger.info(f"    XGBoost Approval Probability: {xgb_prediction['approval_probability']}%")
            logger.info(f"    XGBoost Risk Level: {xgb_prediction['risk_level']}")
        except Exception as e:
            logger.warning(f"    XGBoost prediction failed: {e}, continuing with LLM-only analysis")
            xgb_prediction = None
        
        # STEP 5A: ChromaDB RAG - Retrieve relevant BNM guidelines
        logger.info("  - Retrieving BNM guidelines from ChromaDB (RAG)...")
        rag_context = ""
        try:
            from app.chromadb_rag import get_rag_instance
            rag = get_rag_instance()
            rag_context = rag.get_bnm_context_for_loan(
                loan_type=loan_type,
                banking_system=banking_system,
                customer_type=customer_type
            )
            logger.info(f"    Retrieved {len(rag_context)} characters of BNM context")
        except Exception as e:
            logger.warning(f"    ChromaDB RAG failed: {e}, continuing without RAG")
            rag_context = ""
        
        # STEP 5B: LLM Analysis (GPT-4o with RAG)
        logger.info("  - Calling OpenAI GPT-4o for comprehensive analysis (RAG-enhanced)...")
        analysis_result = await analyze_with_openai(
            extracted_text=combined_text,
            banking_system=banking_system,
            loan_type=loan_type,
            customer_type=customer_type,
            rag_context=rag_context
        )
        
        # STEP 6: Hybrid Fusion (70% XGBoost + 30% LLM)
        logger.info("  - Applying hybrid fusion with weighted scoring...")
        
        # Apply 70/30 fusion if XGBoost is available
        if xgb_prediction:
            # Convert LLM risk level to probability score
            llm_risk_level = analysis_result["risk_analysis"]["risk_level"]
            llm_approval_proba = {
                "LOW": 85,
                "LOW-MEDIUM": 70,
                "MEDIUM": 55,
                "MEDIUM-HIGH": 40,
                "HIGH": 20
            }.get(llm_risk_level, 50)
            
            # Weighted fusion: 70% XGBoost, 30% LLM
            xgb_weight = 0.70
            llm_weight = 0.30
            
            fused_approval_probability = (
                xgb_weight * xgb_prediction['approval_probability'] +
                llm_weight * llm_approval_proba
            )
            
            # Determine fused risk level
            if fused_approval_probability >= 75:
                fused_risk_level = "LOW"
                fused_recommendation = "APPROVED - Strong candidate"
            elif fused_approval_probability >= 60:
                fused_risk_level = "LOW-MEDIUM"
                fused_recommendation = "APPROVED with conditions"
            elif fused_approval_probability >= 45:
                fused_risk_level = "MEDIUM"
                fused_recommendation = "REVIEW REQUIRED - Manual assessment needed"
            elif fused_approval_probability >= 30:
                fused_risk_level = "MEDIUM-HIGH"
                fused_recommendation = "DECLINE with reapplication option"
            else:
                fused_risk_level = "HIGH"
                fused_recommendation = "DECLINE - High risk"
            
            # Update analysis result with fused scores
            analysis_result["risk_analysis"]["risk_level"] = fused_risk_level
            analysis_result["recommendation"] = fused_recommendation
            
            # Add fusion metrics
            analysis_result["fusion_metrics"] = {
                "xgboost_approval_probability": xgb_prediction['approval_probability'],
                "xgboost_risk_level": xgb_prediction['risk_level'],
                "llm_approval_probability": llm_approval_proba,
                "llm_risk_level": llm_risk_level,
                "fused_approval_probability": round(fused_approval_probability, 2),
                "fused_risk_level": fused_risk_level,
                "fusion_weights": f"XGBoost: {int(xgb_weight*100)}%, LLM: {int(llm_weight*100)}%",
                "model_agreement": abs(xgb_prediction['approval_probability'] - llm_approval_proba) < 20
            }
            
            logger.info(f"    Fusion Result: {fused_approval_probability:.2f}% approval ({fused_risk_level})")
            logger.info(f"    Model Agreement: {'Yes' if analysis_result['fusion_metrics']['model_agreement'] else 'No - Review Recommended'}")
        
        # Enhance with fraud detection results
        analysis_result["confidence_metrics"]["document_authenticity"] = fraud_analysis["authenticity_confidence"]
        
        # Add credit score insights
        if credit_analysis["credit_score"] > 0:
            analysis_result["credit_score"] = credit_analysis["credit_score"]
            analysis_result["ml_risk_category"] = credit_analysis["risk_category"]
            analysis_result["quantitative_metrics"] = {
                "dsr": credit_analysis["dsr"],
                "ltv": credit_analysis["ltv"],
                "extracted_income": credit_analysis["extracted_data"]["monthly_income"],
                "extracted_debt": credit_analysis["extracted_data"]["monthly_debt"]
            }
        
        # Add XGBoost insights as finding if available
        if xgb_prediction:
            xgb_finding = {
                "category": "XGBOOST ML MODEL",
                "title": f"{xgb_prediction['risk_level']} Risk - {xgb_prediction['recommendation']}",
                "description": f"Machine learning model trained on 24,000 historical loans predicts {xgb_prediction['approval_probability']}% approval probability with {xgb_prediction['model_confidence']}% confidence. XGBoost analysis based on quantitative features (income, credit score, DTI, employment).",
                "keywords": ["XGBoost", "Machine Learning", "Quantitative Analysis", "Predictive Model"],
                "status": "positive" if xgb_prediction['approval_probability'] >= 60 else "warning"
            }
            analysis_result["findings"].insert(0, xgb_finding)
        
        # Add fraud signals as findings if any
        if fraud_analysis["total_signals"] > 0 and fraud_analysis["fraud_score"] > 25:
            fraud_finding = {
                "category": "FRAUD DETECTION",
                "title": f"{fraud_analysis['risk_level']} - Document Authenticity Alert",
                "description": f"Automated fraud detection identified {fraud_analysis['total_signals']} potential issues: {', '.join(fraud_analysis['signals'][:3])}. Recommend manual verification.",
                "keywords": ["Fraud Detection", "Document Verification", "Risk Alert"],
                "status": "warning"
            }
            analysis_result["findings"].insert(0, fraud_finding)
        
        # Add document quality finding
        quality_finding = {
            "category": "DOCUMENT QUALITY",
            "title": f"Document Quality Score: {quality_analysis['quality_score']}/100",
            "description": f"Document completeness analysis: {quality_analysis['word_count']} words, {quality_analysis['currency_mentions']} financial data points, {quality_analysis['completeness']} coverage. Numerical density: {quality_analysis['numerical_density']}%",
            "keywords": ["Document Quality", "Completeness", "Data Density"],
            "status": "positive" if quality_analysis['quality_score'] >= 70 else "warning"
        }
        analysis_result["findings"].append(quality_finding)
        
        logger.info("  - Analysis complete with ML enhancements!")
        
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

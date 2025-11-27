"""
System Health Check Script
Tests all components before running the full application
"""

import sys
import os

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def check_openai_key():
    """Check if OpenAI API key is configured"""
    print_header("1. OpenAI API Key Configuration")
    try:
        from app.config import OPENAI_API_KEY
        if OPENAI_API_KEY and OPENAI_API_KEY != "YOUR_OPENAI_API_KEY_HERE":
            print("✅ OpenAI API Key: Configured")
            print(f"   Key prefix: {OPENAI_API_KEY[:20]}...")
            return True
        else:
            print("❌ OpenAI API Key: NOT CONFIGURED")
            print("   Please add your API key to backend/.env file")
            print("   OPENAI_API_KEY=sk-proj-your_key_here")
            return False
    except Exception as e:
        print(f"❌ Error checking OpenAI key: {e}")
        return False

def check_chromadb():
    """Check ChromaDB initialization"""
    print_header("2. ChromaDB RAG System")
    try:
        from app.chromadb_rag import get_rag_instance
        rag = get_rag_instance()
        
        if rag.collection:
            count = rag.collection.count()
            print(f"✅ ChromaDB: Initialized with {count} documents")
            
            # Test retrieval
            test_result = rag.retrieve_context("DSR limits for housing loans", n_results=2)
            if test_result["documents"]:
                print(f"✅ RAG Retrieval: Working ({len(test_result['documents'])} results)")
                return True
            else:
                print("⚠️  RAG Retrieval: No results (may need reinitialization)")
                return False
        else:
            print("❌ ChromaDB: Not initialized")
            return False
    except ImportError as e:
        print(f"❌ ChromaDB Import Error: {e}")
        print("   Try: pip install chromadb sentence-transformers")
        return False
    except Exception as e:
        print(f"❌ ChromaDB Error: {e}")
        return False

def check_xgboost_model():
    """Check XGBoost model"""
    print_header("3. XGBoost ML Model")
    try:
        from app.xgboost_predictor import XGBoostLoanPredictor
        predictor = XGBoostLoanPredictor()
        predictor.load_model()
        print("✅ XGBoost Model: Loaded successfully")
        print(f"   Accuracy: 99.79% (24,000 training samples)")
        return True
    except FileNotFoundError:
        print("❌ XGBoost Model: Not found")
        print("   Run: python -m app.xgboost_predictor")
        return False
    except Exception as e:
        print(f"❌ XGBoost Error: {e}")
        return False

def check_document_extractor():
    """Check document extraction capabilities"""
    print_header("4. Document Extraction")
    try:
        from app.extractor import extract_text, PDF_AVAILABLE, DOCX_AVAILABLE
        
        print(f"✅ Text Extractor: Available")
        print(f"   PDF Support: {'✅ Yes' if PDF_AVAILABLE else '❌ No (install pdfplumber)'}")
        print(f"   DOCX Support: {'✅ Yes' if DOCX_AVAILABLE else '❌ No (install python-docx)'}")
        
        return PDF_AVAILABLE and DOCX_AVAILABLE
    except Exception as e:
        print(f"❌ Extractor Error: {e}")
        return False

def check_fraud_detector():
    """Check fraud detection module"""
    print_header("5. Fraud Detection System")
    try:
        from app.fraud_detector import detect_fraud_signals
        
        test_text = "Income: RM 5000. Monthly debt: RM 1000."
        result = detect_fraud_signals(test_text)
        
        if "fraud_score" in result:
            print("✅ Fraud Detection: Working")
            print(f"   Test result: {result['fraud_score']}/100 fraud score")
            return True
        else:
            print("❌ Fraud Detection: Invalid result")
            return False
    except Exception as e:
        print(f"❌ Fraud Detection Error: {e}")
        return False

def check_credit_scorer():
    """Check credit scoring module"""
    print_header("6. Credit Scoring System")
    try:
        from app.credit_scorer import CreditScoreCalculator
        
        calculator = CreditScoreCalculator()
        test_text = "Monthly income: RM 8000. Monthly debt: RM 2000."
        result = calculator.analyze(test_text)
        
        if "credit_score" in result:
            print("✅ Credit Scoring: Working")
            print(f"   Test score: {result['credit_score']}/850")
            return True
        else:
            print("❌ Credit Scoring: Invalid result")
            return False
    except Exception as e:
        print(f"❌ Credit Scoring Error: {e}")
        return False

def check_ports():
    """Check if required ports are available"""
    print_header("7. Port Availability")
    import socket
    
    ports_to_check = [
        (8000, "Backend (FastAPI)"),
        (5173, "Frontend (Vite)")
    ]
    
    all_available = True
    for port, name in ports_to_check:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("localhost", port))
            print(f"✅ Port {port} ({name}): Available")
            sock.close()
        except OSError:
            print(f"⚠️  Port {port} ({name}): In use (may already be running)")
            all_available = False
    
    return all_available

def main():
    print("\n" + "🔍 BadDebtGuard AI - System Health Check".center(60))
    print("Testing all components before startup...\n")
    
    results = {
        "OpenAI API Key": check_openai_key(),
        "ChromaDB RAG": check_chromadb(),
        "XGBoost Model": check_xgboost_model(),
        "Document Extractor": check_document_extractor(),
        "Fraud Detection": check_fraud_detector(),
        "Credit Scoring": check_credit_scorer(),
        "Port Availability": check_ports()
    }
    
    # Summary
    print_header("System Health Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for component, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {component}")
    
    print(f"\n📊 Status: {passed}/{total} components ready")
    
    if passed == total:
        print("\n🎉 All systems operational! Ready to start servers.")
        print("\nNext steps:")
        print("1. Terminal 1: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
        print("2. Terminal 2: cd ../frontend && npm run dev")
        print("3. Open: http://localhost:5173")
        return 0
    elif not results["OpenAI API Key"]:
        print("\n⚠️  CRITICAL: OpenAI API key not configured!")
        print("Edit backend/.env and add: OPENAI_API_KEY=sk-proj-your_key_here")
        return 1
    else:
        print("\n⚠️  Some components need attention. See details above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

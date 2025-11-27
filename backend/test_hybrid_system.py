"""
Test the complete hybrid system: Fraud Detection + Credit Scoring + XGBoost + LLM
"""
import asyncio
from app.fraud_detector import detect_fraud_signals, calculate_document_quality_score
from app.credit_scorer import CreditScoreCalculator
from app.xgboost_predictor import XGBoostLoanPredictor
from app.openai_agent import analyze_with_openai

# Sample loan application text
sample_document = """
LOAN APPLICATION FORM

Applicant Information:
Name: Ahmad bin Hassan
IC Number: 890123-10-5678
Date of Birth: 23/01/1989
Phone: 012-345-6789
Email: ahmad.hassan@email.com
Address: 123, Jalan Merdeka, 50000 Kuala Lumpur

Employment Details:
Employer: Tech Solutions Sdn Bhd
Position: Senior Software Engineer
Employment Type: Permanent
Years with Company: 5 years
Monthly Income: RM 12,500
Employment Status: Employed

Financial Information:
Monthly Debt Obligations: RM 2,000 (Car loan RM 800, Credit card RM 1,200)
Property Ownership: Own apartment (purchased 2018)
Savings Account Balance: RM 85,000

Loan Request:
Loan Amount: RM 80,000
Purpose: Home renovation
Preferred Tenure: 7 years
Property Value (for LTV): RM 450,000

Credit History:
Credit Score: 725
Previous Loans: Car loan (completed), Personal loan (active, good payment history)
Late Payments: None in last 12 months
Bankruptcy Status: Never

Supporting Documents Submitted:
✓ IC Copy
✓ Latest 3 months payslips
✓ EPF statement
✓ Bank statements (6 months)
✓ Property valuation report
✓ Utility bills (proof of address)

Declaration:
I hereby declare that all information provided is true and accurate.

Signature: Ahmad bin Hassan
Date: 20 November 2025
"""

async def test_hybrid_system():
    print("=" * 80)
    print("HYBRID LOAN ASSESSMENT SYSTEM TEST")
    print("XGBoost (70%) + LLM (30%) + Fraud Detection + Credit Scoring")
    print("=" * 80)
    
    # STEP 1: Fraud Detection
    print("\n[1/5] Running Fraud Detection...")
    fraud_analysis = detect_fraud_signals(sample_document)
    print(f"   Fraud Score: {fraud_analysis['fraud_score']}/100")
    print(f"   Risk Level: {fraud_analysis['risk_level']}")
    print(f"   Signals Detected: {fraud_analysis['total_signals']}")
    print(f"   Authenticity Confidence: {fraud_analysis['authenticity_confidence']}%")
    
    # STEP 2: Document Quality
    print("\n[2/5] Assessing Document Quality...")
    quality_analysis = calculate_document_quality_score(sample_document)
    print(f"   Quality Score: {quality_analysis['quality_score']}/100")
    print(f"   Word Count: {quality_analysis['word_count']}")
    print(f"   Numerical Density: {quality_analysis['numerical_density']}%")
    
    # STEP 3: Credit Scoring
    print("\n[3/5] Calculating Credit Score...")
    credit_calculator = CreditScoreCalculator()
    credit_analysis = credit_calculator.analyze(sample_document)
    print(f"   Credit Score: {credit_analysis['credit_score']}/850")
    print(f"   Risk Category: {credit_analysis['risk_category']}")
    print(f"   DSR: {credit_analysis['dsr']}%")
    print(f"   LTV: {credit_analysis['ltv']}%")
    
    # STEP 4: XGBoost Prediction
    print("\n[4/5] XGBoost ML Prediction...")
    xgb_predictor = XGBoostLoanPredictor()
    xgb_predictor.load_model()
    xgb_prediction = xgb_predictor.predict_from_document_data(credit_analysis['extracted_data'])
    print(f"   Approval Probability: {xgb_prediction['approval_probability']}%")
    print(f"   Risk Level: {xgb_prediction['risk_level']}")
    print(f"   Recommendation: {xgb_prediction['recommendation']}")
    print(f"   Model Confidence: {xgb_prediction['model_confidence']}%")
    
    # STEP 5: LLM Analysis
    print("\n[5/5] GPT-4o LLM Analysis...")
    llm_analysis = await analyze_with_openai(
        extracted_text=sample_document,
        banking_system="conventional",
        loan_type="personal",
        customer_type="retail"
    )
    llm_risk_level = llm_analysis["risk_analysis"]["risk_level"]
    llm_confidence = llm_analysis["confidence_metrics"]["overall_recommendation"]
    print(f"   Risk Level: {llm_risk_level}")
    print(f"   Recommendation: {llm_analysis['recommendation']}")
    print(f"   AI Confidence: {llm_confidence}%")
    print(f"   Findings: {len(llm_analysis['findings'])} key findings")
    
    # HYBRID FUSION
    print("\n" + "=" * 80)
    print("HYBRID FUSION ANALYSIS (70% XGBoost + 30% LLM)")
    print("=" * 80)
    
    # Convert LLM risk level to probability
    llm_probability_map = {
        "LOW": 85,
        "LOW-MEDIUM": 70,
        "MEDIUM": 55,
        "MEDIUM-HIGH": 40,
        "HIGH": 20
    }
    llm_approval_proba = llm_probability_map.get(llm_risk_level, 50)
    
    # Calculate weighted fusion
    xgb_weight = 0.70
    llm_weight = 0.30
    
    fused_approval_probability = (
        xgb_weight * xgb_prediction['approval_probability'] +
        llm_weight * llm_approval_proba
    )
    
    # Determine fused recommendation
    if fused_approval_probability >= 75:
        fused_risk_level = "LOW"
        fused_recommendation = "APPROVED - Strong candidate"
    elif fused_approval_probability >= 60:
        fused_risk_level = "LOW-MEDIUM"
        fused_recommendation = "APPROVED with conditions"
    elif fused_approval_probability >= 45:
        fused_risk_level = "MEDIUM"
        fused_recommendation = "REVIEW REQUIRED"
    elif fused_approval_probability >= 30:
        fused_risk_level = "MEDIUM-HIGH"
        fused_recommendation = "DECLINE with reapplication option"
    else:
        fused_risk_level = "HIGH"
        fused_recommendation = "DECLINE - High risk"
    
    print(f"\nXGBoost Score (70%): {xgb_prediction['approval_probability']}%")
    print(f"LLM Score (30%):     {llm_approval_proba}%")
    print(f"\nFused Approval Probability: {fused_approval_probability:.2f}%")
    print(f"Fused Risk Level: {fused_risk_level}")
    print(f"Final Recommendation: {fused_recommendation}")
    
    # Model agreement check
    agreement = abs(xgb_prediction['approval_probability'] - llm_approval_proba) < 20
    print(f"\nModel Agreement: {'✓ Yes' if agreement else '✗ No - Manual review recommended'}")
    
    # Summary
    print("\n" + "=" * 80)
    print("COMPLETE ASSESSMENT SUMMARY")
    print("=" * 80)
    print(f"Fraud Risk:          {fraud_analysis['risk_level']} ({fraud_analysis['fraud_score']}/100)")
    print(f"Document Quality:    {quality_analysis['quality_score']}/100")
    print(f"Credit Score:        {credit_analysis['credit_score']}/850 ({credit_analysis['risk_category']})")
    print(f"XGBoost Prediction:  {xgb_prediction['approval_probability']}% approval ({xgb_prediction['risk_level']})")
    print(f"LLM Analysis:        {llm_risk_level} risk")
    print(f"Final Decision:      {fused_recommendation}")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_hybrid_system())

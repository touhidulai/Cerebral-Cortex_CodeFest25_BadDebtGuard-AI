"""
Credit Scoring Module - Lightweight ML-based scoring
Complements GPT-4o with quantitative risk calculations
"""

import re
from typing import Dict, Optional, Tuple


class CreditScoreCalculator:
    """
    Rule-based credit scoring system using Malaysian banking standards
    """
    
    def __init__(self):
        # Malaysian banking thresholds
        self.MAX_DSR = 70  # Bank Negara Malaysia guideline (70%)
        self.OPTIMAL_DSR = 40
        self.MIN_CREDIT_SCORE = 300
        self.MAX_CREDIT_SCORE = 850
    
    def extract_financial_data(self, text: str) -> Dict:
        """
        Extract numerical financial data from document text
        """
        data = {
            "monthly_income": 0,
            "monthly_debt": 0,
            "employment_years": 0,
            "property_value": 0,
            "loan_amount": 0,
            "savings": 0,
            "age": 0
        }
        
        # Extract monthly income
        income_patterns = [
            r'monthly\s+(?:salary|income|earning).*?RM\s*([\d,]+)',
            r'income.*?RM\s*([\d,]+)',
            r'salary.*?RM\s*([\d,]+)'
        ]
        for pattern in income_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data["monthly_income"] = int(match.group(1).replace(',', ''))
                break
        
        # Extract monthly debt obligations
        debt_patterns = [
            r'(?:loan|debt|payment).*?RM\s*([\d,]+).*?(?:month|monthly)',
            r'monthly\s+(?:payment|commitment).*?RM\s*([\d,]+)'
        ]
        debts = []
        for pattern in debt_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            debts.extend([int(m.replace(',', '')) for m in matches])
        
        if debts:
            data["monthly_debt"] = sum(debts)
        
        # Extract employment duration
        emp_patterns = [
            r'(?:employment|worked|working).*?(\d+)\s+years?',
            r'(\d+)\s+years?.*?(?:employment|experience)'
        ]
        for pattern in emp_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data["employment_years"] = int(match.group(1))
                break
        
        # Extract property value
        prop_patterns = [
            r'property\s+value.*?RM\s*([\d,]+)',
            r'valuation.*?RM\s*([\d,]+)',
            r'purchase\s+price.*?RM\s*([\d,]+)'
        ]
        for pattern in prop_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data["property_value"] = int(match.group(1).replace(',', ''))
                break
        
        # Extract loan amount requested
        loan_patterns = [
            r'loan\s+amount.*?RM\s*([\d,]+)',
            r'financing.*?RM\s*([\d,]+)',
            r'requested.*?RM\s*([\d,]+)'
        ]
        for pattern in loan_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data["loan_amount"] = int(match.group(1).replace(',', ''))
                break
        
        # Extract savings/assets
        savings_patterns = [
            r'savings.*?RM\s*([\d,]+)',
            r'bank\s+balance.*?RM\s*([\d,]+)',
            r'assets?.*?RM\s*([\d,]+)'
        ]
        for pattern in savings_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data["savings"] = int(match.group(1).replace(',', ''))
                break
        
        # Extract age
        age_patterns = [
            r'age.*?(\d{2})',
            r'(\d{2})\s+years?\s+old',
            r'born.*?(\d{4})'
        ]
        for pattern in age_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = int(match.group(1))
                if value > 1900:  # Birth year
                    from datetime import datetime
                    data["age"] = datetime.now().year - value
                else:  # Direct age
                    data["age"] = value
                break
        
        return data
    
    def calculate_dsr(self, monthly_income: float, monthly_debt: float) -> float:
        """Calculate Debt Service Ratio"""
        if monthly_income == 0:
            return 0
        return (monthly_debt / monthly_income) * 100
    
    def calculate_ltv(self, loan_amount: float, property_value: float) -> float:
        """Calculate Loan-to-Value ratio"""
        if property_value == 0:
            return 0
        return (loan_amount / property_value) * 100
    
    def calculate_credit_score(self, data: Dict) -> Tuple[int, Dict]:
        """
        Calculate credit score (300-850) based on extracted data
        Returns: (score, breakdown_dict)
        """
        
        score = 500  # Start at middle
        breakdown = {}
        
        # 1. DSR Assessment (35% weight)
        dsr = self.calculate_dsr(data["monthly_income"], data["monthly_debt"])
        if dsr == 0:
            dsr_score = 0
            breakdown["dsr"] = {"value": "Unknown", "score": 0, "impact": "Neutral"}
        elif dsr <= self.OPTIMAL_DSR:
            dsr_score = 120
            breakdown["dsr"] = {"value": f"{dsr:.1f}%", "score": 120, "impact": "Excellent"}
        elif dsr <= 50:
            dsr_score = 80
            breakdown["dsr"] = {"value": f"{dsr:.1f}%", "score": 80, "impact": "Good"}
        elif dsr <= self.MAX_DSR:
            dsr_score = 40
            breakdown["dsr"] = {"value": f"{dsr:.1f}%", "score": 40, "impact": "Fair"}
        else:
            dsr_score = -50
            breakdown["dsr"] = {"value": f"{dsr:.1f}%", "score": -50, "impact": "Poor"}
        
        score += dsr_score
        
        # 2. Employment Stability (25% weight)
        years = data["employment_years"]
        if years >= 5:
            emp_score = 90
            breakdown["employment"] = {"years": years, "score": 90, "impact": "Excellent"}
        elif years >= 3:
            emp_score = 60
            breakdown["employment"] = {"years": years, "score": 60, "impact": "Good"}
        elif years >= 1:
            emp_score = 30
            breakdown["employment"] = {"years": years, "score": 30, "impact": "Fair"}
        else:
            emp_score = 0
            breakdown["employment"] = {"years": years, "score": 0, "impact": "Limited"}
        
        score += emp_score
        
        # 3. Income Level (15% weight)
        income = data["monthly_income"]
        if income >= 10000:
            income_score = 55
            breakdown["income"] = {"amount": f"RM {income:,}", "score": 55, "impact": "High"}
        elif income >= 5000:
            income_score = 35
            breakdown["income"] = {"amount": f"RM {income:,}", "score": 35, "impact": "Good"}
        elif income >= 3000:
            income_score = 20
            breakdown["income"] = {"amount": f"RM {income:,}", "score": 20, "impact": "Moderate"}
        else:
            income_score = 0
            breakdown["income"] = {"amount": f"RM {income:,}", "score": 0, "impact": "Low"}
        
        score += income_score
        
        # 4. LTV Assessment (15% weight)
        ltv = self.calculate_ltv(data["loan_amount"], data["property_value"])
        if ltv == 0:
            ltv_score = 0
            breakdown["ltv"] = {"value": "Unknown", "score": 0, "impact": "Neutral"}
        elif ltv <= 70:
            ltv_score = 55
            breakdown["ltv"] = {"value": f"{ltv:.1f}%", "score": 55, "impact": "Excellent"}
        elif ltv <= 80:
            ltv_score = 35
            breakdown["ltv"] = {"value": f"{ltv:.1f}%", "score": 35, "impact": "Good"}
        elif ltv <= 90:
            ltv_score = 15
            breakdown["ltv"] = {"value": f"{ltv:.1f}%", "score": 15, "impact": "Fair"}
        else:
            ltv_score = -20
            breakdown["ltv"] = {"value": f"{ltv:.1f}%", "score": -20, "impact": "High Risk"}
        
        score += ltv_score
        
        # 5. Savings/Buffer (10% weight)
        savings = data["savings"]
        monthly_income = data["monthly_income"]
        if monthly_income > 0:
            savings_months = savings / monthly_income if monthly_income > 0 else 0
            if savings_months >= 6:
                savings_score = 35
                breakdown["savings"] = {"months": f"{savings_months:.1f}", "score": 35, "impact": "Strong"}
            elif savings_months >= 3:
                savings_score = 20
                breakdown["savings"] = {"months": f"{savings_months:.1f}", "score": 20, "impact": "Good"}
            elif savings_months >= 1:
                savings_score = 10
                breakdown["savings"] = {"months": f"{savings_months:.1f}", "score": 10, "impact": "Fair"}
            else:
                savings_score = 0
                breakdown["savings"] = {"months": f"{savings_months:.1f}", "score": 0, "impact": "Limited"}
        else:
            savings_score = 0
            breakdown["savings"] = {"months": "Unknown", "score": 0, "impact": "Unknown"}
        
        score += savings_score
        
        # Clamp score to valid range
        final_score = max(self.MIN_CREDIT_SCORE, min(self.MAX_CREDIT_SCORE, score))
        
        return final_score, breakdown
    
    def get_risk_category(self, credit_score: int) -> str:
        """Map credit score to risk category"""
        if credit_score >= 750:
            return "LOW RISK"
        elif credit_score >= 650:
            return "MEDIUM-LOW RISK"
        elif credit_score >= 550:
            return "MEDIUM RISK"
        elif credit_score >= 450:
            return "MEDIUM-HIGH RISK"
        else:
            return "HIGH RISK"
    
    def analyze(self, extracted_text: str) -> Dict:
        """
        Full credit analysis
        """
        # Extract data
        data = self.extract_financial_data(extracted_text)
        
        # Calculate score
        credit_score, breakdown = self.calculate_credit_score(data)
        
        # Get risk category
        risk_category = self.get_risk_category(credit_score)
        
        # Calculate key ratios
        dsr = self.calculate_dsr(data["monthly_income"], data["monthly_debt"])
        ltv = self.calculate_ltv(data["loan_amount"], data["property_value"])
        
        return {
            "credit_score": credit_score,
            "risk_category": risk_category,
            "dsr": round(dsr, 2),
            "ltv": round(ltv, 2),
            "extracted_data": data,
            "score_breakdown": breakdown,
            "recommendations": self._generate_recommendations(credit_score, dsr, ltv, data)
        }
    
    def _generate_recommendations(self, score: int, dsr: float, ltv: float, data: Dict) -> list:
        """Generate actionable recommendations"""
        recommendations = []
        
        if dsr > self.MAX_DSR:
            recommendations.append("DSR exceeds Bank Negara guidelines. Consider debt consolidation or higher income verification.")
        
        if ltv > 90:
            recommendations.append("High LTV ratio. Recommend larger down payment to reduce loan amount.")
        
        if data["employment_years"] < 2:
            recommendations.append("Limited employment history. May require co-borrower or guarantor.")
        
        if data["savings"] < data["monthly_income"] * 3:
            recommendations.append("Limited savings buffer. Recommend building emergency fund before approval.")
        
        if score < 550:
            recommendations.append("Below optimal credit score. Consider credit improvement measures before reapplication.")
        
        if not recommendations:
            recommendations.append("All metrics within acceptable ranges. Applicant qualifies for standard terms.")
        
        return recommendations

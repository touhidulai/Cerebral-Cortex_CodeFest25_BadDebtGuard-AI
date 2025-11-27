"""
Fraud Detection Module - Lightweight ML for Document Authenticity
Uses simple heuristics and pattern matching to flag suspicious documents
"""

import re
from typing import Dict, List, Tuple
from datetime import datetime


def detect_fraud_signals(extracted_text: str) -> Dict:
    """
    Analyze document for fraud indicators using rule-based ML
    
    Returns:
        Dict with fraud_score (0-100), signals found, and authenticity confidence
    """
    
    signals = []
    fraud_score = 0
    
    # 1. Check for copy-paste patterns (repeated blocks)
    text_blocks = extracted_text.split('\n')
    duplicates = len(text_blocks) - len(set(text_blocks))
    if duplicates > 5:
        signals.append("High duplicate content detected")
        fraud_score += 15
    
    # 2. Check for inconsistent formatting
    amount_patterns = re.findall(r'RM\s*[\d,]+\.?\d*', extracted_text)
    if len(amount_patterns) > 0:
        # Check if amounts have consistent formatting
        formats = set(p.replace('RM', '').strip()[0:3] for p in amount_patterns)
        if len(formats) > 3:
            signals.append("Inconsistent number formatting")
            fraud_score += 10
    
    # 3. Check for unrealistic values
    incomes = re.findall(r'income.*?RM\s*([\d,]+)', extracted_text, re.IGNORECASE)
    for income in incomes:
        income_val = int(income.replace(',', ''))
        if income_val > 100000:  # > RM 100k/month
            signals.append("Unusually high income reported")
            fraud_score += 20
        elif income_val < 1000:  # < RM 1k/month
            signals.append("Suspiciously low income")
            fraud_score += 15
    
    # 4. Check for missing critical information
    required_fields = ['name', 'income', 'employment', 'address']
    missing = []
    for field in required_fields:
        if not re.search(field, extracted_text, re.IGNORECASE):
            missing.append(field)
    
    if len(missing) > 1:
        signals.append(f"Missing critical fields: {', '.join(missing)}")
        fraud_score += 10 * len(missing)
    
    # 5. Check for document metadata consistency
    dates = re.findall(r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}', extracted_text)
    if len(dates) > 3:
        # Check for future dates
        current_year = datetime.now().year
        for date_str in dates:
            year = int(date_str.split('/')[-1])
            if len(str(year)) == 2:
                year += 2000
            if year > current_year:
                signals.append("Document contains future dates")
                fraud_score += 25
                break
    
    # 6. Check for excessive manual editing indicators
    corrections = len(re.findall(r'\*+|correction|amended|updated', extracted_text, re.IGNORECASE))
    if corrections > 3:
        signals.append("Multiple corrections/amendments detected")
        fraud_score += 15
    
    # Calculate authenticity confidence (inverse of fraud score)
    authenticity_confidence = max(0, 100 - fraud_score)
    
    # Categorize risk level
    if fraud_score >= 50:
        risk_level = "HIGH FRAUD RISK"
    elif fraud_score >= 25:
        risk_level = "MEDIUM FRAUD RISK"
    else:
        risk_level = "LOW FRAUD RISK"
    
    return {
        "fraud_score": min(fraud_score, 100),
        "authenticity_confidence": authenticity_confidence,
        "risk_level": risk_level,
        "signals": signals if signals else ["No fraud indicators detected"],
        "total_signals": len(signals)
    }


def calculate_document_quality_score(extracted_text: str) -> Dict:
    """
    Calculate document completeness and quality metrics
    """
    
    # Basic metrics
    word_count = len(extracted_text.split())
    char_count = len(extracted_text)
    line_count = len(extracted_text.split('\n'))
    
    # Numerical data density
    numbers = re.findall(r'\d+', extracted_text)
    numerical_density = len(numbers) / max(word_count, 1) * 100
    
    # Currency mentions (financial relevance)
    currency_mentions = len(re.findall(r'RM\s*[\d,]+', extracted_text))
    
    # Calculate quality score
    quality_score = 0
    
    # Length checks
    if word_count > 100:
        quality_score += 20
    if word_count > 500:
        quality_score += 10
    
    # Numerical data presence
    if numerical_density > 5:
        quality_score += 20
    if numerical_density > 10:
        quality_score += 10
    
    # Financial relevance
    if currency_mentions > 5:
        quality_score += 20
    if currency_mentions > 10:
        quality_score += 10
    
    # Structure quality
    if line_count > 20:
        quality_score += 10
    
    # Completeness check
    keywords = ['income', 'employment', 'debt', 'loan', 'bank']
    found_keywords = sum(1 for kw in keywords if kw in extracted_text.lower())
    quality_score += found_keywords * 2
    
    return {
        "quality_score": min(quality_score, 100),
        "word_count": word_count,
        "numerical_density": round(numerical_density, 2),
        "currency_mentions": currency_mentions,
        "completeness": f"{found_keywords}/{len(keywords)} key fields"
    }

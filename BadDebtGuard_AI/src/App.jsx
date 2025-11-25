import React, { useState } from 'react';
import { Upload, FileText, Brain, CheckCircle, AlertCircle, TrendingUp, Building2, User, Home, Car, Briefcase, ChevronRight, Shield, Database, Zap } from 'lucide-react';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedBankingSystem, setSelectedBankingSystem] = useState('');
  const [selectedLoanType, setSelectedLoanType] = useState('');
  const [selectedCustomerType, setSelectedCustomerType] = useState('');
  const [uploadedDocs, setUploadedDocs] = useState([]);
  const [analysisStatus, setAnalysisStatus] = useState('idle');

  const bankingSystems = [
    { id: 'conventional', name: 'Conventional Banking', icon: Building2 },
    { id: 'islamic', name: 'Islamic Banking', icon: Shield }
  ];

  const loanTypes = [
    { id: 'home', name: 'Home Loan', icon: Home, docs: ['Income proof', 'Property valuation', 'SPA', 'Title deed'] },
    { id: 'car', name: 'Car Loan', icon: Car, docs: ['Income proof', 'Vehicle invoice', 'Insurance quote'] },
    { id: 'personal', name: 'Personal Loan', icon: User, docs: ['Income proof', 'Bank statements', 'ID documents'] },
    { id: 'business', name: 'Business Loan', icon: Briefcase, docs: ['Financial statements', 'Business registration', 'Tax returns'] }
  ];

  const customerTypes = [
    { id: 'salaried', name: 'Salaried Employee', requirements: ['Payslips (3 months)', 'EPF statement', 'Employment letter'] },
    { id: 'rental', name: 'Rental Income', requirements: ['Tenancy agreements', 'Rental income statements', 'Property ownership proof'] },
    { id: 'small-business', name: 'Small Business Owner', requirements: ['Business financial statements', 'SSM registration', 'Bank statements (6 months)'] },
    { id: 'large-business', name: 'Large Enterprise', requirements: ['Audited financial statements', 'Company registration', 'Board resolution'] }
  ];

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files);
    setUploadedDocs([...uploadedDocs, ...files.map(f => ({ name: f.name, status: 'uploaded', size: f.size }))]);
  };

  const startAnalysis = () => {
    setAnalysisStatus('analyzing');
    setTimeout(() => setAnalysisStatus('complete'), 4500);
  };

  return (
    <div className="app-container">
      {/* Navigation */}
      <nav className="navbar">
        <div className="nav-content">
          <div className="nav-left">
            <div className="logo-container">
              <div className="logo-icon">
                <Brain className="icon-lg" />
              </div>
              <div>
                <h1 className="logo-title">LoanAI Pro</h1>
                <p className="logo-subtitle">Intelligent Loan Assessment Platform</p>
              </div>
            </div>
            <div className="nav-links">
              <button 
                className={`nav-link ${activeTab === 'dashboard' ? 'active' : ''}`} 
                onClick={() => setActiveTab('dashboard')}
              >
                Dashboard
              </button>
              <button 
                className={`nav-link ${activeTab === 'assessment' ? 'active' : ''}`} 
                onClick={() => setActiveTab('assessment')}
              >
                New Assessment
              </button>
              <button 
                className={`nav-link ${activeTab === 'history' ? 'active' : ''}`} 
                onClick={() => setActiveTab('history')}
              >
                History
              </button>
            </div>
          </div>
          <div className="user-avatar">FI</div>
        </div>
      </nav>

      <div className="main-content">
        {activeTab === 'dashboard' && (
          <div className="dashboard-content">
            {/* Stats Overview */}
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-header">
                  <div className="stat-icon blue">
                    <FileText className="icon-md" />
                  </div>
                  <span className="stat-trend positive">+12%</span>
                </div>
                <h3 className="stat-value">247</h3>
                <p className="stat-label">Applications This Month</p>
              </div>
              <div className="stat-card">
                <div className="stat-header">
                  <div className="stat-icon green">
                    <CheckCircle className="icon-md" />
                  </div>
                  <span className="stat-trend positive">+8%</span>
                </div>
                <h3 className="stat-value">182</h3>
                <p className="stat-label">Approved</p>
              </div>
              <div className="stat-card">
                <div className="stat-header">
                  <div className="stat-icon purple">
                    <Brain className="icon-md" />
                  </div>
                  <span className="stat-trend positive">+23%</span>
                </div>
                <h3 className="stat-value">94%</h3>
                <p className="stat-label">AI Analysis Accuracy</p>
              </div>
              <div className="stat-card">
                <div className="stat-header">
                  <div className="stat-icon amber">
                    <TrendingUp className="icon-md" />
                  </div>
                  <span className="stat-trend positive">-15%</span>
                </div>
                <h3 className="stat-value">3.2 days</h3>
                <p className="stat-label">Avg Processing Time</p>
              </div>
            </div>

            {/* Recent Assessments */}
            <div className="card">
              <h2 className="card-title">Recent Assessments</h2>
              <div className="assessment-list">
                {[
                  { id: 'LA-2024-1148', name: 'Ahmad bin Hassan', type: 'Home Loan', status: 'approved', score: 782 },
                  { id: 'LA-2024-1147', name: 'Siti Nurhaliza', type: 'Car Loan', status: 'pending', score: 715 },
                  { id: 'LA-2024-1146', name: 'Kumar Subramaniam', type: 'Business Loan', status: 'review', score: 698 }
                ].map((assessment) => (
                  <div key={assessment.id} className="assessment-item">
                    <div className="assessment-info">
                      <div className={`status-dot ${assessment.status}`}></div>
                      <div>
                        <p className="assessment-name">{assessment.name}</p>
                        <p className="assessment-meta">{assessment.id} • {assessment.type}</p>
                      </div>
                    </div>
                    <div className="assessment-details">
                      <div className="score-info">
                        <p className="score-value">{assessment.score}</p>
                        <p className="score-label">Credit Score</p>
                      </div>
                      <span className={`status-badge ${assessment.status}`}>
                        {assessment.status.charAt(0).toUpperCase() + assessment.status.slice(1)}
                      </span>
                      <ChevronRight className="icon-sm chevron" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'assessment' && (
          <div className="assessment-content">
            <div className="card">
              <h2 className="section-title">New Loan Assessment</h2>
              <p className="section-subtitle">Configure assessment parameters and upload required documents</p>

              {/* Step 1: Banking System Selection */}
              <div className="step-section">
                <h3 className="step-title">
                  <span className="step-number">1</span>
                  Select Banking System
                </h3>
                <div className="system-grid">
                  {bankingSystems.map((system) => (
                    <button
                      key={system.id}
                      onClick={() => setSelectedBankingSystem(system.id)}
                      className={`system-card ${selectedBankingSystem === system.id ? 'selected' : ''}`}
                    >
                      <div className={`system-icon ${selectedBankingSystem === system.id ? 'selected' : ''}`}>
                        <system.icon className="icon-md" />
                      </div>
                      <span className="system-name">{system.name}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Step 2: Loan Type */}
              <div className="step-section">
                <h3 className="step-title">
                  <span className="step-number">2</span>
                  Loan Type
                </h3>
                <div className="loan-type-grid">
                  {loanTypes.map((loan) => (
                    <button
                      key={loan.id}
                      onClick={() => setSelectedLoanType(loan.id)}
                      className={`loan-type-card ${selectedLoanType === loan.id ? 'selected' : ''}`}
                    >
                      <div className={`loan-icon ${selectedLoanType === loan.id ? 'selected' : ''}`}>
                        <loan.icon className="icon-md" />
                      </div>
                      <p className="loan-name">{loan.name}</p>
                    </button>
                  ))}
                </div>
              </div>

              {/* Step 3: Customer Type */}
              <div className="step-section">
                <h3 className="step-title">
                  <span className="step-number">3</span>
                  Customer Type
                </h3>
                <div className="customer-type-grid">
                  {customerTypes.map((customer) => (
                    <button
                      key={customer.id}
                      onClick={() => setSelectedCustomerType(customer.id)}
                      className={`customer-card ${selectedCustomerType === customer.id ? 'selected' : ''}`}
                    >
                      <p className="customer-name">{customer.name}</p>
                      <div className="requirements-list">
                        {customer.requirements.map((req, idx) => (
                          <p key={idx} className="requirement-item">• {req}</p>
                        ))}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Step 4: Document Upload */}
              {selectedBankingSystem && selectedLoanType && selectedCustomerType && (
                <div className="step-section">
                  <h3 className="step-title">
                    <span className="step-number">4</span>
                    Upload Documents
                  </h3>
                  
                  <div className="upload-zone">
                    <input type="file" multiple onChange={handleFileUpload} className="file-input" id="file-upload" />
                    <label htmlFor="file-upload" className="upload-label">
                      <Upload className="upload-icon" />
                      <p className="upload-title">Click to upload or drag and drop</p>
                      <p className="upload-subtitle">PDF, DOCX, JPG, PNG (Max 10MB per file)</p>
                    </label>
                  </div>

                  {uploadedDocs.length > 0 && (
                    <div className="uploaded-docs">
                      <h4 className="uploaded-title">Uploaded Documents ({uploadedDocs.length})</h4>
                      {uploadedDocs.map((doc, idx) => (
                        <div key={idx} className="doc-item">
                          <div className="doc-info">
                            <FileText className="icon-sm doc-icon" />
                            <span className="doc-name">{doc.name}</span>
                          </div>
                          <CheckCircle className="icon-sm check-icon" />
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* CCRIS Integration */}
              {selectedBankingSystem && selectedLoanType && selectedCustomerType && (
                <div className="step-section">
                  <h3 className="step-title">
                    <span className="step-number">5</span>
                    Bank Negara Malaysia CCRIS Integration
                  </h3>
                  <div className="ccris-card">
                    <div className="ccris-content">
                      <div className="ccris-icon">
                        <Database className="icon-md" />
                      </div>
                      <div className="ccris-info">
                        <p className="ccris-title">Fetch CCRIS Report</p>
                        <p className="ccris-subtitle">Retrieve credit history from Bank Negara Malaysia</p>
                      </div>
                      <button className="fetch-button">
                        <span>Fetch Report</span>
                        <ChevronRight className="icon-sm" />
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Start Analysis Button */}
              {uploadedDocs.length > 0 && (
                <button onClick={startAnalysis} className="analyze-button">
                  <Zap className="icon-sm" />
                  <span>Start AI-Powered Analysis</span>
                </button>
              )}
            </div>

            {/* Analysis Results */}
            {analysisStatus !== 'idle' && (
              <div className="card">
                <h3 className="card-title">AI Analysis Results</h3>
                
                {analysisStatus === 'analyzing' && (
                  <div className="analyzing-state">
                    <div className="analysis-animation">
                      <div className="spinner-large"></div>
                      <div className="pulse-ring"></div>
                    </div>
                    <div className="analyzing-steps">
                      <div className="step-indicator active">
                        <div className="step-dot"></div>
                        <span>Extracting document data...</span>
                      </div>
                      <div className="step-indicator active">
                        <div className="step-dot"></div>
                        <span>Analyzing unstructured content...</span>
                      </div>
                      <div className="step-indicator">
                        <div className="step-dot"></div>
                        <span>Computing risk assessment...</span>
                      </div>
                      <div className="step-indicator">
                        <div className="step-dot"></div>
                        <span>Generating insights...</span>
                      </div>
                    </div>
                    <p className="analyzing-title">AI-Powered Document Analysis in Progress</p>
                    <p className="analyzing-subtitle">Processing {uploadedDocs.length} documents with advanced NLP models</p>
                  </div>
                )}

                {analysisStatus === 'complete' && (
                  <div className="results-content">
                    {/* Risk Assessment Container */}
                    <div className="risk-assessment-container">
                      <h3 className="container-title">
                        <Shield className="icon-sm title-icon" />
                        Loan Risk Assessment
                      </h3>
                      <div className="risk-metrics-grid">
                        <div className="risk-metric-card">
                          <div className="metric-header">
                            <span className="metric-label">Loan Risk Category</span>
                            <div className="metric-badge low-risk">
                              <CheckCircle className="badge-icon" />
                            </div>
                          </div>
                          <div className="metric-value-container">
                            <span className="metric-value large">LOW RISK</span>
                            <span className="metric-subtitle">Tier 1 Classification</span>
                          </div>
                          <div className="risk-bar">
                            <div className="risk-bar-fill low"></div>
                          </div>
                          <div className="risk-scale">
                            <span className="scale-label active">Low</span>
                            <span className="scale-label">Medium</span>
                            <span className="scale-label">High</span>
                          </div>
                        </div>

                        <div className="risk-metric-card">
                          <div className="metric-header">
                            <span className="metric-label">Risk Premium</span>
                            <TrendingUp className="icon-sm metric-icon" />
                          </div>
                          <div className="metric-value-container">
                            <span className="metric-value large">2.45%</span>
                            <span className="metric-subtitle">Below market average</span>
                          </div>
                          <div className="premium-comparison">
                            <div className="comparison-item">
                              <span className="comparison-label">Market Avg:</span>
                              <span className="comparison-value">3.8%</span>
                            </div>
                            <div className="comparison-item">
                              <span className="comparison-label">Your Premium:</span>
                              <span className="comparison-value highlight">2.45%</span>
                            </div>
                          </div>
                          <div className="savings-indicator">
                            <span className="savings-text">1.35% lower than average</span>
                          </div>
                        </div>
                      </div>

                      {/* Additional Risk Indicators */}
                      <div className="risk-indicators">
                        <div className="indicator-item">
                          <div className="indicator-icon green">
                            <CheckCircle className="icon-xs" />
                          </div>
                          <div className="indicator-content">
                            <span className="indicator-label">Default Probability</span>
                            <span className="indicator-value">1.2%</span>
                          </div>
                        </div>
                        <div className="indicator-item">
                          <div className="indicator-icon green">
                            <CheckCircle className="icon-xs" />
                          </div>
                          <div className="indicator-content">
                            <span className="indicator-label">Credit Stability Score</span>
                            <span className="indicator-value">8.7/10</span>
                          </div>
                        </div>
                        <div className="indicator-item">
                          <div className="indicator-icon green">
                            <CheckCircle className="icon-xs" />
                          </div>
                          <div className="indicator-content">
                            <span className="indicator-label">Repayment Capacity</span>
                            <span className="indicator-value">Strong</span>
                          </div>
                        </div>
                        <div className="indicator-item">
                          <div className="indicator-icon blue">
                            <Brain className="icon-xs" />
                          </div>
                          <div className="indicator-content">
                            <span className="indicator-label">AI Confidence Level</span>
                            <span className="indicator-value">94%</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Reasoning and Explanation Container */}
                    <div className="reasoning-container">
                      <h3 className="container-title">
                        <Brain className="icon-sm title-icon" />
                        AI Analysis Reasoning & Document Insights
                      </h3>
                      
                      <div className="reasoning-content">
                        <div className="summary-section">
                          <h4 className="summary-title">Executive Summary</h4>
                          <p className="summary-text">
                            Based on comprehensive analysis of {uploadedDocs.length} submitted documents and CCRIS data, 
                            the applicant demonstrates strong financial stability, consistent income patterns, and low default risk indicators. 
                            The AI model has identified multiple positive signals across employment history, income verification, 
                            and asset ownership documentation.
                          </p>
                        </div>

                        {/* Key Findings from Documents */}
                        <div className="findings-section">
                          <h4 className="findings-title">Key Findings from Document Analysis</h4>
                          
                          <div className="finding-card positive">
                            <div className="finding-header">
                              <CheckCircle className="finding-icon" />
                              <span className="finding-tag">INCOME VERIFICATION</span>
                            </div>
                            <p className="finding-title">Stable Employment & Income Stream</p>
                            <p className="finding-description">
                              Analysis of employment letter and payslips reveals 8-year tenure with progressive salary increments. 
                              Current monthly income of RM 12,500 with consistent payment history detected across all 3 months of payslips.
                            </p>
                            <div className="finding-keywords">
                              <span className="keyword">Long tenure</span>
                              <span className="keyword">Consistent income</span>
                              <span className="keyword">Verified employer</span>
                              <span className="keyword">Progressive growth</span>
                            </div>
                          </div>

                          <div className="finding-card positive">
                            <div className="finding-header">
                              <CheckCircle className="finding-icon" />
                              <span className="finding-tag">CREDIT HISTORY</span>
                            </div>
                            <p className="finding-title">Excellent Credit Profile (CCRIS)</p>
                            <p className="finding-description">
                              CCRIS report shows zero defaults, no legal actions, and perfect payment history across existing 
                              credit facilities. Debt Service Ratio (DSR) calculated at 32%, well within acceptable range for home financing.
                            </p>
                            <div className="finding-keywords">
                              <span className="keyword">Zero defaults</span>
                              <span className="keyword">Low DSR (32%)</span>
                              <span className="keyword">Clean CCRIS</span>
                              <span className="keyword">Active credit facilities: 2</span>
                            </div>
                          </div>

                          <div className="finding-card positive">
                            <div className="finding-header">
                              <CheckCircle className="finding-icon" />
                              <span className="finding-tag">ASSET OWNERSHIP</span>
                            </div>
                            <p className="finding-title">Property & Asset Documentation Verified</p>
                            <p className="finding-description">
                              Property valuation report confirms current market value of RM 680,000 for the subject property. 
                              Loan-to-Value (LTV) ratio of 85% aligns with banking guidelines. Title deed shows clean ownership without encumbrances.
                            </p>
                            <div className="finding-keywords">
                              <span className="keyword">Property value: RM 680K</span>
                              <span className="keyword">LTV: 85%</span>
                              <span className="keyword">Clean title</span>
                              <span className="keyword">Updated valuation</span>
                            </div>
                          </div>

                          <div className="finding-card positive">
                            <div className="finding-header">
                              <CheckCircle className="finding-icon" />
                              <span className="finding-tag">ADDITIONAL INCOME</span>
                            </div>
                            <p className="finding-title">Secondary Income Source Detected</p>
                            <p className="finding-description">
                              Tenancy agreement analysis reveals consistent rental income of RM 2,800/month from investment property. 
                              36-month payment history confirmed through bank statements, adding to total monthly income capacity.
                            </p>
                            <div className="finding-keywords">
                              <span className="keyword">Rental income: RM 2,800</span>
                              <span className="keyword">36-month history</span>
                              <span className="keyword">Verified tenant</span>
                              <span className="keyword">Investment property</span>
                            </div>
                          </div>

                          <div className="finding-card warning">
                            <div className="finding-header">
                              <AlertCircle className="finding-icon" />
                              <span className="finding-tag">MINOR ATTENTION</span>
                            </div>
                            <p className="finding-title">Address Verification Required</p>
                            <p className="finding-description">
                              Utility bill shows different address from IC. Applicant provided explanation letter stating recent relocation. 
                              Recommend verification with updated utility bill or tenancy agreement for current address.
                            </p>
                            <div className="finding-keywords">
                              <span className="keyword">Address mismatch</span>
                              <span className="keyword">Recent relocation</span>
                              <span className="keyword">Explanation provided</span>
                              <span className="keyword">Low priority</span>
                            </div>
                          </div>
                        </div>

                        {/* Risk Calculation Breakdown */}
                        <div className="calculation-section">
                          <h4 className="calculation-title">Risk Premium Calculation Breakdown</h4>
                          <div className="calculation-grid">
                            <div className="calculation-item">
                              <span className="calc-label">Base Rate</span>
                              <span className="calc-value">1.95%</span>
                            </div>
                            <div className="calculation-item">
                              <span className="calc-label">Credit Risk Premium</span>
                              <span className="calc-value">+0.30%</span>
                            </div>
                            <div className="calculation-item">
                              <span className="calc-label">LTV Adjustment</span>
                              <span className="calc-value">+0.25%</span>
                            </div>
                            <div className="calculation-item">
                              <span className="calc-label">Employment Stability Discount</span>
                              <span className="calc-value highlight">-0.15%</span>
                            </div>
                            <div className="calculation-item">
                              <span className="calc-label">Additional Income Discount</span>
                              <span className="calc-value highlight">-0.10%</span>
                            </div>
                            <div className="calculation-item">
                              <span className="calc-label">Clean Credit History Discount</span>
                              <span className="calc-value highlight">-0.20%</span>
                            </div>
                            <div className="calculation-total">
                              <span className="calc-label-total">Total Risk Premium</span>
                              <span className="calc-value-total">2.45%</span>
                            </div>
                          </div>
                        </div>

                        {/* AI Model Confidence */}
                        <div className="confidence-section">
                          <h4 className="confidence-title">AI Model Confidence Metrics</h4>
                          <div className="confidence-bars">
                            <div className="confidence-bar-item">
                              <div className="confidence-label-row">
                                <span className="confidence-label">Document Authenticity</span>
                                <span className="confidence-percentage">98%</span>
                              </div>
                              <div className="confidence-bar">
                                <div className="confidence-fill" style={{width: '98%'}}></div>
                              </div>
                            </div>
                            <div className="confidence-bar-item">
                              <div className="confidence-label-row">
                                <span className="confidence-label">Income Stability Prediction</span>
                                <span className="confidence-percentage">95%</span>
                              </div>
                              <div className="confidence-bar">
                                <div className="confidence-fill" style={{width: '95%'}}></div>
                              </div>
                            </div>
                            <div className="confidence-bar-item">
                              <div className="confidence-label-row">
                                <span className="confidence-label">Default Risk Assessment</span>
                                <span className="confidence-percentage">92%</span>
                              </div>
                              <div className="confidence-bar">
                                <div className="confidence-fill" style={{width: '92%'}}></div>
                              </div>
                            </div>
                            <div className="confidence-bar-item">
                              <div className="confidence-label-row">
                                <span className="confidence-label">Overall Recommendation</span>
                                <span className="confidence-percentage">94%</span>
                              </div>
                              <div className="confidence-bar">
                                <div className="confidence-fill" style={{width: '94%'}}></div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Final Recommendation */}
                    <div className="recommendation-card">
                      <div className="recommendation-header">
                        <CheckCircle className="icon-md" />
                        <h4 className="recommendation-title">Recommended for Approval</h4>
                      </div>
                      <p className="recommendation-text">
                        Based on comprehensive AI analysis and traditional credit assessment, this application demonstrates 
                        strong approval indicators. The applicant qualifies for {selectedBankingSystem === 'conventional' ? 'Conventional' : 'Islamic'} {loanTypes.find(l => l.id === selectedLoanType)?.name} with 
                        favorable terms. Risk premium of 2.45% reflects excellent credit profile and stable financial position.
                      </p>
                      <div className="recommendation-stats">
                        <div className="rec-stat">
                          <span className="rec-stat-value">RM 578,000</span>
                          <span className="rec-stat-label">Approved Amount</span>
                        </div>
                        <div className="rec-stat">
                          <span className="rec-stat-value">35 years</span>
                          <span className="rec-stat-label">Max Tenure</span>
                        </div>
                        <div className="rec-stat">
                          <span className="rec-stat-value">5.20%</span>
                          <span className="rec-stat-label">Indicative Rate</span>
                        </div>
                      </div>
                    </div>

                    <div className="action-buttons">
                      <button className="approve-button">
                        <CheckCircle className="icon-sm" />
                        Approve Application
                      </button>
                      <button className="request-button">
                        <FileText className="icon-sm" />
                        Request Additional Documents
                      </button>
                      <button className="export-button">
                        <Upload className="icon-sm" />
                        Export Report
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === 'history' && (
          <div className="history-content">
            <div className="card">
              <h2 className="card-title">Assessment History</h2>
              <div className="history-list">
                {[...Array(8)].map((_, i) => (
                  <div key={i} className="history-item">
                    <div className="history-info">
                      <div className="status-dot approved"></div>
                      <div>
                        <p className="history-name">Customer #{1150 - i}</p>
                        <p className="history-meta">LA-2024-{1150 - i} • Processed on Nov {25 - i}, 2024</p>
                      </div>
                    </div>
                    <ChevronRight className="icon-sm chevron" />
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
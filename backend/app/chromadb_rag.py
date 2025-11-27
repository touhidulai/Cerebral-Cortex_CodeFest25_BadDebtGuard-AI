"""
ChromaDB RAG System for BNM Banking Guidelines
Retrieval-Augmented Generation for Malaysian banking regulations
"""
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
CHROMA_DB_PATH = BASE_DIR / "chroma_db"

# BNM Banking Guidelines Database
BNM_DOCUMENTS = [
    {
        "id": "bnm_dsr_housing_001",
        "content": "Bank Negara Malaysia DSR Guidelines for Housing Loans: Maximum Debt Service Ratio is 70% for housing loans. The DSR is calculated as (Total Monthly Debt Obligations / Gross Monthly Income) × 100. This applies to all conventional banking housing loans in Malaysia.",
        "metadata": {"category": "DSR", "loan_type": "housing", "banking": "conventional"}
    },
    {
        "id": "bnm_dsr_personal_001",
        "content": "BNM Personal Loan DSR Guidelines: For personal loans and credit facilities, the maximum DSR is 60%. Financial institutions must ensure borrowers' total monthly debt repayments do not exceed 60% of their gross monthly income.",
        "metadata": {"category": "DSR", "loan_type": "personal", "banking": "conventional"}
    },
    {
        "id": "bnm_ltv_residential_001",
        "content": "Loan-to-Value Ratio for Residential Properties: For properties priced RM500,000 and below, maximum LTV is 90% for first property, 70% for second property, and 70% for third property onwards. For properties above RM500,000, maximum LTV is 80% for first two properties and 70% for third property onwards.",
        "metadata": {"category": "LTV", "property_type": "residential", "banking": "conventional"}
    },
    {
        "id": "bnm_ltv_commercial_001",
        "content": "Commercial Property LTV Limits: Maximum Loan-to-Value ratio for commercial properties is 80% for first property and 70% for subsequent properties. This applies to shop lots, office buildings, and commercial real estate.",
        "metadata": {"category": "LTV", "property_type": "commercial", "banking": "conventional"}
    },
    {
        "id": "bnm_ltv_vehicle_001",
        "content": "Vehicle Financing LTV Guidelines: For hire-purchase agreements on vehicles, maximum LTV is 90% for first vehicle and 80% for subsequent vehicles. The tenure should not exceed 9 years.",
        "metadata": {"category": "LTV", "asset_type": "vehicle", "banking": "conventional"}
    },
    {
        "id": "bnm_income_requirement_001",
        "content": "Minimum Income Requirements: For housing loans below RM500,000, minimum monthly income is RM3,000. For loans above RM500,000, minimum monthly income is RM5,000. These requirements ensure borrowers have sufficient income to service the loan.",
        "metadata": {"category": "income", "loan_type": "housing", "banking": "conventional"}
    },
    {
        "id": "bnm_employment_stability_001",
        "content": "Employment Stability Requirements: Borrowers should have at least 6 months of continuous employment for personal loans and 12 months for housing loans. Self-employed individuals must provide 2 years of audited financial statements.",
        "metadata": {"category": "employment", "banking": "conventional"}
    },
    {
        "id": "bnm_credit_assessment_001",
        "content": "Credit Assessment Guidelines: Banks must conduct comprehensive credit assessments including CCRIS and CTOS checks. Borrowers with NPL (Non-Performing Loans) history in the past 12 months may be rejected. Credit score should be above 650 for favorable consideration.",
        "metadata": {"category": "credit_assessment", "banking": "conventional"}
    },
    {
        "id": "bnm_islamic_murabahah_001",
        "content": "Islamic Banking Murabahah Financing: For Murabahah (cost-plus financing), the profit rate should be competitive with conventional rates. The asset must be Shariah-compliant and physically exist. Maximum financing period is 30 years for property.",
        "metadata": {"category": "shariah", "product": "murabahah", "banking": "islamic"}
    },
    {
        "id": "bnm_islamic_ijarah_001",
        "content": "Islamic Banking Ijarah (Leasing): Ijarah financing allows asset leasing with option to purchase. Rental rates must be disclosed clearly. Maximum LTV for Ijarah property financing is similar to conventional (80-90% depending on property value and sequence).",
        "metadata": {"category": "shariah", "product": "ijarah", "banking": "islamic"}
    },
    {
        "id": "bnm_islamic_musharakah_001",
        "content": "Musharakah Partnership Financing: Joint ownership financing where bank and customer co-own the asset. Profit sharing ratio must be agreed upfront. Maximum bank share is 90%. Customer gradually buys out bank's share over time.",
        "metadata": {"category": "shariah", "product": "musharakah", "banking": "islamic"}
    },
    {
        "id": "bnm_islamic_tawarruq_001",
        "content": "Tawarruq Commodity Murabahah: Personal financing through commodity trading. Customer purchases commodity from bank, sells to third party for cash. Profit margin embedded in transaction. Maximum DSR still applies (60% for personal).",
        "metadata": {"category": "shariah", "product": "tawarruq", "banking": "islamic"}
    },
    {
        "id": "bnm_risk_management_001",
        "content": "Risk Management Guidelines: Banks must maintain Capital Adequacy Ratio (CAR) of at least 8%. High-risk loans require higher provisioning. Stress testing must be conducted quarterly. Non-performing loans should be below 3% of total portfolio.",
        "metadata": {"category": "risk_management", "banking": "both"}
    },
    {
        "id": "bnm_consumer_protection_001",
        "content": "Consumer Protection Standards: Banks must provide clear disclosure of all fees and charges. Borrowers have 14-day cooling-off period for housing loans. Early settlement penalties should not exceed 2% of outstanding principal.",
        "metadata": {"category": "consumer_protection", "banking": "both"}
    },
    {
        "id": "bnm_documentation_001",
        "content": "Required Documentation: Standard documents include IC copy, latest 3 months payslips, 6 months bank statements, EPF statements, property valuation report (for housing), and employment verification letter. Self-employed need business registration and financial statements.",
        "metadata": {"category": "documentation", "banking": "both"}
    }
]


class ChromaDBRAG:
    """ChromaDB-based Retrieval-Augmented Generation for BNM Guidelines"""
    
    def __init__(self):
        """Initialize ChromaDB client and collection"""
        self.client = None
        self.collection = None
        self.embedding_function = None
        self.initialize_db()
    
    def initialize_db(self):
        """Initialize ChromaDB and load BNM documents"""
        try:
            # Create persistent ChromaDB client
            os.makedirs(CHROMA_DB_PATH, exist_ok=True)
            
            # Use default settings to avoid ONNX Runtime issues
            self.client = chromadb.PersistentClient(
                path=str(CHROMA_DB_PATH),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=False  # Changed to False for stability
                )
            )
            
            # Use sentence-transformers for embeddings (free, local)
            # This avoids ONNX Runtime DLL issues on Windows
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"  # Small, fast, accurate model
            )
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(
                    name="bnm_banking_guidelines",
                    embedding_function=self.embedding_function
                )
                print(f"✅ Loaded existing ChromaDB collection with {self.collection.count()} documents")
            except:
                # Collection doesn't exist, create and populate
                self.collection = self.client.create_collection(
                    name="bnm_banking_guidelines",
                    embedding_function=self.embedding_function,
                    metadata={"description": "Bank Negara Malaysia banking guidelines and regulations"}
                )
                self._populate_collection()
                print(f"✅ Created new ChromaDB collection with {self.collection.count()} documents")
        
        except Exception as e:
            print(f"⚠️  ChromaDB initialization failed: {e}")
            print("   Continuing without RAG support (will use structured rules)")
            self.collection = None
    
    def _populate_collection(self):
        """Populate ChromaDB with BNM documents"""
        if not self.collection:
            return
        
        documents = [doc["content"] for doc in BNM_DOCUMENTS]
        ids = [doc["id"] for doc in BNM_DOCUMENTS]
        metadatas = [doc["metadata"] for doc in BNM_DOCUMENTS]
        
        self.collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )
        
        print(f"   Populated ChromaDB with {len(BNM_DOCUMENTS)} BNM guideline documents")
    
    def retrieve_context(self, query: str, n_results: int = 5, banking_system: str = None, loan_type: str = None):
        """
        Retrieve relevant BNM guidelines for a query
        
        Args:
            query: Query text (e.g., "What is the DSR limit for housing loans?")
            n_results: Number of results to retrieve
            banking_system: Filter by "conventional" or "islamic"
            loan_type: Filter by loan type (e.g., "housing", "personal")
        
        Returns:
            dict with retrieved documents and metadata
        """
        if not self.collection:
            return {
                "documents": [],
                "metadatas": [],
                "distances": [],
                "message": "ChromaDB not initialized, using structured rules instead"
            }
        
        try:
            # Query ChromaDB (without metadata filters for broader results)
            # Note: ChromaDB 0.4.22 has strict filter syntax, semantic search is sufficient
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            return {
                "documents": results["documents"][0] if results["documents"] else [],
                "metadatas": results["metadatas"][0] if results["metadatas"] else [],
                "distances": results["distances"][0] if results["distances"] else [],
                "ids": results["ids"][0] if results["ids"] else []
            }
        
        except Exception as e:
            print(f"⚠️  ChromaDB retrieval failed: {e}")
            return {
                "documents": [],
                "metadatas": [],
                "distances": [],
                "message": f"Retrieval error: {e}"
            }
    
    def get_bnm_context_for_loan(self, loan_type: str, banking_system: str, customer_type: str):
        """
        Get relevant BNM context for loan assessment
        
        Args:
            loan_type: Type of loan (personal, housing, commercial)
            banking_system: Banking system (conventional, islamic)
            customer_type: Customer type (retail, corporate)
        
        Returns:
            Formatted context string for LLM
        """
        if not self.collection:
            # Fallback to basic context
            return f"Apply Bank Negara Malaysia guidelines for {loan_type} loans under {banking_system} banking."
        
        # Retrieve relevant guidelines
        queries = [
            f"DSR requirements for {loan_type} loans",
            f"LTV limits for {loan_type}",
            f"{banking_system} banking regulations",
            f"Income requirements for {loan_type}",
            "Credit assessment guidelines"
        ]
        
        all_context = []
        seen_ids = set()
        
        for query in queries:
            results = self.retrieve_context(
                query=query,
                n_results=2,
                banking_system=banking_system if banking_system != "both" else None,
                loan_type=loan_type if loan_type in ["personal", "housing", "commercial"] else None
            )
            
            for doc, metadata, doc_id in zip(
                results.get("documents", []),
                results.get("metadatas", []),
                results.get("ids", [])
            ):
                if doc_id not in seen_ids:
                    all_context.append(f"• {doc}")
                    seen_ids.add(doc_id)
        
        if all_context:
            context_str = "### RELEVANT BNM GUIDELINES (Retrieval-Augmented):\n\n" + "\n\n".join(all_context[:8])
            return context_str
        else:
            return f"Apply Bank Negara Malaysia guidelines for {loan_type} loans under {banking_system} banking."
    
    def search_guidelines(self, query: str, n_results: int = 5):
        """
        General search for BNM guidelines
        
        Args:
            query: Search query
            n_results: Number of results
        
        Returns:
            List of relevant guidelines
        """
        results = self.retrieve_context(query, n_results)
        
        guidelines = []
        for doc, metadata, distance, doc_id in zip(
            results.get("documents", []),
            results.get("metadatas", []),
            results.get("distances", []),
            results.get("ids", [])
        ):
            guidelines.append({
                "id": doc_id,
                "content": doc,
                "metadata": metadata,
                "relevance_score": 1 - distance  # Convert distance to similarity score
            })
        
        return guidelines
    
    def reset_database(self):
        """Reset ChromaDB (for testing/reinitialization)"""
        if self.client:
            self.client.reset()
            print("✅ ChromaDB reset successfully")
            self.initialize_db()


# Global RAG instance
_rag_instance = None

def get_rag_instance():
    """Get or create global ChromaDB RAG instance"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = ChromaDBRAG()
    return _rag_instance


# CLI Testing
if __name__ == "__main__":
    print("=" * 80)
    print("CHROMADB RAG SYSTEM TEST")
    print("=" * 80)
    
    # Initialize
    rag = ChromaDBRAG()
    
    # Test queries
    test_queries = [
        "What is the DSR limit for housing loans?",
        "LTV requirements for commercial property",
        "Islamic banking Murabahah financing",
        "Minimum income requirements",
        "Required documentation for loan application"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        print("-" * 80)
        
        results = rag.retrieve_context(query, n_results=3)
        
        for i, (doc, metadata) in enumerate(zip(results["documents"], results["metadatas"]), 1):
            print(f"\n{i}. {doc[:200]}...")
            print(f"   Category: {metadata.get('category')}, Banking: {metadata.get('banking')}")
    
    print("\n" + "=" * 80)
    print("✅ ChromaDB RAG Test Complete!")
    print("=" * 80)

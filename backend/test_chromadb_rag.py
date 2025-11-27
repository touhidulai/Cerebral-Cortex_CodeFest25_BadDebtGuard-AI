"""
Test Script for ChromaDB RAG Integration
Verifies the complete RAG pipeline without running the full API
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_chromadb_installation():
    """Test 1: Verify ChromaDB and sentence-transformers are installed"""
    print("=" * 80)
    print("TEST 1: ChromaDB Package Installation")
    print("=" * 80)
    
    try:
        import chromadb
        print("✅ chromadb package imported successfully")
        print(f"   Version: {chromadb.__version__}")
    except ImportError as e:
        print(f"❌ chromadb import failed: {e}")
        print("   Install with: pip install chromadb==0.4.22")
        return False
    
    try:
        import sentence_transformers
        print("✅ sentence-transformers package imported successfully")
        print(f"   Version: {sentence_transformers.__version__}")
    except ImportError as e:
        print(f"❌ sentence-transformers import failed: {e}")
        print("   Install with: pip install sentence-transformers==2.2.2")
        return False
    
    print("\n✅ All required packages installed!")
    return True


def test_chromadb_initialization():
    """Test 2: Initialize ChromaDB and create collection"""
    print("\n" + "=" * 80)
    print("TEST 2: ChromaDB Initialization")
    print("=" * 80)
    
    try:
        from app.chromadb_rag import ChromaDBRAG
        
        print("Initializing ChromaDB RAG system...")
        rag = ChromaDBRAG()
        
        if rag.collection:
            doc_count = rag.collection.count()
            print(f"✅ ChromaDB initialized successfully")
            print(f"   Collection: {rag.collection.name}")
            print(f"   Documents: {doc_count}")
            try:
                settings = rag.client.get_settings()
                print(f"   Database Path: {settings.persist_directory if hasattr(settings, 'persist_directory') else 'In-memory'}")
            except:
                print(f"   Database: Persistent ChromaDB")
            return rag
        else:
            print("❌ ChromaDB collection not created")
            return None
    
    except Exception as e:
        print(f"❌ ChromaDB initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_rag_retrieval(rag):
    """Test 3: Test RAG retrieval for various queries"""
    print("\n" + "=" * 80)
    print("TEST 3: RAG Retrieval Testing")
    print("=" * 80)
    
    test_cases = [
        {
            "name": "Housing Loan (Conventional)",
            "loan_type": "housing",
            "banking_system": "conventional",
            "customer_type": "salaried"
        },
        {
            "name": "Personal Loan (Islamic)",
            "loan_type": "personal",
            "banking_system": "islamic",
            "customer_type": "self-employed"
        },
        {
            "name": "Commercial Property",
            "loan_type": "commercial",
            "banking_system": "conventional",
            "customer_type": "small-business"
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case['name']}")
        print("-" * 80)
        
        try:
            context = rag.get_bnm_context_for_loan(
                loan_type=test_case["loan_type"],
                banking_system=test_case["banking_system"],
                customer_type=test_case["customer_type"]
            )
            
            if context and len(context) > 100:
                print(f"✅ Retrieved {len(context)} characters of BNM context")
                
                # Show first 300 characters
                preview = context[:300] + "..." if len(context) > 300 else context
                print(f"\n   Preview:\n   {preview}\n")
            else:
                print(f"⚠️  Retrieved only {len(context)} characters (expected >100)")
                all_passed = False
        
        except Exception as e:
            print(f"❌ Retrieval failed: {e}")
            all_passed = False
    
    return all_passed


def test_semantic_search(rag):
    """Test 4: Test semantic search capabilities"""
    print("\n" + "=" * 80)
    print("TEST 4: Semantic Search Testing")
    print("=" * 80)
    
    test_queries = [
        "What is the maximum DSR for housing loans?",
        "LTV requirements for first-time homebuyers",
        "Islamic banking Murabahah financing rules",
        "Minimum income for loan approval",
        "Required documents for loan application"
    ]
    
    all_passed = True
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Query {i}: {query}")
        print("-" * 80)
        
        try:
            results = rag.retrieve_context(query, n_results=3)
            
            if results["documents"] and len(results["documents"]) > 0:
                print(f"✅ Found {len(results['documents'])} relevant documents")
                
                for j, (doc, metadata) in enumerate(zip(results["documents"], results["metadatas"]), 1):
                    print(f"\n   {j}. {doc[:150]}...")
                    print(f"      Category: {metadata.get('category')}, Banking: {metadata.get('banking')}")
            else:
                print(f"⚠️  No documents found for query")
                all_passed = False
        
        except Exception as e:
            print(f"❌ Search failed: {e}")
            all_passed = False
    
    return all_passed


def test_openai_integration():
    """Test 5: Verify openai_agent.py accepts rag_context parameter"""
    print("\n" + "=" * 80)
    print("TEST 5: OpenAI Agent RAG Integration")
    print("=" * 80)
    
    try:
        from app.openai_agent import analyze_with_openai
        import inspect
        
        # Check function signature
        sig = inspect.signature(analyze_with_openai)
        params = list(sig.parameters.keys())
        
        print(f"Function signature: {sig}")
        
        if "rag_context" in params:
            print("✅ openai_agent.py accepts 'rag_context' parameter")
            print(f"   Parameters: {params}")
            return True
        else:
            print("❌ openai_agent.py missing 'rag_context' parameter")
            print(f"   Current parameters: {params}")
            return False
    
    except Exception as e:
        print(f"❌ OpenAI agent check failed: {e}")
        return False


def test_main_integration():
    """Test 6: Verify main.py integrates ChromaDB RAG"""
    print("\n" + "=" * 80)
    print("TEST 6: Main Pipeline RAG Integration")
    print("=" * 80)
    
    try:
        with open("app/main.py", "r", encoding="utf-8") as f:
            main_content = f.read()
        
        checks = [
            ("chromadb_rag import", "from app.chromadb_rag import get_rag_instance"),
            ("RAG retrieval call", "rag.get_bnm_context_for_loan"),
            ("RAG context parameter", "rag_context=rag_context")
        ]
        
        all_passed = True
        
        for check_name, check_string in checks:
            if check_string in main_content:
                print(f"✅ {check_name} found in main.py")
            else:
                print(f"❌ {check_name} NOT found in main.py")
                all_passed = False
        
        return all_passed
    
    except Exception as e:
        print(f"❌ Main.py check failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "CHROMADB RAG INTEGRATION TEST" + " " * 29 + "║")
    print("╚" + "=" * 78 + "╝")
    
    results = {}
    
    # Test 1: Package Installation
    results["packages"] = test_chromadb_installation()
    
    if not results["packages"]:
        print("\n❌ CRITICAL: Install ChromaDB packages first!")
        print("   Run: pip install chromadb==0.4.22 sentence-transformers==2.2.2")
        return
    
    # Test 2: ChromaDB Initialization
    rag = test_chromadb_initialization()
    results["initialization"] = rag is not None
    
    if not rag:
        print("\n❌ CRITICAL: ChromaDB initialization failed!")
        return
    
    # Test 3: RAG Retrieval
    results["retrieval"] = test_rag_retrieval(rag)
    
    # Test 4: Semantic Search
    results["search"] = test_semantic_search(rag)
    
    # Test 5: OpenAI Integration
    results["openai"] = test_openai_integration()
    
    # Test 6: Main Integration
    results["main"] = test_main_integration()
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.upper():.<40} {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for p in results.values() if p)
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! ChromaDB RAG is fully integrated.")
        print("\nNext Steps:")
        print("1. Start backend server: uvicorn app.main:app --reload")
        print("2. Upload loan documents via frontend")
        print("3. Check logs for: 'Retrieving BNM guidelines from ChromaDB (RAG)...'")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Review errors above.")


if __name__ == "__main__":
    main()

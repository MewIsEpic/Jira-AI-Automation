"""
Requirements & Test Case Automation - Main Entry Point
Processes issues with RAG-enhanced requirements analysis and test case generation.
"""
import sys
from jira_client import get_issue, add_comment
from ai_analyzer import analyze_with_rag, generate_test_cases_with_rag
from rag.rag_system import RAGSystem

def process_issue(issue_key):
    """Process a Jira issue with AI analysis"""
    print(f"\n{'='*60}")
    print(f"Processing Jira Issue: {issue_key}")
    print(f"{'='*60}\n")
    
    # Get issue from Jira
    issue = get_issue(issue_key)
    if not issue:
        print(f"[ERROR] Failed to fetch issue {issue_key}")
        return False
    
    print(f"[OK] Found: {issue['summary']}")
    
    # Initialize RAG system
    print("\n[INFO] Loading RAG knowledge base...")
    rag = RAGSystem()
    
    if rag.collection.count() == 0:
        print("[WARNING] Knowledge base is empty!")
        print("   Run: python -m rag.rag_system setup")
        print("   Continuing without RAG context...\n")
    
    # Analyze with RAG (pass full issue object)
    print("[INFO] Analyzing requirements with AI + RAG...")
    analysis = analyze_with_rag(issue, rag)
    
    # Generate test cases with RAG (pass full issue object)
    print("[INFO] Generating test cases with AI + RAG...")
    test_cases = generate_test_cases_with_rag(issue, rag)
    
    # Create comment
    comment = f"""*AI Requirements Analysis (RAG-Enhanced)*

{analysis}

---

*AI-Generated Test Cases (RAG-Enhanced)*

{test_cases}

---
*Generated automatically by CI/CD pipeline*
*Uses knowledge from Confluence and Jira for context-aware analysis*
"""
    
    # Add to Jira
    if add_comment(issue_key, comment):
        print(f"\n[OK] Analysis added to {issue_key}")
        return True
    else:
        print(f"\n[ERROR] Failed to add comment to {issue_key}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py ISSUE-KEY")
        print("Example: python main.py SE-1")
        sys.exit(1)
    
    success = process_issue(sys.argv[1])
    sys.exit(0 if success else 1)


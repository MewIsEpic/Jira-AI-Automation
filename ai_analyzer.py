"""
AI Analyzer - Requirements Analysis & Test Case Generation
Uses RAG for context-aware AI responses
"""
import ollama

# Try to find an available model, fallback to llama3
def get_available_model():
    """Get an available Ollama model, preferring smaller ones"""
    try:
        models = ollama.list()
        if models and hasattr(models, 'models') and models.models:
            # Prefer smaller models first
            for model in models.models:
                model_name = model.name
                if 'tinyllama' in model_name or 'llama3.2' in model_name or 'llama3.1' in model_name:
                    return model_name.split(':')[0]
            # Use first available model
            if models.models:
                return models.models[0].name.split(':')[0]
    except Exception as e:
        print(f"[INFO] Could not auto-detect model: {e}")
    # Fallback - use llama3 which is available
    return "llama3"

OLLAMA_MODEL = get_available_model()
print(f"[INFO] Using Ollama model: {OLLAMA_MODEL}")

def analyze_with_rag(issue, rag_system):
    """Analyze requirements using RAG-enhanced AI"""
    # Extract issue information
    issue_key = issue.get('key', '')
    issue_summary = issue.get('summary', '')
    issue_type = issue.get('type', '')
    issue_status = issue.get('status', '')
    description = issue.get('description') or issue.get('summary', '')
    
    # Get relevant context from RAG
    context = rag_system.get_context(description, top_k=3)
    
    prompt = f"""Analyze this system engineering requirement using the provided context.

Issue Information:
- Issue Key: {issue_key}
- Summary: {issue_summary}
- Type: {issue_type}
- Status: {issue_status}

{context}

Requirement Description:
{description}

Extract and format:
1. Functional Requirements
2. Non-Functional Requirements
3. Technical Specifications
4. Acceptance Criteria

Provide a clear, structured analysis."""
    
    # Try with primary model, fallback to smaller model if memory error
    models_to_try = [OLLAMA_MODEL, "llama3.2:1b", "tinyllama"]
    last_error = None
    
    for i, model in enumerate(models_to_try):
        try:
            print(f"[INFO] Trying model: {model}...")
            response = ollama.chat(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a system engineering expert. Use the provided context to analyze requirements."
                    },
                    {"role": "user", "content": prompt}
                ]
            )
            content = response.get('message', {}).get('content', '')
            if not content:
                raise ValueError("Empty response from model")
            if model != OLLAMA_MODEL:
                print(f"[INFO] Used fallback model: {model}")
            print(f"[OK] Analysis completed successfully")
            return content
        except Exception as e:
            last_error = e
            error_msg = str(e).lower()
            is_memory_error = "memory" in error_msg
            is_last_model = (i == len(models_to_try) - 1)
            
            if is_memory_error:
                print(f"[WARNING] Model {model} failed (memory issue), trying next model...")
            else:
                print(f"[WARNING] Model {model} failed: {e}, trying next model...")
            
            # If this is the last model, we've tried everything
            if is_last_model:
                print(f"[ERROR] All models failed. Last error: {e}")
                return f"Analysis unavailable. Error: {str(e)[:200]}"
    
    return f"Analysis unavailable. Error: {str(last_error)[:200] if last_error else 'Unknown error'}"

def generate_test_cases_with_rag(issue, rag_system):
    """Generate test cases using RAG-enhanced AI"""
    # Extract issue information
    issue_key = issue.get('key', '')
    issue_summary = issue.get('summary', '')
    issue_type = issue.get('type', '')
    issue_status = issue.get('status', '')
    description = issue.get('description') or issue.get('summary', '')
    
    # Get relevant context from RAG
    context = rag_system.get_context(description, top_k=3)
    
    prompt = f"""Generate test cases for this requirement using the provided context.

Issue Information:
- Issue Key: {issue_key}
- Summary: {issue_summary}
- Type: {issue_type}
- Status: {issue_status}

{context}

Requirement:
{description}

For each test case provide:
- Test ID (e.g., TC-001)
- Test Name
- Test Type (Unit/Integration/E2E)
- Priority (High/Medium/Low)
- Test Steps
- Expected Result

Generate comprehensive test cases covering happy path, edge cases, and error handling."""
    
    # Try with primary model, fallback to smaller model if memory error
    models_to_try = [OLLAMA_MODEL, "llama3.2:1b", "tinyllama"]
    last_error = None
    
    for i, model in enumerate(models_to_try):
        try:
            print(f"[INFO] Trying model: {model}...")
            response = ollama.chat(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a test engineering expert. Use the provided context to generate test cases."
                    },
                    {"role": "user", "content": prompt}
                ]
            )
            content = response.get('message', {}).get('content', '')
            if not content:
                raise ValueError("Empty response from model")
            if model != OLLAMA_MODEL:
                print(f"[INFO] Used fallback model: {model}")
            print(f"[OK] Test cases generated successfully")
            return content
        except Exception as e:
            last_error = e
            error_msg = str(e).lower()
            is_memory_error = "memory" in error_msg
            is_last_model = (i == len(models_to_try) - 1)
            
            if is_memory_error:
                print(f"[WARNING] Model {model} failed (memory issue), trying next model...")
            else:
                print(f"[WARNING] Model {model} failed: {e}, trying next model...")
            
            # If this is the last model, we've tried everything
            if is_last_model:
                print(f"[ERROR] All models failed. Last error: {e}")
                return f"Test cases unavailable. Error: {str(e)[:200]}"
    
    return f"Test cases unavailable. Error: {str(last_error)[:200] if last_error else 'Unknown error'}"


"""
RAG System
Handles both retrieval and knowledge loading
"""
import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from bs4 import BeautifulSoup
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from jira_client import extract_project_knowledge
from confluence_client import get_space_pages

VECTOR_DB_DIR = "rag/vector_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

class RAGSystem:
    """RAG system with ChromaDB"""
    
    def __init__(self):
        """Initialize RAG system"""
        print("Initializing RAG system...")
        
        # Load embedding model
        try:
            self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
            print(f"[OK] Loaded embedding model: {EMBEDDING_MODEL}")
        except Exception as e:
            print(f"[ERROR] Failed to load embedding model: {e}")
            self.embedding_model = None
            return
        
        # Initialize ChromaDB
        try:
            os.makedirs(VECTOR_DB_DIR, exist_ok=True)
            self.client = chromadb.PersistentClient(
                path=VECTOR_DB_DIR,
                settings=Settings(anonymized_telemetry=False)
            )
            self.collection = self.client.get_or_create_collection(
                name="knowledge_base",
                metadata={"description": "System Engineering Knowledge Base"}
            )
            print(f"[OK] Vector database ready ({self.collection.count()} documents)")
        except Exception as e:
            print(f"[ERROR] Failed to initialize vector database: {e}")
            self.collection = None
    
    def get_context(self, query, top_k=3):
        """Get relevant context for a query"""
        if not self.collection or not self.embedding_model or self.collection.count() == 0:
            return ""
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search vector database
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Format context
            contexts = []
            if results['documents'] and len(results['documents'][0]) > 0:
                for doc in results['documents'][0]:
                    contexts.append(doc)
            
            if contexts:
                context_text = "\n\n".join([
                    f"--- Context {i+1} ---\n{ctx}"
                    for i, ctx in enumerate(contexts)
                ])
                return f"""Relevant Knowledge from Confluence and Jira:

{context_text}

---
Use this context to provide accurate analysis.
"""
            return ""
        except Exception as e:
            print(f"RAG retrieval error: {e}")
            return ""
    
    def load_knowledge(self, confluence_space=None, jira_project="SE"):
        """Load knowledge from Confluence and Jira"""
        if not self.embedding_model or not self.collection:
            print("[ERROR] RAG system not initialized")
            return
        
        all_documents = []
        all_metadatas = []
        all_ids = []
        
        # Load from Confluence
        if confluence_space:
            print(f"\n[INFO] Loading from Confluence space: {confluence_space}")
            pages = get_space_pages(confluence_space)
            
            for page in pages:
                content = self._clean_html(page['content'])
                if len(content.strip()) < 50:
                    continue
                
                # Split into chunks
                chunks = self._split_chunks(content, chunk_size=500)
                for i, chunk in enumerate(chunks):
                    all_documents.append(chunk)
                    all_metadatas.append({
                        'source': 'confluence',
                        'page_id': page['id'],
                        'title': page['title'],
                        'url': page['url']
                    })
                    all_ids.append(f"confluence_{page['id']}_{i}")
        
        # Load from Jira
        print(f"\n[INFO] Loading from Jira project: {jira_project}")
        jira_docs = extract_project_knowledge(jira_project, max_issues=30)
        
        for doc in jira_docs:
            content = doc['content']
            if len(content.strip()) < 50:
                continue
            
            chunks = self._split_chunks(content, chunk_size=500)
            for i, chunk in enumerate(chunks):
                all_documents.append(chunk)
                all_metadatas.append({
                    'source': 'jira',
                    'doc_id': doc['id'],
                    'title': doc['title'],
                    'url': doc.get('url', '')
                })
                all_ids.append(f"jira_{doc['id']}_{i}")
        
        # Add to vector database
        if all_documents:
            print(f"\n[INFO] Adding {len(all_documents)} chunks to vector database...")
            embeddings = self.embedding_model.encode(all_documents).tolist()
            self.collection.add(
                ids=all_ids,
                embeddings=embeddings,
                documents=all_documents,
                metadatas=all_metadatas
            )
            print(f"[OK] Knowledge base updated! Total documents: {self.collection.count()}")
        else:
            print("[WARNING] No documents to add")
    
    def _clean_html(self, html_content):
        """Clean HTML content"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup.get_text(separator=' ', strip=True)
        except:
            import re
            return re.sub(r'<[^>]+>', '', html_content).strip()
    
    def _split_chunks(self, text, chunk_size=500, overlap=50):
        """Split text into chunks"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            word_size = len(word) + 1
            if current_size + word_size > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                # Keep overlap
                overlap_words = current_chunk[-overlap//10:] if len(current_chunk) > overlap//10 else current_chunk
                current_chunk = overlap_words + [word]
                current_size = sum(len(w) + 1 for w in current_chunk)
            else:
                current_chunk.append(word)
                current_size += word_size
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks

# Setup function for command-line use
def setup():
    """Setup knowledge base from Confluence and Jira"""
    import os
    
    print("="*60)
    print("Setting Up RAG Knowledge Base")
    print("="*60)
    
    rag = RAGSystem()
    
    if not rag.embedding_model or not rag.collection:
        print("[ERROR] Failed to initialize RAG system")
        return
    
    confluence_space = os.getenv("CONFLUENCE_SPACE_KEY", "SEAD")
    jira_project = os.getenv("JIRA_PROJECT_KEY", "SE")
    
    print(f"\nConfiguration:")
    print(f"  Confluence Space: {confluence_space}")
    print(f"  Jira Project: {jira_project}")
    
    rag.load_knowledge(confluence_space=confluence_space, jira_project=jira_project)
    
    print("\n" + "="*60)
    print("[OK] Setup complete!")
    print("="*60)

if __name__ == "__main__":
    setup()


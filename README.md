# Requirements & Test Case Automation

AI-powered **requirements analysis** and **test case generation** using RAG (Retrieval Augmented Generation). Pulls context from your knowledge base (Confluence, Jira, etc.), analyzes requirements, and generates test cases automatically.

## Features

- RAG-enhanced AI analysis using ChromaDB
- Knowledge base integration (Confluence, Jira, and more)
- Automated requirements analysis
- Automated test case generation
- CI/CD ready with GitHub Actions

## Project Structure

```
.
├── main.py                    # Entry point
├── config.py                  # Configuration
├── jira_client.py            # Jira operations
├── confluence_client.py       # Confluence operations
├── ai_analyzer.py            # AI analysis functions
├── rag/
│   ├── rag_system.py         # RAG system (ChromaDB)
│   └── vector_db/            # Vector database (auto-generated)
└── requirements.txt
```

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Install Ollama:**
```bash
# Download from https://ollama.ai
ollama pull llama3
```

3. **Create `.env` file:**
```env
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-token
CONFLUENCE_SPACE_KEY=SEAD
JIRA_PROJECT_KEY=SE
```

4. **Setup knowledge base (first time):**
```bash
python -m rag.rag_system setup
```

This loads knowledge from Confluence and Jira into the vector database.

## Usage

Process a Jira issue:
```bash
python main.py SE-1
```

This will:
1. Fetch the issue from Jira
2. Use RAG to retrieve relevant context
3. Analyze requirements with AI
4. Generate test cases
5. Add results as a comment

## CI/CD

See `.github/workflows/jira_ai_pipeline.yml` for the Requirements & Test Case Pipeline workflow.

## Key Components

### RAG System
- Uses ChromaDB for vector storage
- Sentence transformers for embeddings
- Retrieves relevant context from Confluence and Jira

### AI Analysis
- Requirements analysis with context
- Test case generation with context
- Uses Ollama (llama3 model)

### Integration
- Jira REST API for issue management
- Confluence REST API for documentation
- GitHub Actions for CI/CD automation


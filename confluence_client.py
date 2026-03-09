"""
Confluence Client 
Fetches documents from Confluence for RAG
"""
from config import JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN
import requests
import base64

# Confluence URL (same as Jira URL)
CONFLUENCE_URL = JIRA_URL.replace("/jira", "") if "/jira" in JIRA_URL else JIRA_URL

def get_headers():
    """Get authentication headers"""
    auth = base64.b64encode(f"{JIRA_EMAIL}:{JIRA_API_TOKEN}".encode()).decode()
    return {
        'Authorization': f'Basic {auth}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

def get_space_pages(space_key, limit=50):
    """Get pages from Confluence space"""
    headers = get_headers()
    pages = []
    
    try:
        url = f"{CONFLUENCE_URL}/wiki/rest/api/content"
        params = {
            'spaceKey': space_key,
            'limit': limit,
            'expand': 'body.storage,body.view'
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        for page in response.json().get('results', []):
            body = page.get('body', {})
            content = body.get('storage', {}).get('value', '') or body.get('view', {}).get('value', '')
            
            pages.append({
                'id': page.get('id'),
                'title': page.get('title'),
                'content': content,
                'url': f"{CONFLUENCE_URL}/wiki{page.get('_links', {}).get('webui', '')}"
            })
        
        print(f"[OK] Fetched {len(pages)} pages from Confluence space '{space_key}'")
        return pages
        
    except Exception as e:
        print(f"[WARNING] Confluence error: {e}")
        return []


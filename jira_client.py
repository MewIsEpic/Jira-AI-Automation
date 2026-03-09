"""
Jira Client
Handles Jira API operations
"""
from jira import JIRA
from config import JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN

def get_client():
    """Get Jira client"""
    return JIRA(
        server=JIRA_URL,
        basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN)
    )

def get_issue(issue_key):
    """Get issue details"""
    try:
        jira = get_client()
        issue = jira.issue(issue_key)
        return {
            'key': issue.key,
            'summary': issue.fields.summary,
            'description': issue.fields.description or '',
            'status': issue.fields.status.name,
            'type': issue.fields.issuetype.name
        }
    except Exception as e:
        print(f"Error: {e}")
        return None

def add_comment(issue_key, comment):
    """Add comment to issue"""
    try:
        jira = get_client()
        # Jira comment limit is 32,767 characters
        if len(comment) > 30000:
            comment = comment[:30000] + "\n\n[Truncated due to length]"
        jira.add_comment(issue_key, comment)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def extract_project_knowledge(project_key, max_issues=30):
    """Extract knowledge from Jira project for RAG"""
    jira = get_client()
    knowledge = []
    
    try:
        # Get issues
        jql = f'project = {project_key} ORDER BY created DESC'
        issues = jira.search_issues(jql, maxResults=max_issues)
        
        for issue in issues:
            # Issue document
            doc = {
                'id': issue.key,
                'title': issue.fields.summary,
                'content': f"""Issue: {issue.key} - {issue.fields.summary}
Type: {issue.fields.issuetype.name}
Status: {issue.fields.status.name}

Description:
{issue.fields.description or 'No description'}

Acceptance Criteria:
{getattr(issue.fields, 'customfield_10026', '') or 'No acceptance criteria'}
""",
                'source': 'jira_issue',
                'url': issue.permalink()
            }
            knowledge.append(doc)
            
            # Comments
            for comment in jira.comments(issue):
                comment_doc = {
                    'id': f"{issue.key}-comment-{comment.id}",
                    'title': f"Comment on {issue.key}",
                    'content': f"Issue: {issue.key}\nComment by: {comment.author.displayName}\n\n{comment.body}",
                    'source': 'jira_comment',
                    'url': issue.permalink()
                }
                knowledge.append(comment_doc)
        
        print(f"[OK] Extracted {len(knowledge)} documents from Jira")
        return knowledge
        
    except Exception as e:
        print(f"Error extracting Jira knowledge: {e}")
        return []


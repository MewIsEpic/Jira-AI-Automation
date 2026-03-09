"""
Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

JIRA_URL = os.getenv("JIRA_URL", "")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")

if not all([JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN]):
    raise ValueError(
        "Missing required configuration. Please set in .env file:\n"
        "  - JIRA_URL\n"
        "  - JIRA_EMAIL\n"
        "  - JIRA_API_TOKEN"
    )


#!/usr/bin/env python3
"""
GitHub Issues Integration for AutoSort Analytics

This script demonstrates how to create GitHub issues for unhandled file types
using the GitHub API. This provides a free, public way to collect user feedback.

Requirements:
- GitHub repository
- GitHub Personal Access Token
- requests library

Setup:
1. Create a GitHub repository for AutoSort issues
2. Generate a Personal Access Token with 'repo' permissions
3. Set GITHUB_TOKEN environment variable
4. Update REPO_OWNER and REPO_NAME below
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
REPO_OWNER = "GXboy12345"  # Your GitHub username
REPO_NAME = "autosort-scripts"  # Your repository name
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# GitHub API configuration
GITHUB_API_BASE = "https://api.github.com"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "AutoSort-Analytics/2.3"
}


class GitHubIssuesReporter:
    """Reports unhandled file types to GitHub Issues."""
    
    def __init__(self):
        if not GITHUB_TOKEN:
            logger.warning("GITHUB_TOKEN not set - GitHub reporting disabled")
            self.enabled = False
        else:
            self.enabled = True
    
    def report_unhandled_file_type(self, extension: str, context: str = "unknown", 
                                 version: str = "2.3") -> Optional[str]:
        """
        Create a GitHub issue for an unhandled file type.
        
        Args:
            extension: File extension (e.g., '.xyz')
            context: File context (e.g., 'image', 'document')
            version: AutoSort version
            
        Returns:
            Issue URL if successful, None otherwise
        """
        if not self.enabled:
            return None
        
        # Check if issue already exists
        existing_issue = self._find_existing_issue(extension)
        if existing_issue:
            logger.info(f"Issue already exists for {extension}: {existing_issue['html_url']}")
            return existing_issue["html_url"]
        
        # Create new issue
        issue_data = self._create_issue_data(extension, context, version)
        
        try:
            response = requests.post(
                f"{GITHUB_API_BASE}/repos/{REPO_OWNER}/{REPO_NAME}/issues",
                headers=HEADERS,
                json=issue_data,
                timeout=10
            )
            
            if response.status_code == 201:
                issue = response.json()
                logger.info(f"Created issue for {extension}: {issue['html_url']}")
                return issue["html_url"]
            else:
                logger.error(f"Failed to create issue: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating GitHub issue: {e}")
            return None
    
    def _find_existing_issue(self, extension: str) -> Optional[Dict]:
        """Find existing issue for the given extension."""
        try:
            # Search for issues with the extension in the title
            search_query = f"repo:{REPO_OWNER}/{REPO_NAME} is:issue is:open {extension}"
            
            response = requests.get(
                f"{GITHUB_API_BASE}/search/issues",
                headers=HEADERS,
                params={"q": search_query},
                timeout=10
            )
            
            if response.status_code == 200:
                results = response.json()
                issues = results.get("items", [])
                
                # Look for exact match in title
                for issue in issues:
                    if extension.lower() in issue["title"].lower():
                        return issue
                        
        except Exception as e:
            logger.error(f"Error searching for existing issues: {e}")
        
        return None
    
    def _create_issue_data(self, extension: str, context: str, version: str) -> Dict:
        """Create issue data for GitHub API."""
        title = f"Add support for {extension} files"
        
        body = f"""## File Type Support Request

**Extension:** `{extension}`
**Context:** {context}
**AutoSort Version:** {version}
**Reported:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}

### Description
This file extension was encountered by AutoSort but couldn't be categorized. Please consider adding support for this file type.

### Suggested Category
Based on the context (`{context}`), this file type might belong in one of these categories:
- Images (if image-related)
- Documents (if document-related)
- Code (if code-related)
- Archives (if archive-related)
- Or create a new category if needed

### Additional Information
- This is an automated report from AutoSort users
- No personal information or file content is included
- The extension was encountered in a `{context}` context

---
*This issue was automatically generated by AutoSort Analytics*
"""
        
        labels = [
            "enhancement",
            "file-type-support",
            f"context-{context}",
            f"version-{version}"
        ]
        
        return {
            "title": title,
            "body": body,
            "labels": labels
        }
    
    def get_analytics_summary(self) -> Dict:
        """Get summary of all file type support issues."""
        try:
            # Get all issues with file-type-support label
            response = requests.get(
                f"{GITHUB_API_BASE}/repos/{REPO_OWNER}/{REPO_NAME}/issues",
                headers=HEADERS,
                params={
                    "labels": "file-type-support",
                    "state": "all",
                    "per_page": 100
                },
                timeout=10
            )
            
            if response.status_code == 200:
                issues = response.json()
                
                # Analyze issues
                extensions = []
                contexts = []
                versions = []
                open_issues = 0
                closed_issues = 0
                
                for issue in issues:
                    # Extract extension from title
                    title = issue["title"]
                    if "Add support for" in title:
                        ext_start = title.find("Add support for") + len("Add support for")
                        ext_end = title.find("files", ext_start)
                        if ext_end > ext_start:
                            extension = title[ext_start:ext_end].strip()
                            extensions.append(extension)
                    
                    # Extract context from labels
                    for label in issue["labels"]:
                        if label["name"].startswith("context-"):
                            contexts.append(label["name"][8:])
                        elif label["name"].startswith("version-"):
                            versions.append(label["name"][8:])
                    
                    # Count open/closed
                    if issue["state"] == "open":
                        open_issues += 1
                    else:
                        closed_issues += 1
                
                return {
                    "total_issues": len(issues),
                    "open_issues": open_issues,
                    "closed_issues": closed_issues,
                    "unique_extensions": len(set(extensions)),
                    "top_extensions": list(set(extensions))[:10],
                    "context_breakdown": dict(Counter(contexts)),
                    "version_breakdown": dict(Counter(versions))
                }
            else:
                logger.error(f"Failed to get issues: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting analytics summary: {e}")
            return {}


def main():
    """Test the GitHub Issues reporter."""
    reporter = GitHubIssuesReporter()
    
    if not reporter.enabled:
        print("GitHub reporting disabled - set GITHUB_TOKEN environment variable")
        return 1
    
    # Test reporting
    test_extensions = [".xyz", ".custom", ".newformat"]
    
    print("Testing GitHub Issues reporter...")
    for ext in test_extensions:
        url = reporter.report_unhandled_file_type(ext, "unknown", "2.3")
        if url:
            print(f"✅ Reported {ext}: {url}")
        else:
            print(f"❌ Failed to report {ext}")
    
    # Get summary
    print("\nAnalytics Summary:")
    summary = reporter.get_analytics_summary()
    if summary:
        print(f"Total Issues: {summary.get('total_issues', 0)}")
        print(f"Open Issues: {summary.get('open_issues', 0)}")
        print(f"Closed Issues: {summary.get('closed_issues', 0)}")
        print(f"Unique Extensions: {summary.get('unique_extensions', 0)}")
    else:
        print("Failed to get summary")
    
    return 0


if __name__ == "__main__":
    exit(main())

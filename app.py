#!/usr/bin/env python3
"""
Presto: GitHub PR Comment Workflow Tool

This script helps fetch and analyze comments from GitHub PRs, then assists with generating responses.
"""

def display_bootstrap_prompt():
    """Display the comprehensive workflow documentation as a bootstrap prompt"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    PRESTO: GitHub PR Comment Workflow Tool                  ║
║                         For AI Agents & Code Assistants                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎯 PURPOSE: Systematically handle PR review comments with intelligent organization,
           contextual responses, and automated posting.

═══════════════════════════════════════════════════════════════════════════════
🔄 CORE WORKFLOW - 6 STEPS WITH COMMANDS
═══════════════════════════════════════════════════════════════════════════════

STEP 1: 📊 ANALYZE & ORGANIZE THREADS
┌─────────────────────────────────────────────────────────────────────────────┐
│ COMMAND: presto analyze --repo OWNER/REPO --pr PR_NUMBER                    │
└─────────────────────────────────────────────────────────────────────────────┘
• Fetches all PR comments (general + inline code comments)
• Groups into conversation threads with reply relationships
• Creates session directory: pr_123_review_YYYYMMDD_HHMMSS/
• Applies intelligent skip logic (resolved threads, last commenter detection)
• Generates thread files: thread_01_author_topic.md, thread_02_...
• Files marked [NEEDS RESPONSE] require attention, SKIP_* files are filtered out

STEP 2: 🔍 SEARCH & EXPLORE (Optional)
┌─────────────────────────────────────────────────────────────────────────────┐
│ COMMAND: presto search --repo OWNER/REPO --pr PR_NUMBER --query "text"      │
└─────────────────────────────────────────────────────────────────────────────┘
• Find specific discussions, concerns, or topics
• Locate comment IDs for direct replies
• Understand comment context and relationships

STEP 3: 📚 CONTEXTUAL ANALYSIS (Agent Task)
┌─────────────────────────────────────────────────────────────────────────────┐
│ AGENT ACTION: Process each non-skipped thread systematically                │
└─────────────────────────────────────────────────────────────────────────────┘
• Go through EACH thread file marked [NEEDS RESPONSE] ONE AT A TIME
• For each thread, determine what action is needed (if any)
• Search and read the codebase extensively for relevant files, functions, classes, patterns
• Read source code, tests, documentation, config files thoroughly
• Build comprehensive understanding before drafting any response

STEP 4: ✍️ DRAFT RESPONSES
┌─────────────────────────────────────────────────────────────────────────────┐
│ COMMAND: presto append --thread N --content "response text"                 │
│ COMMAND: presto append --session-dir SESSION_DIR --thread N --content "..." │
└─────────────────────────────────────────────────────────────────────────────┘
• Draft thoughtful, comprehensive responses based on codebase analysis
• Include code examples, explanations, solutions from actual repository code
• CRITICAL: Base all responses on actual code in the repository.  If you dont feel you have enough context, ask the user or search the codebase again.          
• Responses saved as DRAFT RESPONSE sections in thread files
• Multiple drafts can be appended to same thread
• IMPORTANT: You or the user can edit responses directly in thread files before posting.

STEP 5: 🛠️ IMPLEMENT CHANGES (If Needed)
┌─────────────────────────────────────────────────────────────────────────────┐
│ AGENT ACTION: Make code changes, create files, update documentation         │
└─────────────────────────────────────────────────────────────────────────────┘
• Implement suggested fixes or improvements
• Create/modify files as discussed in responses
• Follow established code patterns and best practices
• Commit changes with descriptive messages

STEP 6: 📤 POST RESPONSES
┌─────────────────────────────────────────────────────────────────────────────┐
│ COMMAND: presto post N                    # Post specific thread            │
│ COMMAND: presto post --all               # Post all draft responses         │
│ COMMAND: presto post --dry-run           # Preview what would be posted     │
└─────────────────────────────────────────┘
• Reviews draft responses from thread files
• Posts to GitHub with double-post protection
• Tracks posted responses to prevent duplicates

═══════════════════════════════════════════════════════════════════════════════
🤖 AI AGENT QUICK REFERENCE
═══════════════════════════════════════════════════════════════════════════════

TYPICAL AGENT WORKFLOW:
1. presto analyze --repo owner/repo --pr 123
2. Read session_summary.md for overview
3. Process EACH thread_XX_*.md file marked [NEEDS RESPONSE] ONE BY ONE
4. For each thread:
   - Read thread content and understand the specific discussion/concern
   - Determine if action is needed (some threads may need no response)
   - Search codebase extensively for relevant context (files, functions, patterns)
   - Read actual source code, tests, docs to understand current implementation
   - Draft response based on real codebase evidence: presto append --thread N --content "..."
   - Remember: You can edit the response directly in the thread file if needed
5. presto post --all (or post individually with --dry-run first)

COMMON COMMANDS:
• presto analyze --repo owner/repo --pr 123      # Start workflow
• presto search --repo owner/repo --pr 123 --query "validation"  # Find topics
• presto append --thread 1 --content "response"  # Draft response
• presto post --dry-run                          # Preview posts
• presto post --all                              # Post all drafts
• presto skip 1                                  # Mark thread as skipped
• presto cleanup                                 # Remove session files

SESSION MANAGEMENT:
• Session directories auto-detected when commands run from project root
• Use --session-dir to specify exact session when multiple exist
• Thread files contain all metadata: IDs, authors, timestamps, file paths
• KEY PRINCIPLE: Always investigate the actual codebase thoroughly before responding

ESCAPE SEQUENCES:
• When using presto append with backticks in content, escape them properly
• For complex responses, consider using file input or multiple append calls

═══════════════════════════════════════════════════════════════════════════════
📋 COMMAND REFERENCE
═══════════════════════════════════════════════════════════════════════════════

presto analyze --repo OWNER/REPO --pr NUMBER [--save] [--output file.md]
presto search --repo OWNER/REPO --pr NUMBER --query "search text"
presto reply --repo OWNER/REPO --pr NUMBER --comment-id ID --message "text"
presto append [--session-dir DIR] --thread N --content "text" [--author "name"]
presto post [N] [--session-dir DIR] [--all] [--dry-run] [--yes]
presto skip [N] [--session-dir DIR] [--unmark] [--list]
presto cleanup [--session-dir DIR] [--force]
presto --help                    # Show all available commands

═══════════════════════════════════════════════════════════════════════════════

🚀 START HERE: presto analyze --repo OWNER/REPO --pr PR_NUMBER

This creates your session directory and organized thread files.
Focus on files marked [NEEDS RESPONSE] and ignore SKIP_* prefixed files.
""")


import json
import subprocess
import sys
import argparse
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

class PRCommentWorkflow:
    def __init__(self, repo_owner: str, repo_name: str):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.repo_full_name = f"{repo_owner}/{repo_name}"
        self.current_user = self._get_current_github_user()
    
    def _get_current_github_user(self) -> str:
        """Get the current GitHub user from gh CLI"""
        try:
            result = subprocess.run(['gh', 'api', 'user'], capture_output=True, text=True, check=True)
            user_data = json.loads(result.stdout)
            username = user_data.get('login', 'unknown')
            print(f"🔍 Current GitHub user: {username}")
            return username
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            print(f"⚠️  Could not determine current GitHub user: {e}")
            return 'unknown'
    
    def _should_skip_thread(self, thread_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if a thread should be skipped based on skip criteria
        Returns dict with skip decision and reason
        """
        main_comment = thread_data['main']
        replies = thread_data.get('replies', [])
        
        # Check if thread is resolved/closed
        if self._is_thread_resolved(thread_data):
            return {
                'skip': True,
                'reason': 'Thread is marked as resolved/closed',
                'skip_type': 'resolved'
            }
        
        # Check if current user was the last person to comment
        if self._is_user_last_commenter(thread_data):
            return {
                'skip': True, 
                'reason': f'Current user ({self.current_user}) was the last to comment',
                'skip_type': 'last_commenter'
            }
        
        return {
            'skip': False,
            'reason': 'Thread requires response',
            'skip_type': None
        }
    
    def _is_thread_resolved(self, thread_data: Dict[str, Any]) -> bool:
        """Check if thread appears to be resolved/closed"""
        main_comment = thread_data['main']
        replies = thread_data.get('replies', [])
        all_comments = [main_comment] + replies
        
        # Check for resolution keywords in any comment
        resolution_keywords = [
            'resolved', 'fixed', 'closed', 'done', 'completed',
            'merged', 'addressed', 'solved', 'finished'
        ]
        
        for comment in all_comments:
            body = comment.get('body', '').lower()
            # Look for explicit resolution statements
            if any(keyword in body for keyword in resolution_keywords):
                if any(phrase in body for phrase in [
                    'this is resolved', 'marking as resolved', 'resolved in',
                    'fixed in', 'closed by', 'done in', 'completed in'
                ]):
                    return True
        
        return False
    
    def _is_user_last_commenter(self, thread_data: Dict[str, Any]) -> bool:
        """Check if current user was the last person to comment in thread"""
        if self.current_user == 'unknown':
            return False
            
        main_comment = thread_data['main']
        replies = thread_data.get('replies', [])
        
        # If no replies, check if user made the main comment
        if not replies:
            main_author = main_comment.get('user', {}).get('login', main_comment.get('author', {}).get('login', ''))
            return main_author == self.current_user
        
        # Sort replies by timestamp to find the most recent
        sorted_replies = sorted(replies, key=lambda x: x.get('created_at', ''))
        last_reply = sorted_replies[-1]
        last_author = last_reply.get('user', {}).get('login', '')
        
        return last_author == self.current_user
    
    def fetch_pr_comments(self, pr_number: int) -> Dict[str, Any]:
        """Fetch PR details and comments using gh CLI"""
        try:
            # Get PR details and general comments
            pr_cmd = [
                "gh", "pr", "view", str(pr_number),
                "--repo", self.repo_full_name,
                "--json", "title,author,body,createdAt,state,comments"
            ]
            
            result = subprocess.run(pr_cmd, capture_output=True, text=True, check=True)
            pr_data = json.loads(result.stdout)
            
            # Get review comments (inline code comments)  
            review_cmd = [
                "gh", "api", f"repos/{self.repo_full_name}/pulls/{pr_number}/comments", "--paginate"
            ]
            
            review_result = subprocess.run(review_cmd, capture_output=True, text=True, check=True)
            review_comments = json.loads(review_result.stdout)
            
            return {
                "pr_number": pr_number,
                "title": pr_data.get("title", ""),
                "author": pr_data.get("author", {}).get("login", ""),
                "body": pr_data.get("body", ""),
                "created_at": pr_data.get("createdAt", ""),
                "state": pr_data.get("state", ""),
                "comments": pr_data.get("comments", []),
                "review_comments": review_comments
            }
            
        except subprocess.CalledProcessError as e:
            print(f"Error fetching PR data: {e.stderr}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return None
    
    def find_comment_by_text(self, pr_data: Dict[str, Any], search_text: str) -> List[Dict[str, Any]]:
        """Find comments containing specific text"""
        matches = []
        
        # Search general comments
        for comment in pr_data.get('comments', []):
            if search_text.lower() in comment.get('body', '').lower():
                matches.append({
                    'type': 'general',
                    'id': comment.get('id'),
                    'author': comment.get('author', {}).get('login', 'Unknown'),
                    'created_at': comment.get('createdAt', 'Unknown'),
                    'body': comment.get('body', ''),
                    'comment_data': comment
                })
        
        # Search review comments
        for comment in pr_data.get('review_comments', []):
            if search_text.lower() in comment.get('body', '').lower():
                matches.append({
                    'type': 'review',
                    'id': comment.get('id'),
                    'author': comment.get('user', {}).get('login', 'Unknown'),
                    'created_at': comment.get('created_at', 'Unknown'),
                    'path': comment.get('path', 'Unknown'),
                    'line': comment.get('line'),
                    'body': comment.get('body', ''),
                    'in_reply_to_id': comment.get('in_reply_to_id'),
                    'comment_data': comment
                })
        
        return matches
    
    def reply_to_comment(self, pr_number: int, comment_id: str, reply_body: str, comment_type: str = "review") -> bool:
        """Reply to a specific comment (review or general)"""
        try:
            if comment_type == "review":
                # Reply to a review comment (inline code comment)
                # Use the exact same format as the successful manual command
                cmd = [
                    "gh", "api", f"repos/{self.repo_full_name}/pulls/{pr_number}/comments",
                    "-f", f"body={reply_body}",
                    "--field", f"in_reply_to={comment_id}"
                ]
            else:
                # Reply to a general PR comment
                cmd = [
                    "gh", "api", f"repos/{self.repo_full_name}/issues/{pr_number}/comments",
                    "-f", f"body={reply_body}"
                ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            response = json.loads(result.stdout)
            
            print(f"✅ Successfully replied to comment {comment_id}")
            print(f"📍 Reply URL: {response.get('html_url', 'N/A')}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error replying to comment: {e.stderr}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing response: {e}")
            return False
    
    def get_comment_by_id(self, pr_data: Dict[str, Any], comment_id: str) -> Optional[Dict[str, Any]]:
        """Find a specific comment by its ID"""
        # Check general comments
        for comment in pr_data.get('comments', []):
            if str(comment.get('id')) == str(comment_id):
                return {
                    'type': 'general',
                    'comment_data': comment,
                    'author': comment.get('author', {}).get('login', 'Unknown'),
                    'body': comment.get('body', ''),
                    'created_at': comment.get('createdAt', 'Unknown')
                }
        
        # Check review comments  
        for comment in pr_data.get('review_comments', []):
            if str(comment.get('id')) == str(comment_id):
                return {
                    'type': 'review',
                    'comment_data': comment,
                    'author': comment.get('user', {}).get('login', 'Unknown'),
                    'body': comment.get('body', ''),
                    'created_at': comment.get('created_at', 'Unknown'),
                    'path': comment.get('path', 'Unknown'),
                    'line': comment.get('line')
                }
        
        return None
    
    def format_comments(self, pr_data: Dict[str, Any]) -> str:
        """Format comments for easy reading and analysis"""
        output = []
        
        # PR Header
        output.append(f"# PR #{pr_data['pr_number']}: {pr_data['title']}")
        output.append(f"**Author**: {pr_data['author']}")
        output.append(f"**Created**: {pr_data['created_at']}")
        output.append(f"**State**: {pr_data['state']}")
        output.append("")
        
        # PR Description
        if pr_data['body']:
            output.append("## PR Description")
            output.append(pr_data['body'])
            output.append("")
        
        # General Comments with IDs
        comments = pr_data.get('comments', [])
        if comments:
            output.append("## General Comments")
            for i, comment in enumerate(comments, 1):
                output.append(f"### Comment {i} - ID: {comment.get('id', 'Unknown')}")
                output.append(f"**Author**: {comment.get('author', {}).get('login', 'Unknown')}")
                output.append(f"**Created**: {comment.get('createdAt', 'Unknown')}")
                output.append("")
                output.append(comment.get('body', ''))
                output.append("")
        else:
            output.append("## General Comments")
            output.append("*No general comments found on this PR.*")
            output.append("")
        
        # Review Comments (Inline Code Comments) - Threaded with IDs
        review_comments = pr_data.get('review_comments', [])
        if review_comments:
            output.append("## Review Comments (Inline) - Threaded")
            output.extend(self._format_threaded_comments(review_comments))
        else:
            output.append("## Review Comments (Inline)")
            output.append("*No review comments found on this PR.*")
            output.append("")
        
        # Comment ID Summary
        output.append("## Comment ID Summary")
        output.append("### General Comment IDs:")
        for i, comment in enumerate(comments, 1):
            output.append(f"- Comment {i}: {comment.get('id', 'Unknown')} by {comment.get('author', {}).get('login', 'Unknown')}")
        
        output.append("### Review Comment IDs:")
        for i, comment in enumerate(review_comments, 1):
            output.append(f"- Review Comment {i}: {comment.get('id', 'Unknown')} by {comment.get('user', {}).get('login', 'Unknown')} " +
                         f"(File: {comment.get('path', 'Unknown')}, Line: {comment.get('line', 'N/A')})")
        output.append("")
        
        return "\n".join(output)
    
    def _format_threaded_comments(self, comments: List[Dict]) -> List[str]:
        """Format comments in threaded conversations with IDs"""
        output = []
        
        # Build comment lookup map
        comment_map = {comment['id']: comment for comment in comments}
        
        # Group into threads (top-level comments and their replies)
        threads = {}
        for comment in comments:
            if comment.get('in_reply_to_id') is None:
                # Top-level comment
                threads[comment['id']] = {
                    'main': comment,
                    'replies': []
                }
            else:
                # Reply to another comment
                parent_id = comment['in_reply_to_id']
                if parent_id in threads:
                    threads[parent_id]['replies'].append(comment)
                else:
                    # Parent not found, treat as orphaned thread
                    threads[comment['id']] = {
                        'main': comment,
                        'replies': [],
                        'orphaned': True
                    }
        
        # Sort threads by creation time of main comment
        sorted_threads = sorted(threads.items(), 
                               key=lambda x: x[1]['main']['created_at'])
        
        thread_num = 1
        for thread_id, thread_data in sorted_threads:
            main_comment = thread_data['main']
            replies = sorted(thread_data['replies'], key=lambda x: x['created_at'])
            
            # Thread header
            output.append(f"### 🧵 Thread {thread_num}")
            if thread_data.get('orphaned'):
                output.append("*(Reply to missing comment)*")
            output.append("")
            
            # Main comment with ID
            output.append(f"**💬 {main_comment.get('user', {}).get('login', 'Unknown')}** - *{main_comment.get('created_at', 'Unknown')}*")
            output.append(f"📁 **File**: `{main_comment.get('path', 'Unknown')}`" + 
                         (f" **Line**: {main_comment.get('line')}" if main_comment.get('line') else ""))
            output.append(f"🆔 **Comment ID**: {main_comment.get('id', 'Unknown')}")
            output.append("")
            output.append(main_comment.get('body', ''))
            output.append("")
            
            # Replies with IDs
            for reply in replies:
                output.append(f"  ↳ **{reply.get('user', {}).get('login', 'Unknown')}** - *{reply.get('created_at', 'Unknown')}*")
                output.append(f"    🆔 **Reply ID**: {reply.get('id', 'Unknown')}")
                # Indent reply body
                reply_body = reply.get('body', '')
                for line in reply_body.split('\n'):
                    output.append(f"    {line}")
                output.append("")
            
            output.append("---")
            output.append("")
            thread_num += 1
        
        return output
    
    def save_to_file(self, content: str, filename: str = None):
        """Save formatted content to a file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pr_comments_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Comments saved to: {filename}")
        return filename
    
    def analyze_for_response(self, threads: Dict[str, Any], skip_stats: Dict[str, Any]) -> List[str]:
        """Analyze threads and provide actionable response statistics"""
        suggestions = []
        
        if not threads:
            suggestions.append("No comment threads found in this PR.")
            return suggestions
        
        total_threads = len(threads)
        skipped_threads = skip_stats.get('skipped', 0)
        needs_response = skip_stats.get('needs_response', 0)
        skip_reasons = skip_stats.get('skip_reasons', {})
        
        # Thread-level summary
        suggestions.append(f"📊 **Thread Summary**: {total_threads} total threads")
        suggestions.append(f"⏭️  **Skipped**: {skipped_threads} threads (auto-filtered)")
        suggestions.append(f"💬 **Needs Response**: {needs_response} threads require attention")
        
        # Skip breakdown if there are skipped threads
        if skip_reasons:
            skip_details = []
            if skip_reasons.get('resolved', 0) > 0:
                skip_details.append(f"{skip_reasons['resolved']} resolved")
            if skip_reasons.get('last_commenter', 0) > 0:
                skip_details.append(f"{skip_reasons['last_commenter']} last commenter")
            
            if skip_details:
                suggestions.append(f"📋 **Skip Details**: {', '.join(skip_details)}")
        
        # Action guidance
        if needs_response > 0:
            suggestions.append(f"🎯 **Action Required**: Focus on {needs_response} threads marked [NEEDS RESPONSE]")
            suggestions.append("📁 **File Focus**: Review non-SKIP_ files in the session directory")
        else:
            suggestions.append("✅ **All Clear**: No threads require responses at this time")
        
        return suggestions

    def append_response_to_thread(self, session_dir: str, thread_number: int, response_content: str, author: str = "AI Assistant") -> bool:
        """
        PHASE 5 CONVENIENCE METHOD: Append response to thread file
        
        This method helps AI agents comply with Phase 5 (IMPLEMENTATION & FOLLOW-UP)
        by providing an easy way to append drafted responses to thread files.
        
        Args:
            session_dir: The session directory (e.g., "pr_123_review_20240101_120000")
            thread_number: The thread number (1, 2, 3, etc.)
            response_content: The response content to append
            author: Who is writing the response (default: "AI Assistant")
            
        Returns:
            bool: True if successful, False otherwise
            
        Usage Examples:
            # Basic response appending
            workflow.append_response_to_thread("pr_123_review_20240101_120000", 1, "Thanks for the feedback! I'll address this in the next commit.")
            
            # Code suggestion response
            code_response = '''Here's a suggested fix:
            ```python
            def validate_input(data):
                if not data:
                    raise ValueError("Data cannot be empty")
                return data.strip()
            ```
            This addresses the validation concern you raised.'''
            workflow.append_response_to_thread("pr_123_review_20240101_120000", 2, code_response, "Code Reviewer")
            
            # Multi-part response
            workflow.append_response_to_thread("pr_123_review_20240101_120000", 3, "I agree with your architectural concern.")
            workflow.append_response_to_thread("pr_123_review_20240101_120000", 3, "Let me propose an alternative approach...")
        """
        try:
            # Find the thread file
            thread_files = [f for f in os.listdir(session_dir) if f.startswith(f"thread_{thread_number:02d}_")]
            
            if not thread_files:
                print(f"❌ Thread {thread_number} not found in {session_dir}")
                return False
            
            if len(thread_files) > 1:
                print(f"⚠️  Multiple files found for thread {thread_number}, using first: {thread_files[0]}")
            
            thread_file = os.path.join(session_dir, thread_files[0])
            
            # Check if this is a skipped thread
            if "SKIP_" in thread_files[0]:
                print(f"⚠️  Warning: Thread {thread_number} is marked as SKIP. Adding response anyway.")
            
            # Prepare response section
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            response_section = f"""

---

## 📝 DRAFT RESPONSE ({timestamp})

**Author**: {author}

{response_content}

---
"""
            
            # Append to file
            with open(thread_file, 'a', encoding='utf-8') as f:
                f.write(response_section)
            
            print(f"✅ Response appended to thread {thread_number} ({thread_files[0]})")
            return True
            
        except Exception as e:
            print(f"❌ Error appending response to thread {thread_number}: {e}")
            return False

    def extract_and_organize_threads(self, pr_data: Dict[str, Any]) -> str:
        """
        PHASE 1: THREAD EXTRACTION & ORGANIZATION
        - Create dedicated directory for this PR review session
        - Group comments into conversation threads
        - Write each thread to separate file with proper naming
        - Include all metadata and threading structure
        """
        pr_number = pr_data['pr_number']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = f"pr_{pr_number}_review_{timestamp}"
        
        print(f"📁 Creating review session directory: {session_dir}")
        os.makedirs(session_dir, exist_ok=True)
        
        # Extract all comments and organize into threads
        comments = pr_data.get('comments', [])
        review_comments = pr_data.get('review_comments', [])
        
        print(f"📊 Found {len(comments)} general comments + {len(review_comments)} review comments")
        
        # Build thread structure for review comments (these have threading)
        threads = self._build_thread_structure(review_comments)
        
        # Add general comments as individual threads
        for comment in comments:
            thread_id = f"general_{comment.get('id', 'unknown')}"
            threads[thread_id] = {
                'type': 'general',
                'main': comment,
                'replies': [],
                'metadata': {
                    'status': 'unresolved'
                }
            }
        
        # Apply skip logic to all threads
        skip_stats = {'skipped': 0, 'needs_response': 0, 'skip_reasons': {}}
        
        for thread_id, thread_data in threads.items():
            skip_decision = self._should_skip_thread(thread_data)
            thread_data['skip_decision'] = skip_decision
            
            # Update metadata with skip information
            if skip_decision['skip']:
                thread_data['metadata']['status'] = 'skipped'
                thread_data['metadata']['skip_reason'] = skip_decision['reason']
                skip_stats['skipped'] += 1
                skip_type = skip_decision['skip_type']
                skip_stats['skip_reasons'][skip_type] = skip_stats['skip_reasons'].get(skip_type, 0) + 1
                print(f"⏭️  Skipping thread: {skip_decision['reason']}")
            else:
                thread_data['metadata']['status'] = 'needs_response'
                skip_stats['needs_response'] += 1
        
        print(f"📋 Skip Analysis: {skip_stats['skipped']} skipped, {skip_stats['needs_response']} need responses")
        
        # Write threads to separate files
        thread_files = []
        thread_num = 1
        
        # Sort threads by creation time
        sorted_threads = sorted(threads.items(), 
                               key=lambda x: x[1]['main'].get('created_at', x[1]['main'].get('createdAt', '')))
        
        for thread_id, thread_data in sorted_threads:
            main_comment = thread_data['main']
            
            # Generate filename with author and topic
            author = main_comment.get('user', {}).get('login', main_comment.get('author', {}).get('login', 'unknown'))
            body = main_comment.get('body', '')
            topic = body.split('\n')[0][:30].replace(' ', '_').replace('/', '_').replace('\\', '_')
            topic = ''.join(c for c in topic if c.isalnum() or c in ['_', '-'])
            
            # Add skip status to filename for easy identification
            skip_prefix = "SKIP_" if thread_data['skip_decision']['skip'] else ""
            filename = f"thread_{thread_num:02d}_{skip_prefix}{author}_{topic}.md"
            filepath = os.path.join(session_dir, filename)
            
            # Write thread to file
            thread_content = self._format_thread_for_file(thread_data, thread_num)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(thread_content)
            
            thread_files.append(filepath)
            skip_indicator = "⏭️ " if thread_data['skip_decision']['skip'] else "💾"
            print(f"{skip_indicator} Thread {thread_num}: {filename}")
            thread_num += 1
        
        # Create summary file
        summary_file = os.path.join(session_dir, "session_summary.md")
        summary_content = self._create_session_summary(pr_data, threads, session_dir, skip_stats)
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        print(f"📋 Session summary: session_summary.md")
        print(f"✅ Phase 1 Complete: {len(threads)} threads organized in {session_dir}")
        
        return session_dir, threads, skip_stats
    
    def _build_thread_structure(self, review_comments: List[Dict]) -> Dict[str, Dict]:
        """Build threaded structure from review comments"""
        threads = {}
        comment_map = {comment['id']: comment for comment in review_comments}
        
        for comment in review_comments:
            if comment.get('in_reply_to_id') is None:
                # Top-level comment
                threads[comment['id']] = {
                    'type': 'review',
                    'main': comment,
                    'replies': [],
                    'metadata': {
                        'status': 'unresolved'
                    }
                }
            else:
                # Reply to another comment
                parent_id = comment['in_reply_to_id']
                if parent_id in threads:
                    threads[parent_id]['replies'].append(comment)
                else:
                    # Parent not found, treat as orphaned thread
                    threads[comment['id']] = {
                        'type': 'review',
                        'main': comment,
                        'replies': [],
                        'orphaned': True,
                        'metadata': {
                            'status': 'unresolved'
                        }
                    }
        
        return threads
    
    def _format_thread_for_file(self, thread_data: Dict, thread_num: int) -> str:
        """Format thread data for individual file"""
        main_comment = thread_data['main']
        replies = thread_data.get('replies', [])
        metadata = thread_data.get('metadata', {})
        skip_decision = thread_data.get('skip_decision', {})
        
        output = []
        
        # Thread header with metadata
        output.append(f"# Thread {thread_num:02d}")
        output.append("")
        output.append("## Metadata")
        output.append(f"- **Type**: {thread_data.get('type', 'unknown')}")
        output.append(f"- **Status**: {metadata.get('status', 'unknown')}")
        
        # Add skip information if thread is skipped
        if skip_decision.get('skip'):
            output.append(f"- **Skip Reason**: {metadata.get('skip_reason', 'Unknown')}")
            output.append(f"- **⏭️ Action**: No response needed")
        else:
            output.append(f"- **💬 Action**: Response required")
            
        if thread_data.get('orphaned'):
            output.append("- **Note**: Reply to missing comment")
        output.append("")
        
        # Main comment
        output.append("## Main Comment")
        output.append("")
        author = main_comment.get('user', {}).get('login', main_comment.get('author', {}).get('login', 'Unknown'))
        created_at = main_comment.get('created_at', main_comment.get('createdAt', 'Unknown'))
        
        output.append(f"**Author**: {author}")
        output.append(f"**Created**: {created_at}")
        output.append(f"**Comment ID**: {main_comment.get('id', 'Unknown')}")
        
        if thread_data.get('type') == 'review':
            output.append(f"**File**: `{main_comment.get('path', 'Unknown')}`")
            if main_comment.get('line'):
                output.append(f"**Line**: {main_comment.get('line')}")
        
        output.append("")
        output.append("### Content")
        output.append("")
        output.append(main_comment.get('body', ''))
        output.append("")
        
        # Replies
        if replies:
            output.append("## Replies")
            output.append("")
            
            sorted_replies = sorted(replies, key=lambda x: x.get('created_at', ''))
            for i, reply in enumerate(sorted_replies, 1):
                reply_author = reply.get('user', {}).get('login', 'Unknown')
                reply_created = reply.get('created_at', 'Unknown')
                
                output.append(f"### Reply {i}")
                output.append("")
                output.append(f"**Author**: {reply_author}")
                output.append(f"**Created**: {reply_created}")
                output.append(f"**Reply ID**: {reply.get('id', 'Unknown')}")
                output.append("")
                output.append("#### Content")
                output.append("")
                output.append(reply.get('body', ''))
                output.append("")
        
        return "\n".join(output)
    
    def _create_session_summary(self, pr_data: Dict, threads: Dict, session_dir: str, skip_stats: Dict) -> str:
        """Create session summary file"""
        output = []
        
        output.append(f"# PR {pr_data['pr_number']} Review Session")
        output.append("")
        output.append(f"**Repository**: {pr_data.get('repo', 'Unknown')}")
        output.append(f"**PR Title**: {pr_data.get('title', 'Unknown')}")
        output.append(f"**PR Author**: {pr_data.get('author', 'Unknown')}")
        output.append(f"**Session Directory**: {session_dir}")
        output.append(f"**Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("")
        
        # Statistics
        output.append("## Statistics")
        output.append("")
        general_threads = sum(1 for t in threads.values() if t.get('type') == 'general')
        review_threads = sum(1 for t in threads.values() if t.get('type') == 'review')
        total_replies = sum(len(t.get('replies', [])) for t in threads.values())
        
        output.append(f"- **Total Threads**: {len(threads)}")
        output.append(f"- **General Comments**: {general_threads}")
        output.append(f"- **Review Comments**: {review_threads}")
        output.append(f"- **Total Replies**: {total_replies}")
        output.append("")
        
        # Skip Analysis
        output.append("## Skip Analysis")
        output.append("")
        output.append(f"- **Total Skipped**: {skip_stats['skipped']}")
        output.append(f"- **Total Needs Response**: {skip_stats['needs_response']}")
        output.append("")
        
        output.append("### Skip Reasons")
        for skip_type, count in skip_stats['skip_reasons'].items():
            output.append(f"- **{skip_type}**: {count}")
        
        # Thread list
        output.append("## Thread Files")
        output.append("")
        
        thread_num = 1
        sorted_threads = sorted(threads.items(), 
                               key=lambda x: x[1]['main'].get('created_at', x[1]['main'].get('createdAt', '')))
        
        for thread_id, thread_data in sorted_threads:
            main_comment = thread_data['main']
            author = main_comment.get('user', {}).get('login', main_comment.get('author', {}).get('login', 'unknown'))
            skip_decision = thread_data.get('skip_decision', {})
            
            body = main_comment.get('body', '')
            topic = body.split('\n')[0][:50]
            
            # Add skip indicator to thread listing
            if skip_decision.get('skip'):
                status_icon = "⏭️"
                status_text = f"[SKIP: {skip_decision.get('skip_type', 'unknown')}]"
            else:
                status_icon = "💬"
                status_text = "[NEEDS RESPONSE]"
            
            output.append(f"{thread_num}. {status_icon} **{author}** {status_text} - {topic}")
            thread_num += 1
        
        output.append("")
        output.append("## Next Steps")
        output.append("")
        output.append("1. **Review thread files**: Focus on files marked [NEEDS RESPONSE]")
        output.append("2. **Skip files marked**: ⏭️ SKIP_* files are automatically filtered out")
        output.append("3. **Systematic responses**: Address each remaining thread systematically")
        output.append("4. **Search specific content**: `presto search --repo <OWNER/REPO> --pr <PR> --query <text>`")
        output.append("5. **Post responses**: `presto reply --repo <OWNER/REPO> --pr <PR> --comment-id <ID> --message <text>`")
        output.append("6. **Draft responses**: `presto append --session-dir <SESSION_DIR> --thread <N> --content <text>`")
        output.append("7. **Post responses**: `presto post --session-dir <SESSION_DIR> --thread <N>`")
        output.append("8. **Post all responses**: `presto post --session-dir <SESSION_DIR> --all`")
        output.append("")
        
        return "\n".join(output)

    def post_responses(self, session_dir: str, thread_number: int = None, post_all: bool = False, dry_run: bool = False, auto_yes: bool = False) -> bool:
        """
        PHASE 6: POST draft responses from thread files to GitHub
        
        Args:
            session_dir: Session directory containing thread files
            thread_number: Specific thread to post (optional)
            post_all: Post all unposted draft responses
            dry_run: Show what would be posted without actually posting
            auto_yes: Auto-confirm posting without prompts
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not os.path.exists(session_dir):
            print(f"❌ Session directory '{session_dir}' not found")
            return False
        
        # Get PR number and repo from session directory or summary file
        pr_info = self._extract_pr_info_from_session(session_dir)
        if not pr_info:
            print("❌ Could not determine PR information from session directory")
            return False
        
        # Update workflow repository info for API calls
        self.repo_full_name = pr_info['repo']
        repo_parts = pr_info['repo'].split('/')
        if len(repo_parts) == 2:
            self.repo_owner = repo_parts[0]
            self.repo_name = repo_parts[1]
        
        print(f"🔍 Session: {session_dir}")
        print(f"📋 PR: #{pr_info['pr_number']} in {pr_info['repo']}")
        
        # Get thread files to process
        if thread_number:
            thread_files = [f for f in os.listdir(session_dir) if f.startswith(f"thread_{thread_number:02d}_")]
            if not thread_files:
                print(f"❌ Thread {thread_number} not found in session directory")
                return False
        elif post_all:
            thread_files = [f for f in os.listdir(session_dir) if f.startswith("thread_") and f.endswith(".md")]
            thread_files = [f for f in thread_files if not f.startswith("thread_") or "SKIP_" not in f]
        else:
            print("❌ Must specify either a thread number or --all")
            return False
        
        if not thread_files:
            print("📭 No thread files found to process")
            return True
        
        thread_files.sort()  # Process in order
        
        # Process each thread file
        posted_count = 0
        skipped_count = 0
        would_post_count = 0
        
        # For dry run, show a cleaner summary first
        if dry_run:
            print(f"\n🔍 DRY RUN - Analyzing what would be posted...")
        
        for thread_file in thread_files:
            filepath = os.path.join(session_dir, thread_file)
            
            # Check if thread is manually skipped
            if self._is_manually_skipped(filepath):
                if not dry_run:  # Only show skipped in regular mode
                    print(f"\n📄 Processing: {thread_file}")
                    print("   ⏭️  MANUALLY SKIPPED - will not post")
                skipped_count += 1
                continue
            
            # Extract draft responses from thread file
            draft_responses = self._extract_draft_responses(filepath)
            
            if not draft_responses:
                if not dry_run:  # Only show empty threads in regular mode
                    print(f"\n📄 Processing: {thread_file}")
                    print("   📭 No draft responses found")
                continue
            
            # For dry run, only show threads that would actually post
            if dry_run:
                # Count unposted drafts
                unposted_drafts = [d for d in draft_responses if not d['posted']]
                if unposted_drafts:
                    thread_num = thread_file.split('_')[1]
                    print(f"\n🟢 WOULD POST Thread {int(thread_num)}: {thread_file}")
                    for i, draft in enumerate(unposted_drafts):
                        print(f"   📝 Draft by {draft['author']} ({draft['timestamp']})")
                        print(f"      Preview: {draft['content'][:150]}...")
                    would_post_count += len(unposted_drafts)
                continue
            
            # Regular processing (not dry run)
            print(f"\n📄 Processing: {thread_file}")
            
            # Get thread metadata for posting
            thread_metadata = self._extract_thread_metadata(filepath)
            if not thread_metadata:
                print("   ❌ Could not extract thread metadata")
                continue
            
            # Process each draft response
            for i, draft in enumerate(draft_responses):
                if draft['posted']:
                    print(f"   ⏭️  Draft {i+1}: Already posted ({draft['posted_at']})")
                    skipped_count += 1
                    continue
                
                print(f"   📝 Draft {i+1} by {draft['author']} ({draft['timestamp']}):")
                print(f"      Preview: {draft['content'][:100]}...")
                
                # Dry run already handled above - should not reach here
                if dry_run:
                    continue
                
                # Confirm posting
                if not post_all and thread_number and not auto_yes:
                    confirm = input("   Post this response? (y/N): ").strip().lower()
                    if confirm != 'y':
                        print("   ⏭️  Skipped by user")
                        continue
                elif auto_yes and not post_all and thread_number:
                    print("   ✅ Auto-confirmed (--yes flag)")
                
                # Post to GitHub
                success = self._post_draft_response(
                    pr_info['pr_number'],
                    thread_metadata['comment_id'],
                    draft['content'],
                    thread_metadata['comment_type']
                )
                
                if success:
                    # Mark as posted in the thread file
                    self._mark_response_as_posted(filepath, i, draft)
                    print(f"   ✅ Posted successfully!")
                    posted_count += 1
                else:
                    print(f"   ❌ Failed to post")
                    return False
        
        # Summary
        print(f"\n📊 Summary:")
        if dry_run:
            print(f"   🟢 WOULD POST: {would_post_count} responses")
            if skipped_count > 0:
                print(f"   ⏭️  Skipped (manual): {skipped_count} threads")
            print(f"\n🔍 DRY RUN COMPLETE - No responses were actually posted")
            if would_post_count > 0:
                print(f"💡 To post for real: Remove --dry-run flag")
        else:
            print(f"   ✅ Posted: {posted_count}")
            print(f"   ⏭️  Skipped: {skipped_count}")
        
        return True
    
    def _extract_pr_info_from_session(self, session_dir: str) -> Optional[Dict[str, Any]]:
        """Extract PR number and repo from session directory"""
        # Try to parse from directory name first
        dir_name = os.path.basename(session_dir)
        if dir_name.startswith('pr_'):
            try:
                pr_number = int(dir_name.split('_')[1])
                # Try to get repo from session summary file
                summary_file = os.path.join(session_dir, 'session_summary.md')
                if os.path.exists(summary_file):
                    with open(summary_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for line in content.split('\n'):
                            if line.startswith('**Repository**:'):
                                repo = line.split(':', 1)[1].strip()
                                return {'pr_number': pr_number, 'repo': repo}
                
                # Fallback to current repo
                return {'pr_number': pr_number, 'repo': self.repo_full_name}
            except (ValueError, IndexError):
                pass
        
        return None
    
    def _extract_draft_responses(self, filepath: str) -> List[Dict[str, Any]]:
        """Extract draft responses from a thread file"""
        draft_responses = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all DRAFT RESPONSE sections
            sections = content.split('## 📝 DRAFT RESPONSE')
            
            for i, section in enumerate(sections[1:]):  # Skip first section (before any drafts)
                lines = section.split('\n')
                
                # Extract timestamp from first line
                timestamp_line = lines[0].strip() if lines else ""
                timestamp = timestamp_line.strip('()')
                
                # Extract author
                author = "AI Assistant"  # default
                content_lines = []
                posted_info = None
                
                for line in lines[1:]:
                    if line.startswith('**Author**:'):
                        author = line.split(':', 1)[1].strip()
                    elif line.startswith('**POSTED**:'):
                        posted_info = line.split(':', 1)[1].strip()
                    elif line.strip() and not line.startswith('**') and not line.startswith('---'):
                        content_lines.append(line)
                
                # Join content (skip metadata lines)
                draft_content = '\n'.join(content_lines).strip()
                
                if draft_content:
                    draft_responses.append({
                        'timestamp': timestamp,
                        'author': author,
                        'content': draft_content,
                        'posted': bool(posted_info),
                        'posted_at': posted_info if posted_info else None
                    })
        
        except Exception as e:
            print(f"   ⚠️  Error reading draft responses: {e}")
        
        return draft_responses
    
    def _extract_thread_metadata(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Extract thread metadata needed for posting"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for comment ID and type in the thread content
            comment_id = None
            comment_type = 'review'  # default
            
            lines = content.split('\n')
            for line in lines:
                if '**Comment ID**:' in line or '**ID**:' in line:
                    comment_id = line.split(':', 1)[1].strip()
                elif '**Type**:' in line:
                    type_val = line.split(':', 1)[1].strip().lower()
                    if 'general' in type_val:
                        comment_type = 'general'
            
            if comment_id:
                return {
                    'comment_id': comment_id,
                    'comment_type': comment_type
                }
        
        except Exception as e:
            print(f"   ⚠️  Error reading thread metadata: {e}")
        
        return None
    
    def _post_draft_response(self, pr_number: int, comment_id: str, content: str, comment_type: str) -> bool:
        """Post a draft response to GitHub"""
        return self.reply_to_comment(pr_number, comment_id, content, comment_type)
    
    def _mark_response_as_posted(self, filepath: str, draft_index: int, draft: Dict[str, Any]) -> bool:
        """Mark a draft response as posted in the thread file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find the specific draft response section
            sections = content.split('## 📝 DRAFT RESPONSE')
            
            if draft_index + 1 < len(sections):
                # Add POSTED marker to this section
                section = sections[draft_index + 1]
                lines = section.split('\n')
                
                # Insert POSTED marker after author line
                new_lines = []
                for line in lines:
                    new_lines.append(line)
                    if line.startswith('**Author**:'):
                        new_lines.append(f"**POSTED**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Reconstruct the content
                sections[draft_index + 1] = '\n'.join(new_lines)
                new_content = '## 📝 DRAFT RESPONSE'.join(sections)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                return True
        
        except Exception as e:
            print(f"   ⚠️  Error marking response as posted: {e}")
        
        return False

    def _get_pr_config_path(self, pr_number: int) -> str:
        """Return path to persistent configuration file for this PR"""
        base_dir = os.path.expanduser("~/.presto")
        repo_dir = os.path.join(base_dir, self.repo_owner, self.repo_name)
        os.makedirs(repo_dir, exist_ok=True)
        return os.path.join(repo_dir, f"{pr_number}.txt")

    def _load_skip_registry(self, pr_number: int) -> set:
        """Load skip registry for PR, return set of thread numbers (int)"""
        path = self._get_pr_config_path(pr_number)
        if not os.path.exists(path):
            return set()
        try:
            with open(path, "r", encoding="utf-8") as f:
                return {int(x.strip()) for x in f.readlines() if x.strip().isdigit()}
        except Exception:
            return set()

    def _save_skip_registry(self, pr_number: int, threads: set):
        """Save skip registry for PR"""
        path = self._get_pr_config_path(pr_number)
        try:
            with open(path, "w", encoding="utf-8") as f:
                for t in sorted(threads):
                    f.write(f"{t}\n")
        except Exception as e:
            print(f"⚠️  Error saving PR configuration: {e}")

    def _is_manually_skipped(self, filepath: str) -> bool:
        """Check if a thread file is manually marked as skipped or in registry"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            if '**MANUAL_SKIP**:' in content:
                return True
        except Exception:
            pass
        # Check registry
        session_dir = os.path.dirname(filepath)
        pr_info = self._extract_pr_info_from_session(session_dir)
        if pr_info:
            registry = self._load_skip_registry(pr_info['pr_number'])
            try:
                thread_num = int(os.path.basename(filepath).split('_')[1])
                return thread_num in registry
            except (IndexError, ValueError):
                return False
        return False

    def toggle_manual_skip(self, session_dir: str, thread_number: int, mark_skip: bool) -> bool:
        """
        Mark or unmark a thread as manually skipped (persistent registry + file marker)
        """
        pr_info = self._extract_pr_info_from_session(session_dir)
        pr_number = pr_info['pr_number'] if pr_info else None
        if pr_number is None:
            print("❌ Unable to determine PR number for registry update")
            return False
        registry = self._load_skip_registry(pr_number)
        if mark_skip:
            registry.add(thread_number)
        else:
            registry.discard(thread_number)
        self._save_skip_registry(pr_number, registry)

        # existing logic unchanged below
        try:
            thread_files = [f for f in os.listdir(session_dir) if f.startswith(f"thread_{thread_number:02d}_")]
            if not thread_files:
                print(f"❌ Thread {thread_number} not found in session directory")
                return False
            thread_file = os.path.join(session_dir, thread_files[0])
            with open(thread_file, 'r', encoding='utf-8') as f:
                content = f.read()
            has_manual_skip = '**MANUAL_SKIP**:' in content
            if mark_skip and has_manual_skip:
                return True
            if not mark_skip and not has_manual_skip:
                return True
            lines = content.split('\n')
            new_lines = []
            if mark_skip and not has_manual_skip:
                new_lines = lines + ['- **MANUAL_SKIP**: registry']
            elif not mark_skip and has_manual_skip:
                new_lines = [line for line in lines if not line.strip().startswith('- **MANUAL_SKIP**')]
            else:
                new_lines = lines
            with open(thread_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            return True
        except Exception as e:
            print(f"❌ Error modifying manual skip status: {e}")
            return False

    def list_manually_skipped_threads(self, session_dir: str) -> None:
        """List all manually skipped threads (registry + file markers)"""
        pr_info = self._extract_pr_info_from_session(session_dir)
        pr_number = pr_info['pr_number'] if pr_info else None
        registry = self._load_skip_registry(pr_number) if pr_number else set()
        super_list = []  # collect thread info
        try:
            thread_files = [f for f in os.listdir(session_dir) if f.startswith("thread_") and f.endswith(".md")]
            thread_files.sort()
            for thread_file in thread_files:
                filepath = os.path.join(session_dir, thread_file)
                thread_num = int(thread_file.split('_')[1])
                if thread_num in registry or '**MANUAL_SKIP**:' in open(filepath, encoding='utf-8').read():
                    super_list.append(thread_file)
        except Exception as e:
            print(f"❌ Error listing skipped threads: {e}")
            return
        if not super_list:
            print("📭 No threads are manually marked as skipped (registry + file)")
        else:
            print(f"⏭️  Found {len(super_list)} manually skipped threads:")
            for file in super_list:
                print(f"   • {file}")

    def _auto_detect_session_dir(self, provided_session_dir: str = None) -> str:
        """Auto-detect the most recent session directory if not provided"""
        if provided_session_dir:
            return provided_session_dir
        
        # Look for pr_*_review_* directories in current directory
        try:
            candidates = [d for d in os.listdir('.') if d.startswith('pr_') and '_review_' in d and os.path.isdir(d)]
            if not candidates:
                raise ValueError("No session directories found. Run 'presto analyze' first.")
            
            # Sort by creation time, most recent first
            candidates.sort(key=lambda d: os.path.getctime(d), reverse=True)
            session_dir = candidates[0]
            print(f"🔍 Auto-detected session directory: {session_dir}")
            return session_dir
            
        except Exception as e:
            raise ValueError(f"Could not auto-detect session directory: {e}")

    def cleanup_session(self, session_dir: str, force: bool = False) -> bool:
        """Clean up session directory and files"""
        try:
            if not os.path.exists(session_dir):
                print(f"❌ Session directory '{session_dir}' not found")
                return False
            
            # Check for unposted draft responses unless force is used
            if not force:
                thread_files = [f for f in os.listdir(session_dir) if f.startswith("thread_") and f.endswith(".md")]
                unposted_count = 0
                
                for thread_file in thread_files:
                    filepath = os.path.join(session_dir, thread_file)
                    draft_responses = self._extract_draft_responses(filepath)
                    unposted_drafts = [d for d in draft_responses if not d['posted']]
                    unposted_count += len(unposted_drafts)
                
                if unposted_count > 0:
                    print(f"⚠️  Found {unposted_count} unposted draft responses in session")
                    print(f"💡 Use --force to cleanup anyway, or post responses first with 'presto post --all'")
                    return False
            
            # Remove the entire session directory
            import shutil
            shutil.rmtree(session_dir)
            print(f"🗑️  Removed session directory: {session_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
            return False

def main():
    # Handle bootstrap prompt when no arguments provided
    if len(sys.argv) == 1:
        display_bootstrap_prompt()
        return
    
    parser = argparse.ArgumentParser(
        description="Presto: GitHub PR Comment Workflow Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available Commands:
  analyze     Run Phase 1: Extract and organize PR comment threads (default)
  reply       Reply to a specific comment on GitHub
  append      Append draft response to thread file (Phase 5)
  search      Search comments for specific text
  post        Post draft responses from thread files (Phase 6)
  skip        Manually mark/unmark threads to skip posting
  cleanup     Remove session directory and thread files

Examples:
  presto analyze --repo owner/repo --pr 123
  presto reply --repo owner/repo --pr 123 --comment-id 456 --message "Thanks!"
  presto append --thread 1 --content "Response"
  presto search --repo owner/repo --pr 123 --query "validation"
  presto post 1
  presto skip 1
  presto cleanup

For command-specific help: presto <command> --help
        """)
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # ANALYZE command (default Phase 1 workflow)
    analyze_parser = subparsers.add_parser(
        'analyze', 
        help='Extract and organize PR comment threads (Phase 1)',
        description='Run Phase 1: Thread Extraction & Organization. This is the core workflow that fetches PR comments, organizes them into threads, applies skip logic, and creates session files.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  presto analyze --repo microsoft/vscode --pr 123
  presto analyze --repo owner/repo --pr 456 --save
  presto analyze --repo owner/repo --pr 789 --save --output custom_filename.md
        """)
    analyze_parser.add_argument("--repo", required=True, help="Repository in format owner/repo")
    analyze_parser.add_argument("--pr", required=True, type=int, help="PR number to analyze")
    analyze_parser.add_argument("--save", action="store_true", help="Additionally save formatted comments to a single file")
    analyze_parser.add_argument("--output", help="Output filename for --save option (optional)")
    
    # REPLY command
    reply_parser = subparsers.add_parser(
        'reply',
        help='Reply to a specific comment on GitHub',
        description='Post a reply to a specific comment. Use this for Phase 6: Automated Posting.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  presto reply --repo owner/repo --pr 123 --comment-id 456789 --message "Thanks for the feedback!"
  presto reply --repo owner/repo --pr 123 --comment-id 456789 --message "Here's the fix: [code]"
        """)
    reply_parser.add_argument("--repo", required=True, help="Repository in format owner/repo")
    reply_parser.add_argument("--pr", required=True, type=int, help="PR number")
    reply_parser.add_argument("--comment-id", required=True, help="Comment ID to reply to")
    reply_parser.add_argument("--message", required=True, help="Reply message content")
    
    # APPEND command (Phase 5 convenience)
    append_parser = subparsers.add_parser(
        'append',
        help='Append draft response to thread file (Phase 5)',
        description='Append a draft response to a thread file for review before posting. This supports Phase 5: Implementation & Follow-up.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  presto append --thread 1 --content "Thanks for the feedback!"                                   # Auto-detect session
  presto append --thread 2 --content "Here's a fix..." --author "Senior Dev"                     # Auto-detect session
  presto append --session-dir pr_123_review_20240101_120000 --thread 3 --content "Response..."   # Specific session
        """)
    append_parser.add_argument("--session-dir", help="Session directory containing thread files (auto-detected if not specified)")
    append_parser.add_argument("--thread", required=True, type=int, help="Thread number to append response to")
    append_parser.add_argument("--content", required=True, help="Response content to append")
    append_parser.add_argument("--author", default="AI Assistant", help="Author name for the response")
    
    # SEARCH command
    search_parser = subparsers.add_parser(
        'search',
        help='Search comments for specific text',
        description='Search through PR comments for specific text patterns. Useful for finding relevant discussions.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  presto search --repo owner/repo --pr 123 --query "validation"
  presto search --repo owner/repo --pr 123 --query "security concern"
  presto search --repo owner/repo --pr 123 --query "TODO"
        """)
    search_parser.add_argument("--repo", required=True, help="Repository in format owner/repo")
    search_parser.add_argument("--pr", required=True, type=int, help="PR number to search")
    search_parser.add_argument("--query", required=True, help="Text to search for in comments")
    
    # POST command (Phase 6 workflow)
    post_parser = subparsers.add_parser(
        'post',
        help='Post draft responses from thread files (Phase 6)',
        description='Read draft responses from thread files and post them to GitHub. This implements Phase 6: Automated Posting with double-post protection.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  presto post 1                                                            # Post thread 1 (auto-detect session)
  presto post 1 -y                                                         # Post thread 1 without confirmation
  presto post 2 --dry-run                                                  # Dry run thread 2 (auto-detect session)
  presto post --all                                                        # Post all threads (auto-detect session)
  presto post 1 --session-dir pr_123_review_20240101_120000                # Post thread 1 (specific session)
        """)
    post_parser.add_argument("thread", type=int, nargs='?', help="Thread number to post (optional)")
    post_parser.add_argument("--session-dir", help="Session directory containing thread files (auto-detected if not specified)")
    post_parser.add_argument("--all", action="store_true", help="Post all unposted draft responses")
    post_parser.add_argument("--dry-run", action="store_true", help="Show what would be posted without actually posting")
    post_parser.add_argument("-y", "--yes", action="store_true", help="Auto-confirm posting without prompts")
    
    # SKIP command (Manual skip control)
    skip_parser = subparsers.add_parser(
        'skip',
        help='Manually mark/unmark threads to skip posting',
        description='Mark threads as manually skipped so they won\'t be posted even with draft responses. Useful when you draft a response but decide not to post it.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  presto skip 1                                                            # Mark thread 1 as skipped (auto-detect session)
  presto skip 1 --unmark                                                   # Remove skip marker (auto-detect session)
  presto skip --list                                                       # List all manually skipped threads (auto-detect)
  presto skip 1 --session-dir pr_123_review_20240101_120000                # Mark thread 1 as skipped (specific session)
        """)
    skip_parser.add_argument("thread", type=int, nargs='?', help="Thread number to mark/unmark as skipped")
    skip_parser.add_argument("--session-dir", help="Session directory containing thread files (auto-detected if not specified)")
    skip_parser.add_argument("--unmark", action="store_true", help="Remove manual skip marker from thread")
    skip_parser.add_argument("--list", action="store_true", help="List all manually skipped threads")
    
    # CLEANUP command
    cleanup_parser = subparsers.add_parser(
        'cleanup',
        help='Remove session directory and thread files',
        description='Remove a session directory and all its thread files. Warns if unposted draft responses exist.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  presto cleanup                                                           # Clean up auto-detected session
  presto cleanup --session-dir pr_123_review_20240101_120000              # Clean up specific session
  presto cleanup --force                                                  # Force cleanup even with unposted responses
        """)
    cleanup_parser.add_argument("--session-dir", help="Session directory to remove (auto-detected if not specified)")
    cleanup_parser.add_argument("--force", action="store_true", help="Force cleanup even if unposted draft responses exist")
    
    args = parser.parse_args()
    
    # If no command specified, default to analyze for backward compatibility
    if not hasattr(args, 'command') or args.command is None:
        # Check if old-style arguments are provided
        if '--repo' in sys.argv and '--pr' in sys.argv:
            print("⚠️  Using legacy argument format. Consider using: presto analyze --repo ... --pr ...")
            args.command = 'analyze'
            # Re-parse with analyze parser for backward compatibility
            analyze_args = analyze_parser.parse_args(sys.argv[1:])
            args = analyze_args
            args.command = 'analyze'
        else:
            parser.print_help()
            return
    
    # Parse repository
    try:
        repo_owner, repo_name = args.repo.split('/')
    except ValueError:
        print("Error: Repository must be in format 'owner/repo'")
        sys.exit(1)
    except AttributeError:
        # For 'post' command, we'll get repo info from session directory
        repo_owner = "unknown"
        repo_name = "unknown"
    
    # Initialize workflow
    workflow = PRCommentWorkflow(repo_owner, repo_name)
    
    # Handle commands that don't need PR data first
    if args.command == 'append':
        print("\n" + "="*60)
        print("📝 APPEND RESPONSE MODE (Phase 5)")
        print("="*60)
        
        # Auto-detect session directory if not provided
        session_dir = workflow._auto_detect_session_dir(args.session_dir)
        
        success = workflow.append_response_to_thread(
            session_dir, 
            args.thread, 
            args.content,
            args.author
        )
        
        if success:
            print(f"🎉 Response successfully appended to thread {args.thread}!")
            print(f"💡 Next steps: Review the updated thread file and post using 'presto post' when ready")
        else:
            print("❌ Failed to append response.")
            sys.exit(1)
        return
    
    elif args.command == 'post':
        print("\n" + "="*60)
        print("📤 POST MODE (Phase 6)")
        print("="*60)
        
        # Auto-detect session directory if not provided
        session_dir = workflow._auto_detect_session_dir(args.session_dir)
        
        success = workflow.post_responses(session_dir, args.thread, args.all, args.dry_run, args.yes)
        if success:
            if not args.dry_run:
                print("🎉 Responses posted successfully!")
        else:
            print("❌ Failed to post responses.")
            sys.exit(1)
        return
    
    elif args.command == 'skip':
        print("\n" + "="*60)
        print("⏭️ SKIP CONTROL MODE")
        print("="*60)
        
        # Auto-detect session directory if not provided
        session_dir = workflow._auto_detect_session_dir(args.session_dir)
        
        if args.list:
            workflow.list_manually_skipped_threads(session_dir)
        elif args.thread is not None:
            success = workflow.toggle_manual_skip(session_dir, args.thread, not args.unmark)
            if success:
                action = "unmarked" if args.unmark else "marked"
                print(f"✅ Thread {args.thread} {action} as manually skipped")
            else:
                print(f"❌ Failed to modify skip status for thread {args.thread}")
                sys.exit(1)
        else:
            print("❌ Must specify either a thread number or --list")
            sys.exit(1)
        return
    
    elif args.command == 'cleanup':
        print("\n" + "="*60)
        print("🗑️ CLEANUP MODE")
        print("="*60)
        
        # Auto-detect session directory if not provided
        session_dir = workflow._auto_detect_session_dir(args.session_dir)
        
        success = workflow.cleanup_session(session_dir, args.force)
        if success:
            print("✅ Session cleanup completed successfully!")
        else:
            print("❌ Session cleanup failed.")
            sys.exit(1)
        return
    
    # For commands that need PR data, fetch it first
    if args.command in ['reply', 'search', 'analyze']:
        print(f"🔍 Fetching PR #{args.pr} from {args.repo}...")
        pr_data = workflow.fetch_pr_comments(args.pr)
        
        if not pr_data:
            print("Failed to fetch PR data. Check the PR number and repository.")
            sys.exit(1)
        
        # Add repo info to pr_data for summary
        pr_data['repo'] = args.repo
        
        if args.command == 'reply':
            print("\n" + "="*60)
            print("💬 REPLY MODE (Phase 6)")
            print("="*60)
            comment_info = workflow.get_comment_by_id(pr_data, args.comment_id)
            if not comment_info:
                print(f"Comment ID {args.comment_id} not found in PR #{args.pr}")
                sys.exit(1)
            
            success = workflow.reply_to_comment(args.pr, args.comment_id, args.message, comment_info['type'])
            
            if success:
                print("🎉 Reply posted successfully!")
            else:
                print("❌ Failed to post reply.")
            sys.exit(1)
        elif args.command == 'search':
            print("\n" + "="*60)
            print(f"🔍 SEARCH MODE: '{args.query}'")
            print("="*60)
            matches = workflow.find_comment_by_text(pr_data, args.query)
            if matches:
                print(f"Found {len(matches)} matching comments:")
                for i, match in enumerate(matches, 1):
                    print(f"\n--- Match {i} ---")
                    print(f"Type: {match['type']}")
                    print(f"ID: {match['id']}")
                    print(f"Author: {match['author']}")
                    print(f"Created: {match['created_at']}")
                    if match['type'] == 'review':
                        print(f"File: {match['path']}")
                        if match['line']:
                            print(f"Line: {match['line']}")
                        if match['in_reply_to_id']:
                            print(f"Reply to ID: {match['in_reply_to_id']}")
                    print(f"Body: {match['body'][:100]}..." if len(match['body']) > 100 else f"Body: {match['body']}")
                    print(f"\n💡 To reply: presto reply --repo {args.repo} --pr {args.pr} --comment-id {match['id']} --message '<your response>'")
            else:
                print("No matching comments found.")
            return
        elif args.command == 'analyze':
            # PHASE 1: ALWAYS extract and organize threads (core workflow)
            print("\n" + "="*60)
            print("🔄 PHASE 1: THREAD EXTRACTION & ORGANIZATION")
            print("="*60)
            session_dir, threads, skip_stats = workflow.extract_and_organize_threads(pr_data)
            
            # Optional: Also save formatted comments to single file if requested
            if hasattr(args, 'save') and args.save:
                print("\n" + "="*60)
                print("💾 SAVING FORMATTED COMMENTS")
                print("="*60)
                formatted_content = workflow.format_comments(pr_data)
                output_file = getattr(args, 'output', None)
                workflow.save_to_file(formatted_content, output_file)
            
            # Provide analysis suggestions
            print("\n" + "="*60)
            print("📊 ANALYSIS SUGGESTIONS")
            print("="*60)
            suggestions = workflow.analyze_for_response(threads, skip_stats)
            for suggestion in suggestions:
                print(f"{suggestion}")
            
            print(f"\n✅ Review session complete! Check the '{session_dir}' directory for organized threads.")
            print(f"💡 Next steps:")
            print(f"   • Review thread files marked [NEEDS RESPONSE]")
            print(f"   • Draft responses: presto append --thread <N> --content '<response>'")
            print(f"   • Post replies: presto post <N> (or --all for batch)")
            return

if __name__ == "__main__":
    main() 
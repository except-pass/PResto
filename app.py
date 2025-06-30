#!/usr/bin/env python3
"""
Presto: GitHub PR Comment Workflow Tool

This script helps fetch and analyze comments from GitHub PRs, then assists with generating responses.
"""

def display_bootstrap_prompt():
    """Display the comprehensive workflow documentation as a bootstrap prompt"""
    print("""
Presto: GitHub PR Comment Workflow Tool

This script helps fetch and analyze comments from GitHub PRs, then assists with generating responses.

=== PEER REVIEW WORKFLOW SYSTEM ===

This tool implements a comprehensive, systematic approach to handling PR review comments
that ensures thorough, contextual, and actionable responses. The workflow is designed
to help maintain high code quality and effective communication during peer reviews.

WORKFLOW OVERVIEW:
1. THREAD EXTRACTION & ORGANIZATION
2. INTELLIGENT TRIAGE 
3. CONTEXTUAL ANALYSIS
4. CRAFTED RESPONSES
5. IMPLEMENTATION & FOLLOW-UP
6. AUTOMATED POSTING

--- DETAILED WORKFLOW ---

PHASE 1: THREAD EXTRACTION & ORGANIZATION (ALWAYS EXECUTED)
- Fetch all PR comments (general + review/inline comments)
- Group comments into conversation threads based on reply relationships
- Create a dedicated directory for this PR review session (e.g., `pr_18_review_YYYYMMDD_HHMMSS/`)
- Write each thread to a separate file:
  * File naming: `thread_01_author_topic.md`, `thread_02_author_topic.md`, etc.
  * Include all message IDs, timestamps, authors, file paths, line numbers
  * Preserve threading structure with proper indentation
  * Add metadata: thread status, priority, complexity indicators

PHASE 2: INTELLIGENT TRIAGE (Automated + Human Judgment)
For each thread, determine if it needs addressing:
- SKIP if thread is marked as resolved/closed
- SKIP if current user was the last person to comment (avoid over-commenting)
- SKIP if thread is just informational (no questions/issues raised)
- ANALYZE for threads with:
  * Direct questions requiring answers
  * Concerns about code quality, security, performance
  * Requests for clarification or changes
  * Missing functionality or documentation
  * Design disagreements or suggestions
- ASK USER for ambiguous cases where automated judgment is unclear
- PRIORITIZE threads by impact: Critical > High > Medium > Low

PHASE 3: CONTEXTUAL ANALYSIS (Deep Understanding)
For each thread requiring response:
- SCAN CODEBASE: Identify files/folders likely relevant to the discussion
  * Use semantic search based on thread content
  * Look for related code patterns, similar implementations
  * Find documentation, tests, configuration related to the topic
- DEEP DIVE: Build comprehensive understanding
  * Read relevant source files completely
  * Understand data flows, dependencies, architectural patterns
  * Review related test files and documentation
  * Check for similar patterns elsewhere in the codebase
  * Identify potential impacts of suggested changes
- CONTEXT BUILDING: Create a knowledge base for the response
  * Summarize current implementation
  * Identify constraints and dependencies
  * Note best practices and established patterns
  * Document any risks or trade-offs

PHASE 4: CRAFTED RESPONSES (Thoughtful + Actionable)
For each thread:
- CRAFT ANSWER: Write comprehensive, thoughtful response
  * Address the specific concern or question directly
  * Provide context and reasoning for decisions
  * Suggest specific solutions or alternatives
  * Include code examples where helpful
  * Reference relevant documentation or standards
- WRITE TO FILE: Save response draft before posting
  * File naming: `response_thread_01_author_topic.md`
  * Include original thread reference for clarity
  * Mark any action items or follow-up tasks needed
  * Note any code changes that should be made

PHASE 5: IMPLEMENTATION & FOLLOW-UP (Action-Oriented)
For responses requiring code changes:
- OFFER TO IMPLEMENT: Ask user if they want to make the changes now
- MAKE CHANGES: If approved, implement the necessary modifications
  * Create new files, modify existing code
  * Add documentation, tests, examples as needed
  * Follow established code patterns and standards
- DOCUMENT CHANGES: Update the response file with:
  * List of files modified/created
  * Summary of changes made
  * Any additional considerations or notes
- GIT COMMIT: Create meaningful commit with descriptive message
  * Reference the PR and specific thread being addressed
  * Include co-author information when appropriate

PHASE 6: AUTOMATED POSTING (Threaded + Trackable)
- POST RESPONSES: Submit replies to correct threads using GitHub API
  * Ensure proper threading with `in_reply_to` relationships
  * Include references to any commits made
  * Add actionable next steps if applicable
- TRACK PROGRESS: Update thread files with posting status
- GENERATE SUMMARY: Create overview of review session
  * Threads addressed, changes made, follow-ups needed
  * Statistics on review coverage and responsiveness

--- BENEFITS OF THIS WORKFLOW ---

THOROUGHNESS: Deep codebase understanding before responding
CONSISTENCY: Systematic approach ensures no threads are missed  
QUALITY: Thoughtful, well-researched responses improve discussion
ACTIONABILITY: Concrete changes and follow-ups drive progress
TRACEABILITY: Clear record of decisions and implementations
EFFICIENCY: Automation reduces manual overhead and errors
COLLABORATION: Structured approach improves team communication

--- USAGE EXAMPLES ---

# Basic workflow (Phase 1 always executes)
presto --pr 18 --repo owner/repo

# Search for specific comments
presto --pr 18 --repo owner/repo --search "question"

# Reply to a comment
presto --pr 18 --repo owner/repo --reply 12345 --reply-body "Your response here"

# Save additional formatted output
presto --pr 18 --repo owner/repo --save

--- GETTING STARTED ---

To begin using this tool:
1. Run `presto --pr <PR_NUMBER> --repo <OWNER/REPO>` to start Phase 1
2. Review the organized thread files in the created directory
3. Use `--search <text>` to find specific comments requiring attention
4. Use `--reply <comment_id> --reply-body <response>` to respond to comments
5. Follow the 6-phase workflow for comprehensive PR review

For help with specific commands, run `presto --help`
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
    
    def analyze_for_response(self, pr_data: Dict[str, Any]) -> List[str]:
        """Analyze comments and suggest areas that need responses"""
        suggestions = []
        
        comments = pr_data.get('comments', [])
        review_comments = pr_data.get('review_comments', [])
        all_comments = comments + review_comments
        
        if not all_comments:
            suggestions.append("No comments to respond to yet.")
            return suggestions
        
        suggestions.append(f"Total comments: {len(comments)} general + {len(review_comments)} review = {len(all_comments)} total")
        
        # Check for questions (comments with question marks)
        questions = [c for c in all_comments if '?' in (c.get('body', '') or c.get('body', ''))]
        if questions:
            suggestions.append(f"Found {len(questions)} comments with questions that may need answers.")
        
        # Check for review requests
        review_requests = [c for c in all_comments if any(word in (c.get('body', '') or '').lower() 
                                                        for word in ['review', 'feedback', 'thoughts', 'opinion'])]
        if review_requests:
            suggestions.append(f"Found {len(review_requests)} comments requesting review or feedback.")
        
        # Check for concerns or issues
        concerns = [c for c in all_comments if any(word in (c.get('body', '') or '').lower() 
                                                 for word in ['concern', 'issue', 'problem', 'bug', 'error', 'missing', 'not found'])]
        if concerns:
            suggestions.append(f"Found {len(concerns)} comments mentioning concerns or issues.")
        
        # Check for unresolved discussions
        if len(all_comments) > 3:
            suggestions.append("Multiple comments found - check for ongoing discussions.")
        
        return suggestions
    
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
                    'priority': 'medium',
                    'status': 'unresolved',
                    'complexity': 'low'
                }
            }
        
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
            
            filename = f"thread_{thread_num:02d}_{author}_{topic}.md"
            filepath = os.path.join(session_dir, filename)
            
            # Write thread to file
            thread_content = self._format_thread_for_file(thread_data, thread_num)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(thread_content)
            
            thread_files.append(filepath)
            print(f"💾 Thread {thread_num}: {filename}")
            thread_num += 1
        
        # Create summary file
        summary_file = os.path.join(session_dir, "session_summary.md")
        summary_content = self._create_session_summary(pr_data, threads, session_dir)
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        print(f"📋 Session summary: session_summary.md")
        print(f"✅ Phase 1 Complete: {len(threads)} threads organized in {session_dir}")
        
        return session_dir
    
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
                        'priority': self._assess_priority(comment),
                        'status': 'unresolved',
                        'complexity': self._assess_complexity(comment)
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
                            'priority': self._assess_priority(comment),
                            'status': 'unresolved',
                            'complexity': self._assess_complexity(comment)
                        }
                    }
        
        return threads
    
    def _assess_priority(self, comment: Dict) -> str:
        """Assess priority level of a comment"""
        body = comment.get('body', '').lower()
        
        # High priority keywords
        high_priority = ['critical', 'urgent', 'security', 'bug', 'error', 'broken', 'failing']
        if any(keyword in body for keyword in high_priority):
            return 'high'
        
        # Medium priority keywords  
        medium_priority = ['question', '?', 'concern', 'issue', 'problem', 'unclear']
        if any(keyword in body for keyword in medium_priority):
            return 'medium'
        
        return 'low'
    
    def _assess_complexity(self, comment: Dict) -> str:
        """Assess complexity level of a comment"""
        body = comment.get('body', '')
        
        # High complexity indicators
        if len(body) > 500 or body.count('```') > 2:
            return 'high'
        
        # Medium complexity indicators
        if len(body) > 200 or '```' in body:
            return 'medium'
            
        return 'low'
    
    def _format_thread_for_file(self, thread_data: Dict, thread_num: int) -> str:
        """Format thread data for individual file"""
        main_comment = thread_data['main']
        replies = thread_data.get('replies', [])
        metadata = thread_data.get('metadata', {})
        
        output = []
        
        # Thread header with metadata
        output.append(f"# Thread {thread_num:02d}")
        output.append("")
        output.append("## Metadata")
        output.append(f"- **Type**: {thread_data.get('type', 'unknown')}")
        output.append(f"- **Status**: {metadata.get('status', 'unknown')}")
        output.append(f"- **Priority**: {metadata.get('priority', 'unknown')}")
        output.append(f"- **Complexity**: {metadata.get('complexity', 'unknown')}")
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
    
    def _create_session_summary(self, pr_data: Dict, threads: Dict, session_dir: str) -> str:
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
        
        # Priority breakdown
        priorities = {}
        for thread in threads.values():
            priority = thread.get('metadata', {}).get('priority', 'unknown')
            priorities[priority] = priorities.get(priority, 0) + 1
        
        output.append("## Priority Breakdown")
        output.append("")
        for priority, count in sorted(priorities.items()):
            output.append(f"- **{priority.title()}**: {count}")
        output.append("")
        
        # Thread list
        output.append("## Thread Files")
        output.append("")
        
        thread_num = 1
        sorted_threads = sorted(threads.items(), 
                               key=lambda x: x[1]['main'].get('created_at', x[1]['main'].get('createdAt', '')))
        
        for thread_id, thread_data in sorted_threads:
            main_comment = thread_data['main']
            author = main_comment.get('user', {}).get('login', main_comment.get('author', {}).get('login', 'unknown'))
            priority = thread_data.get('metadata', {}).get('priority', 'unknown')
            
            body = main_comment.get('body', '')
            topic = body.split('\n')[0][:50]
            
            output.append(f"{thread_num}. **{author}** ({priority}) - {topic}")
            thread_num += 1
        
        output.append("")
        output.append("## Next Steps")
        output.append("")
        output.append("1. Review each thread file for context")
        output.append("2. Prioritize responses based on priority levels")
        output.append("3. Use `presto --pr <PR> --repo <REPO> --search <text>` to find specific comments")
        output.append("4. Use `presto --pr <PR> --repo <REPO> --reply <comment_id> --reply-body <text>` to respond")
        output.append("")
        
        return "\n".join(output)

def main():
    # Handle bootstrap prompt when no arguments provided
    if len(sys.argv) == 1:
        display_bootstrap_prompt()
        return
    
    parser = argparse.ArgumentParser(description="Presto: GitHub PR Comment Workflow Tool")
    parser.add_argument("--repo", required=True,
                       help="Repository in format owner/repo")
    parser.add_argument("--pr", required=True, type=int, help="PR number to fetch comments from")
    parser.add_argument("--save", action="store_true", 
                       help="Additionally save formatted comments to a single file")
    parser.add_argument("--output", help="Output filename for --save option (optional)")
    parser.add_argument("--search", help="Search for comments containing specific text")
    parser.add_argument("--reply", help="Reply to a specific comment ID")
    parser.add_argument("--reply-body", help="Body text for the reply (use with --reply)")
    
    args = parser.parse_args()
    
    # Parse repository
    try:
        repo_owner, repo_name = args.repo.split('/')
    except ValueError:
        print("Error: Repository must be in format 'owner/repo'")
        sys.exit(1)
    
    # Initialize workflow
    workflow = PRCommentWorkflow(repo_owner, repo_name)
    
    # Fetch PR data
    print(f"🚀 Fetching PR #{args.pr} from {args.repo}...")
    pr_data = workflow.fetch_pr_comments(args.pr)
    
    if not pr_data:
        print("Failed to fetch PR data. Check the PR number and repository.")
        sys.exit(1)
    
    # Add repo info to pr_data for summary
    pr_data['repo'] = args.repo
    
    # PHASE 1: ALWAYS extract and organize threads (core workflow)
    print("\n" + "="*60)
    print("🔄 PHASE 1: THREAD EXTRACTION & ORGANIZATION")
    print("="*60)
    session_dir = workflow.extract_and_organize_threads(pr_data)
    
    # Handle specific operations if requested
    if args.reply:
        print("\n" + "="*60)
        print("💬 REPLY MODE")
        print("="*60)
        comment_info = workflow.get_comment_by_id(pr_data, args.reply)
        if not comment_info:
            print(f"Comment ID {args.reply} not found in PR #{args.pr}")
            sys.exit(1)
        
        if not args.reply_body:
            print("Error: --reply requires --reply-body")
            sys.exit(1)
                    
        success = workflow.reply_to_comment(args.pr, args.reply, args.reply_body, comment_info['type'])
        
        if success:
            print("🎉 Reply posted successfully!")
        else:
            print("❌ Failed to post reply.")
            sys.exit(1)
        return
    
    # Handle search functionality
    if args.search:
        print("\n" + "="*60)
        print(f"🔍 SEARCH MODE: '{args.search}'")
        print("="*60)
        matches = workflow.find_comment_by_text(pr_data, args.search)
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
                print(f"\n💡 To reply: presto --pr {args.pr} --repo {args.repo} --reply {match['id']} --reply-body '<your response>'")
        else:
            print("No matching comments found.")
    
    # Optional: Also save formatted comments to single file if requested
    if args.save:
        print("\n" + "="*60)
        print("💾 SAVING FORMATTED COMMENTS")
        print("="*60)
        formatted_content = workflow.format_comments(pr_data)
        workflow.save_to_file(formatted_content, args.output)
    
    # Provide analysis suggestions
    print("\n" + "="*60)
    print("📊 ANALYSIS SUGGESTIONS")
    print("="*60)
    suggestions = workflow.analyze_for_response(pr_data)
    for suggestion in suggestions:
        print(f"- {suggestion}")
    
    print(f"\n✅ Review session complete! Check the '{session_dir}' directory for organized threads.")

if __name__ == "__main__":
    main() 
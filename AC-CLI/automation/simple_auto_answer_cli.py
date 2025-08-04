#!/usr/bin/env python3
"""
AC Backend Automation CLI - Simple Automatic Question Answering for All Users (No Rich dependency)

This CLI allows users to:
1. Select a question set by ID
2. Get all created users from the system
3. Automatically answer all questions in the set for each user with random selections
4. Provide detailed progress and statistics
"""

import requests
import json
import sys
import random
import time
from typing import Dict, List, Optional, Tuple

class ACBackendAPI:
    """Client for interacting with the AC Backend API"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make a request to the API"""
        url = f"{self.base_url}/api/v0/collections/{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            return response
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {e}")
    
    def get_all_members(self) -> List[Dict]:
        """Get all members from the system"""
        response = self._make_request("GET", "members/")
        if response.status_code == 200:
            data = response.json().get('data', {})
            return data.get('data', [])
        return []
    
    def get_question_sets(self) -> List[Dict]:
        """Get all question sets"""
        response = self._make_request("GET", "question-sets/")
        if response.status_code == 200:
            data = response.json().get('data', {})
            return data.get('data', [])
        return []
    
    def get_question_set_by_id(self, question_set_id: str) -> Optional[Dict]:
        """Get a specific question set with embedded questions"""
        response = self._make_request("GET", f"question-sets/{question_set_id}")
        if response.status_code == 200:
            return response.json().get('data')
        return None
    
    def submit_member_answer(self, member_id: str, question_id: str, answer_id: str) -> bool:
        """Submit a member's answer to a question"""
        data = {
            "memberId": member_id,
            "questionId": question_id,
            "answerId": answer_id
        }
        response = self._make_request("POST", "member-answers", json=data)
        return response.status_code == 201
    
    def get_member_answers(self, member_id: str) -> List[Dict]:
        """Get all answers for a specific member"""
        response = self._make_request("GET", f"member-answers/?memberId_eq={member_id}")
        if response.status_code == 200:
            data = response.json().get('data', {})
            return data.get('data', [])
        return []

class AutomationStats:
    """Track automation statistics"""
    
    def __init__(self):
        self.total_users = 0
        self.total_questions = 0
        self.total_answers_submitted = 0
        self.successful_submissions = 0
        self.failed_submissions = 0
        self.skipped_questions = 0
        self.start_time = None
        self.end_time = None
    
    def start_timer(self):
        """Start the automation timer"""
        self.start_time = time.time()
    
    def end_timer(self):
        """End the automation timer"""
        self.end_time = time.time()
    
    def get_duration(self) -> float:
        """Get the duration in seconds"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0
    
    def record_success(self):
        """Record a successful answer submission"""
        self.successful_submissions += 1
        self.total_answers_submitted += 1
    
    def record_failure(self):
        """Record a failed answer submission"""
        self.failed_submissions += 1
        self.total_answers_submitted += 1
    
    def record_skip(self):
        """Record a skipped question"""
        self.skipped_questions += 1

class SimpleAutoAnswerCLI:
    """Simple automated question answering CLI"""
    
    def __init__(self):
        self.api = ACBackendAPI()
        self.stats = AutomationStats()
        
    def display_banner(self):
        """Display welcome banner"""
        print("=" * 80)
        print("         AC Backend - Automated Question Answering CLI")
        print("   Automatically answer questions for all users with random selections")
        print("=" * 80)
        print()
    
    def display_question_sets_table(self, question_sets: List[Dict]):
        """Display question sets in a table format"""
        print("Available Question Sets:")
        print("-" * 80)
        print(f"{'ID':<10} {'Name':<40} {'Questions':<10}")
        print("-" * 80)
        
        for qs in question_sets:
            question_count = len(qs.get('questions', []))
            print(f"{str(qs.get('id', 'N/A')):<10} {qs.get('name', 'Unnamed'):<40} {str(question_count):<10}")
        
        print("-" * 80)
        print()
    
    def get_question_set_selection(self) -> Optional[Dict]:
        """Display available question sets and get user selection"""
        try:
            question_sets = self.api.get_question_sets()
            
            if not question_sets:
                print("❌ No question sets available")
                return None
            
            self.display_question_sets_table(question_sets)
            
            while True:
                question_set_id = input("Enter Question Set ID: ").strip()
                
                # Find the selected question set
                selected_qs = next((qs for qs in question_sets if str(qs.get('id')) == question_set_id), None)
                
                if selected_qs:
                    # Get the full question set with embedded questions
                    full_qs = self.api.get_question_set_by_id(question_set_id)
                    if full_qs:
                        questions = full_qs.get('questions', [])
                        print(f"✅ Selected: {full_qs.get('name', 'Unnamed')} ({len(questions)} questions)")
                        return full_qs
                    else:
                        print("❌ Error loading question set details")
                        return None
                else:
                    print("❌ Invalid Question Set ID. Please try again.")
                    
        except Exception as e:
            print(f"❌ Error loading question sets: {e}")
            return None
    
    def get_all_users(self) -> List[Dict]:
        """Get all users from the system"""
        try:
            members = self.api.get_all_members()
            if not members:
                print("⚠️  No users found in the system")
                return []
            
            print(f"✅ Found {len(members)} users in the system")
            return members
            
        except Exception as e:
            print(f"❌ Error loading users: {e}")
            return []
    
    def display_user_summary(self, users: List[Dict]):
        """Display a summary of users to be processed"""
        if not users:
            return
        
        print("\nUsers to Process (Preview):")
        print("-" * 80)
        print(f"{'User ID':<10} {'Name':<30} {'Social Contact':<30}")
        print("-" * 80)
        
        # Show first 10 users
        for user in users[:10]:
            print(f"{str(user.get('userId', 'N/A')):<10} {user.get('name', 'Unknown'):<30} {user.get('socialContact', 'N/A'):<30}")
        
        if len(users) > 10:
            print(f"{'...':<10} {'...':<30} ... and {len(users) - 10} more users")
        
        print("-" * 80)
        print()
    
    def check_existing_answers(self, member_id: str, question_ids: List[str]) -> List[str]:
        """Check which questions the member has already answered"""
        try:
            existing_answers = self.api.get_member_answers(member_id)
            answered_question_ids = [answer.get('questionId') for answer in existing_answers]
            return [qid for qid in question_ids if qid in answered_question_ids]
        except Exception:
            return []  # If we can't check, assume no answers exist
    
    def select_random_answer(self, question: Dict) -> Optional[str]:
        """Select a random answer from the question's available answers"""
        answers = question.get('answers', [])
        if not answers:
            return None
        
        # Select a random answer
        selected_answer = random.choice(answers)
        return selected_answer.get('id')
    
    def display_progress(self, current: int, total: int, prefix: str = "Progress"):
        """Display a simple progress indicator"""
        percent = int((current / total) * 100) if total > 0 else 0
        bar_length = 40
        filled_length = int(bar_length * current // total) if total > 0 else 0
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        print(f"\r{prefix}: |{bar}| {percent}% ({current}/{total})", end='', flush=True)
    
    def process_user_questions(self, user: Dict, questions: List[Dict], user_idx: int, total_users: int) -> Tuple[int, int, int]:
        """Process all questions for a single user"""
        member_id = user.get('id')
        user_name = user.get('name', 'Unknown')
        success_count = 0
        failure_count = 0
        skip_count = 0
        
        print(f"\n👤 Processing user {user_idx + 1}/{total_users}: {user_name}")
        
        # Check for existing answers
        question_ids = [q.get('id') for q in questions]
        existing_answered = self.check_existing_answers(member_id, question_ids)
        
        for i, question in enumerate(questions):
            question_id = question.get('id')
            
            # Display progress
            self.display_progress(i + 1, len(questions), f"  Questions for {user_name}")
            
            # Skip if already answered
            if question_id in existing_answered:
                skip_count += 1
                self.stats.record_skip()
                continue
            
            # Select random answer
            answer_id = self.select_random_answer(question)
            if not answer_id:
                failure_count += 1
                self.stats.record_failure()
                continue
            
            # Submit answer
            try:
                if self.api.submit_member_answer(member_id, question_id, answer_id):
                    success_count += 1
                    self.stats.record_success()
                else:
                    failure_count += 1
                    self.stats.record_failure()
            except Exception as e:
                failure_count += 1
                self.stats.record_failure()
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.1)
        
        print()  # New line after progress bar
        print(f"  ✅ Success: {success_count} | ❌ Failed: {failure_count} | ⏭️  Skipped: {skip_count}")
        
        return success_count, failure_count, skip_count
    
    def run_automation(self, question_set: Dict, users: List[Dict]):
        """Run the automated question answering process"""
        questions = question_set.get('questions', [])
        question_set_name = question_set.get('name', 'Unknown')
        
        if not questions:
            print("❌ No questions found in the selected question set")
            return
        
        # Initialize statistics
        self.stats.total_users = len(users)
        self.stats.total_questions = len(questions)
        total_operations = len(users) * len(questions)
        
        print(f"🚀 Starting automation for '{question_set_name}'")
        print(f"📊 {len(users)} users × {len(questions)} questions = {total_operations} total operations")
        print()
        
        # Confirm before starting
        confirm = input("Start automated answering process? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("⚠️  Automation cancelled")
            return
        
        print("\n" + "="*80)
        print("STARTING AUTOMATION")
        print("="*80)
        
        self.stats.start_timer()
        
        # Process each user
        user_results = []
        
        for user_idx, user in enumerate(users):
            success, failure, skip = self.process_user_questions(user, questions, user_idx, len(users))
            user_results.append({
                'user': user.get('name', 'Unknown'),
                'success': success,
                'failure': failure,
                'skip': skip
            })
        
        self.stats.end_timer()
        
        # Display final results
        self.display_final_results(question_set_name, user_results)
    
    def display_final_results(self, question_set_name: str, user_results: List[Dict]):
        """Display comprehensive automation results"""
        print("\n" + "="*80)
        print("                        AUTOMATION COMPLETE!")
        print("="*80)
        
        # Overall statistics
        duration = self.stats.get_duration()
        
        print(f"Question Set: {question_set_name}")
        print("-" * 80)
        print(f"✅ Successful submissions: {self.stats.successful_submissions}")
        print(f"❌ Failed submissions: {self.stats.failed_submissions}")
        print(f"⏭️  Skipped (already answered): {self.stats.skipped_questions}")
        print(f"📊 Total operations: {self.stats.total_answers_submitted + self.stats.skipped_questions}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        
        if duration > 0:
            rate = (self.stats.total_answers_submitted + self.stats.skipped_questions) / duration
            print(f"⚡ Rate: {rate:.2f} operations/sec")
        
        # Success rate calculation
        if self.stats.total_answers_submitted > 0:
            success_rate = (self.stats.successful_submissions / self.stats.total_answers_submitted) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print("-" * 80)
        
        # Per-user results table
        if user_results:
            print("\nPer-User Results:")
            print("-" * 80)
            print(f"{'User':<30} {'✅ Success':<10} {'❌ Failed':<10} {'⏭️ Skipped':<10} {'📊 Total':<10}")
            print("-" * 80)
            
            for result in user_results:
                total = result['success'] + result['failure'] + result['skip']
                print(f"{result['user']:<30} {result['success']:<10} {result['failure']:<10} {result['skip']:<10} {total:<10}")
            
            print("-" * 80)
        
        print("="*80)
    
    def run(self):
        """Main CLI loop"""
        try:
            self.display_banner()
            
            # Get question set selection
            question_set = self.get_question_set_selection()
            if not question_set:
                return
            
            print()
            
            # Get all users
            users = self.get_all_users()
            if not users:
                return
            
            print()
            
            # Display user summary
            self.display_user_summary(users)
            
            # Run automation
            self.run_automation(question_set, users)
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Automation interrupted by user")
            if self.stats.start_time:
                self.stats.end_timer()
                print(f"Automation ran for {self.stats.get_duration():.2f} seconds")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")

def main():
    """Entry point"""
    cli = SimpleAutoAnswerCLI()
    cli.run()

if __name__ == "__main__":
    main()

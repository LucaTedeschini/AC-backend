#!/usr/bin/env python3
"""
AC Backend Automation CLI - Automatic Question Answering for All Users

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
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, TaskID
from rich.text import Text
from rich import print as rprint

class ACBackendAPI:
    """Client for interacting with the AC Backend API"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
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

class AutoAnswerCLI:
    """Automated question answering CLI"""
    
    def __init__(self):
        self.console = Console()
        self.api = ACBackendAPI()
        self.stats = AutomationStats()
        
    def display_banner(self):
        """Display welcome banner"""
        banner = Panel.fit(
            "[bold blue]AC Backend - Automated Question Answering CLI[/bold blue]\n"
            "[dim]Automatically answer questions for all users with random selections[/dim]",
            border_style="blue"
        )
        self.console.print(banner)
        self.console.print()
    
    def get_question_set_selection(self) -> Optional[Dict]:
        """Display available question sets and get user selection"""
        try:
            question_sets = self.api.get_question_sets()
            
            if not question_sets:
                self.console.print("[red]No question sets available[/red]")
                return None
            
            # Display question sets in a table
            table = Table(title="Available Question Sets")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Questions", style="yellow")
            
            for qs in question_sets:
                question_count = len(qs.get('questions', []))
                table.add_row(
                    str(qs.get('id', 'N/A')), 
                    qs.get('name', 'Unnamed'),
                    str(question_count)
                )
            
            self.console.print(table)
            self.console.print()
            
            while True:
                question_set_id = Prompt.ask("[bold]Enter Question Set ID[/bold]")
                
                # Find the selected question set
                selected_qs = next((qs for qs in question_sets if str(qs.get('id')) == question_set_id), None)
                
                if selected_qs:
                    # Get the full question set with embedded questions
                    full_qs = self.api.get_question_set_by_id(question_set_id)
                    if full_qs:
                        questions = full_qs.get('questions', [])
                        self.console.print(f"[green]✓ Selected: {full_qs.get('name', 'Unnamed')} ({len(questions)} questions)[/green]")
                        return full_qs
                    else:
                        self.console.print("[red]Error loading question set details[/red]")
                        return None
                else:
                    self.console.print("[red]Invalid Question Set ID. Please try again.[/red]")
                    
        except Exception as e:
            self.console.print(f"[red]Error loading question sets: {e}[/red]")
            return None
    
    def get_all_users(self) -> List[Dict]:
        """Get all users from the system"""
        try:
            members = self.api.get_all_members()
            if not members:
                self.console.print("[yellow]No users found in the system[/yellow]")
                return []
            
            self.console.print(f"[green]✓ Found {len(members)} users in the system[/green]")
            return members
            
        except Exception as e:
            self.console.print(f"[red]Error loading users: {e}[/red]")
            return []
    
    def display_user_summary(self, users: List[Dict]):
        """Display a summary of users to be processed"""
        if not users:
            return
        
        # Show first few users as preview
        preview_table = Table(title="Users to Process (Preview)")
        preview_table.add_column("User ID", style="cyan")
        preview_table.add_column("Name", style="green")
        preview_table.add_column("Social Contact", style="yellow")
        
        # Show first 10 users
        for user in users[:10]:
            preview_table.add_row(
                str(user.get('userId', 'N/A')),
                user.get('name', 'Unknown'),
                user.get('socialContact', 'N/A')
            )
        
        if len(users) > 10:
            preview_table.add_row("...", "...", f"... and {len(users) - 10} more users")
        
        self.console.print(preview_table)
        self.console.print()
    
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
    
    def process_user_questions(self, user: Dict, questions: List[Dict], progress: Progress, task_id: TaskID) -> Tuple[int, int, int]:
        """Process all questions for a single user"""
        member_id = user.get('id')
        user_name = user.get('name', 'Unknown')
        success_count = 0
        failure_count = 0
        skip_count = 0
        
        # Check for existing answers
        question_ids = [q.get('id') for q in questions]
        existing_answered = self.check_existing_answers(member_id, question_ids)
        
        for i, question in enumerate(questions):
            question_id = question.get('id')
            question_text = question.get('question', 'Unknown question')
            
            # Skip if already answered
            if question_id in existing_answered:
                self.console.print(f"[yellow]⏭️  Skipping Q{i+1} for {user_name} (already answered)[/yellow]")
                skip_count += 1
                self.stats.record_skip()
                progress.advance(task_id)
                continue
            
            # Select random answer
            answer_id = self.select_random_answer(question)
            if not answer_id:
                self.console.print(f"[red]❌ No answers available for Q{i+1} for {user_name}[/red]")
                failure_count += 1
                self.stats.record_failure()
                progress.advance(task_id)
                continue
            
            # Submit answer
            try:
                if self.api.submit_member_answer(member_id, question_id, answer_id):
                    self.console.print(f"[green]✅ Q{i+1} answered for {user_name}[/green]")
                    success_count += 1
                    self.stats.record_success()
                else:
                    self.console.print(f"[red]❌ Failed to submit Q{i+1} for {user_name}[/red]")
                    failure_count += 1
                    self.stats.record_failure()
            except Exception as e:
                self.console.print(f"[red]❌ Error submitting Q{i+1} for {user_name}: {e}[/red]")
                failure_count += 1
                self.stats.record_failure()
            
            progress.advance(task_id)
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.1)
        
        return success_count, failure_count, skip_count
    
    def run_automation(self, question_set: Dict, users: List[Dict]):
        """Run the automated question answering process"""
        questions = question_set.get('questions', [])
        question_set_name = question_set.get('name', 'Unknown')
        
        if not questions:
            self.console.print("[red]No questions found in the selected question set[/red]")
            return
        
        # Initialize statistics
        self.stats.total_users = len(users)
        self.stats.total_questions = len(questions)
        total_operations = len(users) * len(questions)
        
        self.console.print(f"[blue]🚀 Starting automation for '{question_set_name}'[/blue]")
        self.console.print(f"[blue]📊 {len(users)} users × {len(questions)} questions = {total_operations} total operations[/blue]")
        self.console.print()
        
        # Confirm before starting
        if not Confirm.ask("[bold]Start automated answering process?[/bold]"):
            self.console.print("[yellow]Automation cancelled[/yellow]")
            return
        
        self.stats.start_timer()
        
        # Process each user with progress tracking
        with Progress() as progress:
            task = progress.add_task(f"Processing questions...", total=total_operations)
            
            user_results = []
            
            for user_idx, user in enumerate(users):
                user_name = user.get('name', 'Unknown')
                self.console.print(f"\n[bold cyan]👤 Processing user {user_idx + 1}/{len(users)}: {user_name}[/bold cyan]")
                
                success, failure, skip = self.process_user_questions(user, questions, progress, task)
                user_results.append({
                    'user': user_name,
                    'success': success,
                    'failure': failure,
                    'skip': skip
                })
        
        self.stats.end_timer()
        
        # Display final results
        self.display_final_results(question_set_name, user_results)
    
    def display_final_results(self, question_set_name: str, user_results: List[Dict]):
        """Display comprehensive automation results"""
        self.console.print("\n" + "="*80)
        
        # Overall statistics
        duration = self.stats.get_duration()
        
        summary_panel = Panel(
            f"[bold]Automation Complete for '{question_set_name}'![/bold]\n\n"
            f"[green]✅ Successful submissions: {self.stats.successful_submissions}[/green]\n"
            f"[red]❌ Failed submissions: {self.stats.failed_submissions}[/red]\n"
            f"[yellow]⏭️  Skipped (already answered): {self.stats.skipped_questions}[/yellow]\n"
            f"[blue]📊 Total operations: {self.stats.total_answers_submitted + self.stats.skipped_questions}[/blue]\n"
            f"[cyan]⏱️  Duration: {duration:.2f} seconds[/cyan]\n"
            f"[magenta]⚡ Rate: {(self.stats.total_answers_submitted + self.stats.skipped_questions) / duration:.2f} operations/sec[/magenta]",
            border_style="blue",
            title="📈 Automation Summary"
        )
        self.console.print(summary_panel)
        
        # Per-user results table
        if user_results:
            results_table = Table(title="Per-User Results")
            results_table.add_column("User", style="cyan")
            results_table.add_column("✅ Success", style="green", justify="center")
            results_table.add_column("❌ Failed", style="red", justify="center")
            results_table.add_column("⏭️ Skipped", style="yellow", justify="center")
            results_table.add_column("📊 Total", style="blue", justify="center")
            
            for result in user_results:
                total = result['success'] + result['failure'] + result['skip']
                results_table.add_row(
                    result['user'],
                    str(result['success']),
                    str(result['failure']),
                    str(result['skip']),
                    str(total)
                )
            
            self.console.print(results_table)
        
        # Success rate calculation
        if self.stats.total_answers_submitted > 0:
            success_rate = (self.stats.successful_submissions / self.stats.total_answers_submitted) * 100
            self.console.print(f"\n[bold]📈 Success Rate: {success_rate:.1f}%[/bold]")
    
    def run(self):
        """Main CLI loop"""
        try:
            self.display_banner()
            
            # Get question set selection
            question_set = self.get_question_set_selection()
            if not question_set:
                return
            
            self.console.print()
            
            # Get all users
            users = self.get_all_users()
            if not users:
                return
            
            self.console.print()
            
            # Display user summary
            self.display_user_summary(users)
            
            # Run automation
            self.run_automation(question_set, users)
            
        except KeyboardInterrupt:
            self.console.print("\n\n[yellow]⚠️  Automation interrupted by user[/yellow]")
            if self.stats.start_time:
                self.stats.end_timer()
                self.console.print(f"[cyan]Automation ran for {self.stats.get_duration():.2f} seconds[/cyan]")
        except Exception as e:
            self.console.print(f"\n[red]❌ Unexpected error: {e}[/red]")

def main():
    """Entry point"""
    cli = AutoAnswerCLI()
    cli.run()

if __name__ == "__main__":
    main()

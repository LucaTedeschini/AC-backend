#!/usr/bin/env python3
"""
AC Backend CLI - Interactive Question Answering Interface

This CLI allows users to:
1. Enter their member ID
2. Select a question set
3. Answer questions one by one using keyboard navigation
4. Submit answers to the AC backend server
"""

import requests
import json
import sys
from typing import Dict, List, Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
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
    
    def get_member_by_user_id(self, user_id: str) -> Optional[Dict]:
        """Get member by userId"""
        response = self._make_request("GET", f"members/?userId_eq={user_id}")
        if response.status_code == 200:
            data = response.json().get('data', {})
            members = data.get('data', [])
            if members:
                return members[0]  # Return first member found
        return None
    
    def get_question_sets(self) -> List[Dict]:
        """Get all question sets"""
        response = self._make_request("GET", "question-sets/")
        if response.status_code == 200:
            data = response.json().get('data', {})
            return data.get('data', [])  # Extract the actual data array from pagination structure
        return []
    
    def get_questions_by_ids(self, question_ids: List[str]) -> List[Dict]:
        """Get questions by their IDs with answers - DEPRECATED: Questions are now embedded in question sets"""
        questions = []
        for question_id in question_ids:
            response = self._make_request("GET", f"questions/{question_id}?relations=answers")
            if response.status_code == 200:
                questions.append(response.json().get('data'))
        return questions
    
    def submit_member_answer(self, member_id: str, question_id: str, answer_id: str) -> bool:
        """Submit a member's answer to a question"""
        data = {
            "memberId": member_id,
            "questionId": question_id,
            "answerId": answer_id
        }
        response = self._make_request("POST", "member-answers", json=data)
        return response.status_code == 201

class QuestionAnsweringCLI:
    """Interactive CLI for answering questions"""
    
    def __init__(self):
        self.console = Console()
        self.api = ACBackendAPI()
        
    def display_banner(self):
        """Display welcome banner"""
        banner = Panel.fit(
            "[bold blue]AC Backend - Question Answering CLI[/bold blue]\n"
            "[dim]Interactive interface for answering questions[/dim]",
            border_style="blue"
        )
        self.console.print(banner)
        self.console.print()
    
    def get_member_id(self) -> Optional[str]:
        """Get and validate member ID"""
        while True:
            user_id = Prompt.ask("[bold]Enter your User ID (numeric)[/bold]")
            
            if not user_id.strip():
                self.console.print("[red]User ID cannot be empty[/red]")
                continue
            
            # Validate member exists
            try:
                member = self.api.get_member_by_user_id(user_id)
                if member:
                    self.console.print(f"[green]✓ Member found: {member.get('name', 'Unknown')}[/green]")
                    return member.get('id')  # Return the UUID id for API calls
                else:
                    self.console.print("[red]Member not found. Please check your User ID.[/red]")
            except Exception as e:
                self.console.print(f"[red]Error validating member: {e}[/red]")
                
    def select_question_set(self) -> Optional[Dict]:
        """Display and select question set"""
        try:
            question_sets = self.api.get_question_sets()
            
            if not question_sets:
                self.console.print("[red]No question sets available[/red]")
                return None
            
            # Display question sets in a table
            table = Table(title="Available Question Sets")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            
            for qs in question_sets:
                table.add_row(str(qs.get('id', 'N/A')), qs.get('name', 'Unnamed'))
            
            self.console.print(table)
            self.console.print()
            
            while True:
                question_set_id = Prompt.ask("[bold]Enter Question Set ID[/bold]")
                
                # Find the selected question set
                selected_qs = next((qs for qs in question_sets if str(qs.get('id')) == question_set_id), None)
                
                if selected_qs:
                    self.console.print(f"[green]Selected question set: {selected_qs.get('name', 'Unnamed')}[/green]")
                    return selected_qs  # Return the question set directly with embedded questions
                else:
                    self.console.print("[red]Invalid Question Set ID. Please try again.[/red]")
                    
        except Exception as e:
            self.console.print(f"[red]Error loading question sets: {e}[/red]")
            return None
    
    def display_question_with_answers(self, question: Dict, question_num: int, total_questions: int) -> Optional[str]:
        """Display a question with its answers and get user selection"""
        self.console.print()
        
        # Question header
        header = f"Question {question_num}/{total_questions}"
        question_panel = Panel(
            f"[bold]{question.get('question', 'No question text')}[/bold]",
            title=header,
            border_style="green"
        )
        self.console.print(question_panel)
        
        answers = question.get('answers', [])
        if not answers:
            self.console.print("[red]No answers available for this question[/red]")
            return None
        
        # Display answers
        self.console.print("\n[bold]Available answers:[/bold]")
        for i, answer in enumerate(answers, 1):
            self.console.print(f"  {i}. {answer.get('answer', 'No answer text')}")
        
        # Get user selection
        while True:
            try:
                choice = Prompt.ask(
                    f"\n[bold]Select your answer (1-{len(answers)}) or 'q' to quit[/bold]"
                )
                
                if choice.lower() == 'q':
                    return None
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(answers):
                    selected_answer = answers[choice_num - 1]
                    
                    # Show selected answer and return immediately
                    answer_text = selected_answer.get('answer', 'Unknown answer')
                    self.console.print(f"[green]✓ You selected: {answer_text}[/green]")
                    return selected_answer.get('id')
                else:
                    self.console.print(f"[red]Please enter a number between 1 and {len(answers)}[/red]")
                    
            except ValueError:
                self.console.print("[red]Please enter a valid number or 'q' to quit[/red]")
    
    def process_questions(self, member_id: str, question_set: Dict):
        """Process all questions in the question set"""
        questions = question_set.get('questions', [])
        
        if not questions:
            self.console.print("[red]No questions found in this question set[/red]")
            return
        
        total_questions = len(questions)
        answered_count = 0
        
        self.console.print(f"[green]Found {total_questions} questions to answer[/green]")
        
        for i, question in enumerate(questions, 1):
            answer_id = self.display_question_with_answers(question, i, total_questions)
            
            if answer_id is None:
                if Confirm.ask("\n[yellow]Do you want to quit?[/yellow]"):
                    break
                continue
            
            # Submit answer
            try:
                question_id = question.get('id')
                if self.api.submit_member_answer(member_id, question_id, answer_id):
                    self.console.print("[green]✓ Answer submitted successfully![/green]")
                    answered_count += 1
                else:
                    self.console.print("[red]✗ Failed to submit answer[/red]")
            except Exception as e:
                self.console.print(f"[red]Error submitting answer: {e}[/red]")
        
        # Summary
        self.console.print()
        summary_panel = Panel(
            f"[bold]Session Complete![/bold]\n"
            f"Questions answered: {answered_count}/{total_questions}",
            border_style="blue"
        )
        self.console.print(summary_panel)
    
    def run(self):
        """Main CLI loop"""
        try:
            self.display_banner()
            
            # Get member ID
            member_id = self.get_member_id()
            if not member_id:
                return
            
            self.console.print()
            
            # Select question set
            question_set = self.select_question_set()
            if not question_set:
                return
            
            # Process questions
            self.process_questions(member_id, question_set)
            
        except KeyboardInterrupt:
            self.console.print("\n\n[yellow]Session interrupted by user[/yellow]")
        except Exception as e:
            self.console.print(f"\n[red]Unexpected error: {e}[/red]")

def main():
    """Entry point"""
    cli = QuestionAnsweringCLI()
    cli.run()

if __name__ == "__main__":
    main()

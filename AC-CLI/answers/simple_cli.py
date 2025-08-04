#!/usr/bin/env python3
"""
AC Backend CLI - Simple Question Answering Interface (No Rich dependency)

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

class SimpleQuestionAnsweringCLI:
    """Simple CLI for answering questions"""
    
    def __init__(self):
        self.api = ACBackendAPI()
        
    def display_banner(self):
        """Display welcome banner"""
        print("=" * 60)
        print("          AC Backend - Question Answering CLI")
        print("     Interactive interface for answering questions")
        print("=" * 60)
        print()
    
    def get_member_id(self) -> Optional[str]:
        """Get and validate member ID"""
        while True:
            user_id = input("Enter your User ID (numeric): ").strip()
            
            if not user_id:
                print("❌ User ID cannot be empty")
                continue
            
            # Validate member exists
            try:
                member = self.api.get_member_by_user_id(user_id)
                if member:
                    print(f"✅ Member found: {member.get('name', 'Unknown')}")
                    return member.get('id')  # Return the UUID id for API calls
                else:
                    print("❌ Member not found. Please check your User ID.")
            except Exception as e:
                print(f"❌ Error validating member: {e}")
                
    def select_question_set(self) -> Optional[Dict]:
        """Display and select question set"""
        try:
            question_sets = self.api.get_question_sets()
            
            if not question_sets:
                print("❌ No question sets available")
                return None
            
            # Display question sets
            print("\nAvailable Question Sets:")
            print("-" * 50)
            print(f"{'ID':<20} {'Name'}")
            print("-" * 50)
            
            for qs in question_sets:
                print(f"{str(qs.get('id', 'N/A')):<20} {qs.get('name', 'Unnamed')}")
            
            print("-" * 50)
            print()
            
            while True:
                question_set_id = input("Enter Question Set ID: ").strip()
                
                # Find the selected question set
                selected_qs = next((qs for qs in question_sets if str(qs.get('id')) == question_set_id), None)
                
                if selected_qs:
                    print(f"✅ Selected question set: {selected_qs.get('name', 'Unnamed')}")
                    return selected_qs  # Return the question set directly with embedded questions
                else:
                    print("❌ Invalid Question Set ID. Please try again.")
                    
        except Exception as e:
            print(f"❌ Error loading question sets: {e}")
            return None
    
    def display_question_with_answers(self, question: Dict, question_num: int, total_questions: int) -> Optional[str]:
        """Display a question with its answers and get user selection"""
        print()
        print("=" * 60)
        print(f"                Question {question_num}/{total_questions}")
        print("=" * 60)
        print()
        print(f"📝 {question.get('question', 'No question text')}")
        print()
        
        answers = question.get('answers', [])
        if not answers:
            print("❌ No answers available for this question")
            return None
        
        # Display answers
        print("Available answers:")
        for i, answer in enumerate(answers, 1):
            print(f"  {i}. {answer.get('answer', 'No answer text')}")
        
        print()
        
        # Get user selection
        while True:
            try:
                choice = input(f"Select your answer (1-{len(answers)}) or 'q' to quit: ").strip()
                
                if choice.lower() == 'q':
                    return None
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(answers):
                    selected_answer = answers[choice_num - 1]
                    
                    # Show selected answer and return immediately
                    answer_text = selected_answer.get('answer', 'Unknown answer')
                    print(f"✅ You selected: '{answer_text}'")
                    return selected_answer.get('id')
                else:
                    print(f"❌ Please enter a number between 1 and {len(answers)}")
                    
            except ValueError:
                print("❌ Please enter a valid number or 'q' to quit")
    
    def process_questions(self, member_id: str, question_set: Dict):
        """Process all questions in the question set"""
        questions = question_set.get('questions', [])
        
        if not questions:
            print("❌ No questions found in this question set")
            return
        
        total_questions = len(questions)
        answered_count = 0
        
        print(f"✅ Found {total_questions} questions to answer")
        
        for i, question in enumerate(questions, 1):
            answer_id = self.display_question_with_answers(question, i, total_questions)
            
            if answer_id is None:
                quit_confirm = input("\nDo you want to quit? (y/n): ").strip().lower()
                if quit_confirm in ['y', 'yes']:
                    break
                continue
            
            # Submit answer
            try:
                question_id = question.get('id')
                print("🔄 Submitting answer...")
                
                if self.api.submit_member_answer(member_id, question_id, answer_id):
                    print("✅ Answer submitted successfully!")
                    answered_count += 1
                else:
                    print("❌ Failed to submit answer")
            except Exception as e:
                print(f"❌ Error submitting answer: {e}")
        
        # Summary
        print()
        print("=" * 60)
        print("                   SESSION COMPLETE!")
        print("=" * 60)
        print(f"Questions answered: {answered_count}/{total_questions}")
        print("=" * 60)
    
    def run(self):
        """Main CLI loop"""
        try:
            self.display_banner()
            
            # Get member ID
            member_id = self.get_member_id()
            if not member_id:
                return
            
            print()
            
            # Select question set
            question_set = self.select_question_set()
            if not question_set:
                return
            
            print(f"\n✅ Selected question set: {question_set.get('name', 'Unnamed')}")
            
            # Process questions
            self.process_questions(member_id, question_set)
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Session interrupted by user")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")

def main():
    """Entry point"""
    cli = SimpleQuestionAnsweringCLI()
    cli.run()

if __name__ == "__main__":
    main()

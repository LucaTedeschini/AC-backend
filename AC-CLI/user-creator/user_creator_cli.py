#!/usr/bin/env python3
"""
AC Backend User Creator CLI - Random User Creation Interface

This CLI allows users to:
1. Generate random English names
2. Create users with unique userIds
3. Submit user data to the AC backend server
"""

import requests
import json
import sys
import random
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
    
    def get_all_members(self) -> List[Dict]:
        """Get all members to check for existing userIds"""
        response = self._make_request("GET", "members/")
        if response.status_code == 200:
            data = response.json().get('data', {})
            return data.get('data', [])
        return []
    
    def create_member(self, name: str, user_id: int, social_contact: str) -> bool:
        """Create a new member"""
        data = {
            "name": name,
            "userId": user_id,
            "socialContact": social_contact
        }
        response = self._make_request("POST", "members/", json=data)
        return response.status_code == 201

class RandomNameGenerator:
    """Generator for random English names"""
    
    FIRST_NAMES = [
        "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
        "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
        "Thomas", "Sarah", "Christopher", "Karen", "Charles", "Nancy", "Daniel", "Lisa",
        "Matthew", "Betty", "Anthony", "Helen", "Mark", "Sandra", "Donald", "Donna",
        "Steven", "Carol", "Paul", "Ruth", "Andrew", "Sharon", "Joshua", "Michelle",
        "Kenneth", "Laura", "Kevin", "Sarah", "Brian", "Kimberly", "George", "Deborah",
        "Edward", "Dorothy", "Ronald", "Lisa", "Timothy", "Nancy", "Jason", "Karen",
        "Jeffrey", "Betty", "Ryan", "Helen", "Jacob", "Sandra", "Gary", "Donna",
        "Nicholas", "Carol", "Eric", "Ruth", "Jonathan", "Sharon", "Stephen", "Michelle",
        "Larry", "Laura", "Justin", "Sarah", "Scott", "Kimberly", "Brandon", "Deborah",
        "Benjamin", "Dorothy", "Samuel", "Amy", "Gregory", "Angela", "Alexander", "Ashley",
        "Patrick", "Brenda", "Frank", "Emma", "Raymond", "Olivia", "Jack", "Cynthia",
        "Dennis", "Marie", "Jerry", "Janet", "Tyler", "Catherine", "Aaron", "Frances",
        "Jose", "Christine", "Henry", "Samantha", "Adam", "Debra", "Douglas", "Rachel",
        "Nathan", "Carolyn", "Peter", "Virginia", "Zachary", "Maria", "Kyle", "Heather",
        "Walter", "Diane", "Harold", "Julie", "Arthur", "Joyce", "Carl", "Victoria",
        "Jordan", "Kelly", "Eugene", "Christina", "Wayne", "Joan", "Ralph", "Evelyn",
        "Louis", "Lauren", "Philip", "Judith", "Bobby", "Megan", "Mason", "Cheryl",
        "Roy", "Andrea", "Eugene", "Hannah", "Louis", "Jacqueline", "Philip", "Martha",
        "Johnny", "Gloria", "Ralph", "Teresa", "Wayne", "Sara", "Roger", "Janice",
        "Jesse", "Marie", "Howard", "Julia", "Juan", "Kathryn", "Gerald", "Frances",
        "Harold", "Christine", "Carl", "Brittany", "Arthur", "Samantha", "Eugene", "Debra"
    ]
    
    LAST_NAMES = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
        "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
        "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
        "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
        "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
        "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
        "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy",
        "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey",
        "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson",
        "Watson", "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza",
        "Ruiz", "Hughes", "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers",
        "Long", "Ross", "Foster", "Jimenez", "Powell", "Jenkins", "Perry", "Russell",
        "Sullivan", "Bell", "Coleman", "Butler", "Henderson", "Barnes", "Gonzales", "Fisher",
        "Vasquez", "Simmons", "Romero", "Jordan", "Patterson", "Alexander", "Hamilton", "Graham",
        "Reynolds", "Griffin", "Wallace", "Moreno", "West", "Cole", "Hayes", "Bryant"
    ]
    
    def generate_random_name(self) -> str:
        """Generate a random full name"""
        first_name = random.choice(self.FIRST_NAMES)
        last_name = random.choice(self.LAST_NAMES)
        return f"{first_name} {last_name}"
    
    def generate_social_contact(self, name: str) -> str:
        """Generate a social contact handle from the name"""
        # Convert to lowercase and replace spaces with underscores
        handle = name.lower().replace(" ", "_")
        # Add random number to make it more unique
        random_num = random.randint(10, 999)
        return f"@{handle}{random_num}"

class UserCreatorCLI:
    """Interactive CLI for creating users"""
    
    def __init__(self):
        self.console = Console()
        self.api = ACBackendAPI()
        self.name_generator = RandomNameGenerator()
        
    def display_banner(self):
        """Display welcome banner"""
        banner = Panel.fit(
            "[bold blue]AC Backend - User Creator CLI[/bold blue]\n"
            "[dim]Create random users for the AC backend system[/dim]",
            border_style="blue"
        )
        self.console.print(banner)
        self.console.print()
    
    def get_existing_user_ids(self) -> List[int]:
        """Get all existing user IDs to avoid duplicates"""
        try:
            members = self.api.get_all_members()
            return [member.get('userId') for member in members if member.get('userId')]
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not fetch existing user IDs: {e}[/yellow]")
            return []
    
    def generate_unique_user_id(self, existing_ids: List[int]) -> int:
        """Generate a unique user ID"""
        max_attempts = 1000
        attempts = 0
        
        while attempts < max_attempts:
            # Generate random user ID between 1000 and 9999 for better uniqueness
            user_id = random.randint(1000, 9999)
            if user_id not in existing_ids:
                return user_id
            attempts += 1
        
        # Fallback: find the next available ID
        if existing_ids:
            return max(existing_ids) + 1
        return 1000
    
    def create_single_user(self) -> bool:
        """Create a single user with random data"""
        # Generate random name
        name = self.name_generator.generate_random_name()
        social_contact = self.name_generator.generate_social_contact(name)
        
        # Get existing user IDs and generate unique one
        existing_ids = self.get_existing_user_ids()
        user_id = self.generate_unique_user_id(existing_ids)
        
        # Display generated user data
        user_table = Table(title="Generated User Data")
        user_table.add_column("Field", style="cyan")
        user_table.add_column("Value", style="green")
        
        user_table.add_row("Name", name)
        user_table.add_row("User ID", str(user_id))
        user_table.add_row("Social Contact", social_contact)
        
        self.console.print(user_table)
        self.console.print()
        
        # Confirm creation
        if not Confirm.ask("[bold]Create this user?[/bold]"):
            self.console.print("[yellow]User creation cancelled[/yellow]")
            return False
        
        # Create user
        try:
            self.console.print("[blue]Creating user...[/blue]")
            if self.api.create_member(name, user_id, social_contact):
                self.console.print(f"[green]✓ User '{name}' created successfully![/green]")
                return True
            else:
                self.console.print("[red]✗ Failed to create user[/red]")
                return False
        except Exception as e:
            self.console.print(f"[red]✗ Error creating user: {e}[/red]")
            return False
    
    def create_multiple_users(self) -> int:
        """Create multiple users in batch"""
        while True:
            try:
                count = int(Prompt.ask("[bold]How many users to create?[/bold]", default="5"))
                if count > 0:
                    break
                else:
                    self.console.print("[red]Please enter a positive number[/red]")
            except ValueError:
                self.console.print("[red]Please enter a valid number[/red]")
        
        self.console.print(f"[blue]Creating {count} users...[/blue]")
        self.console.print()
        
        success_count = 0
        existing_ids = self.get_existing_user_ids()
        
        for i in range(count):
            # Generate user data
            name = self.name_generator.generate_random_name()
            social_contact = self.name_generator.generate_social_contact(name)
            user_id = self.generate_unique_user_id(existing_ids)
            existing_ids.append(user_id)  # Add to avoid duplicates in this batch
            
            try:
                if self.api.create_member(name, user_id, social_contact):
                    self.console.print(f"[green]✓ Created: {name} (ID: {user_id})[/green]")
                    success_count += 1
                else:
                    self.console.print(f"[red]✗ Failed: {name} (ID: {user_id})[/red]")
            except Exception as e:
                self.console.print(f"[red]✗ Error creating {name}: {e}[/red]")
        
        return success_count
    
    def display_creation_summary(self, success_count: int, total_count: int):
        """Display creation summary"""
        self.console.print()
        summary_panel = Panel(
            f"[bold]User Creation Complete![/bold]\n"
            f"Successfully created: {success_count}/{total_count} users",
            border_style="blue"
        )
        self.console.print(summary_panel)
    
    def run(self):
        """Main CLI loop"""
        try:
            self.display_banner()
            
            while True:
                self.console.print("[bold]User Creation Options:[/bold]")
                self.console.print("1. Create single user")
                self.console.print("2. Create multiple users")
                self.console.print("3. Exit")
                self.console.print()
                
                choice = Prompt.ask("[bold]Select option[/bold]", choices=["1", "2", "3"], default="1")
                
                if choice == "1":
                    self.create_single_user()
                elif choice == "2":
                    success_count = self.create_multiple_users()
                    total_count = int(Prompt.ask("[bold]Total users attempted[/bold]", default="0"))
                    self.display_creation_summary(success_count, total_count)
                elif choice == "3":
                    self.console.print("[blue]Goodbye![/blue]")
                    break
                
                self.console.print()
                if not Confirm.ask("[bold]Continue with more operations?[/bold]"):
                    break
                    
        except KeyboardInterrupt:
            self.console.print("\n\n[yellow]Session interrupted by user[/yellow]")
        except Exception as e:
            self.console.print(f"\n[red]Unexpected error: {e}[/red]")

def main():
    """Entry point"""
    cli = UserCreatorCLI()
    cli.run()

if __name__ == "__main__":
    main()

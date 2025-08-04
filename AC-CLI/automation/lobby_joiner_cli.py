#!/usr/bin/env python3
"""
AC Backend Lobby Joiner CLI - Join All Users to Available Lobbies

This CLI allows users to:
1. Display available lobbies
2. Select a lobby to join
3. Automatically join all users to the selected lobby
4. Provide detailed progress and statistics
"""

import requests
import json
import sys
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
    
    def get_all_lobbies(self) -> List[Dict]:
        """Get all lobbies from the system with members"""
        response = self._make_request("GET", "lobbies?relations=members")
        if response.status_code == 200:
            data = response.json().get('data', {})
            return data.get('data', [])
        return []
    
    def get_lobby_by_id(self, lobby_id: str) -> Optional[Dict]:
        """Get a specific lobby by ID"""
        response = self._make_request("GET", f"lobbies/{lobby_id}")
        if response.status_code == 200:
            return response.json().get('data')
        return None
    
    def join_lobby(self, member_id: str, lobby_id: str) -> bool:
        """Join a member to a lobby"""
        data = {
            "memberId": member_id,
            "lobbyId": lobby_id
        }
        response = self._make_request("POST", "lobbies/join", json=data)
        return response.status_code in [200, 201]
    
    def get_lobby_members(self, lobby_id: str) -> List[Dict]:
        """Get all members in a specific lobby"""
        response = self._make_request("GET", f"lobby-members/?lobbyId_eq={lobby_id}")
        if response.status_code == 200:
            data = response.json().get('data', {})
            return data.get('data', [])
        return []

class LobbyJoinerStats:
    """Track lobby joining statistics"""
    
    def __init__(self):
        self.total_users = 0
        self.successful_joins = 0
        self.failed_joins = 0
        self.already_joined = 0
        self.start_time = None
        self.end_time = None
    
    def start_timer(self):
        """Start the timer"""
        self.start_time = time.time()
    
    def end_timer(self):
        """End the timer"""
        self.end_time = time.time()
    
    def get_duration(self) -> float:
        """Get the duration in seconds"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0
    
    def record_success(self):
        """Record a successful lobby join"""
        self.successful_joins += 1
    
    def record_failure(self):
        """Record a failed lobby join"""
        self.failed_joins += 1
    
    def record_already_joined(self):
        """Record a user already in lobby"""
        self.already_joined += 1

class LobbyJoinerCLI:
    """Interactive CLI for joining users to lobbies"""
    
    def __init__(self):
        self.console = Console()
        self.api = ACBackendAPI()
        self.stats = LobbyJoinerStats()
        
    def display_banner(self):
        """Display welcome banner"""
        banner = Panel.fit(
            "[bold blue]AC Backend - Lobby Joiner CLI[/bold blue]\n"
            "[dim]Automatically join all users to available lobbies[/dim]",
            border_style="blue"
        )
        self.console.print(banner)
        self.console.print()
    
    def get_lobby_selection(self) -> Optional[Dict]:
        """Display available lobbies and get user selection"""
        try:
            lobbies = self.api.get_all_lobbies()
            
            if not lobbies:
                self.console.print("[red]No lobbies available[/red]")
                return None
            
            # Display lobbies in a table
            table = Table(title="Available Lobbies")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Status", style="yellow")
            table.add_column("Members", style="magenta")
            
            for lobby in lobbies:
                lobby_id = lobby.get('id', 'N/A')
                lobby_name = lobby.get('name', 'Unnamed Lobby')
                lobby_status = lobby.get('status', 'Unknown')
                
                # Get member count from relations
                members = lobby.get('members', [])
                member_count = len(members)
                
                table.add_row(
                    str(lobby_id), 
                    lobby_name,
                    lobby_status,
                    str(member_count)
                )
            
            self.console.print(table)
            self.console.print()
            
            while True:
                lobby_id = Prompt.ask("[bold]Enter Lobby ID[/bold]")
                
                # Find the selected lobby
                selected_lobby = next((lobby for lobby in lobbies if str(lobby.get('id')) == lobby_id), None)
                
                if selected_lobby:
                    # Get the full lobby details
                    full_lobby = self.api.get_lobby_by_id(lobby_id)
                    if full_lobby:
                        self.console.print(f"[green]✓ Selected: {full_lobby.get('name', 'Unnamed Lobby')}[/green]")
                        return full_lobby
                    else:
                        self.console.print("[red]Error loading lobby details[/red]")
                        return None
                else:
                    self.console.print("[red]Invalid Lobby ID. Please try again.[/red]")
                    
        except Exception as e:
            self.console.print(f"[red]Error loading lobbies: {e}[/red]")
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
        preview_table = Table(title="Users to Join Lobby (Preview)")
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
    
    def check_existing_lobby_membership(self, lobby: Dict) -> List[str]:
        """Check which users are already in the lobby using the members relation"""
        try:
            lobby_members = lobby.get('members', [])
            return [member.get('id') for member in lobby_members if member.get('id')]
        except Exception:
            return []  # If we can't check, assume no members
    
    def process_user_joins(self, users: List[Dict], lobby: Dict, progress: Progress, task_id: TaskID) -> Tuple[int, int, int]:
        """Process joining all users to the lobby"""
        lobby_id = lobby.get('id')
        lobby_name = lobby.get('name', 'Unknown Lobby')
        success_count = 0
        failure_count = 0
        already_joined_count = 0
        
        # Check for existing lobby members
        existing_members = self.check_existing_lobby_membership(lobby)
        
        for i, user in enumerate(users):
            member_id = user.get('id')
            user_name = user.get('name', 'Unknown')
            
            # Skip if already in lobby
            if member_id in existing_members:
                self.console.print(f"[yellow]⏭️  {user_name} already in lobby[/yellow]")
                already_joined_count += 1
                self.stats.record_already_joined()
                progress.advance(task_id)
                continue
            
            # Join user to lobby
            try:
                if self.api.join_lobby(member_id, lobby_id):
                    self.console.print(f"[green]✅ {user_name} joined lobby[/green]")
                    success_count += 1
                    self.stats.record_success()
                else:
                    self.console.print(f"[red]❌ Failed to join {user_name} to lobby[/red]")
                    failure_count += 1
                    self.stats.record_failure()
            except Exception as e:
                self.console.print(f"[red]❌ Error joining {user_name}: {e}[/red]")
                failure_count += 1
                self.stats.record_failure()
            
            progress.advance(task_id)
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.1)
        
        return success_count, failure_count, already_joined_count
    
    def run_lobby_joining(self, lobby: Dict, users: List[Dict]):
        """Run the automated lobby joining process"""
        lobby_name = lobby.get('name', 'Unknown Lobby')
        lobby_id = lobby.get('id')
        
        # Initialize statistics
        self.stats.total_users = len(users)
        
        self.console.print(f"[blue]🚀 Starting lobby joining for '{lobby_name}'[/blue]")
        self.console.print(f"[blue]👥 Joining {len(users)} users to lobby[/blue]")
        self.console.print()
        
        # Show current lobby members
        lobby_members = lobby.get('members', [])
        self.console.print(f"[cyan]📊 Current lobby members: {len(lobby_members)}[/cyan]")
        
        # Confirm before starting
        if not Confirm.ask("[bold]Start joining users to lobby?[/bold]"):
            self.console.print("[yellow]Lobby joining cancelled[/yellow]")
            return
        
        self.stats.start_timer()
        
        # Process users with progress tracking
        with Progress() as progress:
            task = progress.add_task(f"Joining users to lobby...", total=len(users))
            
            success, failure, already_joined = self.process_user_joins(users, lobby, progress, task)
        
        self.stats.end_timer()
        
        # Display final results
        self.display_final_results(lobby_name, success, failure, already_joined)
    
    def display_final_results(self, lobby_name: str, success_count: int, failure_count: int, already_joined_count: int):
        """Display comprehensive lobby joining results"""
        self.console.print("\n" + "="*80)
        
        # Overall statistics
        duration = self.stats.get_duration()
        total_processed = success_count + failure_count + already_joined_count
        
        summary_panel = Panel(
            f"[bold]Lobby Joining Complete for '{lobby_name}'![/bold]\n\n"
            f"[green]✅ Successful joins: {self.stats.successful_joins}[/green]\n"
            f"[red]❌ Failed joins: {self.stats.failed_joins}[/red]\n"
            f"[yellow]⏭️  Already in lobby: {self.stats.already_joined}[/yellow]\n"
            f"[blue]👥 Total users processed: {total_processed}[/blue]\n"
            f"[cyan]⏱️  Duration: {duration:.2f} seconds[/cyan]\n"
            f"[magenta]⚡ Rate: {total_processed / duration:.2f} operations/sec[/magenta]",
            border_style="blue",
            title="📈 Lobby Joining Summary"
        )
        self.console.print(summary_panel)
        
        # Success rate calculation
        attempted_joins = self.stats.successful_joins + self.stats.failed_joins
        if attempted_joins > 0:
            success_rate = (self.stats.successful_joins / attempted_joins) * 100
            self.console.print(f"\n[bold]📈 Success Rate: {success_rate:.1f}%[/bold]")
        
        # Final lobby status
        try:
            final_members = self.api.get_lobby_members(lobby_name)
            self.console.print(f"[cyan]🏁 Final lobby member count: {len(final_members)}[/cyan]")
        except:
            self.console.print("[yellow]⚠️  Could not verify final lobby member count[/yellow]")
    
    def run(self):
        """Main CLI loop"""
        try:
            self.display_banner()
            
            # Get lobby selection
            lobby = self.get_lobby_selection()
            if not lobby:
                return
            
            self.console.print()
            
            # Get all users
            users = self.get_all_users()
            if not users:
                return
            
            self.console.print()
            
            # Display user summary
            self.display_user_summary(users)
            
            # Run lobby joining
            self.run_lobby_joining(lobby, users)
            
        except KeyboardInterrupt:
            self.console.print("\n\n[yellow]⚠️  Lobby joining interrupted by user[/yellow]")
            if self.stats.start_time:
                self.stats.end_timer()
                self.console.print(f"[cyan]Operation ran for {self.stats.get_duration():.2f} seconds[/cyan]")
        except Exception as e:
            self.console.print(f"\n[red]❌ Unexpected error: {e}[/red]")

def main():
    """Entry point"""
    cli = LobbyJoinerCLI()
    cli.run()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
AC Backend Lobby Joiner CLI - Simple Join All Users to Available Lobbies (No Rich dependency)

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

class SimpleLobbyJoinerCLI:
    """Simple CLI for joining users to lobbies"""
    
    def __init__(self):
        self.api = ACBackendAPI()
        self.stats = LobbyJoinerStats()
        
    def display_banner(self):
        """Display welcome banner"""
        print("=" * 80)
        print("            AC Backend - Lobby Joiner CLI")
        print("     Automatically join all users to available lobbies")
        print("=" * 80)
        print()
    
    def display_lobbies_table(self, lobbies: List[Dict]):
        """Display lobbies in a table format"""
        print("Available Lobbies:")
        print("-" * 100)
        print(f"{'ID':<40} {'Name':<30} {'Status':<15} {'Members':<10}")
        print("-" * 100)
        
        for lobby in lobbies:
            lobby_id = lobby.get('id', 'N/A')
            lobby_name = lobby.get('name', 'Unnamed Lobby')
            lobby_status = lobby.get('status', 'Unknown')
            
            # Get member count from relations
            members = lobby.get('members', [])
            member_count = len(members)
            
            print(f"{str(lobby_id):<40} {lobby_name:<30} {lobby_status:<15} {str(member_count):<10}")
        
        print("-" * 100)
        print()
    
    def get_lobby_selection(self) -> Optional[Dict]:
        """Display available lobbies and get user selection"""
        try:
            lobbies = self.api.get_all_lobbies()
            
            if not lobbies:
                print("❌ No lobbies available")
                return None
            
            self.display_lobbies_table(lobbies)
            
            while True:
                lobby_id = input("Enter Lobby ID: ").strip()
                
                # Find the selected lobby
                selected_lobby = next((lobby for lobby in lobbies if str(lobby.get('id')) == lobby_id), None)
                
                if selected_lobby:
                    # Get the full lobby details
                    full_lobby = self.api.get_lobby_by_id(lobby_id)
                    if full_lobby:
                        print(f"✅ Selected: {full_lobby.get('name', 'Unnamed Lobby')}")
                        return full_lobby
                    else:
                        print("❌ Error loading lobby details")
                        return None
                else:
                    print("❌ Invalid Lobby ID. Please try again.")
                    
        except Exception as e:
            print(f"❌ Error loading lobbies: {e}")
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
        
        print("\nUsers to Join Lobby (Preview):")
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
    
    def check_existing_lobby_membership(self, lobby: Dict) -> List[str]:
        """Check which users are already in the lobby using the members relation"""
        try:
            lobby_members = lobby.get('members', [])
            return [member.get('id') for member in lobby_members if member.get('id')]
        except Exception:
            return []  # If we can't check, assume no members
    
    def display_progress(self, current: int, total: int, prefix: str = "Progress"):
        """Display a simple progress indicator"""
        percent = int((current / total) * 100) if total > 0 else 0
        bar_length = 40
        filled_length = int(bar_length * current // total) if total > 0 else 0
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        print(f"\r{prefix}: |{bar}| {percent}% ({current}/{total})", end='', flush=True)
    
    def process_user_joins(self, users: List[Dict], lobby: Dict) -> Tuple[int, int, int]:
        """Process joining all users to the lobby"""
        lobby_id = lobby.get('id')
        lobby_name = lobby.get('name', 'Unknown Lobby')
        success_count = 0
        failure_count = 0
        already_joined_count = 0
        
        print(f"\n🚀 Starting to join users to '{lobby_name}'")
        
        # Check for existing lobby members
        existing_members = self.check_existing_lobby_membership(lobby)
        print(f"ℹ️  Found {len(existing_members)} existing members in lobby")
        
        for i, user in enumerate(users):
            member_id = user.get('id')
            user_name = user.get('name', 'Unknown')
            
            # Display progress
            self.display_progress(i + 1, len(users), f"Joining users to lobby")
            
            # Skip if already in lobby
            if member_id in existing_members:
                already_joined_count += 1
                self.stats.record_already_joined()
                continue
            
            # Join user to lobby
            try:
                if self.api.join_lobby(member_id, lobby_id):
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
        print(f"\n✅ Success: {success_count} | ❌ Failed: {failure_count} | ⏭️  Already joined: {already_joined_count}")
        
        return success_count, failure_count, already_joined_count
    
    def run_lobby_joining(self, lobby: Dict, users: List[Dict]):
        """Run the automated lobby joining process"""
        lobby_name = lobby.get('name', 'Unknown Lobby')
        lobby_id = lobby.get('id')
        
        # Initialize statistics
        self.stats.total_users = len(users)
        
        print(f"🚀 Starting lobby joining for '{lobby_name}'")
        print(f"👥 Joining {len(users)} users to lobby")
        print()
        
        # Show current lobby members
        lobby_members = lobby.get('members', [])
        print(f"📊 Current lobby members: {len(lobby_members)}")
        
        # Confirm before starting
        confirm = input("\nStart joining users to lobby? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("⚠️  Lobby joining cancelled")
            return
        
        print("\n" + "="*80)
        print("STARTING LOBBY JOINING")
        print("="*80)
        
        self.stats.start_timer()
        
        # Process users
        success, failure, already_joined = self.process_user_joins(users, lobby)
        
        self.stats.end_timer()
        
        # Display final results
        self.display_final_results(lobby_name, success, failure, already_joined)
    
    def display_final_results(self, lobby_name: str, success_count: int, failure_count: int, already_joined_count: int):
        """Display comprehensive lobby joining results"""
        print("\n" + "="*80)
        print("                    LOBBY JOINING COMPLETE!")
        print("="*80)
        
        # Overall statistics
        duration = self.stats.get_duration()
        total_processed = success_count + failure_count + already_joined_count
        
        print(f"Lobby: {lobby_name}")
        print("-" * 80)
        print(f"✅ Successful joins: {self.stats.successful_joins}")
        print(f"❌ Failed joins: {self.stats.failed_joins}")
        print(f"⏭️  Already in lobby: {self.stats.already_joined}")
        print(f"👥 Total users processed: {total_processed}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        
        if duration > 0:
            rate = total_processed / duration
            print(f"⚡ Rate: {rate:.2f} operations/sec")
        
        # Success rate calculation
        attempted_joins = self.stats.successful_joins + self.stats.failed_joins
        if attempted_joins > 0:
            success_rate = (self.stats.successful_joins / attempted_joins) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # Final lobby status
        try:
            final_members = self.api.get_lobby_members(lobby_name)
            print(f"🏁 Final lobby member count: {len(final_members)}")
        except:
            print("⚠️  Could not verify final lobby member count")
        
        print("-" * 80)
        print("="*80)
    
    def run(self):
        """Main CLI loop"""
        try:
            self.display_banner()
            
            # Get lobby selection
            lobby = self.get_lobby_selection()
            if not lobby:
                return
            
            print()
            
            # Get all users
            users = self.get_all_users()
            if not users:
                return
            
            print()
            
            # Display user summary
            self.display_user_summary(users)
            
            # Run lobby joining
            self.run_lobby_joining(lobby, users)
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Lobby joining interrupted by user")
            if self.stats.start_time:
                self.stats.end_timer()
                print(f"Operation ran for {self.stats.get_duration():.2f} seconds")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")

def main():
    """Entry point"""
    cli = SimpleLobbyJoinerCLI()
    cli.run()

if __name__ == "__main__":
    main()

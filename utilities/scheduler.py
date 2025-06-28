import schedule
import time
import threading
from datetime import datetime, timezone
from utilities.log import Logger
import requests


class LobbyScheduler:
    def __init__(self, manager):
        self.manager = manager
        self.logger = Logger.get_logger("LobbyScheduler")
        self.scheduler_thread = None
        self.running = False
        self.scheduled_jobs = {}  # Track scheduled jobs by lobby_id
        
    def start(self):
        """Start the scheduler in a background thread"""
        if self.running:
            self.logger.warning("Scheduler is already running")
            return
            
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        self.logger.info("Scheduler started successfully")
        
        # Fetch existing lobbies and schedule them
        self.fetch_and_schedule_existing_lobbies()
        
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        self.scheduled_jobs.clear()
        self.logger.info("Scheduler stopped")
        
    def _run_scheduler(self):
        """Run the scheduler loop in background thread"""
        while self.running:
            current_time = datetime.now(timezone.utc)
            
            # Check for scheduled jobs that need to be executed
            jobs_to_execute = []
            for lobby_id, job_info in list(self.scheduled_jobs.items()):
                if not job_info.get('executed', False) and current_time >= job_info['scheduled_date']:
                    jobs_to_execute.append((lobby_id, job_info))
            
            # Execute due jobs
            for lobby_id, job_info in jobs_to_execute:
                self._execute_pre_event_function(lobby_id, job_info['lobby_data'])
                # Mark as executed and remove from scheduled jobs
                del self.scheduled_jobs[lobby_id]
            
            # Also run any other pending schedule jobs (if any)
            schedule.run_pending()
            time.sleep(1)
            
    def fetch_and_schedule_existing_lobbies(self):
        """Fetch existing lobbies from API and schedule pre-event functions"""
        try:
            self.logger.info("Fetching existing lobbies to schedule")
            
            # Make API request to get all lobbies with relations
            response = self.manager.make_api_request(
                requests.get,
                "api/collections/lobbies?relations=questionSet.questions.answers"
            )
            
            if response.status_code != 200:
                self.logger.error(f"Failed to fetch lobbies: {response.status_code} - {response.text}")
                return
                
            lobbies_data = response.json()
            self.logger.debug(f"Received lobbies data: {lobbies_data}")
            
            if 'data' not in lobbies_data:
                self.logger.warning("No data field in lobbies response")
                return
                
            lobbies = lobbies_data['data']
            self.logger.info(f"Found {len(lobbies)} existing lobbies")
            
            current_time = datetime.now(timezone.utc)
            scheduled_count = 0
            
            for lobby in lobbies:
                try:
                    lobby_id = lobby.get('id')
                    pre_event_date_str = lobby.get('preEventDate')
                    
                    if not lobby_id or not pre_event_date_str:
                        self.logger.warning(f"Lobby missing required fields: id={lobby_id}, preEventDate={pre_event_date_str}")
                        continue
                        
                    # Parse the preEventDate
                    pre_event_date = datetime.fromisoformat(pre_event_date_str.replace("Z", "+00:00"))
                    
                    # Only schedule if the preEventDate is in the future
                    if pre_event_date > current_time:
                        self.schedule_pre_event_function(lobby_id, pre_event_date, lobby)
                        scheduled_count += 1
                        self.logger.info(f"Scheduled pre-event function for lobby {lobby_id} at {pre_event_date}")
                    else:
                        self.logger.info(f"Lobby {lobby_id} preEventDate {pre_event_date} has already passed, skipping")
                        
                except Exception as e:
                    self.logger.error(f"Error processing lobby {lobby.get('id', 'unknown')}: {str(e)}")
                    continue
                    
            self.logger.info(f"Successfully scheduled {scheduled_count} lobbies")
            
        except Exception as e:
            self.logger.exception(f"Error fetching and scheduling existing lobbies: {str(e)}")
            
    def schedule_pre_event_function(self, lobby_id, pre_event_date, lobby_data=None):
        """Schedule a function to run at the lobby's preEventDate"""
        try:
            # Store the scheduled job info with target datetime
            self.scheduled_jobs[lobby_id] = {
                'scheduled_date': pre_event_date,
                'lobby_data': lobby_data,
                'executed': False
            }
            
            self.logger.info(f"Scheduled pre-event function for lobby {lobby_id} at {pre_event_date}")
            
        except Exception as e:
            self.logger.error(f"Error scheduling pre-event function for lobby {lobby_id}: {str(e)}")
            
    def _execute_pre_event_function(self, lobby_id, lobby_data=None):
        """Execute the pre-event function for a specific lobby"""
        try:
            self.logger.info(f"🎉 PRE-EVENT TRIGGERED for lobby {lobby_id}")
            
            if lobby_data:
                lobby_name = lobby_data.get('name', 'Unknown')
                event_date = lobby_data.get('eventDate', 'Unknown')
                max_members = lobby_data.get('maxMembers', 'Unknown')
                
                self.logger.info(f"Lobby Details:")
                self.logger.info(f"  - Name: {lobby_name}")
                self.logger.info(f"  - Event Date: {event_date}")
                self.logger.info(f"  - Max Members: {max_members}")
                
                # Print to console as requested
                print(f"🚀 PRE-EVENT FUNCTION EXECUTED!")
                print(f"📍 Lobby: {lobby_name} (ID: {lobby_id})")
                print(f"📅 Event Date: {event_date}")
                print(f"👥 Max Members: {max_members}")
                print(f"⏰ Triggered at: {datetime.now(timezone.utc)}")
                print("-" * 50)
            else:
                print(f"🚀 PRE-EVENT FUNCTION EXECUTED for lobby {lobby_id}")
                print(f"⏰ Triggered at: {datetime.now(timezone.utc)}")
                print("-" * 50)
                
            self.logger.info(f"Successfully executed pre-event function for lobby {lobby_id}")
                
        except Exception as e:
            self.logger.error(f"Error executing pre-event function for lobby {lobby_id}: {str(e)}")
            
    def schedule_new_lobby(self, lobby_data):
        """Schedule a newly created lobby"""
        try:
            lobby_id = lobby_data.get('id')
            pre_event_date_str = lobby_data.get('preEventDate')
            
            if not lobby_id or not pre_event_date_str:
                self.logger.warning(f"Cannot schedule lobby - missing required fields: id={lobby_id}, preEventDate={pre_event_date_str}")
                return False
                
            pre_event_date = datetime.fromisoformat(pre_event_date_str.replace("Z", "+00:00"))
            current_time = datetime.now(timezone.utc)
            
            if pre_event_date > current_time:
                self.schedule_pre_event_function(lobby_id, pre_event_date, lobby_data)
                return True
            else:
                self.logger.info(f"New lobby {lobby_id} preEventDate has already passed, not scheduling")
                return False
                
        except Exception as e:
            self.logger.error(f"Error scheduling new lobby {lobby_data.get('id', 'unknown')}: {str(e)}")
            return False
            
    def cancel_lobby_schedule(self, lobby_id):
        """Cancel scheduled job for a specific lobby"""
        try:
            if lobby_id in self.scheduled_jobs:
                del self.scheduled_jobs[lobby_id]
                self.logger.info(f"Cancelled scheduled job for lobby {lobby_id}")
                return True
            else:
                self.logger.warning(f"No scheduled job found for lobby {lobby_id}")
                return False
        except Exception as e:
            self.logger.error(f"Error cancelling schedule for lobby {lobby_id}: {str(e)}")
            return False
            
    def get_scheduled_lobbies(self):
        """Get list of currently scheduled lobbies"""
        return list(self.scheduled_jobs.keys())
        
    def get_scheduler_status(self):
        """Get current scheduler status"""
        return {
            'running': self.running,
            'scheduled_lobbies_count': len(self.scheduled_jobs),
            'scheduled_lobbies': [
                {
                    'lobby_id': lobby_id,
                    'scheduled_date': job_info['scheduled_date'].isoformat(),
                    'lobby_name': job_info['lobby_data'].get('name', 'Unknown') if job_info['lobby_data'] else 'Unknown'
                }
                for lobby_id, job_info in self.scheduled_jobs.items()
            ]
        }

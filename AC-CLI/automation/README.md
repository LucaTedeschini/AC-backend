# AC Backend Automation CLI

Comprehensive automation tools for the AC Backend system including automated question answering and lobby joining functionality.

## Features

### Question Answering Automation
- **Question Set Selection**: Choose from available question sets by ID
- **Automatic User Discovery**: Fetches all users from the AC backend system
- **Random Answer Selection**: Automatically selects random answers for each question
- **Duplicate Prevention**: Skips questions that users have already answered
- **Progress Tracking**: Real-time progress display during automation
- **Comprehensive Statistics**: Detailed success/failure reporting
- **Performance Metrics**: Tracks timing and operation rates
- **Error Handling**: Robust error handling for API failures

### Lobby Joining Automation
- **Lobby Selection**: Choose from available lobbies by ID
- **Automatic User Discovery**: Fetches all users from the system
- **Bulk Joining**: Automatically joins all users to the selected lobby
- **Membership Prevention**: Skips users already in the lobby
- **Real-time Progress**: Progress tracking during bulk operations
- **Detailed Statistics**: Success/failure/skip reporting
- **Performance Tracking**: Operation timing and rates

## Installation

1. Navigate to the automation directory:
```bash
cd automation
```

2. Install dependencies (choose one):

For full featured version with Rich UI:
```bash
pip install -r requirements.txt
```

For simple version (minimal dependencies):
```bash
pip install -r requirements-simple.txt
```

## Usage

### Question Answering Automation

#### Full Featured Version (with Rich UI)
```bash
python auto_answer_cli.py
```

#### Simple Version (minimal dependencies)
```bash
python simple_auto_answer_cli.py
```

### Lobby Joining Automation

#### Full Featured Version (with Rich UI)
```bash
python lobby_joiner_cli.py
```

#### Simple Version (minimal dependencies)
```bash
python simple_lobby_joiner_cli.py
```

## How it works

### Question Answering Automation

1. **Question Set Selection**: Displays all available question sets with question counts and allows selection by ID
2. **User Discovery**: Automatically fetches all users from the backend system
3. **Duplicate Check**: For each user, checks which questions they've already answered to avoid duplicates
4. **Random Answer Selection**: For each unanswered question, randomly selects one of the available answers
5. **Batch Processing**: Processes all users sequentially with progress tracking
6. **Statistics Reporting**: Provides comprehensive success/failure statistics

### Lobby Joining Automation

1. **Lobby Selection**: Displays all available lobbies with member counts and allows selection by ID
2. **User Discovery**: Automatically fetches all users from the backend system
3. **Membership Check**: For each user, checks if they're already in the lobby to avoid duplicates
4. **Bulk Joining**: Joins all non-member users to the selected lobby
5. **Progress Tracking**: Real-time progress display during joining process
6. **Statistics Reporting**: Provides comprehensive join success/failure statistics

## API Endpoints Used

### Question Answering Automation
- `GET /api/v0/collections/question-sets/` - List all question sets
- `GET /api/v0/collections/question-sets/{id}` - Get specific question set with questions
- `GET /api/v0/collections/members/` - Get all users in the system
- `GET /api/v0/collections/member-answers/?memberId_eq={id}` - Check existing answers for a user
- `POST /api/v0/collections/member-answers/` - Submit new answer for a user

### Lobby Joining Automation
- `GET /api/v0/collections/lobbies?relations=members` - List all lobbies with their members
- `GET /api/v0/collections/lobbies/{id}` - Get specific lobby details
- `GET /api/v0/collections/members/` - Get all users in the system
- `POST /api/v0/collections/lobbies/join` - Join a user to a lobby

## Automation Process

### Question Answering Automation

#### Step 1: Question Set Selection
```
Available Question Sets:
────────────────────────────────────────────────────────────────────────────
ID         Name                                     Questions 
────────────────────────────────────────────────────────────────────────────
1          Customer Satisfaction Survey             15        
2          Product Feedback Questionnaire           8         
3          Employee Engagement Survey               12        
────────────────────────────────────────────────────────────────────────────

Enter Question Set ID: 1
✅ Selected: Customer Satisfaction Survey (15 questions)
```

#### Step 2: User Processing
```
✅ Found 25 users in the system

Users to Process (Preview):
────────────────────────────────────────────────────────────────────────────
User ID    Name                           Social Contact            
────────────────────────────────────────────────────────────────────────────
1234       John Doe                       @john_doe123              
5678       Jane Smith                     @jane_smith456            
...        ...                            ... and 23 more users     
────────────────────────────────────────────────────────────────────────────
```

#### Step 3: Automation Execution
```
🚀 Starting automation for 'Customer Satisfaction Survey'
📊 25 users × 15 questions = 375 total operations

👤 Processing user 1/25: John Doe
  Questions for John Doe: |████████████████████████████████████████| 100% (15/15)
  ✅ Success: 12 | ❌ Failed: 0 | ⏭️ Skipped: 3

👤 Processing user 2/25: Jane Smith
  Questions for Jane Smith: |████████████████████████████████████████| 100% (15/15)
  ✅ Success: 15 | ❌ Failed: 0 | ⏭️ Skipped: 0
```

#### Step 4: Results Summary
```
════════════════════════════════════════════════════════════════════════════
                        AUTOMATION COMPLETE!
════════════════════════════════════════════════════════════════════════════

Question Set: Customer Satisfaction Survey
────────────────────────────────────────────────────────────────────────────
✅ Successful submissions: 342
❌ Failed submissions: 8
⏭️ Skipped (already answered): 25
📊 Total operations: 375
⏱️ Duration: 45.23 seconds
⚡ Rate: 8.29 operations/sec
📈 Success Rate: 97.7%
```

### Lobby Joining Automation

#### Step 1: Lobby Selection
```
Available Lobbies:
────────────────────────────────────────────────────────────────────────────────────────────────────
ID                                       Name                           Status          Members   
────────────────────────────────────────────────────────────────────────────────────────────────────
203de4be-47fc-4c87-b2b3-332aacba57da     Game Room Alpha                Active          5         
f8912345-1234-5678-9abc-def012345678     Beta Testing Lobby             Waiting         0         
c4567890-abcd-ef12-3456-789012345678     VIP Lounge                     Active          12        
────────────────────────────────────────────────────────────────────────────────────────────────────

Enter Lobby ID: 203de4be-47fc-4c87-b2b3-332aacba57da
✅ Selected: Game Room Alpha
```

#### Step 2: User Processing
```
✅ Found 50 users in the system

Users to Join Lobby (Preview):
────────────────────────────────────────────────────────────────────────────
User ID    Name                           Social Contact            
────────────────────────────────────────────────────────────────────────────
1234       John Doe                       @john_doe123              
5678       Jane Smith                     @jane_smith456            
...        ...                            ... and 48 more users     
────────────────────────────────────────────────────────────────────────────
```

#### Step 3: Lobby Joining Execution
```
🚀 Starting lobby joining for 'Game Room Alpha'
👥 Joining 50 users to lobby
📊 Current lobby members: 5

Joining users to lobby: |████████████████████████████████████████| 100% (50/50)

✅ Success: 45 | ❌ Failed: 0 | ⏭️ Already joined: 5
```

#### Step 4: Results Summary
```
════════════════════════════════════════════════════════════════════════════
                    LOBBY JOINING COMPLETE!
════════════════════════════════════════════════════════════════════════════

Lobby: Game Room Alpha
────────────────────────────────────────────────────────────────────────────
✅ Successful joins: 45
❌ Failed joins: 0
⏭️ Already in lobby: 5
👥 Total users processed: 50
⏱️ Duration: 8.45 seconds
⚡ Rate: 5.92 operations/sec
📈 Success Rate: 100.0%
🏁 Final lobby member count: 50
```

## Answer Selection Logic

For each question, the automation:

1. **Retrieves Available Answers**: Gets all possible answers for the question
2. **Random Selection**: Uses Python's `random.choice()` to select one answer
3. **API Submission**: Submits the selected answer via the member-answers endpoint

Example answer selection:
```python
# Question: "How satisfied are you with our service?"
# Available answers: ["Very Satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very Dissatisfied"]
# Random selection: "Satisfied" (randomly chosen)
```

## Lobby Joining Logic

For each user, the automation:

1. **Checks Existing Membership**: Verifies if the user is already in the lobby
2. **Skip if Member**: Skips users already in the lobby to avoid duplicate joins
3. **API Submission**: Submits join request via the lobbies/join endpoint

Example lobby joining:
```python
# Lobby: "Game Room Alpha" (ID: 203de4be-47fc-4c87-b2b3-332aacba57da)
# User: "John Doe" (Member ID: f3865f95-938f-410f-bf5a-4348142c30e9)
# Action: POST /api/v0/collections/lobbies/join
# Payload: {"memberId": "f3865f95-938f-410f-bf5a-4348142c30e9", "lobbyId": "203de4be-47fc-4c87-b2b3-332aacba57da"}
```

## Performance Considerations

- **Rate Limiting**: Includes small delays (0.1s) between API calls to avoid overwhelming the server
- **Batch Processing**: Processes users sequentially to maintain system stability
- **Error Recovery**: Continues processing even if individual submissions fail
- **Memory Efficient**: Processes users one at a time rather than loading all data at once

## Error Handling

The automation handles various error scenarios:

- **Network Issues**: Continues processing other operations if individual API calls fail
- **Invalid Data**: Skips questions with no available answers
- **Duplicate Submissions**: Automatically skips questions already answered by users
- **Server Errors**: Logs failures but continues with remaining operations
- **User Interruption**: Gracefully handles Ctrl+C with statistics summary

## Statistics Tracking

Comprehensive tracking includes:

- **Per-User Results**: Success/failure/skip counts for each user
- **Overall Success Rate**: Percentage of successful submissions
- **Performance Metrics**: Operations per second, total duration
- **Error Analysis**: Detailed breakdown of failure types

## Use Cases

These automation tools are ideal for:

### Question Answering Automation
- **Testing**: Generating test data for analytics and reporting
- **Demos**: Quickly populating systems with realistic answer data
- **Data Generation**: Creating datasets for development and testing
- **Load Testing**: Stress testing the answer submission system
- **Initial Setup**: Populating new systems with sample responses

### Lobby Joining Automation
- **Testing**: Populating lobbies with users for game testing
- **Demos**: Quickly filling lobbies for demonstration purposes
- **Load Testing**: Testing lobby capacity and performance
- **Event Setup**: Rapidly organizing users into lobbies for events
- **Development**: Creating realistic lobby scenarios for testing

## Requirements

- Python 3.7+
- AC Backend server running on localhost:5000
- Network connectivity to the backend API
- `requests` library for API calls
- `rich` library for enhanced UI (optional, use simple version if not available)

## Safety Features

- **Confirmation Prompt**: Requires user confirmation before starting automation
- **Progress Visibility**: Real-time progress updates during execution
- **Interrupt Handling**: Safe interruption with Ctrl+C
- **Duplicate Prevention**: Automatically skips already answered questions
- **Error Logging**: Detailed error reporting for troubleshooting

# AC Backend User Creator CLI

Interactive command-line interface for creating random users in the AC backend system.

## Features

- Generate random English names with high uniqueness (1000+ combinations)
- Automatic unique User ID generation
- Social media handle generation based on names
- Single user creation with confirmation
- Batch user creation mode
- Duplicate User ID prevention
- Beautiful terminal UI with progress feedback

## Installation

1. Navigate to the user-creator directory:
```bash
cd user-creator
```

2. Install dependencies (choose one):

For full featured version with Rich UI:
```bash
pip install -r requirements.txt
```

For simple version (no external dependencies except requests):
```bash
pip install -r requirements-simple.txt
```

## Usage

### Full Featured Version (with Rich UI)
```bash
python user_creator_cli.py
```

### Simple Version (minimal dependencies)
```bash
python simple_user_creator.py
```

## How it works

1. **User ID Uniqueness**: The CLI fetches existing user IDs from the backend to ensure no duplicates
2. **Random Name Generation**: Uses extensive lists of English first and last names for variety
3. **Social Handle Generation**: Creates social media handles based on the generated names with random numbers
4. **User Creation Options**:
   - **Single User**: Generate and review one user before creation
   - **Batch Creation**: Create multiple users automatically
5. **API Integration**: Uses the AC Backend API to create users via POST requests

## API Endpoint Used

- `GET /api/v0/collections/members/` - Fetch existing users to avoid ID conflicts
- `POST /api/v0/collections/members/` - Create new user

### User Creation Payload

```json
{
    "name": "John Doe",
    "userId": 1234,
    "socialContact": "@john_doe123"
}
```

## Name Generation

The CLI includes:
- **120+ First Names**: Common English first names for both male and female
- **120+ Last Names**: Common English surnames
- **Unique Combinations**: Over 14,000 possible name combinations
- **Social Handles**: Automatically generated from names with random numbers (10-999)

## User ID Generation

- **Range**: 1000-9999 for 4-digit IDs
- **Uniqueness**: Checks existing users to avoid conflicts
- **Fallback**: If range is exhausted, uses next available ID after the highest existing one

## Controls

### Single User Mode
- **y/yes**: Confirm user creation
- **n/no**: Cancel user creation
- **q**: Quit application

### Batch Mode
- **Number**: Enter count of users to create
- **Enter**: Use default value (5 users)

### Navigation
- **1**: Create single user
- **2**: Create multiple users  
- **3**: Exit application
- **Ctrl+C**: Emergency exit

## Error Handling

The CLI handles various scenarios:
- Network connectivity issues
- API errors and timeouts
- Invalid input validation
- Duplicate User ID conflicts
- Backend server unavailability

## Example Session

```
=============================================================
         AC Backend - User Creator CLI
    Create random users for the AC backend system
=============================================================

ℹ️  Found 15 existing users

User Creation Options:
1. Create single user
2. Create multiple users
3. Exit

Select option (1-3): 2
How many users to create? (default: 5): 3

🔄 Creating 3 users...

✅ Created: Sarah Johnson (ID: 3847)
✅ Created: Michael Brown (ID: 7291)
✅ Created: Emily Davis (ID: 5643)

=============================================================
              USER CREATION COMPLETE!
=============================================================
Successfully created: 3/3 users
=============================================================
```

## Requirements

- Python 3.7+
- AC Backend server running on localhost:5000
- Network connectivity to the backend API
- `requests` library for API calls
- `rich` library for enhanced UI (optional, use simple version if not available)

# AC Backend CLI

Interactive command-line interface for answering questions from the AC backend system.

## Features

- Interactive user ID validation
- Question set selection
- One-by-one question presentation with keyboard navigation
- Real-time answer submission to the AC backend server
- Beautiful terminal UI with colors and tables

## Installation

1. Navigate to the AC-CLI directory:
```bash
cd AC-CLI
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Make sure the AC backend server is running on `http://localhost:5000`

2. Run the CLI:
```bash
python ac_cli.py
```

3. Follow the interactive prompts:
   - Enter your Member ID
   - Select a Question Set from the displayed table
   - Answer questions one by one using the numbered options
   - Confirm each answer before submission

## How it works

1. **Member Validation**: The CLI validates your member ID against the backend API
2. **Question Set Selection**: Displays all available question sets in a table format
3. **Question Processing**: For each question in the selected set:
   - Displays the question text
   - Shows all available answers with numbers
   - Allows selection using keyboard input (1, 2, 3, etc.)
   - Confirms your selection before submission
   - Submits the answer to the backend API
4. **Progress Tracking**: Shows which question you're on (e.g., "Question 3/10")
5. **Session Summary**: Displays how many questions you answered at the end

## API Endpoints Used

- `GET /api/v0/collections/members/{id}` - Validate member
- `GET /api/v0/collections/question-sets/` - List question sets
- `GET /api/v0/collections/question-sets/{id}` - Get specific question set
- `GET /api/v0/collections/questions/{id}?relations=answers` - Get question with answers
- `POST /api/v0/collections/member-answers/` - Submit answer

## Controls

- **Number keys (1-9)**: Select answer option
- **Enter**: Confirm selection
- **q**: Quit current question/session
- **Ctrl+C**: Emergency exit

## Error Handling

The CLI handles various error scenarios:
- Invalid member IDs
- Network connectivity issues
- Missing question sets or questions
- API errors
- Invalid input validation

## Requirements

- Python 3.7+
- AC Backend server running on localhost:5000
- Network connectivity to the backend API

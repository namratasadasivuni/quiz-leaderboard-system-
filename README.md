# Quiz Leaderboard System

This project is a backend integration solution designed to consume API responses from an external validator system, process them by handling duplicates, and generate a final leaderboard.

## Problem Overview
The system simulates a quiz show where multiple participants receive scores across different rounds. The challenge involves:
1. **Polling**: Fetching data from a REST API across 10 consecutive polls with a mandatory delay.
2. **Deduplication**: Ensuring that scores for the same `roundId` and `participant` are only counted once, even if they appear in multiple polls.
3. **Aggregation**: Summing up the unique scores for each participant.
4. **Leaderboard Generation**: Sorting participants by their total scores in descending order.
5. **Submission**: Posting the final leaderboard back to the validator.

## Features
- **Automated Polling**: Sequentially calls the API from poll index 0 to 9.
- **Robust Deduplication**: Uses a composite key `(roundId, participant)` to identify and ignore duplicate entries.
- **Accurate Aggregation**: Correctly calculates the total score across all unique events.
- **Sorted Leaderboard**: Generates a leaderboard sorted by `totalScore` as required.
- **Submission Logic**: Sends the final result to the `/quiz/submit` endpoint.

## API Details
- **Base URL**: `https://devapigw.vidalhealthtpa.com/srm-quiz-task`
- **Endpoints**:
    - `GET /quiz/messages`: Fetches quiz events for a specific registration number and poll index.
    - `POST /quiz/submit`: Submits the final aggregated leaderboard.

## How to Run
1. Ensure you have Python 3 installed.
2. Install the `requests` library:
   ```bash
   pip install requests
   ```
3. Run the script:
   ```bash
   python quiz_leaderboard.py
   ```

## Implementation Logic
The core logic resides in `quiz_leaderboard.py`:
- **`poll_api()`**: Manages the 10-step polling process and implements a 5-second sleep between requests. It uses a Python `set` to track seen `(roundId, participant)` pairs.
- **`aggregate_scores()`**: Uses a dictionary to sum scores per participant and then converts it to a sorted list of objects.
- **`submit_leaderboard()`**: Constructs the final JSON payload and performs the POST request.

## Submission Result
Upon execution, the system produces a leaderboard and submits it. A successful submission returns a response indicating the `submittedTotal` and verification status.

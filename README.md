# Quiz Leaderboard System
**SRM Internship Assignment — Bajaj Finserv Health**

---

## Problem Statement

A quiz validator API delivers participant scores across 10 polls. The same event data may appear in multiple polls (duplicates). The goal is to:

1. Poll the API 10 times (with a 5-second delay between each)
2. Deduplicate events using `roundId + participant` as the unique key
3. Aggregate scores per participant
4. Submit a correctly sorted leaderboard exactly once

---

## My Result

| Field | Value |
|---|---|
| Participants | 3 (Bob, Alice, Charlie) |
| Unique events | 9 |
| Duplicate events dropped | 6 |
| Grand total submitted | **835** |
| HTTP status | 200 ✅ |

**Final Leaderboard:**
| Rank | Participant | Total Score |
|---|---|---|
| 1 | Bob | 295 |
| 2 | Alice | 280 |
| 3 | Charlie | 260 |

---

## How It Works

### Step 1 — Poll 10 times
```
GET /quiz/messages?regNo=2024CS101&poll=0
GET /quiz/messages?regNo=2024CS101&poll=1
...
GET /quiz/messages?regNo=2024CS101&poll=9
```
A mandatory **5-second delay** is maintained between each poll.

### Step 2 — Deduplicate
Every event is identified by a unique key:
```
key = roundId + "|" + participant
```
This key is stored in a Python `set`. If the same key appears again in a later poll, it is silently ignored.

**Example:**
```
Poll 0 → Alice R1 +10   → key "R1|Alice" not seen → COUNT IT   ✅
Poll 2 → Alice R1 +10   → key "R1|Alice" already seen → SKIP   ❌
```

### Step 3 — Aggregate & Sort
Unique scores are summed per participant, then sorted by `totalScore` descending.

### Step 4 — Submit once
```
POST /quiz/submit
{
  "regNo": "2024CS101",
  "leaderboard": [
    { "participant": "Bob",     "totalScore": 295 },
    { "participant": "Alice",   "totalScore": 280 },
    { "participant": "Charlie", "totalScore": 260 }
  ]
}
```

---

## Tech Stack

- **Language:** Python 3
- **Library:** `requests` (only external dependency)
- No frameworks, no databases — pure Python

---

## Setup & Run

**1. Install dependency**
```bash
pip install requests
```

**2. Set your registration number** in `quiz_leaderboard.py` (line 12):
```python
REG_NO = "2024CS101"   # change to your reg number
```

**3. Run**
```bash
python quiz_leaderboard.py
```

---

## Sample Output

```
=== Quiz Leaderboard System ===
regNo     : 2024CS101
Base URL  : https://devapigw.vidalhealthtpa.com/srm-quiz-task
Polls     : 10  (5s delay between each)

Poll 00: 2 events received — 2 new, 0 duplicates dropped
  Waiting 5s before next poll...
Poll 01: 1 events received — 1 new, 0 duplicates dropped
  Waiting 5s before next poll...
Poll 02: 2 events received — 1 new, 1 duplicates dropped
  ...
Poll 09: 1 events received — 0 new, 1 duplicates dropped

--- Leaderboard (3 participants) ---
   1. Bob                  295
   2. Alice                280
   3. Charlie              260
     Grand total : 835
     Raw events  : 15
     Unique      : 9

Submitting leaderboard...
  [DEBUG] Submit status code : 200
  [DEBUG] Raw response       : {"regNo":"2024CS101","totalPollsMade":4249,"submittedTotal":835,"attemptCount":372}

=== Submit Result ===
  regNo                : 2024CS101
  totalPollsMade       : 4249
  submittedTotal       : 835
  attemptCount         : 372

✓ Success!
```

---

## File Structure

```
├── quiz_leaderboard.py   # main solution
└── README.md             # this file
```

---

## API Reference

**Base URL:** `https://devapigw.vidalhealthtpa.com/srm-quiz-task`

| Endpoint | Method | Description |
|---|---|---|
| `/quiz/messages` | GET | Fetch events for a poll index (0–9) |
| `/quiz/submit` | POST | Submit the final leaderboard |

**Poll request:**
```
GET /quiz/messages?regNo=2024CS101&poll=0
```

**Poll response:**
```json
{
  "regNo": "2024CS101",
  "setId": "SET_1",
  "pollIndex": 0,
  "events": [
    { "roundId": "R1", "participant": "Alice", "score": 10 },
    { "roundId": "R1", "participant": "Bob",   "score": 20 }
  ]
}
```

**Submit request:**
```json
{
  "regNo": "2024CS101",
  "leaderboard": [
    { "participant": "Bob",   "totalScore": 295 },
    { "participant": "Alice", "totalScore": 280 }
  ]
}
```

**Submit response:**
```json
{
  "regNo": "2024CS101",
  "totalPollsMade": 4249,
  "submittedTotal": 835,
  "attemptCount": 372
}
```

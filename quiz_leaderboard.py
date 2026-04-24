import requests
import time
import json

BASE_URL = "https://devapigw.vidalhealthtpa.com/srm-quiz-task"
REG_NO = "2024CS101"

def poll_api():
    all_events = []
    processed_events = set()  # Store (roundId, participant) to deduplicate
    
    print(f"Starting polling for regNo: {REG_NO}")
    
    for i in range(10):
        print(f"Polling {i}/9...")
        try:
            response = requests.get(f"{BASE_URL}/quiz/messages", params={"regNo": REG_NO, "poll": i})
            response.raise_for_status()
            data = response.json()
            
            events = data.get("events", [])
            for event in events:
                round_id = event.get("roundId")
                participant = event.get("participant")
                score = event.get("score")
                
                # Deduplicate using (roundId, participant)
                key = (round_id, participant)
                if key not in processed_events:
                    processed_events.add(key)
                    all_events.append(event)
                else:
                    print(f"  Duplicate found: {key}. Ignoring.")
                    
        except Exception as e:
            print(f"  Error during poll {i}: {e}")
            
        if i < 9:
            print("  Waiting 5 seconds before next poll...")
            time.sleep(5)
            
    return all_events

def aggregate_scores(events):
    leaderboard_dict = {}
    for event in events:
        participant = event.get("participant")
        score = event.get("score")
        leaderboard_dict[participant] = leaderboard_dict.get(participant, 0) + score
        
    # Convert to list of dicts and sort by totalScore descending
    leaderboard = [
        {"participant": p, "totalScore": s} 
        for p, s in leaderboard_dict.items()
    ]
    leaderboard.sort(key=lambda x: x["totalScore"], reverse=True)
    return leaderboard

def submit_leaderboard(leaderboard):
    print("Submitting leaderboard...")
    payload = {
        "regNo": REG_NO,
        "leaderboard": leaderboard
    }
    
    try:
        response = requests.post(f"{BASE_URL}/quiz/submit", json=payload)
        response.raise_for_status()
        result = response.json()
        print("Submission Result:")
        print(json.dumps(result, indent=2))
        return result
    except Exception as e:
        print(f"Error during submission: {e}")
        return None

if __name__ == "__main__":
    # 1. Poll and deduplicate
    unique_events = poll_api()
    
    # 2. Aggregate
    leaderboard = aggregate_scores(unique_events)
    
    # 3. Print final results for verification
    total_score = sum(item["totalScore"] for item in leaderboard)
    print("\nFinal Leaderboard:")
    for entry in leaderboard:
        print(f"{entry['participant']}: {entry['totalScore']}")
    print(f"Total Score: {total_score}")
    
    # 4. Submit
    submit_leaderboard(leaderboard)

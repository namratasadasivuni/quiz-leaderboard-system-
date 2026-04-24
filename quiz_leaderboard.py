import requests
import time
import json

BASE_URL = "https://devapigw.vidalhealthtpa.com/srm-quiz-task"

# 🔥 Use a fresh regNo (VERY IMPORTANT)
REG_NO = "2024CS101_NAM_02"


def fetch_poll_with_retry(poll_index, retries=5):
    url = f"{BASE_URL}/quiz/messages"
    params = {"regNo": REG_NO, "poll": poll_index}

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"  ❌ Poll {poll_index} failed (Attempt {attempt}): {e}")
            if attempt < retries:
                time.sleep(2)
            else:
                print(f"  🚫 Skipping poll {poll_index}")
                return None


def run_quiz_system():
    print(f"--- Starting Clean Run for regNo: {REG_NO} ---")

    seen_events = set()
    participant_scores = {}

    successful_polls = 0
    poll_index = 0

    while successful_polls < 10 and poll_index < 10:
        print(f"\nPolling {poll_index}/9...")

        data = fetch_poll_with_retry(poll_index)

        if data:
            events = data.get("events", [])
            new_events = 0

            for event in events:
                r_id = event.get("roundId")
                p_name = event.get("participant")
                score = event.get("score")

                # ✅ FINAL CORRECT KEY
                key = f"{r_id}|{p_name}|{score}"

                if key not in seen_events:
                    seen_events.add(key)
                    new_events += 1

                    # aggregate
                    participant_scores[p_name] = (
                        participant_scores.get(p_name, 0) + score
                    )

            print(f"  ✅ Received {len(events)} events | New unique: {new_events}")

            successful_polls += 1

            if successful_polls < 10:
                time.sleep(5)

        poll_index += 1

    print(f"\n📊 Total unique events: {len(seen_events)}")

    # leaderboard
    leaderboard = [
        {"participant": p, "totalScore": s}
        for p, s in participant_scores.items()
    ]

    leaderboard.sort(key=lambda x: x["totalScore"], reverse=True)

    total_score = sum(item["totalScore"] for item in leaderboard)

    print("\n🏆 Final Leaderboard:")
    for entry in leaderboard:
        print(f"{entry['participant']}: {entry['totalScore']}")

    print(f"\n🎯 Total Score: {total_score}")

    # submit
    print("\n📤 Submitting...")

    payload = {
        "regNo": REG_NO,
        "leaderboard": leaderboard
    }

    try:
        response = requests.post(
            f"{BASE_URL}/quiz/submit",
            json=payload,
            timeout=15
        )
        response.raise_for_status()
        result = response.json()

        print("\n--- FINAL RESPONSE ---")
        print(json.dumps(result, indent=2))

        if result.get("isCorrect"):
            print("\n🎉 SUCCESS: Correct Leaderboard!")
        else:
            print("\n❌ Still incorrect — but now it's definitely a data issue.")

    except Exception as e:
        print(f"🚨 Submission error: {e}")


if __name__ == "__main__":
    run_quiz_system()

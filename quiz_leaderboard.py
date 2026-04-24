import requests
import time

BASE_URL    = "https://devapigw.vidalhealthtpa.com/srm-quiz-task"
REG_NO      = "2024CS101"   # <-- change this to your reg number
DELAY_SEC   = 5
TOTAL_POLLS = 10


def fetch_poll(poll: int) -> dict:
    url = f"{BASE_URL}/quiz/messages"
    params = {"regNo": REG_NO, "poll": poll}
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def submit_leaderboard(leaderboard: list) -> dict:
    url = f"{BASE_URL}/quiz/submit"
    payload = {"regNo": REG_NO, "leaderboard": leaderboard}
    resp = requests.post(url, json=payload, timeout=30)
    print(f"\n  [DEBUG] Submit status code : {resp.status_code}")
    print(f"  [DEBUG] Raw response       : {resp.text}\n")
    resp.raise_for_status()
    return resp.json()


def main():
    print("\n=== Quiz Leaderboard System ===")
    print(f"regNo     : {REG_NO}")
    print(f"Base URL  : {BASE_URL}")
    print(f"Polls     : {TOTAL_POLLS}  ({DELAY_SEC}s delay between each)\n")

    seen   = set()
    scores = {}
    total_raw = 0

    for poll in range(TOTAL_POLLS):
        if poll > 0:
            print(f"  Waiting {DELAY_SEC}s before next poll...")
            time.sleep(DELAY_SEC)

        print(f"Poll {poll:02d}: ", end="", flush=True)

        try:
            data = fetch_poll(poll)
        except Exception as e:
            print(f"ERROR — {e}")
            continue

        events    = data.get("events", [])
        total_raw += len(events)
        new_count  = 0
        dupe_count = 0

        for ev in events:
            key = f"{ev['roundId']}|{ev['participant']}"
            if key in seen:
                dupe_count += 1
                continue
            seen.add(key)
            scores[ev["participant"]] = scores.get(ev["participant"], 0) + ev["score"]
            new_count += 1

        print(f"{len(events)} events received — {new_count} new, {dupe_count} duplicates dropped")

    leaderboard = [
        {"participant": p, "totalScore": s}
        for p, s in sorted(scores.items(), key=lambda x: x[1], reverse=True)
    ]
    grand_total = sum(p["totalScore"] for p in leaderboard)

    print(f"\n--- Leaderboard ({len(leaderboard)} participants) ---")
    for i, p in enumerate(leaderboard, 1):
        print(f"  {i:2}. {p['participant']:<20} {p['totalScore']}")
    print(f"     Grand total : {grand_total}")
    print(f"     Raw events  : {total_raw}")
    print(f"     Unique      : {len(seen)}")

    print("\nSubmitting leaderboard...")
    try:
        result = submit_leaderboard(leaderboard)
    except Exception as e:
        print(f"Submit failed: {e}")
        return

    print("=== Submit Result ===")
    for key, val in result.items():
        print(f"  {key:<20} : {val}")

    is_correct = (
        result.get("isCorrect")
        or result.get("correct")
        or result.get("status") == "success"
        or str(result.get("message", "")).lower() in ("correct!", "correct", "success")
    )

    if is_correct:
        print("\n✓ Success!")
    else:
        print("\n✗ Check the [DEBUG] raw response above to see what the API returned.")


if __name__ == "__main__":
    main()

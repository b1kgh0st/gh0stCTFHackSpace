import os, hashlib, json
from pathlib import Path

SECRET = os.environ["CTF_SECRET"]
CHALLENGES = {
    1: hashlib.sha256((SECRET + "ghost_injection").encode()).hexdigest()[:32],
    2: hashlib.sha256((SECRET + "phantom_crypto").encode()).hexdigest()[:32],
    3: hashlib.sha256((SECRET + "nebula_signal").encode()).hexdigest()[:32],
    4: hashlib.sha256((SECRET + "spectral_re").encode()).hexdigest()[:32],
    5: hashlib.sha256((SECRET + "void_overflow").encode()).hexdigest()[:32],
}

def verify_submission(file_path):
    with open(file_path) as f:
        data = json.load(f)
    username = data.get("username")
    flags = data.get("flags", {})
    correct = 0
    solved = []
    for cid_str, flag in flags.items():
        cid = int(cid_str)
        if cid in CHALLENGES and flag.strip() == CHALLENGES[cid]:
            correct += 1
            solved.append(cid)
    print(f"Verified {username}: {correct}/5")
    Path("leaderboard").mkdir(exist_ok=True)
    with open(f"leaderboard/{username}.json", "w") as f:
        json.dump({"username": username, "solved": solved, "score": correct}, f, indent=2)

if __name__ == "__main__":
    for f in Path("submissions").glob("*.json"):
        verify_submission(f)

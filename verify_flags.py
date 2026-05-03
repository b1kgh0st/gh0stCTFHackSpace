import os
import json
import hashlib
import sys
from pathlib import Path
import urllib.request

# Load Environment Variables
try:
    SECRET = os.environ["CTF_SECRET"]
    AUTHOR = os.environ["ISSUE_AUTHOR"]
    ISSUE_NUMBER = os.environ["ISSUE_NUMBER"]
    REPO = os.environ["GITHUB_REPOSITORY"]
    GH_TOKEN = os.environ["GH_TOKEN"]
    # GitHub saves the entire event payload to a JSON file locally
    EVENT_PATH = os.environ["GITHUB_EVENT_PATH"] 
except KeyError as e:
    print(f"Missing env var: {e}")
    sys.exit(1)

CHALLENGES = {
    1: hashlib.sha256((SECRET + "ghost_injection").encode()).hexdigest()[:32],
    2: hashlib.sha256((SECRET + "phantom_crypto").encode()).hexdigest()[:32],
    3: hashlib.sha256((SECRET + "nebula_signal").encode()).hexdigest()[:32],
    4: hashlib.sha256((SECRET + "spectral_re").encode()).hexdigest()[:32],
    5: hashlib.sha256((SECRET + "void_overflow").encode()).hexdigest()[:32],
}

def close_and_comment(message):
    """Uses the GitHub API to comment on and close the issue."""
    url = f"https://api.github.com/repos/{REPO}/issues/{ISSUE_NUMBER}/comments"
    req = urllib.request.Request(url, method="POST", headers={
        "Authorization": f"Bearer {GH_TOKEN}",
        "Accept": "application/vnd.github+json"
    }, data=json.dumps({"body": message}).encode("utf-8"))
    urllib.request.urlopen(req)

    # Close the issue
    close_url = f"https://api.github.com/repos/{REPO}/issues/{ISSUE_NUMBER}"
    close_req = urllib.request.Request(close_url, method="PATCH", headers={
        "Authorization": f"Bearer {GH_TOKEN}",
        "Accept": "application/vnd.github+json"
    }, data=json.dumps({"state": "closed"}).encode("utf-8"))
    urllib.request.urlopen(close_req)

def process_issue():
    # Read the issue body securely from the event payload
    with open(EVENT_PATH, 'r') as f:
        event_data = json.load(f)
    
    issue_body = event_data['issue']['body']
    
    # Very basic parsing (You can make this more robust)
    # Expecting format:
    # Challenge: 1
    # Flag: 12345abcdef
    try:
        lines = issue_body.replace('\r', '').split('\n')
        cid = int(lines[0].split(':')[1].strip())
        submitted_flag = lines[1].split(':')[1].strip()
    except Exception:
        close_and_comment("❌ Invalid format. Please use:\nChallenge: <ID>\nFlag: <Hash>")
        sys.exit(0)

    # Verify
    if cid in CHALLENGES and submitted_flag == CHALLENGES[cid]:
        print(f"Correct flag submitted by {AUTHOR} for Challenge {cid}")
        
        # Load existing user data or create new
        Path("leaderboard").mkdir(exist_ok=True)
        user_file = Path(f"leaderboard/{AUTHOR}.json")
        
        if user_file.exists():
            with open(user_file, "r") as f:
                user_data = json.load(f)
        else:
            user_data = {"username": AUTHOR, "solved": [], "score": 0}
            
        # Update if they haven't solved it yet
        if cid not in user_data["solved"]:
            user_data["solved"].append(cid)
            user_data["score"] += 1
            
            with open(user_file, "w") as f:
                json.dump(user_data, f, indent=2)
                
            close_and_comment(f"✅ Correct! You have been awarded points for Challenge {cid}.")
        else:
            close_and_comment("⚠️ You have already solved this challenge.")
    else:
        close_and_comment("❌ Incorrect flag. Keep trying!")

if __name__ == "__main__":
    process_issue()

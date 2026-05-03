import os
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

# 1. Load Environment Variables injected by GitHub Actions
try:
    SECRET = os.environ["CTF_SECRET"]
    GH_TOKEN = os.environ["GH_TOKEN"]
    PR_NUMBER = os.environ["PR_NUMBER"]
    REPO = os.environ["GITHUB_REPOSITORY"] # e.g., "username/gh0stCTF"
except KeyError as e:
    print(f"Missing required environment variable: {e}")
    sys.exit(1)

CHALLENGES = {
    1: hashlib.sha256((SECRET + "ghost_injection").encode()).hexdigest()[:32],
    2: hashlib.sha256((SECRET + "phantom_crypto").encode()).hexdigest()[:32],
    3: hashlib.sha256((SECRET + "nebula_signal").encode()).hexdigest()[:32],
    4: hashlib.sha256((SECRET + "spectral_re").encode()).hexdigest()[:32],
    5: hashlib.sha256((SECRET + "void_overflow").encode()).hexdigest()[:32],
}

def fetch_pr_submission_data():
    """Fetches the changed files from the PR via the GitHub API."""
    url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}/files"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {GH_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    })
    
    try:
        with urllib.request.urlopen(req) as response:
            files_data = json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching PR file list: {e}")
        sys.exit(1)

    # Filter for JSON files that were added or modified
    # (You can add `and f['filename'].startswith('submissions/')` if needed)
    submission_files = [f for f in files_data if f['filename'].endswith('.json') and f['status'] in ['added', 'modified']]

    if not submission_files:
        print("No JSON submission files found in this PR. Skipping.")
        sys.exit(0) # Exit cleanly so the workflow doesn't fail, just skips

    # Fetch the actual content of the first matching file
    raw_url = submission_files[0]['raw_url']
    req_raw = urllib.request.Request(raw_url, headers={
        "Authorization": f"Bearer {GH_TOKEN}"
    })

    try:
        with urllib.request.urlopen(req_raw) as response:
            content = response.read().decode()
            return json.loads(content)
    except Exception as e:
        print(f"Error reading raw submission data: {e}")
        sys.exit(1)

def verify_submission(data):
    """Verifies the parsed JSON data against the challenge hashes."""
    username = data.get("username")
    if not username:
        print("Error: Submission missing 'username' field.")
        sys.exit(1)
        
    flags = data.get("flags", {})
    correct = 0
    solved = []
    
    for cid_str, flag in flags.items():
        try:
            cid = int(cid_str)
        except ValueError:
            continue # Skip invalid challenge IDs
            
        if cid in CHALLENGES and flag.strip() == CHALLENGES[cid]:
            correct += 1
            solved.append(cid)
            
    print(f"Verified {username}: {correct}/5")
    
    # Save the updated leaderboard data
    Path("leaderboard").mkdir(exist_ok=True)
    with open(f"leaderboard/{username}.json", "w") as f:
        json.dump({"username": username, "solved": solved, "score": correct}, f, indent=2)

if __name__ == "__main__":
    print(f"Checking PR #{PR_NUMBER} in {REPO}...")
    
    # 1. Fetch data safely via API
    submission_data = fetch_pr_submission_data()
    
    # 2. Process the data and generate leaderboard file
    verify_submission(submission_data)

import json
from pathlib import Path

def generate_global_leaderboard():
    leaderboard_dir = Path("leaderboard")
    
    # Ensure the directory exists
    if not leaderboard_dir.exists():
        print("No leaderboard directory found. Nothing to update.")
        return

    players = []
    
    # 1. Read all individual player JSON files
    for filepath in leaderboard_dir.glob("*.json"):
        if filepath.name == "global_leaderboard.json":
            continue # Skip the master file if it already exists
            
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                # Ensure the data has the required fields
                if "username" in data and "score" in data:
                    players.append(data)
        except Exception as e:
            print(f"Error reading {filepath.name}: {e}")

    # 2. Sort the players by score (highest to lowest)
    # If you want to add a tie-breaker (like submission time), you would add it here
    players.sort(key=lambda x: x.get("score", 0), reverse=True)

    # 3. Assign ranks (properly handling ties)
    current_rank = 1
    for i, player in enumerate(players):
        # If this isn't the first player, and their score is lower than the previous player's, increase the rank
        if i > 0 and player.get("score") < players[i-1].get("score"):
            current_rank = i + 1
        
        player["rank"] = current_rank

    # 4. Save the aggregated master list
    master_file = leaderboard_dir / "global_leaderboard.json"
    with open(master_file, "w") as f:
        json.dump({"leaderboard": players}, f, indent=2)
        
    print(f"Successfully aggregated {len(players)} players into global_leaderboard.json")

if __name__ == "__main__":
    generate_global_leaderboard()

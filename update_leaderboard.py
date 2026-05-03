import json
from pathlib import Path

leaderboard = []
for f in Path("leaderboard").glob("*.json"):
    with open(f) as file:
        leaderboard.append(json.load(file))

leaderboard.sort(key=lambda x: (-x["score"], x.get("timestamp","")))

html = """<!DOCTYPE html>
<html><head><title>gh0stCTFHackSpace Leaderboard</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-black text-green-400 font-mono p-8">
<h1 class="text-5xl mb-8">👻 LEADERBOARD</h1>
<table class="w-full border-collapse">
<tr><th class="text-left p-4 border-b">Rank</th><th class="text-left p-4 border-b">Player</th><th class="text-left p-4 border-b">Solved</th><th class="text-left p-4 border-b">Score</th></tr>"""
for i, entry in enumerate(leaderboard, 1):
    html += f'<tr><td class="p-4 border-b">{i}</td><td class="p-4 border-b">{entry["username"]}</td><td class="p-4 border-b">{entry["solved"]}</td><td class="p-4 border-b font-bold">{entry["score"]}/5</td></tr>\n'
html += "</table></body></html>"

Path("leaderboard/index.html").write_text(html)
print("Leaderboard updated")

import http.server
import socketserver
import json
import random
import os
from urllib.parse import parse_qs, urlparse

# Load/Save Leaderboard (simple JSON file)
LEADERBOARD_FILE = 'leaderboard.json'
def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'r') as f:
            return json.load(f)
    return {1: [], 2: [], 3: []}  # Levels 1,2,3

def save_leaderboard(data):
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(data, f)

leaderboard = load_leaderboard()

# Game State (in-memory for simplicity; resets on server restart)
game_state = {}  # Stores active games: {session_id: {'targets': {player: target}, 'attempts': int, 'level': int, 'players': list, 'current_player': int, 'scores': {}}}

class GameHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = parse_qs(post_data)
        
        if self.path == '/start_game':
            session_id = data.get('session_id', [''])[0]
            level = int(data.get('level', [1])[0])
            players = json.loads(data.get('players', ['[]'])[0])  # List of player names
            ranges = {1: (1, 50), 2: (1, 100), 3: (1, 500)}
            min_val, max_val = ranges[level]
            # Generate unique random targets for each player (using your original random logic) - FIXED PER PLAYER
            targets = {player: random.randint(min_val, max_val) for player in players}
            game_state[session_id] = {'targets': targets, 'attempts': 0, 'level': level, 'players': players, 'current_player': 0, 'scores': {}}
            print(f"Game started for session {session_id}: Targets {targets}")  # Debug: Shows targets (remove later)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'started'}).encode())
        
        elif self.path == '/guess':
            session_id = data.get('session_id', [''])[0]
            guess = int(data.get('guess', [0])[0])
            if session_id not in game_state:
                self.send_response(400)
                self.end_headers()
                return
            state = game_state[session_id]
            current_player = state['players'][state['current_player']]
            target = state['targets'][current_player]  # TARGET IS FIXED FOR THIS PLAYER'S TURN
            print(f"Guess for {current_player}: {guess}, Target: {target}")  # Debug: Shows target per guess (remove later)
            state['attempts'] += 1
            if guess == target:
                state['scores'][current_player] = state['attempts']
                # Save to leaderboard
                leaderboard[state['level']].append({'name': current_player, 'attempts': state['attempts']})
                leaderboard[state['level']].sort(key=lambda x: x['attempts'])
                leaderboard[state['level']] = leaderboard[state['level']][:10]  # Top 10
                save_leaderboard(leaderboard)
                print(f"Win for {current_player} with {state['attempts']} attempts")  # Debug
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({'result': 'win', 'attempts': state['attempts']}).encode())
            elif guess > target:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({'result': 'high'}).encode())
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({'result': 'low'}).encode())
        
        elif self.path == '/next_player':
            session_id = data.get('session_id', [''])[0]
            state = game_state[session_id]
            state['current_player'] += 1
            state['attempts'] = 0  # Reset attempts for new player
            print(f"Switching to player {state['current_player']}")  # Debug
            if state['current_player'] >= len(state['players']):
                # End multiplayer
                sorted_scores = sorted(state['scores'].items(), key=lambda x: x[1])
                print("Game over, leaderboard:", sorted_scores)  # Debug
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({'result': 'game_over', 'leaderboard': sorted_scores}).encode())
            else:
                next_player = state['players'][state['current_player']]
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({'result': 'next', 'player': next_player}).encode())
        
        elif self.path == '/quit':
            session_id = data.get('session_id', [''])[0]
            del game_state[session_id]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'quit'}).encode())
    
    def do_GET(self):
        if self.path.startswith('/leaderboard'):
            level = int(parse_qs(urlparse(self.path).query).get('level', [1])[0])
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(leaderboard[level]).encode())
        else:
            # Serve static files (HTML, CSS, JS)
            if self.path == '/' or self.path == '/index.html':
                self.serve_file('index.html', 'text/html')
            elif self.path == '/style.css':
                self.serve_file('style.css', 'text/css')
            elif self.path == '/script.js':
                self.serve_file('script.js', 'application/javascript')
    
    def serve_file(self, filename, content_type):
        try:
            with open(filename, 'rb') as f:
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.end_headers()
                self.wfile.write(f.read())
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()

# Run the server
with socketserver.TCPServer(("", 8000), GameHandler) as httpd:
    print("Server running on http://localhost:8000")
    httpd.serve_forever()
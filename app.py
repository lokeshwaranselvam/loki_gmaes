from flask import Flask, request, jsonify, render_template
import json, random, string, os

app = Flask(__name__)
DATA_FILE = 'game_data.json'

# Initialize the JSON data file
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({}, f)

def load_data():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

def generate_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_room', methods=['POST'])
def create_room():
    data = load_data()
    code = generate_room_code()
    while code in data:
        code = generate_room_code()
    data[code] = {
        "players": [],
        "moves": {},
        "score": 0,
        "turn": "batsman"
    }
    save_data(data)
    return jsonify({"room_code": code})

@app.route('/join_room/<room_code>', methods=['POST'])
def join_room(room_code):
    data = load_data()
    if room_code not in data:
        return jsonify({"error": "Room not found"}), 404
    if len(data[room_code]["players"]) >= 2:
        return jsonify({"error": "Room full"}), 403
    player_id = len(data[room_code]["players"])
    data[room_code]["players"].append(f"player{player_id+1}")
    save_data(data)
    return jsonify({"role": "batsman" if player_id == 0 else "bowler"})

@app.route('/submit_move', methods=['POST'])
def submit_move():
    req = request.json
    room = req['room']
    player = req['player']
    move = req['move']
    data = load_data()
    if room in data:
        data[room]["moves"][player] = move
        save_data(data)
        return jsonify({"status": "Move recorded"})
    return jsonify({"error": "Room not found"}), 404

@app.route('/get_state/<room>', methods=['GET'])
def get_state(room):
    data = load_data()
    if room in data:
        return jsonify(data[room])
    return jsonify({"error": "Room not found"}), 404

@app.route('/reset_moves/<room>', methods=['POST'])
def reset_moves(room):
    data = load_data()
    if room in data:
        data[room]["moves"] = {}
        save_data(data)
        return jsonify({"status": "Moves reset"})
    return jsonify({"error": "Room not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)

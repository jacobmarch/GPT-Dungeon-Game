from flask import Flask, render_template, request, redirect, url_for, session
import json
from Constants import API_KEY

app = Flask(__name__)
app.secret_key = API_KEY  # Needed for session management

# Initialize the game state
def init_game():
    grid = [[' ' for _ in range(3)] for _ in range(3)]
    # Positions of player, enemy, friendly AI, and trap
    positions = {'player': (0, 0), 'enemy': (2, 2), 'friendly_ai': (0, 2), 'trap': (1, 1)}
    grid[positions['player'][0]][positions['player'][1]] = 'P'
    grid[positions['enemy'][0]][positions['enemy'][1]] = 'E'
    grid[positions['friendly_ai'][0]][positions['friendly_ai'][1]] = 'F'
    grid[positions['trap'][0]][positions['trap'][1]] = 'T'
    session['grid'] = grid
    session['positions'] = positions

@app.route('/')
def home():
    if 'grid' not in session:
        init_game()
    return render_template('game.html', grid=session['grid'])

@app.route('/reset')
def reset_game():
    init_game()
    return redirect(url_for('home'))

def move_player(direction):
    positions = session['positions']
    grid = session['grid']
    x, y = positions['player']
    new_pos = (x, y)  # Default to current position in case of no movement

    if direction == "up" and x > 0:
        new_pos = (x - 1, y)
    elif direction == "down" and x < 2:
        new_pos = (x + 1, y)
    elif direction == "left" and y > 0:
        new_pos = (x, y - 1)
    elif direction == "right" and y < 2:
        new_pos = (x, y + 1)

    # Update grid
    grid[positions['player'][0]][positions['player'][1]] = ' '  # Clear old position
    positions['player'] = new_pos
    grid[new_pos[0]][new_pos[1]] = 'P'  # Move player to new position

    entity = grid[new_pos[0]][new_pos[1]]  # Get entity at new position
    message, item = encounter_check(entity, new_pos)  # Pass entity and new position
    session['grid'] = grid
    return message, item

def encounter_check(entity, new_pos):
    x, y = new_pos
    if entity == 'E':
        return 'You have encountered an enemy!', None
    elif entity == 'F':
        return 'You meet a friendly wizard. He gives you a potion.', 'Potion'
    elif entity == 'T':
        return 'You stepped on a trap! It hurts.', None
    return 'You move safely.', None

@app.route('/move/<direction>')
def move(direction):
    if 'grid' not in session:
        init_game()
    message, item = move_player(direction)
    inventory = session.get('inventory', [])
    if item:
        inventory.append(item)
        session['inventory'] = inventory
    return {'grid': session['grid'], 'message': message, 'inventory': inventory}

if __name__ == "__main__":
    app.run(debug=True)

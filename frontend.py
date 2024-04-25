from engine import Engine

# Symbols for entities
EMPTY = ' '
PLAYER = 'P'
ENEMY = 'E'
FRIENDLY_AI = 'F'  # For example, a wizard
TRAP = 'T'

# Initialize a 3x3 grid
grid = [[EMPTY for _ in range(3)] for _ in range(3)]

# Positions of entities
positions = {
    "player": (0, 0),
    "enemy": (2, 2),
    "friendly_ai": (0, 2),  # Example: wizard's position
    "trap": (1, 1)
}

engine = Engine(positions)

# Place entities on the grid
grid[engine.positions["player"][0]][engine.positions["player"][1]] = PLAYER
grid[engine.positions["enemy"][0]][engine.positions["enemy"][1]] = ENEMY
grid[engine.positions["friendly_ai"][0]][engine.positions["friendly_ai"][1]] = FRIENDLY_AI
grid[engine.positions["trap"][0]][engine.positions["trap"][1]] = TRAP

def display_grid():
    for row in grid:
        print('|'.join(row))
        print('-' * 5)  # Separator for rows
        
def move_player(direction):
    global positions  # Ensure we're modifying the global positions
    
    # Calculate new position
    x, y = positions["player"]
    if direction == "up":
        x = max(0, x - 1)
    elif direction == "down":
        x = min(2, x + 1)
    elif direction == "left":
        y = max(0, y - 1)
    elif direction == "right":
        y = min(2, y + 1)
    
    new_pos = (x, y)
    
    # Update player position on grid
    grid[engine.positions["player"][0]][engine.positions["player"][1]] = EMPTY
    engine.positions["player"] = new_pos
    grid[x][y] = PLAYER
    
    # Check for encounters
    engine.encounter_check(new_pos)
    
def main():
    while True:
        display_grid()
        command = input("Enter your move (up, down, left, right) or 'quit' to exit: ").lower()
        if command == "quit":
            break
        move_player(command)

if __name__ == "__main__":
    main()
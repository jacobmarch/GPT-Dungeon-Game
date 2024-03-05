from openai import OpenAI

client = OpenAI(api_key="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")

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

# Place entities on the grid
grid[positions["player"][0]][positions["player"][1]] = PLAYER
grid[positions["enemy"][0]][positions["enemy"][1]] = ENEMY
grid[positions["friendly_ai"][0]][positions["friendly_ai"][1]] = FRIENDLY_AI
grid[positions["trap"][0]][positions["trap"][1]] = TRAP

def navigate_trap(player_input):
    resolved = False
    while not resolved:
        conversation = [
            {"role": "system", "content": "You are the dungeon master narrating the outcome of a player's attempt to navigate or disarm a trap. The trap is a hidden pitfall covered with fragile planks disguised as solid ground."},
            {"role": "user", "content": player_input}
        ]
        
        response = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=conversation)
        
        dm_response = response.choices[0].message.content
        print(f"\"{dm_response}\"")
        
        # Check if the situation is resolved based on the response
        # This can be a keyword or phrase indicating resolution
        if "successfully" in dm_response or "fail" in dm_response:
            resolved = True
        else:
            player_input = input("What do you do next? ")


def encounter_enemy(player_input):
    resolved = False
    while not resolved:
        conversation = [
            {"role": "system", "content": "You are the dungeon master. Narrate the outcome of a player's encounter with a goblin armed with a rusty sword. The player has a shield and a dagger."},
            {"role": "user", "content": player_input}
        ]
        
        response = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=conversation)
        
        dm_response = response.choices[0].message.content
        print(f"\"{dm_response}\"")
        
        # Check for resolution indicators
        if "defeats the goblin" in dm_response or "is defeated" in dm_response:
            resolved = True
        else:
            player_input = input("What do you do next? ")

    
def interact_with_friendly(player_input):
    conversation = [
        {"role": "system", "content": "You are the dungeon master in a fantasy RPG setting. A player has encountered a wise wizard. The player is allowed to make one request or ask one question. The wizard, known for his knowledge and magical abilities, will provide an answer, a magical item, or assistance, based on what he deems most helpful to the player's journey. After fulfilling the request, the wizard will leave, concluding the interaction. Your narration should include the wizard's response to the player's request, detail the item or information provided, and describe the wizard's departure in a way that feels meaningful and impactful."},
        {"role": "user", "content": player_input}
    ]
    
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=conversation)
    
    dm_response = response.choices[0].message.content
    print(f"\"{dm_response}\"")




def encounter_check(position):
    if position == positions["enemy"]:
        player_input = input("You encounter a menacing goblin. What do you do? ")
        encounter_enemy(player_input)
    elif position == positions["friendly_ai"]:
        player_input = input("A wise wizard greets you. What do you ask? ")
        interact_with_friendly(player_input)
    elif position == positions["trap"]:
        player_input = input("A hidden trap lies before you. How do you proceed? ")
        navigate_trap(player_input)


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
    grid[positions["player"][0]][positions["player"][1]] = EMPTY
    positions["player"] = new_pos
    grid[x][y] = PLAYER
    
    # Check for encounters
    encounter_check(new_pos)


def main():
    while True:
        display_grid()
        command = input("Enter your move (up, down, left, right) or 'quit' to exit: ").lower()
        if command == "quit":
            break
        move_player(command)

if __name__ == "__main__":
    main()

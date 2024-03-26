from openai import OpenAI
from Constants import API_KEY
import json

client = OpenAI(api_key=API_KEY)

# Symbols for entities
EMPTY = ' '
PLAYER = 'P'
ENEMY = 'E'
FRIENDLY_AI = 'F'  # For example, a wizard
TRAP = 'T'

# Initialize a 3x3 grid
grid = [[EMPTY for _ in range(3)] for _ in range(3)]

conversation_history = []

# Positions of entities
positions = {
    "player": (0, 0),
    "enemy": (2, 2),
    "friendly_ai": (0, 2),  # Example: wizard's position
    "trap": (1, 1)
}

encounter_status = {
    "enemy": False,  # Initially not completed
    "friendly_ai": False,
    "trap": False
}

def parse_ai_response(response, player_info):
    lines = response.split("\n")
    for line in lines:
        if line.startswith("GAIN ITEM"):
            item = line.split("GAIN ITEM")[1].strip()
            player_info["equipment"].append(item)
        elif line.startswith("GAIN SKILL"):
            skill = line.split("GAIN SKILL")[1].strip()
            player_info["skills"].append(skill)
        elif line.startswith("GAIN SPELL"):
            spell = line.split("GAIN SPELL")[1].strip()
            player_info["spells"].append(spell)
        elif line.startswith("LOST ITEM"):
            item = line.split("LOST ITEM")[1].strip()
            if item in player_info["equipment"]:
                player_info["equipment"].remove(item)
        elif line.startswith("LOST SKILL"):
            skill = line.split("LOST SKILL")[1].strip()
            if skill in player_info["skills"]:
                player_info["skills"].remove(skill)
        elif line.startswith("LOST SPELL"):
            spell = line.split("LOST SPELL")[1].strip()
            if spell in player_info["spells"]:
                player_info["spells"].remove(spell)
        elif line.startswith("DAMAGE"):
            # Handle damage to the player
            pass

    with open("db.json", "r") as f:
        data = json.load(f)

    # Save the updated player information back to the JSON file
    with open("db.json", "w") as f:
        json.dump({"scenarios": data["scenarios"], "player": player_info}, f, indent=2)

def encounter_check(position):
    player_info = load_player_info()
    if position == positions["enemy"] and not encounter_status["enemy"]:
        player_input = input("You encounter a menacing goblin. What do you do? ")
        if encounter_enemy(player_input, player_info):
            encounter_status["enemy"] = True
    elif position == positions["friendly_ai"] and not encounter_status["friendly_ai"]:
        player_input = input("A wise wizard greets you. What do you ask? ")
        if interact_with_friendly(player_input, player_info):
            encounter_status["friendly_ai"] = True
    elif position == positions["trap"] and not encounter_status["trap"]:
        player_input = input("A hidden trap lies before you. How do you proceed? ")
        if navigate_trap(player_input, player_info):
            encounter_status["trap"] = True

# Place entities on the grid
grid[positions["player"][0]][positions["player"][1]] = PLAYER
grid[positions["enemy"][0]][positions["enemy"][1]] = ENEMY
grid[positions["friendly_ai"][0]][positions["friendly_ai"][1]] = FRIENDLY_AI
grid[positions["trap"][0]][positions["trap"][1]] = TRAP

def retrieve_context(situation):
    """Retrieves relevant knowledge from the knowledge base."""
    with open("db.json", "r") as f:
        data = json.load(f)
    return data["scenarios"].get(situation, {}).get("description", None)

def load_player_info():
    with open("db.json", "r") as f:
        data = json.load(f)
    return data["player"]

def navigate_trap(player_input, player_info):
    context = retrieve_context("trap")
    conversation = conversation_history + [ 
        {"role": "system", "content": "You are the dungeon master narrating the outcome of a player's attempt to navigate or disarm a trap. The trap is a hidden pitfall covered with fragile planks disguised as solid ground."},
    ]

    if context:
        conversation.append({"role": "system", "content": context}) 

    conversation.append({"role": "system", "content": f"Player Information:\nSkills: {', '.join(player_info['skills'])}\nSpells: {', '.join(player_info['spells'])}\nEquipment: {', '.join(player_info['equipment'])}"})

    conversation.append({"role": "system", "content": "The outcome of this encounter depends entirely on the player's actions and your interpretation of the situation. If the player successfully navigates or disarms the trap, narrate the outcome and include the phrase 'Encounter Completed'. If the player fails to overcome the trap, describe the consequences. Please format your response as follows:\n\nNarrative: [Describe what happened after the player's action]\n\nGAIN ITEM item_name (if the player gained an item)\nGAIN SKILL skill_name (if the player gained a skill)\nGAIN SPELL spell_name (if the player gained a spell)\nLOST ITEM item_name (if the player lost an item or had it changed to a different item)\nLOST SKILL skill_name (if the player lost a skill)\nLOST SPELL spell_name (if the player lost a spell)\nDAMAGE (if the player was harmed in some way)"})  

    encounter_completed = False
    while not encounter_completed:
        conversation.append({"role": "user", "content": player_input})

        response = client.chat.completions.create(model="ft:gpt-3.5-turbo-0125:personal::96kWJrDA", messages=conversation)
        dm_response = response.choices[0].message.content
        print(f"\"{dm_response}\"")

        conversation_history.append({"role": "system", "content": dm_response}) 

        encounter_completed = "Encounter Completed" in dm_response  

        parse_ai_response(dm_response, player_info)

        if not encounter_completed:
            player_input = input("What do you do next? ") 
    
    conversation_history.clear()  # Clear history after each attempt
    
    return True

def encounter_enemy(player_input, player_info):
    context = retrieve_context("enemy")
    conversation = conversation_history + [
        {"role": "system", "content": "You are the dungeon master. Narrate the outcome of a player's encounter with a goblin armed with a rusty sword. The player has a shield and a dagger."},
    ]

    if context:
        conversation.append({"role": "system", "content": context}) 

    conversation.append({"role": "system", "content": f"Player Information:\nSkills: {', '.join(player_info['skills'])}\nSpells: {', '.join(player_info['spells'])}\nEquipment: {', '.join(player_info['equipment'])}"})

    conversation.append({"role": "system", "content": "The outcome of this encounter depends entirely on the player's actions and your interpretation of the situation. If the player successfully defeats the goblin, narrate the outcome and include the phrase 'Encounter Completed'. If the goblin overcomes the player, describe the consequences. Please format your response as follows:\n\nNarrative: [Describe what happened after the player's action]\n\nGAIN ITEM item_name (if the player gained an item)\nGAIN SKILL skill_name (if the player gained a skill)\nGAIN SPELL spell_name (if the player gained a spell)\nLOST ITEM item_name (if the player lost an item or had it changed to a different item)\nLOST SKILL skill_name (if the player lost a skill)\nLOST SPELL spell_name (if the player lost a spell)\nDAMAGE (if the player was harmed in some way)"})

    encounter_completed = False
    while not encounter_completed:
        conversation.append({"role": "user", "content": player_input})

        response = client.chat.completions.create(model="ft:gpt-3.5-turbo-0125:personal::96kWJrDA", messages=conversation)
        dm_response = response.choices[0].message.content
        print(f"\"{dm_response}\"")

        conversation_history.append({"role": "system", "content": dm_response}) 

        encounter_completed = "Encounter Completed" in dm_response  

        parse_ai_response(dm_response, player_info)

        if not encounter_completed:
            player_input = input("What do you do next? ")
    
    conversation_history.clear()
    return True


def interact_with_friendly(player_input, player_info):
    context = retrieve_context("friendly") 
    conversation = conversation_history + [
        {"role": "system", "content": "You are the dungeon master in a fantasy RPG setting. A player has encountered a wise wizard. The player is allowed to make one request or ask one question. The wizard, known for his knowledge and magical abilities, will provide an answer, a magical item, or assistance, based on what he deems most helpful to the player's journey. After fulfilling the request, the wizard will leave, concluding the interaction. Your narration should include the wizard's response to the player's request, detail the item or information provided, and describe the wizard's departure in a way that feels meaningful and impactful."},
    ]

    if context:
        conversation.append({"role": "system", "content": context}) 

    conversation.append({"role": "system", "content": f"Player Information:\nSkills: {', '.join(player_info['skills'])}\nSpells: {', '.join(player_info['spells'])}\nEquipment: {', '.join(player_info['equipment'])}"})

    conversation.append({"role": "system", "content": "Please format your response as follows:\n\nNarrative: [Describe the wizard's response to the player's request, the item or information provided, and the wizard's departure]\n\nGAIN ITEM item_name (if the player gained an item)\nGAIN SKILL skill_name (if the player gained a skill)\nGAIN SPELL spell_name (if the player gained a spell)\nLOST ITEM item_name (if the player lost an item or had it changed to a different item)\nLOST SKILL skill_name (if the player lost a skill)\nLOST SPELL spell_name (if the player lost a spell)\nDAMAGE (if the player was harmed in some way)"})

    conversation.append({"role": "user", "content": player_input})

    response = client.chat.completions.create(model="ft:gpt-3.5-turbo-0125:personal::96kWJrDA", messages=conversation)
    dm_response = response.choices[0].message.content
    print(f"\"{dm_response}\"")

    conversation_history.append({"role": "system", "content": dm_response}) 

    parse_ai_response(dm_response, player_info)

    conversation_history.clear()  # Clear history after wizard interaction
    
    return True


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

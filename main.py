from openai import OpenAI
from Constants import API_KEY
import json
import random

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

    with open("player_info.json", "r") as f:
        data = json.load(f)

    # Save the updated player information back to the JSON file
    with open("player_info.json", "w") as f:
        json.dump({"scenarios": data["scenarios"], "player": player_info}, f, indent=2)

enemy_type = random.choice(["Goblins", "Skeletons", "Mimics"])
friendly_type = random.choice(["Wizards", "Blacksmiths"])
trap_type = random.choice(["Pitfall traps", "Poison dart traps", "Spiked walls"])

def encounter_check(position):
    player_info = load_player_info()
    if position == positions["enemy"] and not encounter_status["enemy"]:
        player_input = input(f"You encounter a menacing {enemy_type.lower()}. What do you do? ")
        if encounter_enemy(player_input, player_info):
            encounter_status["enemy"] = True
    elif position == positions["friendly_ai"] and not encounter_status["friendly_ai"]:
        player_input = input(f"A {friendly_type.lower()} greets you. What do you ask? ")
        if interact_with_friendly(player_input, player_info):
            encounter_status["friendly_ai"] = True
    elif position == positions["trap"] and not encounter_status["trap"]:
        player_input = input(f"A hidden {trap_type.lower()} lies before you. How do you proceed? ")
        if navigate_trap(player_input, player_info):
            encounter_status["trap"] = True

# Place entities on the grid
grid[positions["player"][0]][positions["player"][1]] = PLAYER
grid[positions["enemy"][0]][positions["enemy"][1]] = ENEMY
grid[positions["friendly_ai"][0]][positions["friendly_ai"][1]] = FRIENDLY_AI
grid[positions["trap"][0]][positions["trap"][1]] = TRAP

def retrieve_context(situation, entity_type):
    """Retrieves relevant knowledge from the knowledge base."""
    with open("dungeon_knowledge.json", "r") as f:
        data = json.load(f)
    
    if entity_type not in data:
        print(f"Warning: '{entity_type}' key not found in dungeon_knowledge.json for situation '{situation}'")
        return None
    
    for entity in data[entity_type]:
        if entity["type"].lower() == situation.lower():
            return entity["details"]
    
    return None

def load_player_info():
    with open("player_info.json", "r") as f:
        data = json.load(f)
    return data["player"]

def navigate_trap(player_input, player_info):
    context = retrieve_context(trap_type, "Traps")
    conversation = conversation_history + [
        {"role": "system", "content": "You are the dungeon master narrating the outcome of a player's attempt to navigate or disarm a trap."},
    ]

    if context:
        conversation.append({"role": "system", "content": context})

    conversation.append({"role": "system", "content": f"Player Information:\nSkills: {', '.join(player_info['skills'])}\nSpells: {', '.join(player_info['spells'])}\nEquipment: {', '.join(player_info['equipment'])}"})

    conversation.append({"role": "system", "content": "Guide the player through the process of navigating or disarming the trap. Provide descriptions and prompts based on the player's actions. Do not include the phrase 'Encounter Completed' or any information about damage or trap completion. Please format your response as follows:\n\nNarrative: [Describe what happened after the player's action]\n\nWhat do you do next?"})

    encounter_completed = False
    while not encounter_completed:
        conversation_context = conversation.copy()
        conversation_context.append({"role": "user", "content": player_input})

        response = client.chat.completions.create(model="ft:gpt-3.5-turbo-0125:personal::96kWJrDA", messages=[
            {"role": "system", "content": "Context:"},
            {"role": "system", "content": "\n".join([msg["content"] for msg in conversation])},
            {"role": "system", "content": "User Input:"},
            {"role": "user", "content": player_input}
        ])

        dm_response = response.choices[0].message.content
        print(f"\"{dm_response}\"")

        conversation.append({"role": "system", "content": dm_response})

        # Make a second API call to determine if the user has completed the encounter or taken damage
        completion_response = client.chat.completions.create(model="ft:gpt-3.5-turbo-0125:personal::96kWJrDA", messages=[
            {"role": "system", "content": "Based on the player's action and the outcome, determine if the player has completed the trap encounter or taken damage. Respond with 'DAMAGE' if the player has taken damage, 'TRAP COMPLETE' if the player has successfully navigated or disarmed the trap, or 'CONTINUE' if the encounter is still ongoing."},
            {"role": "system", "content": dm_response},
            {"role": "user", "content": player_input}
        ])

        completion_status = completion_response.choices[0].message.content.strip().upper()

        if completion_status == "DAMAGE":
            # Handle damage to the player (e.g., update health stat)
            pass
        elif completion_status == "TRAP COMPLETE":
            encounter_completed = True
            conversation.append({"role": "system", "content": "The trap has been expended. There is no longer any risk in the room that you can see. You may proceed forward."})
        else:
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

    conversation.append({"role": "system", "content": "Guide the player through the process of fighting the goblin. Provide descriptions and prompts based on the player's actions. Do not include the phrase 'Encounter Completed' until the player has successfully defeated the goblin or escaped from the encounter. If the player fails to overcome the goblin, describe the consequences without using 'Encounter Completed'. Do not include any questions at the end of your message. If the player has defeated the enemy or escaped, describe the consequences using the phrase 'Encounter Completed'. Please format your response as follows:\n\nNarrative: [Describe what happened after the player's action]\n\nGAIN ITEM item_name (if the player gained an item)\nGAIN SKILL skill_name (if the player gained a skill)\nGAIN SPELL spell_name (if the player gained a spell)\nLOST ITEM item_name (if the player lost an item or had it changed to a different item)\nLOST SKILL skill_name (if the player lost a skill)\nLOST SPELL spell_name (if the player lost a spell)\nDAMAGE (if the player was harmed in some way)\nOnly include the LOST ITEM, GAIN SKILL, etc. if it actually is updating something. Otherwise, if the player does not learn anything, please do not include that as a part of the message."})

    encounter_completed = False
    while not encounter_completed:
        conversation_context = conversation.copy()
        conversation_context.append({"role": "user", "content": player_input})

        response = client.chat.completions.create(model="ft:gpt-3.5-turbo-0125:personal::96kWJrDA", messages=[
            {"role": "system", "content": "Context:"},
            {"role": "system", "content": "\n".join([msg["content"] for msg in conversation])},
            {"role": "system", "content": "User Input:"},
            {"role": "user", "content": player_input}
        ])

        dm_response = response.choices[0].message.content
        print(f"\"{dm_response}\"")

        conversation.append({"role": "system", "content": dm_response})

        parse_ai_response(dm_response, player_info)

        # Check for specific keywords or phrases that indicate the goblin has been defeated or the player has escaped
        encounter_completed = any(keyword in dm_response.lower() for keyword in ["defeat", "escape", "overcome", "encounter completed"])

        if not encounter_completed:
            player_input = input("What do you do next? ")
        else:
            conversation.append({"role": "system", "content": "Encounter Completed"})

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

from openai import OpenAI
from Constants import API_KEY
import json

"""
This function should be used to handle combat between the player and an enemy.
"""
def start_combat(enemy_info, player_info):
    pass
    

class Engine:
    def __init__(self, positions, encounter_status):
        self.client = OpenAI(api_key=API_KEY)
        self.positions = positions
        self.encounter_status = encounter_status
        self.game_info = json.load(open("dungeon_knowledge.json"))
        self.player_info = json.load(open("player_info.json"))
        
    def encounter_enemy(self, player_input):
        start_combat
    
    def encounter_friendly_ai(self, player_input, player_info):
        pass
    
    def encounter_trap(self, player_input, player_info):
        pass  
        
    def encounter_check(self, position):
        if position == self.positions["enemy"] and not self.encounter_status["enemy"]:
            player_input = input("You encounter a menacing goblin. What do you do? ")
            if self.encounter_enemy(player_input, self.player_info):
                self.encounter_status["enemy"] = True
        elif position == self.positions["friendly_ai"] and not self.encounter_status["friendly_ai"]:
            player_input = input("A wise wizard greets you. What do you ask? ")
            if self.encounter_friendly_ai(player_input, self.player_info):
                self.encounter_status["friendly_ai"] = True
        elif position == self.positions["trap"] and not self.encounter_status["trap"]:
            player_input = input("A hidden trap lies before you. How do you proceed? ")
            if self.encounter_trap(player_input, self.player_info):
                self.encounter_status["trap"] = True
         
        
    

    


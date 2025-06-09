import json
import os
from datetime import datetime

class SaveSystem:
    def __init__(self):
        self.save_dir = "saves"
        self.ensure_save_directory()
        
    def ensure_save_directory(self):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    
    def save_game(self, stats, score, wave):
        # Create save data dictionary
        save_data = {
            "timestamp": datetime.now().isoformat(),
            "stats": {
                "level": stats.level,
                "experience": stats.experience,
                "experience_to_next_level": stats.experience_to_next_level,
                "skill_points": stats.skill_points,
                "strength": stats.strength,
                "agility": stats.agility,
                "vitality": stats.vitality,
                "wisdom": stats.wisdom,
                "luck": stats.luck
            },
            "game_state": {
                "score": score,
                "wave": wave
            }
        }
        
        # Save to file
        save_path = os.path.join(self.save_dir, "save_game.json")
        with open(save_path, 'w') as f:
            json.dump(save_data, f, indent=4)
            
        # Update high scores
        self.update_high_scores(score)
    
    def load_game(self):
        save_path = os.path.join(self.save_dir, "save_game.json")
        if not os.path.exists(save_path):
            return None
            
        try:
            with open(save_path, 'r') as f:
                save_data = json.load(f)
            return save_data
        except:
            return None
    
    def update_high_scores(self, new_score):
        scores = self.get_high_scores()
        
        # Add new score
        scores.append({
            "score": new_score,
            "timestamp": datetime.now().isoformat()
        })
        
        # Sort by score (highest first) and keep top 10
        scores.sort(key=lambda x: x["score"], reverse=True)
        scores = scores[:10]
        
        # Save high scores
        scores_path = os.path.join(self.save_dir, "high_scores.json")
        with open(scores_path, 'w') as f:
            json.dump(scores, f, indent=4)
    
    def get_high_scores(self):
        scores_path = os.path.join(self.save_dir, "high_scores.json")
        if not os.path.exists(scores_path):
            return []
            
        try:
            with open(scores_path, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def apply_save_data(self, stats, save_data):
        if not save_data:
            return
            
        # Apply stats
        stats.level = save_data["stats"]["level"]
        stats.experience = save_data["stats"]["experience"]
        stats.experience_to_next_level = save_data["stats"]["experience_to_next_level"]
        stats.skill_points = save_data["stats"]["skill_points"]
        stats.strength = save_data["stats"]["strength"]
        stats.agility = save_data["stats"]["agility"]
        stats.vitality = save_data["stats"]["vitality"]
        stats.wisdom = save_data["stats"]["wisdom"]
        stats.luck = save_data["stats"]["luck"]
        
        # Update derived stats
        stats.update_derived_stats()
        
        return save_data["game_state"] 
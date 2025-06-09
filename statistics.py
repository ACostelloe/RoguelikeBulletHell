import json
import os
from datetime import datetime, timedelta

class GameStats:
    def __init__(self):
        self.stats = {
            # Combat stats
            "total_kills": 0,
            "kills_by_type": {
                "basic": 0,
                "fast": 0,
                "tank": 0,
                "boss": 0,
                "jumper": 0,
                "charger": 0,
                "bomber": 0,
                "sniper": 0,
                "summoner": 0,
                "shooter": 0
            },
            "total_damage_dealt": 0,
            "total_damage_taken": 0,
            "critical_hits": 0,
            "total_shots_fired": 0,
            "shots_hit": 0,
            
            # Time stats
            "total_playtime": 0,  # in seconds
            "longest_survival": 0,  # in seconds
            "current_session_start": None,
            "last_session_end": None,
            
            # Wave stats
            "highest_wave": 0,
            "waves_completed": 0,
            "total_waves_attempted": 0,
            
            # Score stats
            "highest_score": 0,
            "total_score": 0,
            "average_score": 0,
            
            # Death stats
            "total_deaths": 0,
            "deaths_by_wave": {},  # wave number -> count
            
            # Level stats
            "highest_level": 1,
            "total_levels_gained": 0,
            "total_experience_gained": 0,
            
            # Achievement progress
            "achievements": {
                "first_kill": False,
                "wave_5": False,
                "wave_10": False,
                "wave_20": False,
                "level_5": False,
                "level_10": False,
                "level_20": False,
                "kill_100": False,
                "kill_1000": False,
                "kill_10000": False,
                "survive_5min": False,
                "survive_10min": False,
                "survive_30min": False,
                "score_1000": False,
                "score_10000": False,
                "score_100000": False
            }
        }
        self.session_start_time = datetime.now()
        
    def start_session(self):
        self.session_start_time = datetime.now()
        self.stats["current_session_start"] = self.session_start_time.isoformat()
        
    def end_session(self):
        if self.session_start_time:
            session_duration = (datetime.now() - self.session_start_time).total_seconds()
            self.stats["total_playtime"] += session_duration
            self.stats["last_session_end"] = datetime.now().isoformat()
            if session_duration > self.stats["longest_survival"]:
                self.stats["longest_survival"] = session_duration
                
    def record_kill(self, enemy_type):
        self.stats["total_kills"] += 1
        self.stats["kills_by_type"][enemy_type] += 1
        
        # Check kill-based achievements
        if self.stats["total_kills"] >= 1 and not self.stats["achievements"]["first_kill"]:
            self.stats["achievements"]["first_kill"] = True
        if self.stats["total_kills"] >= 100 and not self.stats["achievements"]["kill_100"]:
            self.stats["achievements"]["kill_100"] = True
        if self.stats["total_kills"] >= 1000 and not self.stats["achievements"]["kill_1000"]:
            self.stats["achievements"]["kill_1000"] = True
        if self.stats["total_kills"] >= 10000 and not self.stats["achievements"]["kill_10000"]:
            self.stats["achievements"]["kill_10000"] = True
            
    def record_damage(self, damage, is_dealt=True):
        if is_dealt:
            self.stats["total_damage_dealt"] += damage
        else:
            self.stats["total_damage_taken"] += damage
            
    def record_shot(self, hit=False):
        self.stats["total_shots_fired"] += 1
        if hit:
            self.stats["shots_hit"] += 1
            
    def record_critical(self):
        self.stats["critical_hits"] += 1
        
    def record_wave(self, wave_number, completed=False):
        if wave_number > self.stats["highest_wave"]:
            self.stats["highest_wave"] = wave_number
            
        self.stats["total_waves_attempted"] += 1
        if completed:
            self.stats["waves_completed"] += 1
            
        # Check wave-based achievements
        if wave_number >= 5 and not self.stats["achievements"]["wave_5"]:
            self.stats["achievements"]["wave_5"] = True
        if wave_number >= 10 and not self.stats["achievements"]["wave_10"]:
            self.stats["achievements"]["wave_10"] = True
        if wave_number >= 20 and not self.stats["achievements"]["wave_20"]:
            self.stats["achievements"]["wave_20"] = True
            
    def record_score(self, score):
        self.stats["total_score"] += score
        if score > self.stats["highest_score"]:
            self.stats["highest_score"] = score
        self.stats["average_score"] = self.stats["total_score"] / max(1, self.stats["total_deaths"])
        
        # Check score-based achievements
        if score >= 1000 and not self.stats["achievements"]["score_1000"]:
            self.stats["achievements"]["score_1000"] = True
        if score >= 10000 and not self.stats["achievements"]["score_10000"]:
            self.stats["achievements"]["score_10000"] = True
        if score >= 100000 and not self.stats["achievements"]["score_100000"]:
            self.stats["achievements"]["score_100000"] = True
            
    def record_death(self, wave_number):
        self.stats["total_deaths"] += 1
        self.stats["deaths_by_wave"][str(wave_number)] = self.stats["deaths_by_wave"].get(str(wave_number), 0) + 1
        
    def record_level(self, level, experience_gained):
        if level > self.stats["highest_level"]:
            self.stats["highest_level"] = level
        self.stats["total_levels_gained"] += 1
        self.stats["total_experience_gained"] += experience_gained
        
        # Check level-based achievements
        if level >= 5 and not self.stats["achievements"]["level_5"]:
            self.stats["achievements"]["level_5"] = True
        if level >= 10 and not self.stats["achievements"]["level_10"]:
            self.stats["achievements"]["level_10"] = True
        if level >= 20 and not self.stats["achievements"]["level_20"]:
            self.stats["achievements"]["level_20"] = True
            
    def check_survival_achievements(self):
        current_session = (datetime.now() - self.session_start_time).total_seconds()
        if current_session >= 300 and not self.stats["achievements"]["survive_5min"]:  # 5 minutes
            self.stats["achievements"]["survive_5min"] = True
        if current_session >= 600 and not self.stats["achievements"]["survive_10min"]:  # 10 minutes
            self.stats["achievements"]["survive_10min"] = True
        if current_session >= 1800 and not self.stats["achievements"]["survive_30min"]:  # 30 minutes
            self.stats["achievements"]["survive_30min"] = True
            
    def get_accuracy(self):
        if self.stats["total_shots_fired"] == 0:
            return 0
        return (self.stats["shots_hit"] / self.stats["total_shots_fired"]) * 100
        
    def get_critical_rate(self):
        if self.stats["total_shots_fired"] == 0:
            return 0
        return (self.stats["critical_hits"] / self.stats["total_shots_fired"]) * 100
        
    def get_kills_per_death(self):
        if self.stats["total_deaths"] == 0:
            return self.stats["total_kills"]
        return self.stats["total_kills"] / self.stats["total_deaths"]
        
    def get_playtime_formatted(self):
        total_seconds = int(self.stats["total_playtime"])
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
    def get_achievements_progress(self):
        total = len(self.stats["achievements"])
        completed = sum(1 for achieved in self.stats["achievements"].values() if achieved)
        return (completed, total)
        
    def save_stats(self):
        stats_dir = "saves"
        if not os.path.exists(stats_dir):
            os.makedirs(stats_dir)
            
        stats_path = os.path.join(stats_dir, "statistics.json")
        with open(stats_path, 'w') as f:
            json.dump(self.stats, f, indent=4)
            
    def load_stats(self):
        stats_path = os.path.join("saves", "statistics.json")
        if os.path.exists(stats_path):
            try:
                with open(stats_path, 'r') as f:
                    self.stats = json.load(f)
            except:
                pass  # If loading fails, keep default stats 

    def update(self):
        pass 
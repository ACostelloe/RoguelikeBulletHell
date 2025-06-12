"""
Enemy AI module.
"""
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum, auto
import random
import math
import pygame
from logger import logger
import traceback

class AIState(Enum):
    """States for enemy AI."""
    IDLE = auto()
    PATROL = auto()
    CHASE = auto()
    ATTACK = auto()
    FLEE = auto()
    STUNNED = auto()
    DEAD = auto()

@dataclass
class AICondition:
    """Condition for AI state transitions."""
    name: str
    check: Callable[[], bool]
    priority: int = 0

@dataclass
class AIAction:
    """Action for AI state."""
    name: str
    execute: Callable[[], None]
    duration: float = 0.0
    cooldown: float = 0.0
    last_executed: float = 0.0

class BehaviorNode:
    """Base class for behavior tree nodes."""
    def __init__(self, name: str):
        self.name = name
        self.children: List[BehaviorNode] = []
        
    def add_child(self, child: 'BehaviorNode') -> None:
        """Add a child node."""
        self.children.append(child)
        
    def evaluate(self) -> bool:
        """Evaluate the node."""
        raise NotImplementedError()

class SequenceNode(BehaviorNode):
    """Node that executes children in sequence."""
    def evaluate(self) -> bool:
        """Evaluate all children in sequence."""
        for child in self.children:
            if not child.evaluate():
                return False
        return True

class SelectorNode(BehaviorNode):
    """Node that executes first successful child."""
    def evaluate(self) -> bool:
        """Evaluate children until one succeeds."""
        for child in self.children:
            if child.evaluate():
                return True
        return False

class ConditionNode(BehaviorNode):
    """Node that checks a condition."""
    def __init__(self, name: str, condition: Callable[[], bool]):
        super().__init__(name)
        self.condition = condition
        
    def evaluate(self) -> bool:
        """Evaluate the condition."""
        return self.condition()

class ActionNode(BehaviorNode):
    """Node that executes an action."""
    def __init__(self, name: str, action: Callable[[], None]):
        super().__init__(name)
        self.action = action
        
    def evaluate(self) -> bool:
        """Execute the action."""
        self.action()
        return True

class EnemyAI:
    """AI controller for enemies."""
    
    def __init__(self, enemy: 'Enemy'):
        """Initialize the AI controller."""
        self.enemy = enemy
        self.state = AIState.IDLE
        self.state_time = 0.0
        self.target = None
        self.patrol_points = []
        self.current_patrol_index = 0
        self.behavior_tree = None
        self.conditions: Dict[str, AICondition] = {}
        self.actions: Dict[str, AIAction] = {}
        self._initialize_behavior()
        
    def _initialize_behavior(self) -> None:
        """Initialize the behavior tree and conditions."""
        try:
            # Create conditions
            self.conditions = {
                "has_target": AICondition(
                    "has_target",
                    lambda: self.target is not None,
                    priority=1
                ),
                "target_in_range": AICondition(
                    "target_in_range",
                    lambda: self._is_target_in_range(),
                    priority=2
                ),
                "is_stunned": AICondition(
                    "is_stunned",
                    lambda: self.enemy.is_stunned,
                    priority=3
                ),
                "is_low_health": AICondition(
                    "is_low_health",
                    lambda: self.enemy.health < self.enemy.max_health * 0.3,
                    priority=4
                ),
                "has_patrol_points": AICondition(
                    "has_patrol_points",
                    lambda: len(self.patrol_points) > 0,
                    priority=5
                )
            }
            
            # Create actions
            self.actions = {
                "idle": AIAction(
                    "idle",
                    self._action_idle,
                    duration=1.0
                ),
                "patrol": AIAction(
                    "patrol",
                    self._action_patrol,
                    duration=0.5
                ),
                "chase": AIAction(
                    "chase",
                    self._action_chase,
                    duration=0.2
                ),
                "attack": AIAction(
                    "attack",
                    self._action_attack,
                    duration=0.5,
                    cooldown=1.0
                ),
                "flee": AIAction(
                    "flee",
                    self._action_flee,
                    duration=0.3
                )
            }
            
            # Create behavior tree
            self.behavior_tree = SelectorNode("root")
            
            # Add stunned behavior
            stunned_sequence = SequenceNode("stunned")
            stunned_sequence.add_child(ConditionNode("is_stunned", self.conditions["is_stunned"].check))
            stunned_sequence.add_child(ActionNode("wait", lambda: None))
            self.behavior_tree.add_child(stunned_sequence)
            
            # Add flee behavior
            flee_sequence = SequenceNode("flee")
            flee_sequence.add_child(ConditionNode("is_low_health", self.conditions["is_low_health"].check))
            flee_sequence.add_child(ActionNode("flee", self.actions["flee"].execute))
            self.behavior_tree.add_child(flee_sequence)
            
            # Add attack behavior
            attack_sequence = SequenceNode("attack")
            attack_sequence.add_child(ConditionNode("target_in_range", self.conditions["target_in_range"].check))
            attack_sequence.add_child(ActionNode("attack", self.actions["attack"].execute))
            self.behavior_tree.add_child(attack_sequence)
            
            # Add chase behavior
            chase_sequence = SequenceNode("chase")
            chase_sequence.add_child(ConditionNode("has_target", self.conditions["has_target"].check))
            chase_sequence.add_child(ActionNode("chase", self.actions["chase"].execute))
            self.behavior_tree.add_child(chase_sequence)
            
            # Add patrol behavior
            patrol_sequence = SequenceNode("patrol")
            patrol_sequence.add_child(ConditionNode("has_patrol_points", self.conditions["has_patrol_points"].check))
            patrol_sequence.add_child(ActionNode("patrol", self.actions["patrol"].execute))
            self.behavior_tree.add_child(patrol_sequence)
            
            # Add idle behavior
            idle_sequence = SequenceNode("idle")
            idle_sequence.add_child(ActionNode("idle", self.actions["idle"].execute))
            self.behavior_tree.add_child(idle_sequence)
            
        except Exception as e:
            logger.error(f"Error initializing enemy AI: {str(e)}")
            logger.error(traceback.format_exc())
            
    def update(self, dt: float) -> None:
        """Update the AI state."""
        try:
            # Update state time
            self.state_time += dt
            
            # Update action cooldowns
            for action in self.actions.values():
                if action.last_executed > 0:
                    action.last_executed -= dt
                    
            # Evaluate behavior tree
            if self.behavior_tree:
                self.behavior_tree.evaluate()
                
        except Exception as e:
            logger.error(f"Error updating enemy AI: {str(e)}")
            logger.error(traceback.format_exc())
            
    def set_target(self, target: 'Entity') -> None:
        """Set the AI target."""
        self.target = target
        
    def clear_target(self) -> None:
        """Clear the AI target."""
        self.target = None
        
    def set_patrol_points(self, points: List[Tuple[float, float]]) -> None:
        """Set patrol points for the AI."""
        self.patrol_points = points
        self.current_patrol_index = 0
        
    def _is_target_in_range(self) -> bool:
        """Check if target is in attack range."""
        if not self.target:
            return False
            
        distance = math.sqrt(
            (self.enemy.x - self.target.x) ** 2 +
            (self.enemy.y - self.target.y) ** 2
        )
        return distance <= self.enemy.attack_range
        
    def _action_idle(self) -> None:
        """Execute idle action."""
        self.enemy.velocity_x = 0
        self.enemy.velocity_y = 0
        
    def _action_patrol(self) -> None:
        """Execute patrol action."""
        if not self.patrol_points:
            return
            
        target_x, target_y = self.patrol_points[self.current_patrol_index]
        dx = target_x - self.enemy.x
        dy = target_y - self.enemy.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < 5:
            self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
        else:
            self.enemy.velocity_x = dx / distance * self.enemy.speed
            self.enemy.velocity_y = dy / distance * self.enemy.speed
            
    def _action_chase(self) -> None:
        """Execute chase action."""
        if not self.target:
            return
            
        dx = self.target.x - self.enemy.x
        dy = self.target.y - self.enemy.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            self.enemy.velocity_x = dx / distance * self.enemy.speed
            self.enemy.velocity_y = dy / distance * self.enemy.speed
            
    def _action_attack(self) -> None:
        """Execute attack action."""
        action = self.actions["attack"]
        if action.last_executed > 0:
            return
            
        if self.target:
            self.enemy.attack(self.target)
            action.last_executed = action.cooldown
            
    def _action_flee(self) -> None:
        """Execute flee action."""
        if not self.target:
            return
            
        dx = self.enemy.x - self.target.x
        dy = self.enemy.y - self.target.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            self.enemy.velocity_x = dx / distance * self.enemy.speed * 1.5
            self.enemy.velocity_y = dy / distance * self.enemy.speed * 1.5
            
    def get_state(self) -> Dict[str, Any]:
        """Get the current AI state."""
        return {
            "state": self.state.name,
            "state_time": self.state_time,
            "has_target": self.target is not None,
            "patrol_points": len(self.patrol_points),
            "current_patrol_index": self.current_patrol_index
        }
        
    def set_state(self, state: Dict[str, Any]) -> None:
        """Set the AI state from a dictionary."""
        try:
            self.state = AIState[state["state"]]
            self.state_time = state["state_time"]
            self.current_patrol_index = state["current_patrol_index"]
        except Exception as e:
            logger.error(f"Error setting AI state: {str(e)}")
            logger.error(traceback.format_exc())

class EnemyBehavior:
    pass

class EnemyState:
    pass 
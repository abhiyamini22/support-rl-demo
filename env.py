import random
import uuid
import time
from typing import Dict, Any, Tuple

class SimpleSupportEnv:
    """Simple customer support environment for Hugging Face Spaces demo."""
    
    def __init__(self, difficulty: str = "medium"):
        self.difficulty = difficulty
        self.ticket_pool = self._generate_tickets()
        self.current_ticket_index = 0
        self.step_count = 0
        self.total_reward = 0
        
    def _generate_tickets(self) -> list:
        """Generate ticket pool based on difficulty."""
        base_tickets = [
            {"query": "payment failed", "priority": "urgent", "category": "payment"},
            {"query": "hello", "priority": "low", "category": "general"},
            {"query": "refund status", "priority": "normal", "category": "billing"},
            {"query": "account hacked", "priority": "urgent", "category": "security"},
            {"query": "discount?", "priority": "low", "category": "general"},
            {"query": "system down", "priority": "urgent", "category": "technical"},
            {"query": "delivery issue", "priority": "normal", "category": "logistics"},
            {"query": "feature request", "priority": "low", "category": "product"},
            {"query": "billing question", "priority": "normal", "category": "billing"},
            {"query": "thank you", "priority": "low", "category": "general"},
        ]
        
        # Adjust pool size based on difficulty
        if self.difficulty == "easy":
            return base_tickets[:10]
        elif self.difficulty == "medium":
            return base_tickets * 2
        else:  # hard
            return base_tickets * 3
    
    def reset(self) -> Dict[str, Any]:
        """Reset environment and return initial observation."""
        self.current_ticket_index = 0
        self.step_count = 0
        self.total_reward = 0
        
        if self.ticket_pool:
            ticket = self.ticket_pool[self.current_ticket_index]
            return {
                "ticket": ticket,
                "step": self.step_count,
                "done": False
            }
        else:
            return {
                "ticket": None,
                "step": self.step_count,
                "done": True
            }
    
    def step(self, action: str) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        """Execute action and return observation, reward, done, info."""
        if self.current_ticket_index >= len(self.ticket_pool):
            return {"ticket": None, "step": self.step_count, "done": True}, 0.0, True, {}
        
        ticket = self.ticket_pool[self.current_ticket_index]
        priority = ticket["priority"]
        
        # Calculate reward based on action appropriateness
        if priority == "urgent" and action == "escalate":
            reward = 0.9
        elif priority == "low" and action == "auto_reply":
            reward = 0.8
        elif priority == "normal" and action == "ask_info":
            reward = 0.7
        else:
            reward = 0.3
        
        self.total_reward += reward
        self.step_count += 1
        self.current_ticket_index += 1
        
        # Check if episode is done
        done = self.current_ticket_index >= len(self.ticket_pool)
        
        if not done:
            next_ticket = self.ticket_pool[self.current_ticket_index]
            observation = {
                "ticket": next_ticket,
                "step": self.step_count,
                "done": done
            }
        else:
            observation = {
                "ticket": None,
                "step": self.step_count,
                "done": done
            }
        
        info = {
            "total_reward": self.total_reward,
            "avg_reward": self.total_reward / self.step_count if self.step_count > 0 else 0
        }
        
        return observation, reward, done, info
    
    def get_state(self) -> Dict[str, Any]:
        """Get current environment state."""
        return {
            "difficulty": self.difficulty,
            "step_count": self.step_count,
            "tickets_remaining": len(self.ticket_pool) - self.current_ticket_index,
            "total_reward": self.total_reward,
            "current_ticket_index": self.current_ticket_index
        }

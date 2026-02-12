import logging
from enum import Enum
from dataclasses import dataclass
from typing import Tuple, Dict, Any
from config.settings import HORMONE_CONFIG

class AgentState(Enum):
    IDLE = "IDLE"
    THINKING = "THINKING"
    PROACTIVE = "PROACTIVE"
    DREAMING = "DREAMING"
    HIGH_STRESS_EXPAND = "EXPAND"
    STABILITY_PRUNE = "PRUNE"

@dataclass
class HormoneState:
    stress: float
    reward: float
    stability: float
    
    def to_dict(self) -> dict:
        return {
            "stress": round(self.stress, 3),
            "reward": round(self.reward, 3),
            "stability": round(self.stability, 3)
        }

class HormoneModulator:
    def __init__(self):
        self.stress = HORMONE_CONFIG["stress_baseline"]
        self.reward = HORMONE_CONFIG["reward_baseline"]
        self.stability = HORMONE_CONFIG["stability_baseline"]
        self.decay_rate = HORMONE_CONFIG["decay_rate"]
        self.history = []
        logging.info(f"[Hormone] Initialized: S={self.stress}, R={self.reward}, St={self.stability}")

    def evaluate_state(self, feedback_signal: float) -> Tuple[float, float, float]:
        feedback_signal = max(-1.0, min(1.0, feedback_signal))
        stress_delta = reward_delta = stability_delta = 0.0
        
        if feedback_signal < -0.5:
            stress_delta, reward_delta, stability_delta = abs(feedback_signal) * 0.8, -0.2, -0.15
        elif feedback_signal < 0:
            stress_delta, reward_delta, stability_delta = abs(feedback_signal) * 0.4, -0.1, -0.05
        elif feedback_signal < 0.3:
            stress_delta, reward_delta, stability_delta = -0.1, 0.1, 0.02
        elif feedback_signal < 0.7:
            stress_delta, reward_delta, stability_delta = -0.2, feedback_signal * 0.6, 0.08
        else:
            stress_delta, reward_delta, stability_delta = -0.3, feedback_signal * 0.8, 0.15
        
        return stress_delta, reward_delta, stability_delta

    def update_hormones(self, stress_delta: float, reward_delta: float, stability_delta: float = 0.0) -> HormoneState:
        # DECAY
        self.stress += (HORMONE_CONFIG["stress_baseline"] - self.stress) * self.decay_rate
        self.reward += (HORMONE_CONFIG["reward_baseline"] - self.reward) * self.decay_rate
        self.stability += (HORMONE_CONFIG["stability_baseline"] - self.stability) * self.decay_rate
        
        # APPLY DELTAS
        self.stress += stress_delta
        self.reward += reward_delta
        self.stability += stability_delta
        
        self.stress = max(0.0, min(1.0, self.stress))
        self.reward = max(0.0, min(1.0, self.reward))
        self.stability = max(0.0, min(1.0, self.stability))
        
        new_state = HormoneState(self.stress, self.reward, self.stability)
        self.history.append(new_state)
        if len(self.history) > 100: self.history.pop(0)
        
        return new_state

    def get_state(self) -> Dict[str, float]:
        return HormoneState(self.stress, self.reward, self.stability).to_dict()

    def suggest_state_transition(self) -> AgentState:
        if self.stress > HORMONE_CONFIG["stress_threshold"]:
            return AgentState.HIGH_STRESS_EXPAND if self.stability < 0.4 else AgentState.STABILITY_PRUNE
        
        if self.reward < HORMONE_CONFIG["reward_threshold"]:
            return AgentState.PROACTIVE
        
        if self.stability > HORMONE_CONFIG["stability_threshold"]:
            return AgentState.THINKING
        
        return AgentState.DREAMING if self.reward > 0.5 else AgentState.IDLE

    def internal_validation_signal(self) -> float:
        signal = (self.stability * 0.5 + self.reward * 0.3 - self.stress * 0.4)
        return max(-1.0, min(1.0, signal))

    def get_diagnostics(self) -> Dict[str, Any]:
        return {
            "current": self.get_state(),
            "suggested_state": self.suggest_state_transition().value,
            "internal_validation": round(self.internal_validation_signal(), 3),
            "history_length": len(self.history)
        }

# === Memory System ===
MEMORY_CONFIG = {
    "use_chroma": True,           
    "chroma_persist_dir": "chroma_db",
    "stm_buffer_size": 10,        
    "embedding_model": "all-MiniLM-L6-v2", 
}

# === Hormone System ===
HORMONE_CONFIG = {
    "stress_baseline": 0.1,
    "reward_baseline": 0.5,
    "stability_baseline": 0.7,
    "decay_rate": 0.05, 
}

# === Neural Engine ===
NEURAL_CONFIG = {
    "initial_complexity": 1.0,
    "use_fast_mode": True, 
}

# === Agent Behavior ===
BEHAVIOR_CONFIG = {
    "proactive_delay": 30,  
    "dream_delay": 60,      
    "stress_threshold_expand": 0.6,  
    "stress_threshold_dream": 0.4,   
    "reward_threshold_proactive": 0.3,  
}

# === Model Config ===
MODEL_CONFIG = {
    "ollama_base_url": "http://localhost:11434",
    "model_name": "neural-chat", 
    "context_window": 4096,
}

# === Logging ===
LOG_CONFIG = {
    "level": "INFO",  
    "format": "%(asctime)s - [%(levelname)s] - %(message)s"
}

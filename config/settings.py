# === Model & Neural Engine ===
MODEL_CONFIG = {
    "ollama_base_url": "http://localhost:11434",
    "model_name": "qwen2.5:1.5b",
    "fast_model": "qwen2.5:0.5b",
    "context_window": 2048,
    "temperature": 0.7,
    "fast_temperature": 0.1,
}

NEURAL_CONFIG = {
    "initial_complexity": 1,
    "max_complexity": 10,
    "min_complexity": 1,
}

# === Memory System ===
MEMORY_CONFIG = {
    "use_chroma": True,
    "chroma_persist_dir": "chroma_db",
    "chroma_collection": "pkic_memory",
    "stm_buffer_size": 10,
    "embedding_model": "all-MiniLM-L6-v2",
    "memory_db_file": "memory_db.json",
    "profile_file": "profile.json",
    "retrieval_threshold": 1.2
}

# === Hormone System ===
HORMONE_CONFIG = {
    "stress_baseline": 0.1,
    "reward_baseline": 0.5,
    "stability_baseline": 0.7,
    "decay_rate": 0.05,
    "stress_threshold": 0.6,
    "reward_threshold": 0.3,
    "stability_threshold": 0.7,
}

# === Agent Behavior ===
BEHAVIOR_CONFIG = {
    "proactive_idle_min": 30,
    "proactive_idle_max": 60,
    "dream_idle_min": 60,
    "evolve_cooldown": 120,
}

# === Logging ===
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - [%(levelname)s] - %(message)s"
}

# 🧬 Bio-Inspired Cognitive Agent (H-SEA Architecture)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-WebSockets-green)
![AI](https://img.shields.io/badge/AI-Ollama%20%2F%20LLM-orange)
![DB](https://img.shields.io/badge/VectorDB-ChromaDB-purple)

> **Experimental AI architecture simulating biological cognitive processes: Hormonal Modulation, Synaptic Pruning, and Memory Consolidation (Dreaming).**

![Architecture Diagram](./assets/architecture_diagram.png)
*(Please add your architecture image to the assets folder)*

## 📖 Project Overview

This project implements a **Self-Evolving AI Agent** that goes beyond static LLM interactions. Inspired by biological systems, it maintains a dynamic internal state ("Hormones") that modulates its behavior, neural complexity, and memory processing in real-time.

Designed to solve the problem of static, stateless AI, this agent possesses a **"Mood"** (Stress/Reward/Stability) and performs **"Dreaming"** (Self-play simulation) to consolidate short-term experiences into long-term semantic memory.

## 🚀 Key Features

### 1. Hormone Modulation System 🧪
- **Dynamic State:** Tracks `Stress`, `Reward`, and `Stability` levels based on user interaction sentiment.
- **Behavioral Adaptation:** 
    - High Stress → **High Alert Mode** (Concise, defensive responses).
    - High Reward → **Proactive Mode** (Initiates conversation).

### 2. Neuro-Evolution Mechanism 🧠
- **NAS (Neural Architecture Search) Simulation:** 
    - **Expand:** Increases prompt complexity and reasoning depth under high cognitive load.
    - **Prune:** Optimizes for efficiency when the system is stable.

### 3. Dreaming & Memory Consolidation 🛌
- **Self-Play Simulation:** During idle periods, the agent enters a "Dreaming" loop.
- **Memory Transfer:** Compresses short-term buffer logs into semantic vectors and stores them in **ChromaDB** (Long-Term Memory).

### 4. Continuous Inference Engine ⚡
- **Real-time WebSockets:** Supports streaming responses and "Chain of Thought" visualization.
- **Context-Aware:** Retrieves relevant memories using semantic similarity search before generating responses.

## 🛠 Tech Stack

- **Backend:** Python, FastAPI, Uvicorn
- **Communication:** WebSockets (Real-time dashboard)
- **AI/LLM:** Ollama (Local LLM), PyTorch
- **Memory/Database:** ChromaDB (Vector Store), NumPy
- **Frontend:** HTML5, JavaScript (Real-time Visualization)

## 📂 Project Structure

```bash
├── execution/           # Core Logic Modules
│   ├── hormone_system.py  # Hormone calculation & State machine
│   ├── neural_engine.py   # Interface with LLM & NAS logic
│   ├── memory_system.py   # Hybrid Memory (Buffer + VectorDB)
│   └── inference_loop.py  # Main thinking process
├── templates/           # Dashboard UI
├── main.py              # Application Entry Point
└── tests/               # System Integrity Tests
💻 Installation & Usage
Prerequisites
Python 3.9+
Ollama running locally
Steps
Clone the repository
code
Bash
git clone https://github.com/[YOUR_USERNAME]/Bio-Inspired-Cognitive-Agent.git
cd Bio-Inspired-Cognitive-Agent
Install dependencies
code
Bash
pip install -r requirements.txt
Run the Server
code
Bash
python main.py
Access Dashboard
Open browser: http://localhost:8000
Observe the agent's hormone levels change as you chat.
🔍 System Verification
Run the integrated test suite to verify hormone logic and memory persistence:
code
Bash
python test_system.py
👨‍💻 Developer Note
This project demonstrates the potential of biologically plausible AI architectures. By introducing internal states and sleep cycles, we can create agents that are not just reactive text generators, but persistent, evolving digital organisms.
License: MIT
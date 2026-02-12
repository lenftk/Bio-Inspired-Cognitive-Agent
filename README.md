# 🧬 Bio-Inspired Cognitive Agent (H-SEA Architecture)

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005850?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-orange?style=for-the-badge)](https://ollama.ai/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-purple?style=for-the-badge)](https://www.trychroma.com/)

> **Experimental AI architecture simulating biological cognitive processes: Hormonal Modulation, Synaptic Pruning, and Memory Consolidation.**

---

## 🌟 Project Overview

This project implements a **Self-Evolving AI Agent** inspired by biological neural systems. Unlike static LLMs, this agent maintains a dynamic internal state ("Hormones") that influences its mood, reasoning complexity, and memory management.

### core Biological Concepts
- **Hormonal Modulation:** Real-time state updates (Stress, Reward, Stability) based on interaction sentiment.
- **Neuro-Evolution:** Dynamic adjustment of neural complexity (NAS) under varying cognitive loads.
- **Memory Consolidation:** A "Dreaming" cycle that compresses short-term experiences into long-term semantic memory.

---

## ⚡ Key Features

| Feature | Description |
| :--- | :--- |
| **Hormone System** | Tracks `Stress`, `Reward`, and `Stability` to modulate response style. |
| **Neural Engine** | Dynamically expands or prunes reasoning depth based on internal state. |
| **Hybrid Memory** | Combines STM (Short-Term Buffer) with LTM (ChromaDB Vector Store). |
| **Dreaming Loop** | Consolidates knowledge and evolves the agent during idle periods. |
| **Real-time UI** | Live dashboard showing hormone levels, thoughts, and memory retrieval. |

---

## 🛠 Tech Stack

- **Logic:** Python 3.9+, NumPy, Sentence-Transformers
- **API/Web:** FastAPI, WebSockets, Jinja2
- **Vector DB:** ChromaDB
- **LLM Engine:** Ollama (qwen2.5:1.5b / qwen2.5:0.5b)

---

## 📂 Project Structure

```bash
├── config/              # Centralized Settings
│   └── settings.py      # Project configurations
├── core/                # Bio-Inspired Engine
│   ├── hormone_system.py  # Hormonal logic & states
│   ├── neural_engine.py   # LLM interface & evolution
│   ├── memory_system.py   # Memory management logic
│   ├── chroma_store.py    # Vector database interface
│   └── inference_loop.py  # Main cognitive process
├── templates/           # Web Dashboard UI
├── main.py              # Application Entry Point
└── tests/               # System Verification Tests
```

---

## 🚀 Installation & Setup

1. **Clone & Navigate**
   ```bash
   git clone https://github.com/[YOUR_USERNAME]/Bio-Inspired-Cognitive-Agent.git
   cd Bio-Inspired-Cognitive-Agent
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Ollama**
   Ensure Ollama is running and you have the required models:
   ```bash
   ollama pull qwen2.5:1.5b
   ollama pull qwen2.5:0.5b
   ```

4. **Launch the Agent**
   ```bash
   python main.py
   ```
   Access the dashboard at: `http://localhost:8000`

---

## 👨‍💻 Developer & Contact

**Juhomin**
📧 [juhomin16@gmail.com](mailto:juhomin16@gmail.com)

---
*This project is an experimental demonstration of biologically plausible AI architectures. License: MIT*
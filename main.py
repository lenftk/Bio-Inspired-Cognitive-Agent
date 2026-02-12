import asyncio
import json
import logging
import time
import os
import random
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn

from core.hormone_system import HormoneModulator
from core.memory_system import ContextManager, ProfileManager
from core.neural_engine import DynamicNeuralNetwork
from core.inference_loop import InferenceEngine
from config.settings import BEHAVIOR_CONFIG, LOG_CONFIG, MEMORY_CONFIG

logging.basicConfig(level=LOG_CONFIG["level"], format=LOG_CONFIG["format"])
app = FastAPI()
templates = Jinja2Templates(directory="templates")

hormone_sys = HormoneModulator()
memory_ctx = ContextManager()
profile_mgr = ProfileManager()
neural_net = DynamicNeuralNetwork()
brain = InferenceEngine(neural_net, memory_ctx, hormone_sys, profile_mgr)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections: self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try: await connection.send_json(message)
            except: pass

manager = ConnectionManager()
global_state = {
    "status": "IDLE",
    "last_active": time.time(),
    "interrupted": False,
    "last_evolve_time": 0
}

def is_interrupted(): return global_state["interrupted"]

async def life_cycle_loop():
    logging.info("🌱 [Life] Organism started.")
    while True:
        await asyncio.sleep(2)
        hormone_sys.update_hormones(0, 0, 0)
        state = hormone_sys.get_state()
        suggested_state = hormone_sys.suggest_state_transition()
        
        await manager.broadcast({
            "type": "status_update", "hormones": state, "status": global_state["status"],
            "suggested_next_state": suggested_state.value, "diagnostics": hormone_sys.get_diagnostics()
        })

        now = time.time()
        if now - global_state["last_evolve_time"] > BEHAVIOR_CONFIG["evolve_cooldown"]:
            if suggested_state.value in ["EXPAND", "PRUNE"]:
                neural_net.evolve(suggested_state.value)
                global_state["last_evolve_time"] = now
                await manager.broadcast({"type": "log", "msg": f"🔧 Neural net evolved: {suggested_state.value}"})
        
        idle_time = now - global_state["last_active"]
        if global_state["status"] == "IDLE":
            if BEHAVIOR_CONFIG["proactive_idle_min"] < idle_time < BEHAVIOR_CONFIG["proactive_idle_max"]:
                if state['reward'] > 0.3:
                    global_state["status"] = "PROACTIVE"
                    await manager.broadcast({"type": "log", "msg": "✨ Initiating conversation..."})
                    facts = profile_mgr.data.get('facts', [])
                    prompt = f"Ask a follow-up about {facts[-1]}. One sentence." if facts else "Ask a friendly question to learn about the user. One sentence."
                    msg = await neural_net.forward(prompt, "You are curious and friendly.", use_fast=True)
                    await manager.broadcast({"type": "agent_msg", "text": msg})
                    memory_ctx.add_to_buffer("Agent", msg)
                    global_state["last_active"] = now
                    global_state["status"] = "IDLE"

            elif idle_time > BEHAVIOR_CONFIG["dream_idle_min"] and state['stress'] < 0.4:
                global_state["status"] = "DREAMING"
                await manager.broadcast({"type": "log", "msg": "💭 Entering dream state..."})
                global_state["interrupted"] = False
                await brain.dream_loop(is_interrupted)
                global_state["status"] = "IDLE"
                await manager.broadcast({"type": "log", "msg": "💭 Dream finished."})

@app.on_event("startup")
async def startup():
    asyncio.create_task(life_cycle_loop())

@app.get("/", response_class=HTMLResponse)
async def get_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/status")
async def get_status():
    return {
        "agent_status": global_state["status"],
        "hormones": hormone_sys.get_state(),
        "diagnostics": hormone_sys.get_diagnostics(),
        "memory": memory_ctx.get_memory_stats(),
        "profile": {"name": profile_mgr.data.get("name", "Nova"), "facts_count": len(profile_mgr.data.get("facts", []))}
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            msg_data = json.loads(data)
            user_msg = msg_data.get("message")
            if not user_msg: continue
            
            global_state["interrupted"] = True
            global_state["last_active"] = time.time()
            global_state["status"] = "THINKING"
            
            sentiment = 0.1
            if any(w in user_msg.lower() for w in ["bad", "hate", "terrible", "angry"]): sentiment = -0.7
            elif any(w in user_msg.lower() for w in ["good", "love", "great", "happy"]): sentiment = 0.8
            
            s_delta, r_delta, st_delta = hormone_sys.evaluate_state(sentiment)
            hormone_sys.update_hormones(s_delta, r_delta, st_delta)
            
            memory_ctx.add_to_buffer("User", user_msg)
            relevant = memory_ctx.retrieve_relevant(user_msg, top_k=3)
            if relevant:
                await manager.broadcast({"type": "log", "msg": f"📚 Retrieved: {relevant[0][:50]}..."})
            
            current_hormones = hormone_sys.get_state()
            if current_hormones['stress'] < 0.6:
                thought = await neural_net.forward(f"Think briefly about: '{user_msg}'", "One short inner voice sentence.", use_fast=True)
                await manager.broadcast({"type": "thought", "text": thought})
            
            memory_ctx.add_to_buffer("Agent", "[generating...]")
            global_state["interrupted"] = False
            collected = ""
            async for token in brain.run_chat(user_msg, is_interrupted):
                if token == "[Interrupted]": break
                collected += token
                await websocket.send_json({"type": "stream", "token": token})
            
            if collected: memory_ctx.buffer[-1] = f"Agent: {collected}"
            await websocket.send_json({"type": "stream_end"})
            global_state["status"] = "IDLE"
            asyncio.create_task(memory_ctx.process_queue(neural_net))
            
    except WebSocketDisconnect: manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
import logging
import asyncio

class InferenceEngine:
    def __init__(self, network, memory_system, hormone_system, profile_manager):
        self.net = network
        self.mem = memory_system
        self.hormones = hormone_system
        self.profile = profile_manager

    async def run_chat(self, user_message, state_check_func):
        self.mem.add_to_buffer("User", user_message)
        asyncio.create_task(self._analyze_input(user_message))
        
        relevant_mems = self.mem.retrieve_relevant(user_message)
        context_str = "\n".join([f"[Memory] {m}" for m in relevant_mems])
        
        sys_prompt = self.net._build_system_prompt(self.hormones.get_state())
        core_identity = self.profile.get_core_prompt()
        full_system_prompt = f"{sys_prompt}\n{core_identity}\nCONTEXT:\n{context_str}"
        
        stream = await self.net.forward(user_message, full_system_prompt, stream=True)
        if stream is None:
            yield "Sorry, I encountered an error."
            return
        
        full_response = ""
        async for chunk in stream:
            if state_check_func and state_check_func():
                yield "[Interrupted]"
                break
            content = chunk['message']['content']
            full_response += content
            yield content
            
        self.mem.add_to_buffer("Agent", full_response)

    async def _analyze_input(self, text):
        data = await self.net.extract_facts(text)
        if data.get("new_name"): self.profile.update("name", data["new_name"])
        if data.get("preference"): self.profile.add_fact(data["preference"])

    async def dream_loop(self, interrupt_check):
        h_state = self.hormones.get_state()
        topic = "a futuristic city" if h_state['stress'] < 0.5 else "handling a difficult error"
        logging.info(f"[Dream] Dreaming about {topic}...")
        
        stream = await self.net.forward(f"Describe a scene about {topic}.", "You are dreaming. Be creative.", use_fast=True, stream=True)
        full_dream = ""
        async for chunk in stream:
            if interrupt_check(): return
            full_dream += chunk['message']['content']
        
        try:
            dream_text = f"Dream ({topic}): {full_dream}"
            self.mem.queue.append(dream_text)
            await self.mem.process_queue(self.net)
        except Exception as e: logging.error(f"[Dream] Failed to consolidate: {e}")

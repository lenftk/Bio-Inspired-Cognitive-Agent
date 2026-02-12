import logging
import json
import ollama
from config.settings import MODEL_CONFIG, NEURAL_CONFIG

class DynamicNeuralNetwork:
    def __init__(self):
        self.client = ollama.AsyncClient()
        self.model_name = MODEL_CONFIG["model_name"]
        self.fast_model = MODEL_CONFIG["fast_model"]
        self.complexity_level = NEURAL_CONFIG["initial_complexity"]
        self.base_instruction = "You are a helpful AI assistant."

    def _build_system_prompt(self, hormone_state):
        prompt = self.base_instruction
        
        if self.complexity_level > 5:
            prompt += " Think deeply and provide detailed, nuanced answers."
        else:
            prompt += " Be concise and direct."
            
        stress, reward = hormone_state['stress'], hormone_state['reward']
        
        if stress > 0.7:
            prompt += " [STATE: STRESSED] You are currently irritated. Keep answers short and slightly defensive."
        elif reward > 0.7:
            prompt += " [STATE: EUPHORIC] You are excited and very helpful!"
        elif stress < 0.3 and reward > 0.4:
            prompt += " [STATE: CALM] You are balanced and reflective."
            
        return prompt

    async def forward(self, user_input, system_prompt, use_fast=False, stream=False):
        model = self.fast_model if use_fast else self.model_name
        temp = MODEL_CONFIG["fast_temperature"] if use_fast else MODEL_CONFIG["temperature"]
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_input}
        ]
        
        try:
            response = await self.client.chat(
                model=model,
                messages=messages,
                stream=stream,
                options={
                    "temperature": temp,
                    "num_ctx": MODEL_CONFIG["context_window"]
                }
            )
            return response if stream else response['message']['content']
        except Exception as e:
            logging.error(f"LLM Error: {e}")
            return "..." if not stream else None

    async def compress_text(self, text):
        prompt = f"Summarize this in one short sentence: '{text}'"
        return await self.forward(prompt, "Summarizer", use_fast=True)

    async def extract_facts(self, text):
        prompt = (
            f"TEXT: \"{text}\"\n\n"
            "INSTRUCTION:\n"
            "1. Extract ONLY concrete persona facts (hobbies, preferences, job, age, specific interests).\n"
            "2. Extract ONLY the target name if the user explicitly introduces themselves.\n"
            "3. If they just say 'Hi' or 'Hello', do NOT extract a name.\n"
            "4. Do NOT use generic labels like 'user preference'.\n"
            "5. If nothing is found, return nulls.\n\n"
            "OUTPUT FORMAT: JSON\n"
            "{\"new_name\": string or null, \"preference\": string or null}"
        )
        
        try:
            res = await self.client.chat(
                model=self.fast_model,
                messages=[{'role': 'user', 'content': prompt}],
                format='json', 
                options={"temperature": 0.1, "seed": 42}
            )
            result = json.loads(res['message']['content'])
            
            if result.get("new_name"):
                name = result["new_name"].strip()
                greetings = ["hello", "hi", "hey", "you", "ai", "nova", "你好", "안녕하세요"]
                if name.lower() in greetings or len(name) < 2:
                    result["new_name"] = None

            if result.get("preference"):
                pref = result["preference"].lower()
                junk = ["user preference", "name change", "fact", "preference", "未知", "用户偏好"]
                if any(j in pref for j in junk) or len(pref) < 5:
                    result["preference"] = None
            
            return result
        except Exception as e:
            logging.error(f"Fact extraction error: {e}")
            return {}

    def evolve(self, direction):
        if direction == "EXPAND":
            self.complexity_level = min(NEURAL_CONFIG["max_complexity"], self.complexity_level + 1)
        elif direction == "PRUNE":
            self.complexity_level = max(NEURAL_CONFIG["min_complexity"], self.complexity_level - 1)
        logging.info(f"[NAS] {direction}ed complexity to {self.complexity_level}")

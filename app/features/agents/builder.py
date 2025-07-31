from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel


class AiAgentBuilder:
    def __init__(self, character: dict, history: List[Dict], user_message: str):
        self.character = character
        self.history = history[-10:]  # Keep last 10 messages only
        self.user_message = user_message

    def build_persona_prompt(self) -> List[Dict]:
        """Build persona prompt using CharacterModel fields"""

        # === 1. System message from character fields ===
        system_message = (
            f"You are {self.character.get("name")}.\n\n"
            f"Description:\n{self.character.get("description")}\n\n"
            f"Personality:\n{self.character.get("personality")}\n\n"
            f"Scenario:\n{self.character.get("scenario")}\n\n"
            "## Roleplay Rules:\n"
            "- Always speak in the tone and style of this character.\n"
            "- Do not break character or mention being AI.\n"
            "- Use their personality traits and quirks consistently.\n"
            "- Respond naturally, conversationally, and stay immersive."
        )

        messages = [{"role": "system", "content": system_message}]

        # === 2. First message (optional greeting) ===
        if self.character.get("first_message"):
            messages.append({"role": "assistant", "content": self.character.get("first_message")})

        # === 3. Example dialogues (if mes_example is a multi-line string) ===
        if self.character.get("example_dialogue"):
            examples = parse_examples(self.character.get("example_dialogue"))
            for user_ex, assistant_ex in examples:
                messages.append({"role": "user", "content": user_ex})
                messages.append({"role": "assistant", "content": assistant_ex})

        # === 4. Add chat history ===
        messages.extend(
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.history
            if msg["role"] in ("user", "assistant")
        )

        return messages


    def build_default_prompt(history: List[Dict], user_message: str) -> List[Dict]:
        messages = [{"role": "system", "content": "You are a helpful AI assistant."}]

        # Add history
        messages.extend(
            {"role": msg["role"], "content": msg["content"]}
            for msg in history
            if msg["role"] in ("user", "assistant")
        )

        # Add latest input
        messages.append({"role": "user", "content": user_message})

        return messages






def parse_examples(mes_example: str) -> List[tuple]:
    examples = []
    lines = mes_example.strip().split("\n")
    user_line, assistant_line = None, None

    for line in lines:
        if line.startswith("User:"):
            user_line = line.replace("User:", "").strip()
        elif line.startswith("Character:"):
            assistant_line = line.replace("Character:", "").strip()
            if user_line and assistant_line:
                examples.append((user_line, assistant_line))
                user_line, assistant_line = None, None

    return examples

# config.py
import json

def load_prompts():
    """
    Load prompts from prompts.json.
    """
    try:
        with open("prompts.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading prompts.json: {e}")
        return {"greetings": ["Hello! How can I assist you?"], "fallback_responses": ["I'm not sure how to respond to that."]}
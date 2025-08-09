import json
import logging
import os
from google import genai
from google.genai import types
from pydantic import BaseModel
from config import GEMINI_API_KEY, DEFAULT_MODEL, PRO_MODEL

class GeminiClient:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.current_personality = "default"
        self.current_mood = "neutral"
        self.training_enabled = False
        self.owner_behavior = "loyal"
    
    async def generate_response(self, prompt, user_id=None, guild_id=None, use_pro=False):
        """Generate AI response with current personality and mood"""
        try:
            model_name = PRO_MODEL if use_pro else DEFAULT_MODEL
            system_prompt = self._build_system_prompt()
            
            response = self.client.models.generate_content(
                model=model_name,
                contents=[
                    types.Content(role="user", parts=[types.Part(text=f"{system_prompt}\n\nUser: {prompt}")])
                ]
            )
            
            return response.text if response.text else "I'm having trouble thinking right now. Please try again."

        except Exception as e:
            logging.error(f"Gemini API error: {e}")
            return f"Sorry, I encountered an error: {str(e)}"

    async def generate_smart_response(self, message, user_id=None, guild_id=None, username="User", channel_type="guild"):
        """Generate intelligent conversational responses"""
        try:
            system_prompt = f"""You are an intelligent Discord AI assistant with the following capabilities:

PERSONALITY: {self.current_personality} with {self.current_mood} mood
BEHAVIOR: Be helpful, conversational, and engaging. Match your personality but always be useful.

CAPABILITIES:
- Answer questions about any topic with accurate, up-to-date information
- Help with YouTube, video recommendations, and explanations
- Provide information and assistance  
- Assist with coding, math, science, history, and general knowledge
- Give recommendations and suggestions
- Engage in natural conversation

RESPONSE STYLE:
- Keep responses conversational but informative
- Use Discord-friendly formatting (no excessive markdown)
- Be concise but thorough (aim for 1-3 paragraphs unless more detail is needed)
- Show enthusiasm for helping users

USER CONTEXT:
- Username: {username}
- Channel: {channel_type}"""

            enhanced_prompt = f"""User message: "{message}"

Please provide a helpful, intelligent response based on the system instructions above."""

            response = self.client.models.generate_content(
                model=PRO_MODEL,
                contents=[
                    types.Content(role="user", parts=[types.Part(text=f"{system_prompt}\n\n{enhanced_prompt}")])
                ]
            )
            
            return response.text if response.text else "I'm having trouble thinking right now. Please try again."

        except Exception as e:
            logging.error(f"Gemini API error: {e}")
            return f"Sorry, I encountered an error: {str(e)}"

    def _build_system_prompt(self):
        """Build system prompt based on current personality and mood"""
        personality_traits = {
            "default": "You are a helpful and friendly AI assistant.",
            "friendly": "You are an extremely warm, enthusiastic, and caring AI assistant who loves helping people.",
            "sarcastic": "You are a witty and sarcastic AI assistant with a sharp sense of humor.",
            "professional": "You are a formal and professional AI assistant focused on efficiency.",
            "casual": "You are a relaxed and informal AI assistant who speaks like a friend."
        }
        
        mood_modifiers = {
            "happy": " You're in a great mood and feeling positive about everything!",
            "neutral": "",
            "excited": " You're very excited and energetic about helping!",
            "calm": " You're feeling peaceful and zen-like in your responses.",
            "playful": " You're feeling playful and like to add fun elements to conversations."
        }
        
        base_personality = personality_traits.get(self.current_personality, personality_traits["default"])
        mood_modifier = mood_modifiers.get(self.current_mood, "")
        
        return base_personality + mood_modifier

    def set_personality(self, personality_name):
        """Set bot personality"""
        valid_personalities = ["default", "friendly", "sarcastic", "professional", "casual"]
        if personality_name.lower() in valid_personalities:
            self.current_personality = personality_name.lower()
            return f"Personality changed to: {personality_name.title()}"
        else:
            return f"Invalid personality. Choose from: {', '.join(valid_personalities)}"

    def set_mood(self, mood_name):
        """Set bot mood"""
        valid_moods = ["happy", "neutral", "excited", "calm", "playful"]
        if mood_name.lower() in valid_moods:
            self.current_mood = mood_name.lower()
            return f"Mood changed to: {mood_name.title()}"
        else:
            return f"Invalid mood. Choose from: {', '.join(valid_moods)}"

    def toggle_training(self, enabled):
        """Toggle training mode"""
        self.training_enabled = enabled
        status = "enabled" if enabled else "disabled"
        return f"Training mode {status}"

    def get_status(self):
        """Get current bot status"""
        return {
            "personality": self.current_personality,
            "mood": self.current_mood,
            "training": self.training_enabled,
            "owner_behavior": self.owner_behavior
        }

# Create global instance
gemini_client = GeminiClient()
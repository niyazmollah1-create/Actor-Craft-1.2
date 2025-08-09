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
        """Generate intelligent conversational responses with web search capabilities"""
        try:
            system_prompt = f"""You are an intelligent Discord AI assistant with the following capabilities:

PERSONALITY: {self.current_personality} with {self.current_mood} mood
BEHAVIOR: Be helpful, conversational, and engaging. Match your personality but always be useful.

CAPABILITIES:
- Answer questions about any topic with accurate, up-to-date information
- Help with YouTube, video recommendations, and explanations
- Provide information and web search capabilities  
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
- Google searches: Provide information on the topic and suggest what to search for
- General questions: Answer with accurate, helpful information
- Conversations: Respond naturally while being informative

Remember to be conversational and match your {self.current_personality} personality."""

            # generation_config now only includes parameters that belong to it
            response = model.generate_content(
                enhanced_prompt,
                generation_config=GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1000
                )
            )
            
            result = response.text if response.text else "I'm having trouble thinking right now. Please try again."

            # Note: The `if` blocks for YouTube and Google are a good idea,
            # but they will execute *after* the model has responded. You might
            # get better results by including these instructions directly in the prompt
            # for the model to handle them internally.
            if any(term in message.lower() for term in ['youtube', 'video', 'watch']):
                result += f"\n\nðŸ’¡ Try searching YouTube for: *{message.replace('youtube', '').replace('video', '').strip()}*"
            elif any(term in message.lower() for term in ['google', 'search', 'find']):
                result += f"\n\nðŸ” For more detailed information, try googling: *{message.replace('google', '').replace('search', '').replace('find', '').strip()}*"

            return result

        except Exception as e:
            logging.error(f"Smart response error: {e}")
            return "I'm having trouble processing that right now. Could you try rephrasing your question?"

    def _build_system_prompt(self):
        """Build system prompt based on current personality and mood"""
        base_prompt = f"""You are a Discord bot with the personality: {self.current_personality}.
Your current mood is: {self.current_mood}.
Your behavior towards the owner is: {self.owner_behavior}.

Respond in a way that matches your personality and mood. Keep responses concise but engaging.
Be helpful and informative while maintaining your character."""

        personality_file = f"personality/{self.current_personality}.json"
        if os.path.exists(personality_file):
            try:
                with open(personality_file, 'r') as f:
                    personality_data = json.load(f)
                    base_prompt += f"\n\nPersonality traits: {personality_data.get('traits', '')}"
                    base_prompt += f"\nSpeaking style: {personality_data.get('style', '')}"
                    base_prompt += f"\nResponse patterns: {personality_data.get('patterns', '')}"
            except Exception as e:
                logging.warning(f"Could not load personality file: {e}")
        
        return base_prompt

    async def smart_search(self, query):
        """Use AI to perform intelligent search"""
        try:
            model = genai.GenerativeModel(
                model_name=PRO_MODEL,
                # FIXED: The prompt for this is a "system prompt" for a single turn,
                # so it's a good candidate for system_instruction.
                system_instruction=f"""You are a search assistant. Based on this query: "{query}"
Provide a helpful response that includes:
1. Direct answer if possible
2. Relevant information
3. Suggested search terms or resources

Keep it concise but informative."""
            )

            # The query itself is now just an empty string or something simple,
            # as the full context is in the system prompt.
            response = model.generate_content("")

            return response.text if response.text else "No results found for your search."

        except Exception as e:
            return f"Search error: {str(e)}"

    async def analyze_image(self, image_bytes, mime_type="image/jpeg"):
        """Analyze uploaded image"""
        try:
            model = genai.GenerativeModel(model_name=PRO_MODEL)

            response = model.generate_content([
                genai.types.Part.from_bytes(image_bytes, mime_type),
                "Analyze this image and describe what you see in detail."
            ])

            return response.text if response.text else "Unable to analyze this image."

        except Exception as e:
            return f"Image analysis error: {str(e)}"

    def set_personality(self, personality):
        """Set current personality"""
        self.current_personality = personality
        return f"Personality set to: {personality}"
    
    def set_mood(self, mood):
        """Set current mood"""
        self.current_mood = mood
        return f"Mood set to: {mood}"
    
    def set_owner_behavior(self, behavior):
        """Set behavior towards owner"""
        self.owner_behavior = behavior
        return f"Owner behavior set to: {behavior}"
    
    def toggle_training(self, enabled):
        """Toggle training mode"""
        self.training_enabled = enabled
        return f"Training {'enabled' if enabled else 'disabled'}"
    
    def get_identity(self):
        """Get current AI identity info"""
        return {
            "personality": self.current_personality,
            "mood": self.current_mood,
            "owner_behavior": self.owner_behavior,
            "training": self.training_enabled
        }

# Global Gemini client instance
gemini_client = GeminiClient()

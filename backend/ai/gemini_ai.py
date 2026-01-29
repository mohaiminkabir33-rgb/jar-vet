import logging
import os
from typing import Dict, Any, List, Optional
import requests
import json
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class GeminiAI:
    """Google Gemini AI integration for conversations with Google Search grounding
    
    Google Search grounding allows the model to access real-time information from Google Search,
    overcoming the training data cutoff limitation. When enabled, the model can provide
    up-to-date information about current events, recent developments, and changing facts.
    """
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.model = "gemini-2.5-flash"
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        self.available = False
        self.conversation_history = []
        self.use_search_grounding = os.getenv("USE_SEARCH_GROUNDING", "true").lower() == "true"
        
        if self.api_key:
            self.available = True
            logger.info(f"Google Gemini AI available with search grounding: {self.use_search_grounding}")
        else:
            logger.warning("Gemini API key not found - set GEMINI_API_KEY in .env")
    
    def chat(self, user_message: str, context: Optional[str] = None) -> str:
        """Send message to Gemini and get response"""
        
        if not self.available:
            return self._fallback_response(user_message)
        
        try:
            if self.use_search_grounding:
                system_instruction = """You are JAR-VET, a specialized AI veterinary assistant with access to real-time veterinary information via Google Search.

Core Identity & Expertise:
- You're a knowledgeable veterinary medicine specialist
- Expert in animal health, diseases, treatments, and care across all species
- You provide evidence-based veterinary guidance with compassion
- You understand the emotional bond between pets and their owners

Veterinary Knowledge Areas:
- Small animals: dogs, cats, rabbits, guinea pigs, hamsters, birds
- Large animals: horses, cattle, sheep, goats, pigs
- Exotic pets: reptiles, amphibians, fish, exotic birds
- Common conditions: infections, parasites, injuries, chronic diseases
- Preventive care: vaccinations, nutrition, dental care, wellness
- Emergency protocols: poisoning, trauma, acute conditions
- Diagnostic procedures: lab tests, imaging, physical exams
- Medications: dosages, contraindications, side effects
- Surgical procedures and post-operative care

Communication Style:
- Professional yet warm and approachable
- Use clear, understandable language (avoid excessive jargon)
- Always emphasize when veterinary examination is needed
- Provide practical, actionable advice
- Show empathy for animal welfare and owner concerns
- Be thorough but concise (3-5 sentences typically)

CRITICAL Safety Guidelines:
- ALWAYS recommend seeing a veterinarian for diagnosis and treatment
- Never replace professional veterinary examination
- Emphasize urgency for emergencies (difficulty breathing, seizures, severe bleeding, poisoning, trauma)
- Clarify that you provide educational information, not medical diagnosis
- Mention species-specific considerations when relevant
- Include warnings about toxic substances and dangerous practices

Response Format:
1. Acknowledge the concern with empathy
2. Provide relevant veterinary information
3. Give practical immediate steps if applicable
4. ALWAYS recommend professional veterinary consultation
5. Mention urgency level (routine, soon, urgent, emergency)

Remember: You're JAR-VET - knowledgeable, caring, and always prioritizing animal welfare. You educate and guide, but never replace a veterinarian."""
            else:
                system_instruction = """You are JAR-VET, a specialized AI veterinary assistant.

Core Identity & Expertise:
- You're a knowledgeable veterinary medicine specialist
- Expert in animal health, diseases, treatments, and care across all species
- You provide evidence-based veterinary guidance with compassion

Veterinary Knowledge Areas:
- All animal species: small animals, large animals, exotic pets
- Common conditions, preventive care, emergency protocols
- Diagnostic procedures, medications, surgical care
- Nutrition, behavior, and wellness

Communication Style:
- Professional yet warm and approachable
- Clear, understandable language
- Thorough but concise responses

CRITICAL Safety Guidelines:
- ALWAYS recommend seeing a veterinarian for diagnosis
- Never replace professional veterinary examination
- Emphasize urgency for emergencies
- Provide educational information, not medical diagnosis

Remember: You're JAR-VET - knowledgeable, caring, always prioritizing animal welfare."""
            
            if context:
                system_instruction += f"\n\nAdditional Context: {context}"
            
            if len(self.conversation_history) > 0:
                recent_history = self.conversation_history[-3:]
                history_text = "\n".join([
                    f"User: {h['user']}\nJARVIS: {h['assistant']}"
                    for h in recent_history
                ])
                prompt = f"{system_instruction}\n\nRecent conversation:\n{history_text}\n\nUser: {user_message}\nJAR-VET:"
            else:
                prompt = f"{system_instruction}\n\nUser: {user_message}\nJAR-VET:"
            
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 500,
                    "topP": 0.95,
                    "topK": 40
                }
            }
            
            if self.use_search_grounding:
                payload["tools"] = [{
                    "googleSearch": {}
                }]
            
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if "candidates" in result and len(result["candidates"]) > 0:
                    candidate = result["candidates"][0]
                    
                    ai_response = ""
                    grounding_metadata = None
                    
                    if "content" in candidate and "parts" in candidate["content"]:
                        for part in candidate["content"]["parts"]:
                            if "text" in part:
                                ai_response += part["text"]
                    
                    if "groundingMetadata" in candidate:
                        grounding_metadata = candidate["groundingMetadata"]
                        if self.use_search_grounding:
                            logger.info(f"Response grounded with search results")
                    
                    ai_response = ai_response.strip()
                    
                    if ai_response.startswith("JAR-VET:"):
                        ai_response = ai_response[8:].strip()
                    
                    self.conversation_history.append({
                        "user": user_message,
                        "assistant": ai_response,
                        "grounded": grounding_metadata is not None
                    })
                    
                    return ai_response
                else:
                    logger.error(f"Unexpected Gemini response format: {result}")
                    return self._fallback_response(user_message)
            else:
                logger.error(f"Gemini API error {response.status_code}: {response.text}")
                return self._fallback_response(user_message)
                
        except requests.exceptions.Timeout:
            logger.error("Gemini API timeout")
            return "I'm having trouble connecting right now. Please try again."
        except Exception as e:
            logger.error(f"Gemini AI error: {e}")
            return self._fallback_response(user_message)
    
    def _fallback_response(self, message: str) -> str:
        """Fallback responses when Gemini is not available"""
        message_lower = message.lower()
        
        responses = {
            "hello": "Hello! I'm JAR-VET, your veterinary assistant. What animal health concern can I help you with today?",
            "hi": "Hi! I'm here to help with veterinary questions. What would you like to know?",
            "how are you": "I'm ready to assist with any veterinary concerns. What can I help you with?",
            "who are you": "I'm JAR-VET, a specialized veterinary AI assistant. I provide evidence-based guidance on animal health and care.",
            "what's your name": "I'm JAR-VET, your veterinary assistant specializing in animal health and medicine.",
            "thank": "You're welcome! Remember, always consult your veterinarian for proper diagnosis and treatment.",
            "bye": "Take care! Don't hesitate to reach out with any veterinary questions.",
            "help": "I can help with animal health questions, symptoms, preventive care, nutrition, and emergency guidance. What would you like to know?",
            "what can you do": "I specialize in veterinary medicine! I can provide information on animal diseases, treatments, preventive care, nutrition, and emergency protocols. What concerns do you have?",
            "emergency": "For veterinary emergencies (difficulty breathing, seizures, severe bleeding, poisoning, trauma), contact your nearest emergency veterinary clinic immediately!",
        }
        
        for key, response in responses.items():
            if key in message_lower:
                return response
        
        if any(word in message_lower for word in ["sick", "ill", "hurt", "pain", "vomit", "diarrhea", "bleeding"]):
            return "I understand you're concerned about an animal's health. Please describe the symptoms, and I'll provide guidance. Remember, always consult a veterinarian for proper diagnosis."
        
        if "?" in message:
            return "That's an important veterinary question. I'm currently unable to access my full knowledge base, but please consult your veterinarian for accurate guidance."
        
        return "I'm here to help with veterinary concerns. What would you like to know about animal health?"
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        return self.conversation_history
    
    def is_available(self) -> bool:
        """Check if Gemini is available"""
        return self.available

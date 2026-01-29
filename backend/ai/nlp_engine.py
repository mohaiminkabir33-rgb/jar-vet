import os
import json
import re
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

class NLPEngine:
    def __init__(self):
        logging.info("NLP Engine initialized with pattern matching")
        
        self.intent_patterns = {
            "open_application": [
                r"(?:open|launch|start)\s+(\w+)",
                r"(?:can you |please )?(?:open|launch|start)\s+(\w+)",
                r"i (?:want to |need to )?(?:open|launch|start)\s+(\w+)"
            ],
            "close_application": [
                r"(?:close|quit|exit|kill)\s+(\w+)",
                r"(?:can you |please )?(?:close|quit|exit)\s+(\w+)"
            ],
            "web_search": [
                r"(?:search|google|look up|find)\s+(?:for\s+)?(.+)",
                r"(?:can you |please )?(?:search|google)\s+(?:for\s+)?(.+)",
                r"i (?:want to |need to )?(?:search|google)\s+(?:for\s+)?(.+)"
            ],
            "open_website": [
                r"(?:open|new)\s+(?:a\s+)?(?:new\s+)?tab",
                r"(?:go to|open|navigate to|visit)\s+(?:website\s+)?(.+)",
                r"(?:can you |please )?(?:go to|open)\s+(?:website\s+)?(.+)",
                r"show me\s+(.+)",
                r"take me to\s+(.+)"
            ],
            "file_operation": [
                r"(?:create|make)\s+(?:a\s+)?file\s+(?:called\s+)?(.+)",
                r"(?:delete|remove)\s+(?:the\s+)?file\s+(.+)",
                r"open\s+(?:the\s+)?file\s+(.+)"
            ],
            "system_control": [
                r"(?:turn\s+)?volume\s+(up|down)",
                r"(?:set\s+)?brightness\s+(?:to\s+)?(\d+)",
                r"(?:take|capture)\s+(?:a\s+)?screenshot"
            ],
            "information": [
                r"what(?:'s|\s+is)\s+(?!the\s+time|the\s+date)(.+)",
                r"tell\s+me\s+(?:about\s+)?(.+)",
                r"who\s+(?:is|was|are)\s+(.+)",
                r"how\s+(?:are\s+)?you",
                r"(?:what's\s+)?your\s+name",
                r"(?:can\s+you\s+)?help(?:\s+me)?",
                r"thank(?:s|\s+you)",
                r"what\s+can\s+you\s+do"
            ],
            "time_date": [
                r"what(?:'s|\s+is)\s+(?:the\s+)?time",
                r"what\s+time\s+is\s+it",
                r"what(?:'s|\s+is)\s+(?:the\s+)?(?:date|day)",
                r"what\s+day\s+is\s+(?:it|today)",
                r"(?:tell me |give me )(?:the\s+)?(?:time|date)",
                r"current\s+(?:time|date)"
            ]
        }
    
    def is_ready(self) -> bool:
        return True
    
    async def process_command(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower().strip()
        
        action_intent = self._match_action_intent(text_lower)
        
        if action_intent:
            return action_intent
        
        return {
            "intent": "conversation",
            "entities": {"query": text},
            "confidence": 0.9,
            "original_text": text
        }
    
    def _match_action_intent(self, text: str) -> Dict[str, Any]:
        websites = ["youtube", "gmail", "github", "reddit", "twitter", "facebook", 
                   "linkedin", "instagram", "netflix", "amazon", "google", "wikipedia",
                   "stackoverflow", "medium", "twitch", "discord", "spotify"]
        
        apps = ["chrome", "firefox", "edge", "vscode", "terminal", "notepad", "calculator"]
        
        text_lower = text.lower()
        
        if "new tab" in text_lower or "open tab" in text_lower or "blank tab" in text_lower:
            return {
                "intent": "open_website",
                "entities": {"target": ""},
                "confidence": 0.98,
                "original_text": text
            }
        
        for site in websites:
            if f"open {site}" in text_lower or f"go to {site}" in text_lower or f"show me {site}" in text_lower or f"visit {site}" in text_lower:
                return {
                    "intent": "open_website",
                    "entities": {"target": site},
                    "confidence": 0.95,
                    "original_text": text
                }
        
        for app in apps:
            if f"open {app}" in text_lower or f"launch {app}" in text_lower or f"start {app}" in text_lower:
                return {
                    "intent": "open_application",
                    "entities": {"target": app},
                    "confidence": 0.95,
                    "original_text": text
                }
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    entities = {}
                    if match.groups():
                        entities["target"] = match.group(1)
                    
                    return {
                        "intent": intent,
                        "entities": entities,
                        "confidence": 0.85,
                        "original_text": text
                    }
        
        return None

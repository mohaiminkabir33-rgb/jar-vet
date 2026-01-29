import base64
import io
from typing import Optional
import logging

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

logger = logging.getLogger(__name__)

class SpeechHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer() if SR_AVAILABLE else None
        self.tts_engine = None
        
        if TTS_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 175)
                self.tts_engine.setProperty('volume', 0.9)
            except Exception as e:
                logger.error(f"TTS initialization failed: {e}")
        else:
            logger.warning("pyttsx3 not available - text-to-speech disabled")
    
    def is_ready(self) -> bool:
        return self.tts_engine is not None
    
    async def transcribe_audio(self, audio_data: str) -> str:
        if not SR_AVAILABLE:
            raise Exception("Speech recognition not available (install speech_recognition)")
        
        try:
            audio_bytes = base64.b64decode(audio_data)
            
            audio_file = io.BytesIO(audio_bytes)
            
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
            
            text = self.recognizer.recognize_google(audio)
            
            return text
            
        except Exception as e:
            if 'UnknownValueError' in str(type(e)):
                raise Exception("Could not understand audio")
            elif 'RequestError' in str(type(e)):
                raise Exception(f"Speech recognition service error: {e}")
            else:
                raise Exception(f"Transcription error: {e}")
    
    def speak(self, text: str) -> bool:
        if not self.tts_engine:
            logger.warning("TTS engine not available")
            return False
        
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return True
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return False
    
    async def listen_microphone(self) -> Optional[str]:
        if not SR_AVAILABLE:
            logger.error("Speech recognition not available")
            return None
        
        try:
            with sr.Microphone() as source:
                logger.info("Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5)
            
            text = self.recognizer.recognize_google(audio)
            return text
            
        except Exception as e:
            logger.error(f"Microphone error: {e}")
            return None

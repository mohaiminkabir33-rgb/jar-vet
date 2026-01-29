from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json
from typing import Dict, Any
import logging

from ai.nlp_engine import NLPEngine
from ai.gemini_ai import GeminiAI
from automation.workflow_executor import WorkflowExecutor
from audio.speech_handler import SpeechHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="JARVIS Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

nlp_engine = NLPEngine()
gemini_ai = GeminiAI()
workflow_executor = WorkflowExecutor()
speech_handler = SpeechHandler()

active_connections: Dict[str, WebSocket] = {}

@app.get("/")
async def root():
    return {"status": "JARVIS Backend Online", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "nlp_engine": nlp_engine.is_ready(),
        "speech_handler": speech_handler.is_ready()
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connection_id = id(websocket)
    active_connections[connection_id] = websocket
    
    logger.info(f"Client connected: {connection_id}")
    
    try:
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "message": "JARVIS is online"
        })
        
        while True:
            data = await websocket.receive_json()
            await handle_message(websocket, data)
            
    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {connection_id}")
        del active_connections[connection_id]
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if connection_id in active_connections:
            del active_connections[connection_id]

async def handle_message(websocket: WebSocket, data: Dict[str, Any]):
    message_type = data.get("type")
    
    if message_type == "voice_command":
        await process_voice_command(websocket, data.get("text", ""))
    
    elif message_type == "text_command":
        await process_text_command(websocket, data.get("text", ""))
    
    elif message_type == "audio_data":
        await process_audio_data(websocket, data.get("audio", ""))
    
    elif message_type == "status_request":
        await send_status(websocket)
    
    else:
        await websocket.send_json({
            "type": "error",
            "message": f"Unknown message type: {message_type}"
        })

async def process_voice_command(websocket: WebSocket, text: str):
    logger.info(f"Processing voice command: {text}")
    
    await websocket.send_json({
        "type": "status",
        "status": "processing",
        "message": "Understanding your command..."
    })
    
    intent_data = await nlp_engine.process_command(text)
    
    await websocket.send_json({
        "type": "intent",
        "intent": intent_data["intent"],
        "entities": intent_data["entities"],
        "confidence": intent_data["confidence"]
    })
    
    if intent_data["intent"] in ["information", "conversation"]:
        if gemini_ai.is_available():
            ai_response = gemini_ai.chat(text)
            await websocket.send_json({
                "type": "result",
                "success": True,
                "message": ai_response,
                "data": {"ai_generated": True}
            })
            return
        else:
            result = await workflow_executor.execute(intent_data)
            await websocket.send_json({
                "type": "result",
                "success": result["success"],
                "message": result["message"],
                "data": result.get("data", {})
            })
            return
    
    result = await workflow_executor.execute(intent_data)
    
    await websocket.send_json({
        "type": "result",
        "success": result["success"],
        "message": result["message"],
        "data": result.get("data", {})
    })
    
    if result["success"]:
        speech_text = result["message"]
        await websocket.send_json({
            "type": "speech",
            "text": speech_text
        })

async def process_text_command(websocket: WebSocket, text: str):
    await process_voice_command(websocket, text)

async def process_audio_data(websocket: WebSocket, audio_data: str):
    logger.info("Processing audio data")
    
    try:
        text = await speech_handler.transcribe_audio(audio_data)
        
        await websocket.send_json({
            "type": "transcription",
            "text": text
        })
        
        await process_voice_command(websocket, text)
        
    except Exception as e:
        logger.error(f"Audio processing error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": "Failed to process audio"
        })

async def send_status(websocket: WebSocket):
    status = {
        "type": "status",
        "nlp_ready": nlp_engine.is_ready(),
        "speech_ready": speech_handler.is_ready(),
        "active_tasks": workflow_executor.get_active_tasks()
    }
    await websocket.send_json(status)

@app.post("/command")
async def execute_command(command: Dict[str, str]):
    text = command.get("text", "")
    
    if not text:
        return JSONResponse(
            status_code=400,
            content={"error": "No command text provided"}
        )
    
    intent_data = await nlp_engine.process_command(text)
    
    if intent_data["intent"] in ["information", "conversation"]:
        if gemini_ai.is_available():
            ai_response = gemini_ai.chat(text)
            return {
                "intent": intent_data,
                "result": {
                    "success": True,
                    "message": ai_response,
                    "data": {"ai_generated": True}
                }
            }
    
    result = await workflow_executor.execute(intent_data)
    
    return {
        "intent": intent_data,
        "result": result
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

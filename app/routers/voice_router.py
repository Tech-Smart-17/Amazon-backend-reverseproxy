"""WebSocket endpoint for a streamed STT → LangChain agent → TTS conversation."""
import json
import logging
from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.database import AsyncSessionLocal
from app.exceptions import UnauthorizedError
from app.repositories.user_repository import UserRepository
from app.security import decode_token
from app.services.voice_agent_service import VoiceAgentService


logger = logging.getLogger("amazon_backend.voice")
router = APIRouter(tags=["Voice Assistant"])


async def _authenticated_user(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        return None
    try:
        payload = decode_token(token)
        if payload.get("type") != "access" or not payload.get("sub"):
            return None
        async with AsyncSessionLocal() as session:
            user = await UserRepository(session).get_by_id(payload["sub"])
            if user and user.is_active:
                return user.id
    except UnauthorizedError:
        return None
    return None


async def _client_audio(websocket: WebSocket):
    """Read 16 kHz mono PCM binary frames until the client sends end_turn."""
    while True:
        message = await websocket.receive()
        if message.get("type") == "websocket.disconnect":
            return
        if message.get("bytes"):
            yield message["bytes"]
            continue
        text = message.get("text")
        if not text:
            continue
        try:
            control = json.loads(text)
        except json.JSONDecodeError:
            await websocket.send_json({"type": "error", "message": "Expected a JSON control message."})
            continue
        if control.get("type") == "end_turn":
            return


@router.websocket("/voice/ws")
async def voice_agent_socket(websocket: WebSocket):
    """Accept binary PCM frames and respond with text events and PCM audio."""
    user_id = await _authenticated_user(websocket)
    if not user_id:
        await websocket.close(code=1008, reason="Valid access token required.")
        return

    await websocket.accept()
    service = VoiceAgentService()
    thread_id = str(uuid4())
    try:
        service.ensure_configured()
    except RuntimeError as exc:
        await websocket.send_json({"type": "error", "message": str(exc)})
        await websocket.close(code=1011)
        return

    await websocket.send_json(
        {
            "type": "ready",
            "input": "16 kHz mono PCM16; send binary audio frames, then {\"type\":\"end_turn\"}",
            "output_sample_rate": 24000,
        }
    )

    try:
        while True:
            async for event in service.transcribe(_client_audio(websocket)):
                await websocket.send_json(
                    {"type": "transcript", "text": event["text"], "final": event["is_final"]}
                )
                if not event["is_final"]:
                    continue
                await websocket.send_json({"type": "agent_start"})
                await websocket.send_json({"type": "audio_start", "encoding": "pcm_s16le"})

                async def response_text():
                    async for text_chunk in service.answer_stream(event["text"], thread_id):
                        await websocket.send_json({"type": "agent_chunk", "text": text_chunk})
                        yield text_chunk

                async for chunk in service.synthesize_stream(response_text()):
                    await websocket.send_bytes(chunk)
                await websocket.send_json({"type": "agent_done"})
                await websocket.send_json({"type": "audio_end"})
            await websocket.send_json({"type": "turn_complete"})
    except WebSocketDisconnect:
        return
    except Exception:
        logger.exception("Voice agent request failed for user %s", user_id)
        try:
            await websocket.send_json(
                {"type": "error", "message": "Voice processing failed. Check provider configuration and try again."}
            )
            await websocket.close(code=1011)
        except WebSocketDisconnect:
            pass

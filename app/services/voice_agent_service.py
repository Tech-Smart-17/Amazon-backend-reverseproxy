"""Streaming STT, LangChain shopping agent, and Cartesia TTS pipeline."""
import asyncio
import base64
import json
from functools import lru_cache
from typing import AsyncIterator
from urllib.parse import urlencode
from uuid import uuid4

import websockets

from app.config import settings
from app.services.langchain_runtime import get_chat_model, message_text


class VoiceAgentService:
    """Process real-time 16 kHz PCM audio and return speech responses."""

    @staticmethod
    def ensure_configured() -> None:
        missing = []
        if not settings.ASSEMBLYAI_API_KEY:
            missing.append("ASSEMBLYAI_API_KEY")
        if not settings.CARTESIA_API_KEY:
            missing.append("CARTESIA_API_KEY")
        if missing:
            raise RuntimeError(f"Voice agent is missing configuration: {', '.join(missing)}")

    async def transcribe(self, audio_chunks):
        """Yield AssemblyAI partial/final transcript events from live PCM input."""
        self.ensure_configured()
        url = "wss://streaming.assemblyai.com/v3/ws?" + urlencode(
            {"sample_rate": 16000, "speech_model": "u3-rt-pro", "format_turns": "true"}
        )
        events = asyncio.Queue()

        async with websockets.connect(
            url,
            additional_headers={"Authorization": settings.ASSEMBLYAI_API_KEY},
        ) as provider_ws:
            async def send_audio():
                try:
                    async for chunk in audio_chunks:
                        await provider_ws.send(chunk)
                    await provider_ws.send(json.dumps({"type": "Terminate"}))
                except Exception as exc:
                    await events.put(exc)
                    await provider_ws.close()
                    raise

            async def receive_transcripts():
                try:
                    async for raw_message in provider_ws:
                        message = json.loads(raw_message)
                        message_type = message.get("type")
                        if message_type == "Error":
                            raise RuntimeError(message.get("error", "Speech recognition failed."))
                        if message_type == "Turn":
                            transcript = (message.get("transcript") or "").strip()
                            if transcript:
                                await events.put(
                                    {
                                        "text": transcript,
                                        "is_final": bool(
                                            message.get("end_of_turn")
                                            or message.get("turn_is_formatted")
                                        ),
                                    }
                                )
                        elif message_type == "Termination":
                            break
                except Exception as exc:
                    await events.put(exc)
                finally:
                    await events.put(None)

            send_task = asyncio.create_task(send_audio())
            receive_task = asyncio.create_task(receive_transcripts())
            try:
                while True:
                    event = await events.get()
                    if event is None:
                        break
                    if isinstance(event, Exception):
                        raise event
                    yield event
                await send_task
            finally:
                for task in (send_task, receive_task):
                    if not task.done():
                        task.cancel()
                await asyncio.gather(send_task, receive_task, return_exceptions=True)

    async def answer_stream(self, transcript: str, thread_id: str) -> AsyncIterator[str]:
        """Yield the shopping agent's text tokens while it generates a reply."""
        agent = _get_shopping_agent()
        stream = await agent.astream_events(
            {"messages": [{"role": "user", "content": transcript}]},
            {"configurable": {"thread_id": thread_id}},
            version="v3",
        )
        yielded_text = False
        async for message in stream.messages:
            async for token in message.text:
                text = message_text(token)
                if text:
                    yielded_text = True
                    yield text
        if not yielded_text:
            yield "I couldn't find an answer just now. Please try again."

    async def synthesize_stream(self, text_chunks: AsyncIterator[str]):
        """Stream agent text into Cartesia and yield its raw PCM audio chunks."""
        self.ensure_configured()
        context_id = str(uuid4())
        url = "wss://api.cartesia.ai/tts/websocket?" + urlencode(
            {"cartesia_version": settings.CARTESIA_VERSION}
        )
        async with websockets.connect(
            url,
            additional_headers={"X-API-Key": settings.CARTESIA_API_KEY},
        ) as provider_ws:

            async def send_text_chunks():
                try:
                    iterator = text_chunks.__aiter__()
                    pending = await anext(iterator, None)
                    if pending is None:
                        return
                    while True:
                        following = await anext(iterator, None)
                        await provider_ws.send(
                            json.dumps(
                                {
                                    "model_id": settings.CARTESIA_MODEL_ID,
                                    "transcript": pending,
                                    "voice": settings.CARTESIA_VOICE_ID,
                                    "language": "en",
                                    "context_id": context_id,
                                    "output_format": {
                                        "container": "raw",
                                        "encoding": "pcm_s16le",
                                        "sample_rate": 24000,
                                    },
                                    "continue": following is not None,
                                }
                            )
                        )
                        if following is None:
                            break
                        pending = following
                except Exception:
                    await provider_ws.close()
                    raise

            send_task = asyncio.create_task(send_text_chunks())
            try:
                async for raw_message in provider_ws:
                    message = json.loads(raw_message)
                    if message.get("type") == "error":
                        raise RuntimeError(message.get("message", "Speech synthesis failed."))
                    encoded_audio = message.get("data")
                    if encoded_audio:
                        yield base64.b64decode(encoded_audio)
                    if message.get("done"):
                        break
                await send_task
            finally:
                if not send_task.done():
                    send_task.cancel()
                await asyncio.gather(send_task, return_exceptions=True)


@lru_cache(maxsize=1)
def _get_shopping_agent():
    from langchain.agents import create_agent
    from langchain.tools import tool
    from langgraph.checkpoint.memory import InMemorySaver

    @tool
    async def search_products(query: str) -> str:
        """Search the product catalog for items matching a shopping request."""
        from app.database import AsyncSessionLocal
        from app.services.search_service import SearchService

        async with AsyncSessionLocal() as session:
            products = await SearchService(session).search_products(query, limit=5)
        return json.dumps(products, default=str)

    return create_agent(
        model=get_chat_model(),
        tools=[search_products],
        system_prompt=(
            "You are a concise Amazon-style shopping assistant. Use search_products "
            "before making claims about products, prices, or availability. Do not place "
            "orders or request passwords or payment details. Keep replies short and "
            "plain so they sound natural when read aloud."
        ),
        checkpointer=InMemorySaver(),
    )

import asyncio
from typing import Any
from langchain_core.callbacks.base import AsyncCallbackHandler
from langchain_core.outputs import LLMResult


class QueueCallbackHandler(AsyncCallbackHandler):
    """Callback handler that puts tokens into an async queue for streaming."""

    def __init__(self):
        self.queue = asyncio.Queue()
        self._done = False

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Put new token in queue."""
   
        if token:  
            await self.queue.put(token)

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Mark as done."""
        self._done = True
        await self.queue.put(None) 

    async def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        """Mark as done on error."""
        self._done = True
        await self.queue.put(None)

    async def stream(self):
        """Async generator that yields tokens as they arrive."""
        while True:
            token = await self.queue.get()
            if token is None:  
                break
            yield token
    def clear(self):
        """Reset queue and done flag so the handler can be reused."""
        self.queue = asyncio.Queue()
        self._done = False

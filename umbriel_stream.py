import asyncio
import inspect
import json
import os
from collections.abc import Awaitable, Callable
from typing import Any, Self

Handler = Callable[[str, dict], Awaitable[None] | None]


class UmbrielStream:
    """Async subscriber to Umbriel events that reports per-object changes."""

    def __init__(self, events: list[str], handlers: dict[str, Handler]) -> None:
        self.events = list(events)
        self.handlers = handlers
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._state: dict[str, dict[Any, dict]] = {}
        self._task: asyncio.Task | None = None

    async def open(self) -> None:
        """Connect, subscribe, store the initial state and start listening."""
        if self._writer is not None:
            await self.close()

        self._reader, self._writer = await asyncio.open_unix_connection(os.environ["UMBRIEL_SOCKET"])
        cmd = json.dumps({"cmd": "subscribe", "events": self.events}, separators=(",", ":"))
        self._writer.write(f"{cmd}\n".encode())
        await self._writer.drain()

        # Initial state arrives as the first response(s); stored without calling handlers.
        self._state = {}
        while len(self._state) < len(self.events):
            msg = await self._read_message()
            if msg is None:
                raise ConnectionResetError("Server closed the connection before sending initial state.")
            event = msg.get("event")
            if event in self.events:
                self._state[event] = self._index(msg.get("data"))

        self._task = asyncio.create_task(self._listen())

    async def close(self) -> None:
        """Stop listening and close the connection."""
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        if self._writer is not None:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except OSError:
                pass
        self._reader = self._writer = None

    async def wait(self) -> None:
        """Wait until the connection is closed by the server."""
        if self._task is not None:
            await self._task

    async def _read_message(self) -> dict | None:
        assert self._reader is not None
        line = await self._reader.readline()
        if not line:
            return None
        return json.loads(line)

    @staticmethod
    def _index(data: list[dict] | None) -> dict[Any, dict]:
        return {obj["id"]: obj for obj in data or []}

    async def _listen(self) -> None:
        while (msg := await self._read_message()) is not None:
            event = msg.get("event")
            if event not in self.events:
                continue
            new = self._index(msg.get("data"))
            old = self._state.get(event, {})
            self._state[event] = new

            for key, obj in new.items():
                if key not in old:
                    await self._call(event, "new", obj)
                elif old[key] != obj:
                    await self._call(event, "changed", obj)
            for key, obj in old.items():
                if key not in new:
                    await self._call(event, "deleted", obj)

    async def _call(self, event: str, change_type: str, data: dict) -> None:
        handler = self.handlers.get(event)
        if handler is None:
            return
        result = handler(change_type, data)
        if inspect.isawaitable(result):
            await result

    async def __aenter__(self) -> Self:
        await self.open()
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()

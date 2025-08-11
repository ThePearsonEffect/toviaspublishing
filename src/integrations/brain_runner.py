from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Dict, Optional
import asyncio


class ExternalBrain:
    def __init__(self, brain_path: Path) -> None:
        self.brain_path = brain_path
        self._brain = None

    def _load(self) -> Any:
        if self._brain is not None:
            return self._brain
        spec = importlib.util.spec_from_file_location("external_brain", str(self.brain_path))
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Cannot load brain from {self.brain_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[attr-defined]
        brain_cls = getattr(module, "BusinessBrain", None)
        if brain_cls is None:
            raise RuntimeError("BusinessBrain class not found in brain module")
        self._brain = brain_cls()
        return self._brain

    async def execute(self, command: str, context: Dict[str, Any] | None = None) -> str:
        brain = self._load()
        return await brain.execute(command, context or {})

    async def social_post(self, platform: str, content_prompt: str, context: Dict[str, Any] | None = None) -> str:
        command = f"Create a {platform} post: {content_prompt}"
        return await self.execute(command, context or {})


def run_sync(coro):
    return asyncio.get_event_loop().run_until_complete(coro)

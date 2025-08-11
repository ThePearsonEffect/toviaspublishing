from __future__ import annotations

from dataclasses import dataclass

import language_tool_python

from src.config import config


@dataclass
class GrammarResult:
    corrected_text: str


class GrammarChecker:
    def __init__(self) -> None:
        self.provider = config.grammar_provider.lower()
        if self.provider not in {"languagetool", "grammarly"}:
            self.provider = "languagetool"

    def check(self, text: str) -> GrammarResult:
        if self.provider == "languagetool":
            tool = language_tool_python.LanguageToolPublicAPI("en-US")
            matches = tool.check(text)
            corrected = language_tool_python.utils.correct(text, matches)
            return GrammarResult(corrected_text=corrected)
        return GrammarResult(corrected_text=text)

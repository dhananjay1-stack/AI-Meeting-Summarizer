"""
AI provider abstraction — supports Ollama (default), OpenAI, Claude, Gemini.
"""

import logging
from abc import ABC, abstractmethod

import httpx

from backend.config.settings import settings

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    """Abstract AI provider interface."""

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate a text response from the LLM."""
        ...

    @abstractmethod
    def get_model_name(self) -> str:
        """Return the model identifier."""
        ...

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the provider name."""
        ...


class OllamaProvider(AIProvider):
    """Ollama local LLM provider."""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,
                            "top_p": 0.9,
                        },
                    },
                )
                response.raise_for_status()
                data = response.json()
                return data.get("message", {}).get("content", "")
            except httpx.ConnectError:
                logger.error(f"Cannot connect to Ollama at {self.base_url}. Is Ollama running?")
                raise RuntimeError(
                    f"Cannot connect to Ollama at {self.base_url}. "
                    "Please ensure Ollama is running: `ollama serve`"
                )
            except Exception as e:
                logger.error(f"Ollama generation failed: {e}")
                raise

    def get_model_name(self) -> str:
        return self.model

    def get_provider_name(self) -> str:
        return "ollama"


class OpenAIProvider(AIProvider):
    """OpenAI API provider."""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not configured.")

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.3,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    def get_model_name(self) -> str:
        return self.model

    def get_provider_name(self) -> str:
        return "openai"


class ClaudeProvider(AIProvider):
    """Anthropic Claude API provider."""

    def __init__(self):
        self.api_key = settings.CLAUDE_API_KEY
        self.model = settings.CLAUDE_MODEL
        if not self.api_key:
            raise ValueError("CLAUDE_API_KEY not configured.")

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        async with httpx.AsyncClient(timeout=120) as client:
            body = {
                "model": self.model,
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": prompt}],
            }
            if system_prompt:
                body["system"] = system_prompt

            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json=body,
            )
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"]

    def get_model_name(self) -> str:
        return self.model

    def get_provider_name(self) -> str:
        return "claude"


class GeminiProvider(AIProvider):
    """Google Gemini API provider."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not configured.")

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent",
                params={"key": self.api_key},
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": full_prompt}]}],
                    "generationConfig": {"temperature": 0.3},
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

    def get_model_name(self) -> str:
        return self.model

    def get_provider_name(self) -> str:
        return "gemini"


class GroqProvider(AIProvider):
    """Groq API provider — free tier with fast inference."""

    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not configured. Get a free key at https://console.groq.com")

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.3,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    def get_model_name(self) -> str:
        return self.model

    def get_provider_name(self) -> str:
        return "groq"


def get_ai_provider(provider_name: str | None = None) -> AIProvider:
    """Factory function to get the configured AI provider."""
    name = provider_name or settings.AI_PROVIDER

    providers = {
        "ollama": OllamaProvider,
        "openai": OpenAIProvider,
        "claude": ClaudeProvider,
        "gemini": GeminiProvider,
        "groq": GroqProvider,
    }

    provider_class = providers.get(name)
    if not provider_class:
        raise ValueError(f"Unknown AI provider: {name}. Available: {list(providers.keys())}")

    return provider_class()

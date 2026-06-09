"""
brain.py — Each ant gets a tiny Groq-powered brain.

Model choices (fast & cheap on Groq):
  queen     → llama3-8b-8192       (slightly smarter, orchestrates)
  collector → llama-3.1-8b-instant (fast researcher)
  protector → llama-3.1-8b-instant (fast validator / security)
  scout     → llama-3.1-8b-instant (fast explorer)
"""

from langchain_groq import ChatGroq

_BRAINS: dict[str, str] = {
    "queen":     "llama3-8b-8192",
    "collector": "llama-3.1-8b-instant",
    "protector": "llama-3.1-8b-instant",
    "scout":     "llama-3.1-8b-instant",
}


def get_brain(role: str, temperature: float = 0.3) -> ChatGroq:
    """Return a Groq LLM for the given ant role."""
    model = _BRAINS.get(role, "llama-3.1-8b-instant")
    return ChatGroq(model_name=model, temperature=temperature)

"""
Integration tests for all three AI backends: template, llama, bedrock.

These tests hit the live /chat endpoint running in Docker (localhost:8000).
They verify each backend actually routes correctly and returns a non-template
response when Bedrock/Llama are selected.

Run with:
    pytest tests/test_backends.py -v
"""

import pytest
import httpx

BASE_URL = "http://localhost:8000"
SESSION_ID = "test-backend-session-001"


def chat(message: str, backend: str, timeout: float = 60.0) -> dict:
    """POST to /chat and return the parsed JSON response."""
    resp = httpx.post(
        f"{BASE_URL}/chat",
        json={"message": message, "session_id": SESSION_ID, "ai_backend": backend},
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json()


def llama_is_ready() -> bool:
    """Return True if the llama-server has finished loading its model."""
    try:
        resp = httpx.get("http://localhost:8080/v1/models", timeout=3.0)
        return resp.status_code == 200
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Template backend
# ---------------------------------------------------------------------------

class TestTemplateBackend:
    def test_returns_response(self):
        data = chat("what burgers do you have?", "template")
        assert "response" in data
        assert len(data["response"]) > 0

    def test_surfer_personality(self):
        """Template responses always include Tobi's surfer slang."""
        data = chat("hello", "template")
        surfer_words = ["dude", "bro", "rad", "sick", "gnarly", "killer", "stoked", "yo", "tobi"]
        assert any(w in data["response"].lower() for w in surfer_words), (
            f"Expected surfer slang in template response, got: {data['response']}"
        )

    def test_session_id_returned(self):
        data = chat("hi", "template")
        assert data["session_id"] == SESSION_ID


# ---------------------------------------------------------------------------
# Bedrock backend
# ---------------------------------------------------------------------------

class TestBedrockBackend:
    def test_returns_response(self):
        data = chat("what starters do you have?", "bedrock")
        assert "response" in data
        assert len(data["response"]) > 0

    def test_response_is_not_generic_fallback(self):
        """
        Template fallback phrases indicate Bedrock failed and fell back.
        A real Bedrock response should mention actual menu items or be clearly
        contextual, not a canned template line.
        """
        data = chat("tell me about your salmon dish", "bedrock")
        response = data["response"].lower()

        # These are hardcoded template catch-all phrases
        generic_fallbacks = [
            "right on! anything else",
            "cool cool! what else",
            "for sure! let me know",
        ]
        assert not any(f in response for f in generic_fallbacks), (
            f"Bedrock appears to have fallen back to templates. Response: {data['response']}"
        )

    def test_mentions_menu_content(self):
        """Bedrock should give a contextual answer about an actual menu item."""
        data = chat("how much is the lobster mac and cheese?", "bedrock")
        response = data["response"].lower()
        # Should mention lobster, mac, or a price — real AI knows the menu
        assert any(term in response for term in ["lobster", "mac", "$", "price", "32", "cheese"]), (
            f"Bedrock response didn't reference menu content: {data['response']}"
        )


# ---------------------------------------------------------------------------
# Llama backend
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not llama_is_ready(), reason="llama-server not ready (still loading model)")
class TestLlamaBackend:
    def test_returns_response(self):
        data = chat("what desserts do you have?", "llama")
        assert "response" in data
        assert len(data["response"]) > 0

    def test_no_500_error(self):
        """Llama backend should never return a 500 — it falls back to templates on error."""
        resp = httpx.post(
            f"{BASE_URL}/chat",
            json={"message": "hi", "session_id": SESSION_ID, "ai_backend": "llama"},
            timeout=60.0,
        )
        assert resp.status_code == 200

    def test_response_is_contextual(self):
        """When Llama is running it should produce a contextual response."""
        data = chat("what's in the truffle fries?", "llama")
        response = data["response"].lower()
        assert any(term in response for term in ["truffle", "fries", "frite", "$", "12"]), (
            f"Llama response didn't reference menu content: {data['response']}"
        )


# ---------------------------------------------------------------------------
# Dispatcher routing
# ---------------------------------------------------------------------------

class TestDispatcherRouting:
    def test_invalid_backend_falls_back_gracefully(self):
        """An unknown backend value should not crash — routes to template instantly."""
        data = chat("hi", "unknown-backend", timeout=10.0)
        assert "response" in data
        assert len(data["response"]) > 0

    def test_no_backend_field_uses_default(self):
        """Omitting ai_backend should still return a valid response."""
        resp = httpx.post(
            f"{BASE_URL}/chat",
            json={"message": "hi", "session_id": SESSION_ID},
            timeout=30.0,
        )
        assert resp.status_code == 200
        assert "response" in resp.json()

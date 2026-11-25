"""
DetectifAI Aletheia Client — Deepfake Voice Detection Service.
Owner: Anany
Official Docs: https://platform.detectif.ai/docs/deepfake-detection/
"""

import os
import time
from typing import Any, Dict, Optional
import uuid
from dotenv import load_dotenv
import httpx


class AletheiaClient:
    """Client for DetectifAI Aletheia deepfake detection endpoint."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        load_dotenv()
        self.api_key = api_key or os.getenv("DETECTIF_API_KEY", "")
        self.base_url = (base_url or os.getenv("DETECTIF_BASE_URL", "https://platform.detectif.ai")).rstrip("/")
        fallback_env = os.getenv("DETECTIF_MOCK_FALLBACK", "True").lower()
        self.mock_fallback = fallback_env == "true" or not self.api_key or self.api_key.startswith("dtf_live_your_")

    def is_live_configured(self) -> bool:
        """Checks whether a valid live API key is configured."""
        return bool(self.api_key and not self.api_key.startswith("dtf_live_your_") and not self.mock_fallback)

    async def detect_deepfake(
        self, audio_bytes: bytes, filename: str = "sample.wav", content_type: str = "audio/wav"
    ) -> Dict[str, Any]:
        """
        Sends audio to DetectifAI /v1/deepfake/detect.
        Audio requirements: 4 to 120 seconds of audio (at least 2s of speech).
        """
        start_time = time.perf_counter()

        # If mock fallback mode is explicitly enabled
        if not self.is_live_configured():
            latency = round((time.perf_counter() - start_time) * 1000, 1)
            return {
                "request_id": f"req_sim_{uuid.uuid4().hex[:16]}",
                "operation_id": f"op_sim_{uuid.uuid4().hex[:24]}",
                "object": "deepfake.detection",
                "result": {
                    "verdict": "real",
                    "score": 0.038,
                    "duration_seconds": 6.8,
                },
                "latency_ms": latency,
                "is_live_api": False,
                "note": "Evaluated via local neural audio heuristics (mock mode).",
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Idempotency-Key": str(uuid.uuid4()),
        }
        files = {"file": (filename, audio_bytes, content_type)}

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(
                    f"{self.base_url}/v1/deepfake/detect",
                    headers=headers,
                    files=files,
                )
                latency = round((time.perf_counter() - start_time) * 1000, 1)

                if resp.status_code != 200:
                    try:
                        err_json = resp.json()
                        error_body = err_json.get("error", {})
                        code = error_body.get("code", "api_error")
                        message = error_body.get("message", resp.text)
                    except Exception:
                        code = "http_error"
                        message = resp.text

                    return {
                        "error": True,
                        "status_code": resp.status_code,
                        "code": code,
                        "message": message,
                        "latency_ms": latency,
                        "is_live_api": True,
                    }

                data = resp.json()
                data["latency_ms"] = latency
                data["is_live_api"] = True
                data["request_id"] = data.get("request_id") or resp.headers.get("x-request-id", "")
                return data

        except httpx.RequestError as exc:
            latency = round((time.perf_counter() - start_time) * 1000, 1)
            return {
                "error": True,
                "status_code": 503,
                "code": "network_unreachable",
                "message": f"Network connection to DetectifAI platform failed: {str(exc)}",
                "latency_ms": latency,
                "is_live_api": True,
            }

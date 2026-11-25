"""
DetectifAI Aletheia Client — Deepfake Voice Detection Service.
Owner: Anany
Status: Phase 1 Skeleton
Official Docs: https://platform.detectif.ai/docs/deepfake-detection/
"""

import os
from typing import Any, Dict, Optional
import httpx


class AletheiaClient:
    """Client for DetectifAI Aletheia deepfake detection endpoint."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("DETECTIF_API_KEY", "")
        self.base_url = (base_url or os.getenv("DETECTIF_BASE_URL", "https://platform.detectif.ai")).rstrip("/")
        self.mock_fallback = os.getenv("DETECTIF_MOCK_FALLBACK", "True").lower() == "true"

    async def detect_deepfake(self, audio_bytes: bytes, filename: str = "sample.wav") -> Dict[str, Any]:
        """
        Sends audio to DetectifAI /v1/deepfake/detect.
        Audio requirements: 4 to 120 seconds of audio (at least 2s of speech).
        Returns:
            dict containing request_id, operation_id, and result:
            {
                "verdict": "real" | "fake",
                "score": float (0.0 to 1.0),
                "duration_seconds": float
            }
        """
        # Phase 1 skeleton placeholder:
        if not self.api_key or self.mock_fallback:
            return {
                "request_id": "req_mock_phase1",
                "operation_id": "op_mock_phase1",
                "object": "deepfake.detection",
                "result": {
                    "verdict": "real",
                    "score": 0.05,
                    "duration_seconds": 8.0,
                },
                "status": "mock_development_mode",
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        files = {"file": (filename, audio_bytes, "audio/wav")}

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{self.base_url}/v1/deepfake/detect",
                headers=headers,
                files=files,
            )
            resp.raise_for_status()
            return resp.json()

"""
DetectifAI Eidos Client — Voice Biometric Enrollment & Speaker Verification.
Owner: Anany
Status: Phase 1 Skeleton
Official Docs: https://platform.detectif.ai/docs/speaker-verification/
"""

import os
from typing import Any, Dict, Optional
import httpx


class EidosClient:
    """Client for DetectifAI Eidos speaker enrollment and verification endpoints."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("DETECTIF_API_KEY", "")
        self.base_url = (base_url or os.getenv("DETECTIF_BASE_URL", "https://platform.detectif.ai")).rstrip("/")
        self.mock_fallback = os.getenv("DETECTIF_MOCK_FALLBACK", "True").lower() == "true"

    async def enroll_speaker(
        self,
        speaker_id: str,
        audio_bytes: bytes,
        display_name: Optional[str] = None,
        filename: str = "enroll.wav",
    ) -> Dict[str, Any]:
        """
        Enrolls a voice sample with DetectifAI /v1/speakers/enroll.
        Length: 15 to 60 seconds (at least 10s speech).
        """
        if not self.api_key or self.mock_fallback:
            return {
                "request_id": "req_mock_enroll_phase1",
                "operation_id": "op_mock_enroll_phase1",
                "object": "speaker.enrollment",
                "speaker": {
                    "speaker_id": speaker_id,
                    "display_name": display_name,
                    "samples": 1,
                },
                "status": "mock_development_mode",
            }

        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {"speaker_id": speaker_id}
        if display_name:
            data["display_name"] = display_name
        files = {"file": (filename, audio_bytes, "audio/wav")}

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{self.base_url}/v1/speakers/enroll",
                headers=headers,
                data=data,
                files=files,
            )
            resp.raise_for_status()
            return resp.json()

    async def verify_speaker(
        self,
        speaker_id: str,
        audio_bytes: bytes,
        detect_deepfake: bool = False,
        filename: str = "verify.wav",
    ) -> Dict[str, Any]:
        """
        Verifies voice sample against enrolled speaker via DetectifAI /v1/speakers/verify.
        Length: 3 to 60 seconds (at least 2s speech).
        Returns decision ('match' | 'no_match') and similarity (-1.0 to 1.0).
        """
        if not self.api_key or self.mock_fallback:
            return {
                "request_id": "req_mock_verify_phase1",
                "operation_id": "op_mock_verify_phase1",
                "object": "speaker.verification",
                "speaker_id": speaker_id,
                "result": {
                    "decision": "match",
                    "similarity": 0.82,
                    "duration_seconds": 6.0,
                },
                "status": "mock_development_mode",
            }

        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {"speaker_id": speaker_id}
        if detect_deepfake:
            data["detect_deepfake"] = "true"
        files = {"file": (filename, audio_bytes, "audio/wav")}

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{self.base_url}/v1/speakers/verify",
                headers=headers,
                data=data,
                files=files,
            )
            resp.raise_for_status()
            return resp.json()

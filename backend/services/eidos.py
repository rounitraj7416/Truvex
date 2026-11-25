"""
DetectifAI Eidos Client — Voice Biometric Enrollment & Speaker Verification.
Owner: Anany
Official Docs: https://platform.detectif.ai/docs/speaker-verification/
"""

from datetime import datetime, timezone
import os
from typing import Any, Dict, Optional
import uuid
from dotenv import load_dotenv
import httpx

load_dotenv()


class EidosClient:
    """Client for DetectifAI Eidos speaker enrollment and verification endpoints."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("DETECTIF_API_KEY", "")
        self.base_url = (base_url or os.getenv("DETECTIF_BASE_URL", "https://platform.detectif.ai")).rstrip("/")
        fallback_env = os.getenv("DETECTIF_MOCK_FALLBACK", "True").lower()
        self.mock_fallback = fallback_env == "true" or not self.api_key or self.api_key.startswith("dtf_live_your_")

    def is_live_configured(self) -> bool:
        """Checks whether a valid live API key is configured."""
        return bool(self.api_key and not self.api_key.startswith("dtf_live_your_") and not self.mock_fallback)

    async def enroll_speaker(
        self,
        speaker_id: str,
        audio_bytes: bytes,
        display_name: Optional[str] = None,
        filename: str = "enroll.wav",
        content_type: str = "audio/wav",
    ) -> Dict[str, Any]:
        """
        Enrolls a voice sample with DetectifAI /v1/speakers/enroll.
        Length: 15 to 60 seconds (at least 10s speech).
        """
        if not self.is_live_configured():
            return {
                "request_id": f"req_sim_{uuid.uuid4().hex[:16]}",
                "operation_id": f"op_sim_{uuid.uuid4().hex[:24]}",
                "object": "speaker.enrollment",
                "speaker": {
                    "speaker_id": speaker_id,
                    "display_name": display_name or speaker_id,
                    "samples": 1,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
                "quality": {
                    "speech_seconds": 16.5,
                    "duration_seconds": 18.0,
                },
                "model": {
                    "name": "eidos",
                    "version": "1.0",
                },
                "is_live_api": False,
                "note": "Voice biometric profile enrolled in local biometric vault (mock mode).",
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Idempotency-Key": str(uuid.uuid4()),
        }
        data = {"speaker_id": speaker_id}
        if display_name:
            data["display_name"] = display_name
        files = {"file": (filename, audio_bytes, content_type)}

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{self.base_url}/v1/speakers/enroll",
                headers=headers,
                data=data,
                files=files,
            )
            if resp.status_code not in (200, 201):
                error_body = resp.json().get("error", {})
                return {
                    "error": True,
                    "status_code": resp.status_code,
                    "code": error_body.get("code", "api_error"),
                    "message": error_body.get("message", resp.text),
                    "is_live_api": True,
                }
            data_resp = resp.json()
            data_resp["is_live_api"] = True
            return data_resp

    async def verify_speaker(
        self,
        speaker_id: str,
        audio_bytes: bytes,
        detect_deepfake: bool = False,
        filename: str = "verify.wav",
        content_type: str = "audio/wav",
    ) -> Dict[str, Any]:
        """
        Verifies voice sample against enrolled speaker via DetectifAI /v1/speakers/verify.
        Length: 3 to 60 seconds (at least 2s speech).
        """
        if not self.is_live_configured():
            return {
                "request_id": f"req_sim_{uuid.uuid4().hex[:16]}",
                "operation_id": f"op_sim_{uuid.uuid4().hex[:24]}",
                "object": "speaker.verification",
                "speaker_id": speaker_id,
                "result": {
                    "decision": "match",
                    "similarity": 0.884,  # high similarity score
                    "duration_seconds": 5.4,
                },
                "is_live_api": False,
                "note": "Biometric match verified against enrolled acoustic embeddings (mock mode).",
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Idempotency-Key": str(uuid.uuid4()),
        }
        data = {"speaker_id": speaker_id}
        if detect_deepfake:
            data["detect_deepfake"] = "true"
        files = {"file": (filename, audio_bytes, content_type)}

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{self.base_url}/v1/speakers/verify",
                headers=headers,
                data=data,
                files=files,
            )
            if resp.status_code != 200:
                error_body = resp.json().get("error", {})
                return {
                    "error": True,
                    "status_code": resp.status_code,
                    "code": error_body.get("code", "api_error"),
                    "message": error_body.get("message", resp.text),
                    "is_live_api": True,
                }
            data_resp = resp.json()
            data_resp["is_live_api"] = True
            return data_resp

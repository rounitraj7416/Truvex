"""
TRUVEX Five-Layer Trust Engine.
Owner: Anany
Implements strict security boundaries where no average score can override
a failed mandatory security check (deepfake detected, speaker mismatch, unapproved company).
"""

from typing import Any, Dict


class TrustEngine:
    """Computes composite Trust Index (0-100%) across five verification boundaries."""

    WEIGHT_BUSINESS = 20.0
    WEIGHT_EMPLOYEE = 20.0
    WEIGHT_ALETHEIA = 20.0
    WEIGHT_EIDOS = 20.0
    WEIGHT_AUTHORITY = 20.0

    @classmethod
    def evaluate(
        cls,
        company_status: str,
        employee_status: str,
        can_initiate_calls: bool,
        aletheia_data: Dict[str, Any],
        eidos_data: Dict[str, Any],
        communication_category: str = "fraud_prevention",
    ) -> Dict[str, Any]:
        """
        Evaluates the five layers and enforces zero-tolerance hard security checks.
        """
        hard_failures = []

        # 1. Layer 1: Business Verification
        l1_passed = company_status == "approved"
        if not l1_passed:
            hard_failures.append("Company is not approved or is currently suspended.")
        l1_score = cls.WEIGHT_BUSINESS if l1_passed else 0.0

        # 2. Layer 2: Employee Identity Verification
        l2_passed = employee_status == "active"
        if not l2_passed:
            hard_failures.append("Employee status is inactive, suspended, or terminated.")
        l2_score = cls.WEIGHT_EMPLOYEE if l2_passed else 0.0

        # 3. Layer 3: Voice Authenticity (DetectifAI Aletheia)
        # Check for API error
        if aletheia_data.get("error"):
            verdict = "uncertain"
            aletheia_score = 0.5
            l3_passed = False
            hard_failures.append(f"Aletheia Deepfake API Error: {aletheia_data.get('message', 'Unknown error')}")
            l3_score = 0.0
        else:
            res_aletheia = aletheia_data.get("result", {})
            verdict = res_aletheia.get("verdict", "unknown")
            aletheia_score = float(res_aletheia.get("score", 0.05))  # 0=real, 1=fake
            l3_passed = verdict == "real" and aletheia_score < 0.35
            if not l3_passed:
                hard_failures.append(f"Potential synthetic / deepfake voice detected (verdict: {verdict}).")
            l3_score = cls.WEIGHT_ALETHEIA * max(0.0, 1.0 - aletheia_score) if l3_passed else 0.0

        # 4. Layer 4: Speaker Biometrics (DetectifAI Eidos)
        if eidos_data.get("error"):
            decision = "uncertain"
            similarity = 0.0
            l4_passed = False
            hard_failures.append(f"Eidos Biometrics API Error: {eidos_data.get('message', 'Unknown error')}")
            l4_score = 0.0
        else:
            res_eidos = eidos_data.get("result", {})
            decision = res_eidos.get("decision", "no_match")
            similarity = float(res_eidos.get("similarity", 0.0))  # -1.0 to 1.0
            l4_passed = decision == "match" and similarity > 0.45
            if not l4_passed:
                hard_failures.append("Speaker voiceprint does not match the enrolled employee biometric profile.")
            normalized_sim = max(0.0, min(1.0, (similarity + 1.0) / 2.0))
            l4_score = cls.WEIGHT_EIDOS * normalized_sim if l4_passed else 0.0

        # 5. Layer 5: Communication Authority & Session Context
        l5_passed = can_initiate_calls
        if not l5_passed:
            hard_failures.append("Employee lacks permission to initiate outbound customer calls.")
        l5_score = cls.WEIGHT_AUTHORITY if l5_passed else 0.0

        # Composite Score Calculation
        raw_total = l1_score + l2_score + l3_score + l4_score + l5_score

        # Rule: A failed mandatory security check CANNOT be averaged out!
        if hard_failures:
            verdict_str = "REJECTED"
            trust_score = min(raw_total, 45.0)  # Capped if any hard check fails
        elif raw_total >= 85.0:
            verdict_str = "VERIFIED"
            trust_score = raw_total
        elif raw_total >= 70.0:
            verdict_str = "MANUAL_REVIEW"
            trust_score = raw_total
        else:
            verdict_str = "REJECTED"
            trust_score = raw_total

        return {
            "trust_score": round(trust_score, 1),
            "verdict": verdict_str,
            "hard_failures": hard_failures,
            "layers": {
                "business": {
                    "passed": l1_passed,
                    "score": round(l1_score, 1),
                    "status": "APPROVED" if l1_passed else "UNAPPROVED",
                },
                "employee": {
                    "passed": l2_passed,
                    "score": round(l2_score, 1),
                    "status": "ACTIVE" if l2_passed else "INACTIVE",
                },
                "voice_authenticity": {
                    "passed": l3_passed,
                    "score": round(l3_score, 1),
                    "verdict": verdict,
                    "raw_score": aletheia_score,
                },
                "speaker_biometrics": {
                    "passed": l4_passed,
                    "score": round(l4_score, 1),
                    "decision": decision,
                    "similarity": similarity,
                },
                "authority": {
                    "passed": l5_passed,
                    "score": round(l5_score, 1),
                    "status": "AUTHORIZED" if l5_passed else "UNAUTHORIZED",
                },
            },
        }

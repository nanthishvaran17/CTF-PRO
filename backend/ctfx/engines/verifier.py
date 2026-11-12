import re
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional

class FlagStatus(str, Enum):
    DISCOVERED = "DISCOVERED"
    CANDIDATE = "CANDIDATE"
    EVIDENCE_SUPPORTED = "EVIDENCE-SUPPORTED"
    VALIDATION_PENDING = "VALIDATION-PENDING"
    VERIFIED_BY_CHALLENGE = "VERIFIED-BY-CHALLENGE"
    REJECTED = "REJECTED"
    UNRESOLVED = "UNRESOLVED"

DECOY_KEYWORDS = [
    "example", "sample", "dummy", "placeholder", "test_flag",
    "insert_flag_here", "flag_goes_here", "fake_flag", "demo",
    "your_flag_here", "flag{flag}", "template"
]

class CandidateVerifier:
    """Manages flag candidate validation lifecycle, decoy classification, and authoritative events."""

    @classmethod
    def evaluate_decoy_indicators(cls, flag_text: str, source_context: Optional[str] = None) -> Dict[str, Any]:
        """Inspect flag token and context for decoy/placeholder signals with explainable evidence reasons."""
        reasons: List[str] = []
        is_decoy = False
        lower_flag = flag_text.lower()

        for kw in DECOY_KEYWORDS:
            if kw in lower_flag:
                reasons.append(f"Flag contains known dummy/placeholder term '{kw}'")
                is_decoy = True

        if source_context:
            ctx_lower = source_context.lower()
            if any(term in ctx_lower for term in ["readme", "example", "usage:", "documentation"]):
                reasons.append("Discovered inside documentation or example text block")
                is_decoy = True

        # Check for trivial inner contents like FLAG{1234} or FLAG{a}
        inner_match = re.search(r"\{([^}]+)\}", flag_text)
        if inner_match:
            inner = inner_match.group(1).strip()
            if len(inner) < 3:
                reasons.append("Flag inner payload is suspiciously short (< 3 chars)")
                is_decoy = True
            if len(set(inner)) == 1:
                reasons.append("Flag inner payload consists of a single repeated character")
                is_decoy = True

        return {
            "is_probable_decoy": is_decoy,
            "reasons": reasons if reasons else ["No known decoy signals detected; appears authentic."]
        }

    @classmethod
    def create_candidate(
        cls,
        flag: str,
        source_file_id: Optional[str] = None,
        source_sha256: Optional[str] = None,
        byte_offset: Optional[int] = None,
        encoding: str = "utf-8",
        extraction_method: str = "direct_scan",
        transform_chain: Optional[List[Dict[str, Any]]] = None,
        source_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Construct an evidence-backed candidate in EVIDENCE-SUPPORTED or CANDIDATE state."""
        decoy_analysis = cls.evaluate_decoy_indicators(flag, source_context)
        
        # State begins as EVIDENCE-SUPPORTED if cryptographic provenance is present
        initial_status = FlagStatus.EVIDENCE_SUPPORTED if (source_sha256 and byte_offset is not None) else FlagStatus.CANDIDATE

        return {
            "flag": flag,
            "source_file_id": source_file_id,
            "source_sha256": source_sha256,
            "byte_offset": byte_offset,
            "encoding": encoding,
            "extraction_method": extraction_method,
            "transform_chain": transform_chain or [],
            "discovery_time": datetime.now(timezone.utc).isoformat(),
            "status": initial_status.value,
            "is_probable_decoy": decoy_analysis["is_probable_decoy"],
            "evidence_reasons": decoy_analysis["reasons"],
            "verification_events": []
        }

    @classmethod
    def record_validation_event(
        cls,
        candidate: Dict[str, Any],
        validator: str,
        is_success: bool,
        raw_response: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Record authoritative verification attempt (e.g. platform API submission or challenge organizer check)."""
        new_status = FlagStatus.VERIFIED_BY_CHALLENGE if is_success else FlagStatus.REJECTED
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "validator": validator,
            "result": "ACCEPTED" if is_success else "REJECTED",
            "new_status": new_status.value,
            "raw_response": raw_response,
            "notes": notes or ""
        }
        candidate["status"] = new_status.value
        candidate.setdefault("verification_events", []).append(event)
        return candidate

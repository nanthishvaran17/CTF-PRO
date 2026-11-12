from typing import Dict, Any, List, Optional
import httpx

class AIAdvisor:
    """Provides advisory hypotheses, clue explanations, and tool recommendations.
    Strictly isolated: All suggestions are labelled 'HYPOTHESIS' and never claim execution or fabricate flags."""

    @classmethod
    def generate_rule_based_hypothesis(
        cls,
        file_type: str,
        challenge_desc: str = "",
        discovered_findings: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Offline / AI-Off fallback generator providing deterministic, evidence-based hypotheses."""
        hypotheses = []
        suggested_decodes = []
        desc_lower = challenge_desc.lower()

        if file_type == "PNG":
            hypotheses.append("The PNG container may embed secret data within least-significant bits (LSB) or custom chunks.")
            suggested_decodes.extend(["Inspect chunk types", "Extract RGB LSB bit-plane", "Check for trailing bytes past IEND"])

        elif file_type in ("PCAP", "PCAPNG"):
            hypotheses.append("The network capture appears to record unencrypted TCP or HTTP sessions with transmitted flags or authorization tokens.")
            suggested_decodes.extend(["Reassemble TCP conversations", "Carve HTTP request payloads", "Filter for basic auth credentials"])

        elif file_type in ("ELF", "PE"):
            hypotheses.append("The executable binary likely contains hardcoded comparison strings or checks an algorithmic keygen.")
            suggested_decodes.extend(["Extract ASCII & UTF-16 strings", "Inspect imports and exported symbols", "Check for suspicious anti-analysis syscalls"])

        elif file_type == "ZIP":
            hypotheses.append("Archive may contain nested files, hidden directory structures, or comment payloads in Central Directory.")
            suggested_decodes.extend(["Safe recursive decompression", "Inspect ZIP file comments"])

        if any(term in desc_lower for term in ["caesar", "rot", "shift"]):
            hypotheses.append("Challenge title/description strongly suggests a rotation or Caesar shift cipher.")
            suggested_decodes.append("Execute 25-shift Caesar frequency analysis")

        if any(term in desc_lower for term in ["xor", "key"]):
            hypotheses.append("Challenge context hints at symmetric XOR obfuscation.")
            suggested_decodes.append("Run single-byte XOR brute force")

        return {
            "type": "HYPOTHESIS",
            "model": "Deterministic Rule-Based Advisor (AI-Offline)",
            "disclaimer": "This output represents an advisory hypothesis only. It does NOT claim execution or produce verified flags.",
            "hypotheses": hypotheses,
            "suggested_actions": suggested_decodes
        }

    @classmethod
    async def query_ollama_hypothesis(
        cls,
        prompt: str,
        ollama_endpoint: str = "http://localhost:11434/api/generate",
        model: str = "llama3"
    ) -> Dict[str, Any]:
        """Optional query to a local Ollama instance if configured."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    ollama_endpoint,
                    json={
                        "model": model,
                        "prompt": f"You are a CTF security tutor. Provide a brief analysis hypothesis for: {prompt}. Do not make up fake flags.",
                        "stream": False
                    }
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return {
                        "type": "HYPOTHESIS",
                        "model": f"Ollama ({model})",
                        "disclaimer": "AI Hypothesis - Not authoritative. Must be verified with real tools.",
                        "response": data.get("response", "")
                    }
        except Exception as e:
            pass

        return cls.generate_rule_based_hypothesis("UNKNOWN", prompt)

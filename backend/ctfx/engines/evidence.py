import json
from typing import List, Dict, Any, Optional

class EvidenceGraphBuilder:
    """Builds an interactive Directed Acyclic Graph (DAG) connecting files, extractions, decodes, and flags."""

    @classmethod
    def build_graph(
        cls,
        files: List[Dict[str, Any]],
        artifacts: List[Dict[str, Any]],
        candidates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        nodes = []
        edges = []

        # 1. File nodes
        for f in files:
            f_id = f.get("id") or f.get("sha256", "file_root")
            nodes.append({
                "id": f"file_{f_id}",
                "label": f.get("name") or f"File ({f_id[:8]})",
                "type": "file",
                "metadata": {
                    "sha256": f.get("sha256"),
                    "size": f.get("size_bytes"),
                    "file_type": f.get("file_type")
                }
            })

        # 2. Artifact nodes (extracted from archives or stego)
        for a in artifacts:
            a_id = a.get("id") or a.get("sha256", "art_node")
            nodes.append({
                "id": f"art_{a_id}",
                "label": a.get("name", "Extracted Artifact"),
                "type": "artifact",
                "metadata": a
            })
            if a.get("parent_id"):
                edges.append({
                    "from": f"file_{a['parent_id']}",
                    "to": f"art_{a_id}",
                    "label": a.get("extraction_method", "extracted")
                })

        # 3. Candidate & Transform nodes
        for c in candidates:
            c_id = c.get("id") or f"flag_{abs(hash(c.get('flag', '')))}"
            flag_node_id = f"flag_{c_id}"
            nodes.append({
                "id": flag_node_id,
                "label": c.get("flag", "FLAG"),
                "type": "candidate",
                "status": c.get("status", "CANDIDATE"),
                "metadata": {
                    "offset": c.get("byte_offset"),
                    "status": c.get("status"),
                    "source_sha256": c.get("source_sha256")
                }
            })

            # Check transforms
            transforms = c.get("transform_chain") or []
            last_parent_id = f"file_{c.get('source_file_id') or c.get('source_sha256', 'file_root')}"
            
            for idx, step in enumerate(transforms):
                t_node_id = f"step_{c_id}_{idx}"
                nodes.append({
                    "id": t_node_id,
                    "label": f"{step.get('method', 'decode')} (step {step.get('step', idx+1)})",
                    "type": "transform",
                    "metadata": step
                })
                edges.append({
                    "from": last_parent_id,
                    "to": t_node_id,
                    "label": step.get("method", "decode")
                })
                last_parent_id = t_node_id

            edges.append({
                "from": last_parent_id,
                "to": flag_node_id,
                "label": c.get("extraction_method", "discovered")
            })

        return {"nodes": nodes, "edges": edges}


class ReproduceScriptGenerator:
    """Generates standalone Python and Shell reproduction scripts for verified flag discoveries."""

    @classmethod
    def generate_python_script(cls, candidate: Dict[str, Any], file_meta: Optional[Dict[str, Any]] = None) -> str:
        chain = candidate.get("transform_chain", [])
        flag = candidate.get("flag", "")
        offset = candidate.get("byte_offset")
        method = candidate.get("extraction_method", "scan")
        sha256 = candidate.get("source_sha256", "unknown")

        lines = [
            "# CTF HUNTER X - Automated Reproduction Script",
            f"# Target Flag: {flag}",
            f"# Source SHA-256: {sha256}",
            f"# Byte Offset: {offset}",
            "import base64, codecs, html, urllib.parse",
            "",
            "def reproduce():",
            f"    # Provenance Method: {method}"
        ]

        if not chain:
            if offset is not None:
                lines.extend([
                    "    with open('target_file', 'rb') as f:",
                    f"        f.seek({offset})",
                    f"        data = f.read({len(flag)})",
                    f"        print('Extracted:', data.decode('utf-8', errors='replace'))"
                ])
            else:
                lines.append(f"    print('Direct Flag found: {flag}')")
        else:
            lines.append("    # Multi-layer decode pipeline:")
            first = chain[0].get("input_preview", "")
            lines.append(f"    current = {repr(first)}")
            for step in chain:
                m = step.get("method", "")
                if m == "base64":
                    lines.append("    current = base64.b64decode(current).decode('utf-8')")
                elif m == "hex":
                    lines.append("    current = bytes.fromhex(current).decode('utf-8')")
                elif m == "rot13":
                    lines.append("    current = codecs.decode(current, 'rot_13')")
                elif m == "url":
                    lines.append("    current = urllib.parse.unquote(current)")
                elif m == "html":
                    lines.append("    current = html.unescape(current)")
                elif m.startswith("xor_key_0x"):
                    key = int(m.split("0x")[1], 16)
                    lines.append(f"    current = bytes(b ^ {key} for b in bytes.fromhex(current)).decode('utf-8')")

            lines.append("    print('Reproduced result:', current)")

        lines.extend(["", "if __name__ == '__main__':", "    reproduce()"])
        return "\n".join(lines)


class AutoWriteupGenerator:
    """Generates comprehensive CTF writeup in GitHub Flavored Markdown from actual evidence chains."""

    @classmethod
    def generate_markdown(
        cls,
        challenge_name: str,
        files: List[Dict[str, Any]],
        candidates: List[Dict[str, Any]],
        notes: str = ""
    ) -> str:
        lines = [
            f"# CTF Writeup: {challenge_name}",
            "",
            "> **Generated by CTF HUNTER X - Evidence-based Analysis Workstation**",
            "",
            "## 1. Challenge Overview & Artifacts",
            ""
        ]

        for f in files:
            lines.extend([
                f"- **Filename**: `{f.get('name', 'file')}`",
                f"  - **SHA-256**: `{f.get('sha256')}`",
                f"  - **Size**: {f.get('size_bytes', 0):,} bytes",
                f"  - **Detected True Type**: `{f.get('file_type')}` ({f.get('type_description', '')})",
                f"  - **Entropy**: {f.get('entropy', 'N/A')}",
                ""
            ])

        lines.extend([
            "## 2. Evidence Chains & Flag Findings",
            ""
        ])

        if not candidates:
            lines.append("*No flag candidates discovered yet.*")
        else:
            for idx, c in enumerate(candidates, 1):
                lines.extend([
                    f"### Finding #{idx}: `{c.get('flag')}`",
                    f"- **Status**: `{c.get('status')}`",
                    f"- **Source File Hash**: `{c.get('source_sha256')}`",
                    f"- **Byte Offset**: `{c.get('byte_offset')}`",
                    f"- **Extraction Method**: `{c.get('extraction_method')}`",
                    f"- **Probable Decoy**: `{c.get('is_probable_decoy', False)}`",
                    f"- **Evaluation Reasons**: {', '.join(c.get('evidence_reasons', []))}",
                    ""
                ])

                chain = c.get("transform_chain") or []
                if chain:
                    lines.append("#### Decoding Pipeline:")
                    for s in chain:
                        lines.append(f"1. **Step {s.get('step')}** (`{s.get('method')}`): `{s.get('output_preview')}`")
                    lines.append("")

        if notes:
            lines.extend([
                "## 3. Analyst Notes",
                "",
                notes,
                ""
            ])

        lines.extend([
            "## 4. Platform Verification Status",
            "",
            "Flags marked `VERIFIED-BY-CHALLENGE` have been independently validated against the target scoreboard/organizer oracle.",
            ""
        ])

        return "\n".join(lines)


class SmartTriageEngine:
    """Recommends actionable, evidence-based next analysis steps based on file signature & metadata."""

    @classmethod
    def recommend_next_steps(cls, file_info: Dict[str, Any], challenge_desc: str = "") -> List[Dict[str, Any]]:
        steps = []
        ftype = file_info.get("file_type", "BINARY")
        entropy = file_info.get("entropy", 0.0)
        trailing = file_info.get("trailing_anomaly")
        desc_lower = challenge_desc.lower()

        if ftype == "PNG":
            steps.append({
                "action": "Steganographic Bit-Plane & LSB Extraction",
                "priority": "HIGH",
                "reason": "PNG images frequently conceal flags in Least Significant Bits (LSB) or custom chunks."
            })
            if trailing and trailing.get("has_trailing_bytes"):
                steps.append({
                    "action": "Extract Appended Trailing Bytes",
                    "priority": "CRITICAL",
                    "reason": f"Discovered {trailing.get('trailing_byte_count')} bytes beyond PNG IEND marker."
                })

        elif ftype in ("PCAP", "PCAPNG"):
            steps.append({
                "action": "TCP Stream Reassembly & Credential Hunting",
                "priority": "HIGH",
                "reason": "Network packet captures typically contain unencrypted HTTP, DNS, or credentials in TCP payloads."
            })

        elif ftype in ("ELF", "PE", "MACHO_64", "MACHO_32"):
            steps.append({
                "action": "Static Binary Reverse Engineering & Symbol Inspection",
                "priority": "HIGH",
                "reason": "Compiled executable identified. Inspect strings, imported library functions, and entrypoint."
            })

        elif ftype in ("ZIP", "TAR", "GZIP", "7Z"):
            steps.append({
                "action": "Safe Recursive Archive Decompression",
                "priority": "HIGH",
                "reason": "Archive container identified. Unpack entries while enforcing zip-slip defenses."
            })

        if entropy > 7.5:
            steps.append({
                "action": "High-Entropy Cryptanalysis & Compression Scan",
                "priority": "MEDIUM",
                "reason": f"Entropy is {entropy}/8.0, indicating heavy encryption or raw compressed payload."
            })

        if any(term in desc_lower for term in ["rot", "caesar", "shift", "cipher", "secret"]):
            steps.append({
                "action": "Caesar / ROT / Substitution Cipher Suite",
                "priority": "HIGH",
                "reason": "Challenge description hints at classic or substitution cryptography."
            })

        return steps

import base64
import re
import struct
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict
from ..engines.flag_finder import FlagFinder

class ForensicsAnalyzer:
    """Network packet capture (PCAP/PCAPNG) and system log analysis engine."""

    @classmethod
    def analyze_pcap(cls, file_path: Path, max_packets: int = 5000) -> Dict[str, Any]:
        """Analyze PCAP capture: extract protocols, reassemble TCP streams, carve credentials and flags."""
        packets_summary = []
        protocols_count = defaultdict(int)
        tcp_streams = defaultdict(bytearray)
        credentials = []
        http_conversations = []
        flag_finder = FlagFinder()
        discovered_flags = []

        # Check scapy availability
        use_scapy = False
        try:
            from scapy.all import rdpcap, TCP, UDP, IP, Raw, DNS
            use_scapy = True
        except ImportError:
            use_scapy = False

        if use_scapy:
            try:
                packets = rdpcap(str(file_path), count=max_packets)
                for idx, pkt in enumerate(packets):
                    summary_entry = {
                        "packet_id": idx + 1,
                        "time": float(pkt.time),
                        "length": len(pkt),
                        "protocol": "OTHER"
                    }

                    if IP in pkt:
                        src_ip = pkt[IP].src
                        dst_ip = pkt[IP].dst
                        summary_entry["src"] = src_ip
                        summary_entry["dst"] = dst_ip

                        if TCP in pkt:
                            sport = pkt[TCP].sport
                            dport = pkt[TCP].dport
                            summary_entry["protocol"] = "TCP"
                            summary_entry["sport"] = sport
                            summary_entry["dport"] = dport
                            protocols_count["TCP"] += 1

                            stream_key = tuple(sorted([(src_ip, sport), (dst_ip, dport)]))
                            if Raw in pkt:
                                payload = bytes(pkt[Raw].load)
                                tcp_streams[stream_key].extend(payload)

                        elif UDP in pkt:
                            sport = pkt[UDP].sport
                            dport = pkt[UDP].dport
                            summary_entry["protocol"] = "UDP"
                            summary_entry["sport"] = sport
                            summary_entry["dport"] = dport
                            protocols_count["UDP"] += 1

                            if DNS in pkt:
                                protocols_count["DNS"] += 1
                                summary_entry["protocol"] = "DNS"
                    else:
                        protocols_count["NON_IP"] += 1

                    if len(packets_summary) < 200:
                        packets_summary.append(summary_entry)
            except Exception as e:
                return {"is_pcap": False, "error": f"Scapy parse error: {str(e)}"}
        else:
            # Pure Python fallback PCAP parser
            try:
                with open(file_path, "rb") as f:
                    magic = f.read(4)
                    if magic not in (b"\xd4\xc3\xb2\xa1", b"\xa1\xb2\xc3\xd4", b"\x4d\x3c\xb2\xa1", b"\xa1\xb2\x3c\x4d"):
                        return {"is_pcap": False, "error": "Not a recognized standard PCAP format"}
                    
                    is_little = magic in (b"\xd4\xc3\xb2\xa1", b"\x4d\x3c\xb2\xa1")
                    endian = "<" if is_little else ">"
                    
                    # Read rest of 24-byte file header
                    f.read(20)
                    pkt_id = 0

                    while pkt_id < max_packets:
                        hdr = f.read(16)
                        if len(hdr) < 16:
                            break
                        ts_sec, ts_usec, incl_len, orig_len = struct.unpack(f"{endian}IIII", hdr)
                        pkt_data = f.read(incl_len)
                        if len(pkt_data) < incl_len:
                            break

                        pkt_id += 1
                        protocols_count["PACKETS"] += 1
                        # Ethernet header is 14 bytes
                        if len(pkt_data) > 14:
                            eth_type = struct.unpack(">H", pkt_data[12:14])[0]
                            if eth_type == 0x0800:  # IPv4
                                ip_data = pkt_data[14:]
                                if len(ip_data) >= 20:
                                    ip_proto = ip_data[9]
                                    src_ip = ".".join(str(b) for b in ip_data[12:16])
                                    dst_ip = ".".join(str(b) for b in ip_data[16:20])
                                    
                                    ihl = (ip_data[0] & 0x0F) * 4
                                    transport_data = ip_data[ihl:]

                                    if ip_proto == 6 and len(transport_data) >= 20:  # TCP
                                        sport, dport = struct.unpack(">HH", transport_data[:4])
                                        protocols_count["TCP"] += 1
                                        tcp_offset = ((transport_data[12] >> 4) & 0x0F) * 4
                                        payload = transport_data[tcp_offset:]
                                        if payload:
                                            stream_key = tuple(sorted([(src_ip, sport), (dst_ip, dport)]))
                                            tcp_streams[stream_key].extend(payload)
                                    elif ip_proto == 17:  # UDP
                                        protocols_count["UDP"] += 1

                        if len(packets_summary) < 200:
                            packets_summary.append({
                                "packet_id": pkt_id,
                                "time": ts_sec + ts_usec / 1e6,
                                "length": incl_len,
                                "protocol": "TCP" if protocols_count["TCP"] > 0 else "IP"
                            })
            except Exception as e:
                return {"is_pcap": False, "error": f"Fallback PCAP parse error: {str(e)}"}

        # Inspect reassembled TCP streams for flags, HTTP, and credentials
        streams_summary = []
        for (ep1, ep2), stream_data in tcp_streams.items():
            stream_flags = flag_finder.scan_binary(bytes(stream_data), source_file=f"stream_{ep1[0]}:{ep1[1]}-{ep2[0]}:{ep2[1]}")
            discovered_flags.extend(stream_flags)

            text_preview = stream_data.decode("latin1", errors="replace")

            # Look for HTTP request
            if "HTTP/" in text_preview:
                protocols_count["HTTP"] += 1
                lines = text_preview.split("\r\n")
                if len(lines) > 0 and any(m in lines[0] for m in ["GET", "POST", "PUT", "DELETE", "HTTP/"]):
                    http_conversations.append({
                        "endpoint": f"{ep1[0]}:{ep1[1]} <-> {ep2[0]}:{ep2[1]}",
                        "first_line": lines[0][:120],
                        "bytes": len(stream_data)
                    })

            # Check for HTTP Basic Auth
            for line in text_preview.split("\r\n"):
                if "Authorization: Basic " in line:
                    b64_creds = line.split("Authorization: Basic ")[1].strip()
                    try:
                        decoded = base64.b64decode(b64_creds).decode("utf-8", errors="replace")
                        credentials.append({
                            "type": "HTTP_BASIC_AUTH",
                            "raw": line,
                            "credentials": decoded
                        })
                    except Exception:
                        pass
                elif line.startswith("USER ") or line.startswith("PASS "):
                    credentials.append({
                        "type": "FTP/SMTP_PLAINTEXT",
                        "credentials": line.strip()
                    })

            if len(streams_summary) < 50:
                streams_summary.append({
                    "endpoints": f"{ep1[0]}:{ep1[1]} <-> {ep2[0]}:{ep2[1]}",
                    "total_bytes": len(stream_data),
                    "flags_count": len(stream_flags),
                    "snippet": text_preview[:100]
                })

        return {
            "is_pcap": True,
            "packets_inspected": len(packets_summary),
            "protocols": dict(protocols_count),
            "tcp_streams_count": len(tcp_streams),
            "tcp_streams": streams_summary,
            "http_conversations": http_conversations[:25],
            "credentials_found": credentials,
            "flags_discovered": discovered_flags,
            "packets_sample": packets_summary[:50]
        }

    @classmethod
    def analyze_logs(cls, file_path: Path) -> Dict[str, Any]:
        """Parse server or authentication logs, normalize timestamps, and surface suspicious events & flags."""
        entries = []
        suspicious_events = []
        flag_finder = FlagFinder()
        discovered_flags = []

        attack_patterns = [
            (re.compile(r"(union\s+select|select\s+.*\s+from)", re.IGNORECASE), "SQL Injection (SQLi) attempt"),
            (re.compile(r"(\.\./|\.\.\\)", re.IGNORECASE), "Path Traversal (Directory Traversal) attempt"),
            (re.compile(r"(<script|alert\(|onerror=)", re.IGNORECASE), "Cross-Site Scripting (XSS) probe"),
            (re.compile(r"(;\s*(?:id|whoami|cat\s+/etc/passwd|bash|nc\s+))", re.IGNORECASE), "Remote Command Injection attempt"),
            (re.compile(r"(401\s+|403\s+|500\s+)", re.IGNORECASE), "Failed HTTP Authentication / Server Error"),
        ]

        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            for line_no, raw_line in enumerate(f, 1):
                line = raw_line.strip()
                if not line:
                    continue

                # Check for flags in line
                flags = flag_finder.scan_text(line, source_context={"line": line_no})
                discovered_flags.extend(flags)

                # Check attack patterns
                for pat, label in attack_patterns:
                    if pat.search(line):
                        suspicious_events.append({
                            "line_number": line_no,
                            "type": label,
                            "snippet": line[:150]
                        })
                        break

                if len(entries) < 100:
                    entries.append({
                        "line": line_no,
                        "text": line[:120]
                    })

        return {
            "total_lines_analyzed": line_no if 'line_no' in locals() else 0,
            "suspicious_events_count": len(suspicious_events),
            "suspicious_events": suspicious_events[:50],
            "flags_discovered": discovered_flags,
            "sample_entries": entries[:25]
        }

import ipaddress
import re
import socket
import urllib.parse
from typing import Dict, Any, List, Optional

class SSRFProtectionError(Exception):
    """Raised when an address resolves to a local, private, or metadata IP address."""
    pass

class WebAnalyzer:
    """Safe, SSRF-protected web resource and client-side code analysis engine."""

    DISALLOWED_NETWORKS = [
        ipaddress.ip_network("127.0.0.0/8"),      # Loopback
        ipaddress.ip_network("10.0.0.0/8"),       # Private RFC 1918
        ipaddress.ip_network("172.16.0.0/12"),    # Private RFC 1918
        ipaddress.ip_network("192.168.0.0/16"),   # Private RFC 1918
        ipaddress.ip_network("169.254.0.0/16"),   # Link-Local / Cloud Metadata
        ipaddress.ip_network("::1/128"),          # IPv6 Loopback
        ipaddress.ip_network("fc00::/7"),         # IPv6 Unique Local
        ipaddress.ip_network("fe80::/10"),        # IPv6 Link-Local
    ]

    @classmethod
    def validate_url_safe(cls, url: str) -> str:
        """Validate that the URL uses HTTP/HTTPS and resolves exclusively to a public routable IP."""
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise SSRFProtectionError(f"Prohibited protocol scheme: '{parsed.scheme}'. Only HTTP and HTTPS are permitted.")

        hostname = parsed.hostname
        if not hostname:
            raise SSRFProtectionError("Invalid URL: missing hostname")

        # Resolve DNS
        try:
            addr_info = socket.getaddrinfo(hostname, None)
            ips = [item[4][0] for item in addr_info]
        except socket.gaierror as e:
            raise SSRFProtectionError(f"DNS resolution failed for hostname '{hostname}': {str(e)}")

        for ip_str in ips:
            ip = ipaddress.ip_address(ip_str)
            if ip.is_loopback or ip.is_private or ip.is_link_local or ip.is_reserved or ip.is_multicast:
                raise SSRFProtectionError(
                    f"SSRF Protection Blocked: Host '{hostname}' resolves to private/restricted IP '{ip_str}'"
                )
            for net in cls.DISALLOWED_NETWORKS:
                if ip in net:
                    raise SSRFProtectionError(
                        f"SSRF Protection Blocked: IP '{ip_str}' falls within disallowed subnet {net}"
                    )

        return url

    @classmethod
    def inspect_html(cls, html_content: str) -> Dict[str, Any]:
        """Statically inspect HTML for comments, hidden fields, endpoints, and flags."""
        comments = re.findall(r"<!--(.*?)-->", html_content, re.DOTALL)
        hidden_inputs = re.findall(r"<input[^>]+type=[\"']hidden[\"'][^>]*>", html_content, re.IGNORECASE)
        scripts = re.findall(r"<script[^>]+src=[\"']([^\"']+)[\"']", html_content, re.IGNORECASE)

        from ..engines.flag_finder import FlagFinder
        finder = FlagFinder()
        flags = finder.scan_text(html_content)

        return {
            "total_bytes": len(html_content),
            "html_comments": [c.strip() for c in comments if c.strip()][:25],
            "hidden_input_fields": hidden_inputs[:25],
            "script_references": scripts[:25],
            "flags_found": [f["flag"] for f in flags]
        }

    @classmethod
    def inspect_javascript(cls, js_code: str) -> Dict[str, Any]:
        """Perform static analysis on JavaScript code for endpoints, API keys, JWTs, and flags."""
        endpoints = re.findall(r"[\"'](/(?:api|v[0-9]+|auth|user|admin|flag)/[a-zA-Z0-9_\-\./]*)[\"']", js_code)
        # JWT pattern: eyJ...
        jwts = re.findall(r"\beyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\b", js_code)
        # Generic API keys or tokens
        api_keys = re.findall(r"(?:api_key|apiKey|secret|token|auth_token)\s*[:=]\s*[\"']([a-zA-Z0-9_\-]{16,64})[\"']", js_code, re.IGNORECASE)
        # Source map references
        source_maps = re.findall(r"//#\s*sourceMappingURL=([^\s]+)", js_code)

        from ..engines.flag_finder import FlagFinder
        finder = FlagFinder()
        flags = finder.scan_text(js_code)

        return {
            "total_lines": js_code.count("\n") + 1,
            "discovered_endpoints": list(set(endpoints))[:30],
            "discovered_jwts": list(set(jwts))[:10],
            "potential_api_keys": list(set(api_keys))[:10],
            "source_map_references": source_maps,
            "flags_found": [f["flag"] for f in flags]
        }

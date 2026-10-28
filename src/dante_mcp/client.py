# manifest_hash: 573c978f422e5c379830c2736505b260b93186f28715b081388ec45acccfd1ac
"""
src/dante_mcp/client.py
Dante IX — Official Model Context Protocol (MCP) Connector (`dante-mcp` v2.1.0).
Provides a zero-dependency STDIO-to-HTTPS JSON-RPC 2.0 client connecting
Claude Desktop, Cursor, Windsurf, and Google Antigravity to `https://danteix.com/api/mcp/invoke`.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, Callable, Dict, List, Optional
import urllib.error
import urllib.request

MCP_EDGE_V1_MANIFEST_HASH = "682d6526f8ca2cb93de4ebf5da6b2d6c3b5999de287bbf5d95e70739b96bca5e"
MCP_PRIVACY_SHIELD_V1_MANIFEST_HASH = "a2ba6fd338a8e531b28bbb35480a72ab5a6bdc24ae7187deeb9f3cfd7df0b730"
MCP_CLEANROOM_RELEASE_V1_MANIFEST_HASH = "573c978f422e5c379830c2736505b260b93186f28715b081388ec45acccfd1ac"
DEFAULT_GATEWAY_URL = "https://danteix.com/api/mcp/invoke"

MCP_TOOLS_SCHEMA: List[Dict[str, Any]] = [
    {
        "name": "dante.run_audit",
        "description": (
            "Execute a 9-Circle Dante IX Brand, Reputation & Multi-Model GEO Audit "
            "(ChatGPT, Gemini, Perplexity) with cryptographic SHA-256 attestation on danteix.com."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "target_name": {"type": "string", "description": "Brand, product, or organization name"},
                "industry_or_context": {"type": "string", "description": "Industry vertical and market context"},
                "vertical_mode": {
                    "type": "string",
                    "description": "Vertical mode: 'COMMERCIAL_BRAND', 'INTERNAL_PROJECT', or 'POLITICAL_WAR_ROOM'",
                    "default": "COMMERCIAL_BRAND",
                },
                "live_geo": {"type": "boolean", "default": False, "description": "Run live multi-model queries (requires paid DANTE_API_KEY)"},
                "lang": {"type": "string", "default": "es", "description": "Output language: 'es' or 'en'"},
            },
            "required": ["target_name", "industry_or_context"],
        },
    },
    {
        "name": "dante.probe_geo_share",
        "description": (
            "Measure Generative Engine Optimization (GEO) Share of Model (SoM) and First-Choice Win Rate "
            "across OpenAI (ChatGPT), Google Gemini, and Perplexity."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "target_name": {"type": "string", "description": "Brand or entity to evaluate across AI engines"},
                "industry_or_context": {"type": "string", "description": "Industry category or competitive niche"},
                "vertical_mode": {"type": "string", "default": "COMMERCIAL_BRAND"},
                "live": {"type": "boolean", "default": False, "description": "Execute live API queries (requires paid DANTE_API_KEY)"},
                "lang": {"type": "string", "default": "es"},
            },
            "required": ["target_name", "industry_or_context"],
        },
    },
    {
        "name": "dante.query_street_friction",
        "description": (
            "Search your isolated tenant intelligence vault for real customer complaints, "
            "irony/sarcasm signals, coordinated bot anomalies, and competitive market gaps."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search keywords (e.g. 'precios OR demoras OR soporte')"},
                "limit": {"type": "integer", "default": 10, "description": "Maximum records to return (1 to 100)"},
                "voice_filter": {"type": "string", "default": "ALL"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "dante.forge_geo_shield",
        "description": (
            "Synthesize production-ready /llms.txt, /.well-known/ai-catalog.json, "
            "Schema.org JSON-LD, and robots.txt rules for AI crawlers."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_name": {"type": "string", "description": "Official brand name (2..80 chars)"},
                "domain_url": {"type": "string", "description": "Canonical website URL (https://...)"},
                "industry_context": {"type": "string", "description": "Industry category and positioning"},
                "products_or_services": {"type": "array", "items": {"type": "string"}},
                "official_facts": {"type": "array", "items": {"type": "string"}},
                "competitors": {"type": "array", "items": {"type": "string"}},
                "lang": {"type": "string", "default": "es"},
            },
            "required": ["brand_name", "domain_url", "industry_context", "products_or_services", "official_facts"],
        },
    },
    {
        "name": "dante.remediate_hallucination",
        "description": (
            "Generate structured semantic counterweight blocks (Markdown + HTML ClaimReview), "
            "FAQPage JSON-LD, and verification prompts to remediate inaccurate AI claims."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_name": {"type": "string"},
                "domain_url": {"type": "string"},
                "target_oracle": {"type": "string", "description": "Target AI engine (ChatGPT, Perplexity, Gemini)"},
                "hallucination_claim": {"type": "string"},
                "verified_fact": {"type": "string"},
                "source_url_to_counter": {"type": "string"},
                "lang": {"type": "string", "default": "es"},
            },
            "required": ["brand_name", "domain_url", "target_oracle", "hallucination_claim", "verified_fact"],
        },
    },
]


class DanteMcpThinClient:
    """Pure stdlib JSON-RPC 2.0 Thin Client to `https://danteix.com/api/mcp/invoke`."""

    def __init__(
        self,
        gateway_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout_seconds: int = 30,
        transport_fn: Optional[Callable[[Dict[str, Any], Dict[str, str], int], Dict[str, Any]]] = None,
    ) -> None:
        env_endpoint = os.getenv("DANTE_MCP_ENDPOINT", DEFAULT_GATEWAY_URL)
        env_timeout = os.getenv("DANTE_MCP_TIMEOUT_SEC", str(timeout_seconds))
        self.gateway_url = (gateway_url or env_endpoint or DEFAULT_GATEWAY_URL).strip()
        self.api_key = (api_key if api_key is not None else os.getenv("DANTE_API_KEY", "")).strip()
        self.timeout_seconds = max(5, min(60, int(env_timeout)))
        self._transport_fn = transport_fn

    def _post_remote(self, rpc_req: Dict[str, Any]) -> Dict[str, Any]:
        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "dante-mcp-thin-client/2.1.0",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        if self._transport_fn is not None:
            return self._transport_fn(rpc_req, headers, self.timeout_seconds)

        data_bytes = json.dumps(rpc_req, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(self.gateway_url, data=data_bytes, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=float(self.timeout_seconds)) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                return json.loads(raw)
        except urllib.error.HTTPError as http_err:
            err_body = http_err.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(err_body)
                if isinstance(parsed, dict) and "jsonrpc" in parsed:
                    return parsed
            except Exception:
                pass
            return {
                "jsonrpc": "2.0",
                "id": rpc_req.get("id"),
                "error": {
                    "code": -32002,
                    "message": f"HTTP {http_err.code} from Dante IX Cloud Gateway",
                },
            }
        except Exception as exc:
            return {
                "jsonrpc": "2.0",
                "id": rpc_req.get("id"),
                "error": {
                    "code": -32002,
                    "message": f"TRANSIENT_UPSTREAM_FAULT: Unable to reach {self.gateway_url} ({exc})",
                },
            }

    def handle_request_dict(self, req: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        req_id = req.get("id")
        method = str(req.get("method") or "").strip()

        if req_id is None and method.startswith("notifications/"):
            return None

        if req.get("jsonrpc") != "2.0" or not method:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32600, "message": "Invalid Request: jsonrpc='2.0' and method required."},
            }

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {
                        "name": "dante-mcp",
                        "version": "2.1.0",
                        "manifest_hash": MCP_EDGE_V1_MANIFEST_HASH,
                    },
                    "capabilities": {"tools": {"listChanged": False}},
                },
            }

        if method == "ping":
            return {"jsonrpc": "2.0", "id": req_id, "result": {}}

        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": MCP_TOOLS_SCHEMA},
            }

        if method == "tools/call":
            return self._post_remote(req)

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }

    def handle_line(self, raw_line: str) -> Optional[str]:
        stripped = (raw_line or "").strip()
        if not stripped:
            return None
        try:
            req = json.loads(stripped)
        except Exception as exc:
            return json.dumps(
                {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": f"Parse error: {exc}"}},
                ensure_ascii=False,
            )
        if not isinstance(req, dict):
            return json.dumps(
                {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Invalid Request object."}},
                ensure_ascii=False,
            )
        resp = self.handle_request_dict(req)
        if resp is None:
            return None
        return json.dumps(resp, ensure_ascii=False)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    client = DanteMcpThinClient()
    for raw_line in sys.stdin:
        out_line = client.handle_line(raw_line)
        if out_line is not None:
            sys.stdout.write(out_line + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()

# manifest_hash: 573c978f422e5c379830c2736505b260b93186f28715b081388ec45acccfd1ac
# glama_tdqs_v1_manifest_hash: 8cb223f84cb8937ba078a4b03436c981092a1eaeadbd44b71142f3750c672b63
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
MCP_GLAMA_TDQS_V1_MANIFEST_HASH = "8cb223f84cb8937ba078a4b03436c981092a1eaeadbd44b71142f3750c672b63"
DEFAULT_GATEWAY_URL = "https://danteix.com/api/mcp/invoke"

MCP_TOOLS_SCHEMA: List[Dict[str, Any]] = [
    {
        "name": "dante.run_audit",
        "title": "Run Full Brand Reputation & Multi-Model GEO Audit",
        "description": (
            "Execute a comprehensive 9-dimension brand reputation, social sentiment, and Generative Engine Optimization (GEO) "
            "audit across ChatGPT, Google Gemini, and Perplexity. "
            "Returns a structured JSON report (`audit_id`, `fsm_state`, `som_score`, `win_rate`, `own_voice_count`, "
            "`ally_adversary_count`, `sector_street_count`, `recalibrated_count`, `suspected_bot_count`, and cryptographic SHA-256 attestation). "
            "Side effects & latency: Non-destructive; persists an isolated audit snapshot in the caller's tenant vault so subsequent calls to "
            "`dante.query_street_friction` can search the indexed signals. Completes in <1s when `live_geo=false` (deterministic baseline) or 5-15s "
            "when `live_geo=true` (live multi-LLM network queries). "
            "Auth & quota: If `DANTE_API_KEY` is omitted, runs in free 30% preview mode at $0 cost (`live_geo` is forced to `false`). "
            "With a paid `dnt_live_` key (`PRO_INHOUSE` 25/mo or `AGENCY_PARTNER` 100/mo), returns 100% unredacted results and consumes 1 monthly quota unit when `live_geo=true`. "
            "When to use: Use `dante.run_audit` for a complete end-to-end diagnostic combining social sentiment, bot detection, and AI search share. "
            "Use `dante.probe_geo_share` instead when you only need a fast AI citation Share-of-Model check without social listening, or "
            "`dante.forge_geo_shield` when you already know your brand facts and want to generate `/llms.txt` and `Schema.org JSON-LD`."
        ),
        "annotations": {
            "title": "Run Full Brand & GEO Audit",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "target_name": {
                    "type": "string",
                    "minLength": 2,
                    "maxLength": 120,
                    "description": "Brand, product, organization, or public figure name to audit (2 to 120 characters, e.g. 'Stripe' or 'Mayo Clinic').",
                },
                "industry_or_context": {
                    "type": "string",
                    "minLength": 3,
                    "maxLength": 240,
                    "description": "Industry vertical, competitive niche, and geographic market context (3 to 240 characters, e.g. 'B2B payment processing in North America').",
                },
                "vertical_mode": {
                    "type": "string",
                    "enum": ["COMMERCIAL_BRAND", "INTERNAL_PROJECT", "POLITICAL_WAR_ROOM"],
                    "default": "COMMERCIAL_BRAND",
                    "description": "Evaluation rubric mode: 'COMMERCIAL_BRAND' for B2B/B2C companies, 'INTERNAL_PROJECT' for software/product launches, or 'POLITICAL_WAR_ROOM' for public figures and civic campaigns.",
                },
                "live_geo": {
                    "type": "boolean",
                    "default": False,
                    "description": "Set to true to execute live network queries against ChatGPT, Gemini, and Perplexity (takes 5-15s and requires a paid DANTE_API_KEY; defaults to false for <1s deterministic baseline).",
                },
                "lang": {
                    "type": "string",
                    "enum": ["es", "en"],
                    "default": "es",
                    "description": "Report and prompt language code: 'en' for English or 'es' for Spanish (defaults to 'es').",
                },
            },
            "required": ["target_name", "industry_or_context"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "audit_id": {"type": "string", "description": "Unique audit identifier (e.g. AUD-...)."},
                "fsm_state": {"type": "string", "description": "Terminal execution state of the audit pipeline."},
                "target_name": {"type": "string", "description": "Audited brand or entity name."},
                "som_score": {"type": "string", "description": "Fixed-point Share of Model score in [0.0000, 1.0000]."},
                "win_rate": {"type": "string", "description": "First-choice recommendation win rate across queried AI models."},
                "tier_mode": {"type": "string", "description": "Active license tier ('FREE_TRIAL_30PCT_PREVIEW', 'PRO_INHOUSE', or 'AGENCY_PARTNER')."},
            },
        },
    },
    {
        "name": "dante.probe_geo_share",
        "title": "Probe AI Search Share of Model (GEO)",
        "description": (
            "Measure Generative Engine Optimization (GEO) Share of Model (SoM) and First-Choice Win Rate for a brand across "
            "OpenAI (ChatGPT), Google Gemini, and Perplexity. "
            "Returns a structured JSON object (`target_name`, `som_score`, `win_rate`, `consensus_quorum`, `oracle_breakdown`, and `tier_mode`). "
            "Side effects & latency: Strictly read-only (`readOnlyHint=true`) and non-destructive; does not mutate customer records. "
            "Completes in <1s when `live=false` or 4-12s when `live=true`. "
            "Auth & quota: Runs at $0 cost in 30% preview mode when `DANTE_API_KEY` is omitted (`live` defaults to `false`). "
            "Setting `live=true` requires a valid `dnt_live_` API key and consumes 1 monthly live probe credit. "
            "When to use: Use `dante.probe_geo_share` when you only need a fast, read-only check of how often AI assistants recommend a brand "
            "versus its competitors. Use `dante.run_audit` instead when you also need social sentiment, sarcasm calibration, and bot detection, "
            "or `dante.remediate_hallucination` when an AI engine is stating a specific false claim about the brand."
        ),
        "annotations": {
            "title": "Probe AI Search Share of Model",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "target_name": {
                    "type": "string",
                    "minLength": 2,
                    "maxLength": 120,
                    "description": "Brand, company, or product name to benchmark across AI answer engines (2 to 120 characters).",
                },
                "industry_or_context": {
                    "type": "string",
                    "minLength": 3,
                    "maxLength": 240,
                    "description": "Category, buyer intent query context, and geographic region (3 to 240 characters, e.g. 'Cloud CRM for mid-market sales teams in the US').",
                },
                "vertical_mode": {
                    "type": "string",
                    "enum": ["COMMERCIAL_BRAND", "INTERNAL_PROJECT", "POLITICAL_WAR_ROOM"],
                    "default": "COMMERCIAL_BRAND",
                    "description": "Domain prompt template selector: 'COMMERCIAL_BRAND' (buyer recommendation prompts), 'INTERNAL_PROJECT' (technical adoption prompts), or 'POLITICAL_WAR_ROOM' (public trust prompts).",
                },
                "live": {
                    "type": "boolean",
                    "default": False,
                    "description": "Set to true to query live AI models over the network (4-12s latency, requires a paid DANTE_API_KEY; false returns an instant <1s deterministic benchmark).",
                },
                "lang": {
                    "type": "string",
                    "enum": ["es", "en"],
                    "default": "es",
                    "description": "Prompt and response language: 'en' for English or 'es' for Spanish (defaults to 'es').",
                },
            },
            "required": ["target_name", "industry_or_context"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "target_name": {"type": "string", "description": "Evaluated brand or entity name."},
                "som_score": {"type": "string", "description": "Share of Model ratio formatted to 4 decimal places."},
                "win_rate": {"type": "string", "description": "Primary recommendation win rate across AI engines."},
                "oracle_breakdown": {"type": "array", "description": "Per-model citation and recommendation verdicts."},
                "tier_mode": {"type": "string", "description": "Active license tier ('FREE_TRIAL_30PCT_PREVIEW', 'PRO_INHOUSE', or 'AGENCY_PARTNER')."},
            },
        },
    },
    {
        "name": "dante.query_street_friction",
        "title": "Query Customer Friction & Social Signal Vault",
        "description": (
            "Search the caller's isolated tenant signal vault for customer complaints, sarcasm/irony-calibrated sentiment records, "
            "coordinated bot anomaly alerts, and unmet competitor gaps. "
            "Returns a JSON object (`query`, `voice_filter`, `matched_count`, `records`, and `tier_mode`). "
            "Side effects & latency: Strictly read-only (`readOnlyHint=true`), deterministic, and zero external LLM cost; executes in <200ms against "
            "the isolated tenant index. Never accesses or leaks signals belonging to other tenants. "
            "Auth & quota: Consumes 0 live audit credits. Without `DANTE_API_KEY`, searches the isolated free-trial sandbox vault and returns a 30% preview; "
            "with a paid `dnt_live_` key, searches the caller's dedicated private tenant vault and returns full records. "
            "When to use: Use `dante.query_street_friction` to inspect specific recurring customer pain points (e.g. 'pricing OR billing OR delay') "
            "after running `dante.run_audit`. Do not use this tool to query live external LLMs (use `dante.probe_geo_share` instead) or to generate "
            "website schema files (use `dante.forge_geo_shield` instead)."
        ),
        "annotations": {
            "title": "Query Customer Friction Vault",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "minLength": 2,
                    "maxLength": 240,
                    "description": "Search keywords or boolean expression to match against indexed social and customer signals (2 to 240 chars, e.g. 'pricing OR support OR latency').",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 10,
                    "description": "Maximum number of matching signal records to return (integer between 1 and 100, defaults to 10).",
                },
                "voice_filter": {
                    "type": "string",
                    "enum": ["ALL", "OWN_VOICE", "ALLY_ADVERSARY_VOICE", "SECTOR_STREET_VOICE"],
                    "default": "ALL",
                    "description": "Filter records by source voice category: 'ALL' (every source), 'OWN_VOICE' (official brand channels), 'ALLY_ADVERSARY_VOICE' (competitors/press/affiliates), or 'SECTOR_STREET_VOICE' (organic customers).",
                },
            },
            "required": ["query"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Executed search query string."},
                "voice_filter": {"type": "string", "description": "Applied voice category filter."},
                "matched_count": {"type": "integer", "description": "Number of matching records returned."},
                "records": {"type": "array", "description": "List of attested customer signal records with sentiment and bot-risk flags."},
                "tier_mode": {"type": "string", "description": "Active license tier."},
            },
        },
    },
    {
        "name": "dante.forge_geo_shield",
        "title": "Forge Technical GEO Shield (llms.txt & Schema.org JSON-LD)",
        "description": (
            "Generate production-ready technical Generative Engine Optimization (GEO) artifacts for a brand domain: "
            "`/llms.txt` manifest, `/.well-known/ai-catalog.json`, `Schema.org JSON-LD` (`Organization`, `Service`, `FAQPage`), "
            "and `robots.txt` rules for AI crawlers (`GPTBot`, `OAI-SearchBot`, `ClaudeBot`, `PerplexityBot`, `Google-Extended`). "
            "Returns a JSON bundle (`llms_txt_content`, `ai_catalog_json`, `json_ld_script`, `robots_txt_snippet`, and `domain_seal_sha256`). "
            "Side effects & latency: Read-only deterministic synthesis (<300ms); never modifies external websites and makes zero LLM calls. "
            "Constraints: `brand_name` must match the stem of `domain_url`, and URLs in `official_facts` must belong to `domain_url`. "
            "Auth & quota: Consumes 0 live audit credits. Without `DANTE_API_KEY`, returns a 30% preview at $0 cost; with a paid `dnt_live_` "
            "key (`PRO_INHOUSE` 1 domain or `AGENCY_PARTNER` 10 domains), returns 100% deployable files sealed for that domain. "
            "When to use: Use `dante.forge_geo_shield` to generate `/llms.txt` and `JSON-LD` files for AI crawler discovery. "
            "Use `dante.remediate_hallucination` instead when countering a specific false AI claim."
        ),
        "annotations": {
            "title": "Forge Technical GEO Shield",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_name": {
                    "type": "string",
                    "minLength": 2,
                    "maxLength": 80,
                    "description": "Official brand or organization name (2 to 80 characters; must correspond to the root stem of `domain_url`, e.g. 'Acme Cloud').",
                },
                "domain_url": {
                    "type": "string",
                    "minLength": 8,
                    "maxLength": 253,
                    "description": "Canonical HTTPS website URL for the brand (e.g. 'https://acmecloud.com'). Bound to the license's allowed domain slots.",
                },
                "industry_context": {
                    "type": "string",
                    "minLength": 4,
                    "maxLength": 240,
                    "description": "Primary industry category, target audience, and market positioning (4 to 240 characters).",
                },
                "products_or_services": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                    "maxItems": 25,
                    "description": "Non-empty list of core products, services, or clinical/technical offerings (1 to 25 strings).",
                },
                "official_facts": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                    "maxItems": 30,
                    "description": "Non-empty list of verified ground-truth facts, pricing, certifications, or SLAs (1 to 30 strings; any embedded URLs must belong to `domain_url`).",
                },
                "competitors": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 15,
                    "description": "Optional list of competitor names for semantic disambiguation in `disambiguatingDescription` (0 to 15 strings).",
                },
                "lang": {
                    "type": "string",
                    "enum": ["es", "en"],
                    "default": "es",
                    "description": "Language for generated `/llms.txt` and `JSON-LD` descriptions: 'en' for English or 'es' for Spanish (defaults to 'es').",
                },
            },
            "required": ["brand_name", "domain_url", "industry_context", "products_or_services", "official_facts"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "brand_name": {"type": "string", "description": "Canonical brand name."},
                "domain_url": {"type": "string", "description": "Normalized HTTPS domain URL."},
                "llms_txt_content": {"type": "string", "description": "Complete `/llms.txt` markdown manifest for AI crawlers."},
                "ai_catalog_json": {"type": "string", "description": "JSON payload for `/.well-known/ai-catalog.json`."},
                "json_ld_script": {"type": "string", "description": "HTML `<script type='application/ld+json'>` block."},
                "robots_txt_snippet": {"type": "string", "description": "Crawler allow rules for `robots.txt`."},
                "domain_seal_sha256": {"type": "string", "description": "64-character hex SHA-256 authenticity seal verifiable at `https://danteix.com/api/mcp/verify-seal`."},
            },
        },
    },
    {
        "name": "dante.remediate_hallucination",
        "title": "Remediate AI Hallucination with ClaimReview Counterweights",
        "description": (
            "Synthesize structured semantic counterweight artifacts to correct an inaccurate or outdated claim (hallucination) made by an AI assistant "
            "(ChatGPT, Perplexity, or Google Gemini) about a brand. "
            "Returns a JSON package (`markdown_counterweight_block`, `html_claim_review_snippet`, `faq_json_ld_script`, `verification_prompts`, and `domain_seal_sha256`). "
            "Side effects & latency: Purely deterministic, read-only synthesis (<300ms) with zero external LLM calls and zero destructive behavior. "
            "Security & parameter constraints: `brand_name` must match the stem of `domain_url`, and `verified_fact` must not contain third-party foreign URLs. "
            "Auth & quota: Consumes 0 live audit credits. Runs in 30% preview mode at $0 cost when `DANTE_API_KEY` is omitted; returns 100% unredacted "
            "`ClaimReview` and `FAQPage` artifacts when called with a paid `dnt_live_` license key. "
            "When to use: Use `dante.remediate_hallucination` when an AI assistant is actively stating false pricing, wrong features, or outdated ownership "
            "about a brand and you need an authoritative `Schema.org ClaimReview` + `FAQPage` correction block. Use `dante.forge_geo_shield` instead for "
            "general site-wide `/llms.txt` and `Organization` schema generation, or `dante.probe_geo_share` to check current AI citations."
        ),
        "annotations": {
            "title": "Remediate AI Hallucination",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_name": {
                    "type": "string",
                    "minLength": 2,
                    "maxLength": 80,
                    "description": "Official brand or organization name (2 to 80 characters; must align with `domain_url`).",
                },
                "domain_url": {
                    "type": "string",
                    "minLength": 8,
                    "maxLength": 253,
                    "description": "Canonical HTTPS URL of the official brand website where the correction will be published (e.g. 'https://acmecloud.com').",
                },
                "target_oracle": {
                    "type": "string",
                    "minLength": 2,
                    "maxLength": 60,
                    "description": "Name of the AI assistant exhibiting the inaccurate claim (e.g. 'ChatGPT', 'Perplexity', 'Gemini', or 'Claude').",
                },
                "hallucination_claim": {
                    "type": "string",
                    "minLength": 10,
                    "maxLength": 600,
                    "description": "Exact inaccurate, fabricated, or outdated statement currently produced by the AI engine (10 to 600 characters).",
                },
                "verified_fact": {
                    "type": "string",
                    "minLength": 10,
                    "maxLength": 1200,
                    "description": "Authoritative, verifiable ground-truth correction supported by first-party evidence on `domain_url` (10 to 1200 characters).",
                },
                "source_url_to_counter": {
                    "type": "string",
                    "maxLength": 500,
                    "description": "Optional outdated third-party article or directory URL that the AI assistant is erroneously citing as its source.",
                },
                "lang": {
                    "type": "string",
                    "enum": ["es", "en"],
                    "default": "es",
                    "description": "Language for generated `ClaimReview` HTML, `FAQPage JSON-LD`, and verification prompts: 'en' for English or 'es' for Spanish (defaults to 'es').",
                },
            },
            "required": ["brand_name", "domain_url", "target_oracle", "hallucination_claim", "verified_fact"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "brand_name": {"type": "string", "description": "Official brand name."},
                "target_oracle": {"type": "string", "description": "Target AI engine remediated."},
                "markdown_counterweight_block": {"type": "string", "description": "Markdown correction block for `/llms.txt` and documentation pages."},
                "html_claim_review_snippet": {"type": "string", "description": "Semantic HTML + microdata `ClaimReview` fact-check block."},
                "faq_json_ld_script": {"type": "string", "description": "`Schema.org FAQPage` JSON-LD script overriding the false claim."},
                "verification_prompts": {"type": "array", "description": "Follow-up prompts to verify the AI assistant has updated its answer."},
                "domain_seal_sha256": {"type": "string", "description": "64-character hex SHA-256 cryptographic authenticity seal."},
            },
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

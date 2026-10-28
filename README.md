<!-- manifest_hash: 573c978f422e5c379830c2736505b260b93186f28715b081388ec45acccfd1ac -->
<!-- mcp-name: io.github.heuristicolab/dante-mcp -->

# 🔦 Dante IX (`dante-mcp`) — Autonomous Brand, Social Listening & Multi-Model GEO Agency MCP

[![MCP Protocol](https://img.shields.io/badge/MCP-2024--11--05-D92B4B)](https://modelcontextprotocol.io)
[![Website](https://img.shields.io/badge/Cloud_Gateway-danteix.com-F59E0B)](https://danteix.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-10B981.svg)](LICENSE)

`mcp-name: io.github.heuristicolab/dante-mcp`

**Dante IX (`dante-mcp`)** is the official Model Context Protocol (MCP) connector for **[danteix.com](https://danteix.com)** — the 9-Circle Brand Intelligence, Social Listening, and Generative Engine Optimization (GEO) platform built by **Heurístico Lab**.

It equips **Claude Desktop, Claude Code, Cursor, Windsurf, and Google Antigravity** with 5 tools to audit how AI engines (**ChatGPT, Gemini, Perplexity**) recommend or hallucinate about your brand, analyze real customer friction across digital channels, and synthesize production-ready GEO technical shields (`/llms.txt`, `/.well-known/ai-catalog.json`, `Schema.org JSON-LD`, and `ClaimReview` counterweights).

---

## 🛠️ Exposed MCP Tools (5 Capabilities)

1. **`dante.run_audit`** — Executes a complete 9-Circle Brand, Social Listening & Multi-Model GEO Audit attested with a cryptographic SHA-256 seal.
2. **`dante.probe_geo_share`** — Measures Share of Model (SoM) and First-Choice Win Rate across OpenAI (`ChatGPT`), Google `Gemini`, and `Perplexity`.
3. **`dante.query_street_friction`** — Searches your isolated tenant intelligence vault for customer complaints, irony/sarcasm signals (Circle IV), coordinated bot alerts (Circle VIII), and competitive market opportunities.
4. **`dante.forge_geo_shield`** — Synthesizes production-ready `/llms.txt`, `/.well-known/ai-catalog.json`, `Schema.org JSON-LD`, and `robots.txt` rules for AI crawlers (`GPTBot`, `OAI-SearchBot`, `ClaudeBot`, `PerplexityBot`, `Google-Extended`).
5. **`dante.remediate_hallucination`** — Generates semantic counterweight blocks (`Markdown` + `HTML ClaimReview`), `FAQPage JSON-LD`, and verification prompts to remediate inaccurate AI claims.

---

## ⚡ Quickstart (`Claude Desktop` / `Cursor` / `Windsurf` / `Antigravity`)

Install via `pip` or run directly with `uvx`:

```bash
pip install dante-mcp
```

Add to your `claude_desktop_config.json` or `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "dante": {
      "command": "uvx",
      "args": ["dante-mcp"],
      "env": {
        "DANTE_API_KEY": "dnt_live_YOUR_KEY_HERE"
      }
    }
  }
}
```

> **Note (`FREE_TRIAL` Preview Mode)**: If `DANTE_API_KEY` is omitted, `dante-mcp` runs in **30% Preview Mode** at `$0` cost so you can test all 5 tools immediately. To unlock 100% of live multi-model probes and full GEO artifacts, get a **`PRO_INHOUSE` ($199/mo)** or **`AGENCY_PARTNER` ($499/mo)** key at **[https://danteix.com/#modalities](https://danteix.com/#modalities)**.

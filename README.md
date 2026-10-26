# NameScout: the brand-clearance agent that can explain why

Open Agent Hackathon 2026, Track 02 ("The Agent That Can Explain Why"). Built by Tali, an AI agent, for Mykel Nelson.

Founders pick a product name, then find out weeks later that the .com, the handles, an app or a live trademark already belong to someone else. NameScout checks independent public sources in parallel and returns a verdict (LIKELY CLEAR / CAUTION / AVOID). Every reason in the verdict cites the evidence that produced it ([E#], with source and UTC time). Sources that would not answer are labelled "unconfirmed" and never counted as available.

- **Evidence:** a **Zetaris** Lightning view of the company's own names (CRM accounts, products, vendors); **Meterless H-MEM** memory of earlier verdicts; RDAP (IANA bootstrap) or WHOIS for domains; GitHub, Reddit and YouTube handles; the Apple App Store (iTunes Search API); USPTO tmsearch.
- **Reasoning:** explicit, auditable scoring rules. An exact live trademark adds 40, a registered .com adds 25, and so on.
- **Explanation:** a deterministic cited explanation. An optional LLM (NVIDIA Nemotron via `LLM_BASE_URL`, `LLM_API_KEY` and `LLM_MODEL`) can rewrite it in plain English, but its output is rejected unless every citation exists and every original citation is kept. This guards against hallucinated reasons.
- **Output:** JSON plus an HTML report whose citations link to the evidence table.

```
cd memory && npm i && cd ..        # installs tsx for the H-MEM bridge (Node 18+)
python3 agent.py notion zqvoralyn   # writes reports/<name>.json and .html
python3 -m pytest -q
```

It makes read-only lookups only and never registers or reserves anything. Trademark results are a starting point, not legal advice.

## Requirements
Python 3.9+ standard library only (pytest for tests), plus Node 18+ for the H-MEM memory bridge. No API keys are needed for public sources or memory. Zetaris and the LLM narration are optional and are configured through environment variables.

## Sponsor integrations
**Zetaris (internal-collision source).** `zetaris_source.py` runs a read-only SQL query against a Zetaris Lightning view through the run-query REST route (`POST {ZETARIS_BASE_URL}/api/proxy/sql-editor/sqls/run-query`, the same route used by zetaris/getting-started `zetaris_api.py`). `zetaris/portfolio_view.sql` gives an example view that unions CRM accounts, catalogue products and ERP vendors. An exact internal match adds 35 points and a near match adds 10, each with its own citation. The name is reduced to alphanumerics before it goes into the SQL. Set `ZETARIS_BASE_URL`, `ZETARIS_API_KEY` and `ZETARIS_ORG_ID`, and optionally `ZETARIS_PORTFOLIO_VIEW` and `ZETARIS_ENGINE_ID`. When these aren't set, the source is skipped. Status: the adapter is unit-tested against a mocked Zetaris response. It has not yet been run against a live Zetaris instance.

**Meterless H-MEM (agent memory and audit).** `memory/bridge.ts` drives the open-source Meterless H-MEM reference engine. Each verdict is stored with provenance (`namescout:<name>`, risk and reasons). Later checks recall prior verdicts on similar names (difflib ratio ≥ 0.7) as cited, unscored context, and `audit` returns the trust-ledger history for a memory. Memory is kept in `.hmem/`, or in `NAMESCOUT_HMEM_DIR`. Set `NAMESCOUT_NO_MEMORY=1` to turn it off. If memory fails, it is reported as unconfirmed and the check carries on.

**NVIDIA.** The optional narrator is OpenAI-compatible and targets NVIDIA Nemotron (`LLM_BASE_URL=https://integrate.api.nvidia.com/v1`, `LLM_MODEL=nvidia/llama-3.3-nemotron-super-49b-v1`). A validator rejects its output if it drops or invents a citation.

## Pre-existing and third-party code
- `memory/vendor/hmem/` contains the Meterless H-MEM reference engine (Apache-2.0, github.com/Meterless/Meterless), vendored unchanged with its LICENSE. `memory/engine.ts` is adapted from the Meterless agentathon starter.
- Everything else was written for this hackathon on 2026-10-26.
- Cursor was not used. The project was built by an autonomous AI agent working in a Linux shell.

## Demo and deck
- Demo video (3:46): see the GitHub release `v1.0` asset `demo.mp4`
- Screenshots: [docs/](docs/)
- Deck: [deck/NameScout_deck.pdf](deck/NameScout_deck.pdf) (the source is `deck/build_deck.py`)

## Sample reports
- [reports/notion.html](reports/notion.html): AVOID, 100/100 (live USPTO mark, App Store apps, notion.com taken)
- [reports/linear.html](reports/linear.html): AVOID, 100/100
- [reports/zqvoralyn.html](reports/zqvoralyn.html): LIKELY CLEAR, 0/100
- [reports/notions.html](reports/notions.html): AVOID, with an H-MEM recall of the earlier `notion` verdict

The trademark evidence comes from the public USPTO Trademark Search backend (`tmsearch.uspto.gov/prod-stage-v1-0-0/tmsearch`), with live marks listed first.

## AI authorship
The code, tests, README, reports, deck and demo video were written by Tali, an autonomous AI agent (Grok Bot), working for Mykel Nelson. A human picked the project and reviewed it.

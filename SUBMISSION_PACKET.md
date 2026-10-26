# NameScout: Open Agent Hackathon 2026 submission packet
Deadline: **Tue Oct 27, 7:45 PM ET** (23:45 UTC). Results: Nov 6.
Event page: https://hackathon.genai.works/event/open-agent-hackathon-2026

## Assets (all public)
| Item | URL |
|---|---|
| GitHub repo + README | https://github.com/talibot-agent/namescout |
| Demo video, 3:46 (MP4) | https://github.com/talibot-agent/namescout/releases/download/v1.0/demo.mp4 |
| Slide deck (PDF, 8 slides) | https://github.com/talibot-agent/namescout/releases/download/v1.0/NameScout_deck.pdf (also `deck/NameScout_deck.pptx`) |
| Screenshots | https://github.com/talibot-agent/namescout/tree/main/docs |
| Release | https://github.com/talibot-agent/namescout/releases/tag/v1.0 |

The local copies are in /workspace/projects/open-agent-hack/namescout (`demo.mp4`, `deck/`, `docs/`). If the form wants a YouTube or Loom link instead of an MP4 URL, upload demo.mp4 there first.

## Form fields (copy and paste)
**Project name:** NameScout

**Tagline:** The brand-clearance agent that can explain why. Every verdict cites its evidence.

**Track:** Track 02, "The Agent That Can Explain Why"

**Team / builder:** Mykel Nelson (built with Tali, an autonomous AI agent)

**Problem:** Founders and brand teams fall in love with a name, then find out weeks later that the .com, the social handles, an App Store app, a live trademark, or one of their own products or vendors already uses it. Existing checkers answer "available" or "taken" with no reasons, and they quietly treat "no answer" as "free".

**Solution / description:**
NameScout checks independent sources in parallel and returns LIKELY CLEAR, CAUTION or AVOID. The sources are RDAP/WHOIS domains, GitHub/Reddit/YouTube handles, the Apple App Store, the USPTO Trademark Search, the company's own name data through a Zetaris Lightning view, and Meterless H-MEM memory of earlier verdicts.

Every risk factor follows an explicit, auditable point rule and cites numbered evidence ([E#]) with its source endpoint and UTC timestamp. Sources that won't answer are labelled "unconfirmed" and never counted as available. An optional NVIDIA Nemotron narrator rewrites the explanation in plain English, and a validator rejects its output if it invents or drops a single citation. Each run produces JSON plus an HTML report whose citations link to the evidence table.

**How Zetaris is used:** `zetaris_source.py` sends a read-only, sanitised SQL query to a Zetaris Lightning view (`namescout.brand_portfolio`; `zetaris/portfolio_view.sql` shows an example that unions CRM accounts, catalogue products and ERP vendors). It goes through the Zetaris run-query REST route, `POST {base}/api/proxy/sql-editor/sqls/run-query`, with Bearer API key and X-Org-ID headers. An exact internal collision adds 35 risk points and a near match adds 10, each cited. This answers the question public checkers can't: "do *we* already use this name?" Status: the adapter is unit-tested against a mocked Zetaris response. A live run against a Zetaris instance is pending.

**How Meterless is used:** The open-source Meterless H-MEM reference engine is the agent's memory. A TypeScript bridge (`memory/bridge.ts`) stores each verdict with provenance (store service). When a later check is on a similar name, it recalls prior verdicts (retrieval service) and shows them as cited context that is not scored. Its trust ledger also gives an audit history for every memory. In the demo, checking "notions" recalls the earlier "notion" AVOID verdict.

**NVIDIA:** An optional OpenAI-compatible narrator targets NVIDIA Nemotron (`nvidia/llama-3.3-nemotron-super-49b-v1` at integrate.api.nvidia.com). Its output is accepted only if the citation validator passes.

**Cursor:** Not used. The project was built by an autonomous AI agent (Tali, Grok Bot) in a Linux shell, with Mykel Nelson directing and reviewing.

**Tech stack:** Python 3 (stdlib only, ThreadPoolExecutor), RDAP (IANA bootstrap) and WHOIS port 43, iTunes Search API, USPTO tmsearch, Zetaris REST, Meterless H-MEM (TypeScript via tsx, Node 18+), NVIDIA Nemotron (optional), pytest (8 tests).

**What makes it unique:** Explainability is enforced in code, not left to a prompt. It also answers three questions in one report: does the world use this name (public registries), do we already use it (Zetaris), and what did we decide last time (H-MEM)?

**Pre-existing code declaration:** `memory/vendor/hmem/` is the Meterless H-MEM reference engine (Apache-2.0, github.com/Meterless/Meterless), vendored unchanged with its LICENSE. `memory/engine.ts` is adapted from the Meterless agentathon starter. Everything else was written during the hackathon, on 2026-10-26.

**Future plans:** EU (EUIPO) and WIPO trademark sources, phonetic and sound-alike matching, ready-made Zetaris connectors for Salesforce and HubSpot, a feedback loop through the H-MEM trust ledger, and a hosted web UI.

**AI disclosure:** Tali, an autonomous AI agent, wrote the code, tests, README, deck and demo video for Mykel Nelson. Mykel directed and reviewed the work.

## LinkedIn post (required, with #OpenAgentHackathon)
```
I just submitted NameScout to the #OpenAgentHackathon (Track 02: "The Agent That Can Explain Why"), hosted by @Zetaris and @GenAI.works.

The problem: you fall in love with a product name, then find out weeks later that the .com, the handles, an App Store app, a live trademark, or even one of your own products already uses it.

NameScout checks domains, social handles, the App Store and USPTO trademarks in parallel. It also queries your internal CRM, product and vendor names through a Zetaris view, and it remembers past verdicts using Meterless H-MEM. It returns LIKELY CLEAR, CAUTION or AVOID, and every reason cites its evidence with a source and timestamp. An optional NVIDIA Nemotron narrator explains the result in plain English, but anything it writes is rejected unless every citation is real.

Full transparency: an AI agent I run built this. It wrote the code, tests, deck and demo, and I directed and reviewed the work.

Demo + code: https://github.com/talibot-agent/namescout

#OpenAgentHackathon #AIAgents #ExplainableAI #Zetaris #Meterless
```

## Remaining browser steps (Mykel)
1. **Submit on HackOS:** log in at https://hackathon.genai.works/event/open-agent-hackathon-2026, open the event's Submit Project form (you need to be registered and on a team), and paste the fields above. Use the video, deck and repo URLs from the table. Do this before Tue Oct 27, 7:45 PM ET.
2. **LinkedIn:** create a post at https://www.linkedin.com/feed/ (Start a post) with the text above. Attach demo.mp4 or the deck PDF if you'd like. If the form asks for the post URL, copy it from the post's "Copy link to post" menu and paste it into the form.
3. **Optional, makes Zetaris live:** sign up at https://zetaris.com (a cloud trial, or a Docker host with 8 GB RAM; the box has no Docker). Create the `namescout.brand_portfolio` view from `zetaris/portfolio_view.sql`, export ZETARIS_BASE_URL, ZETARIS_API_KEY and ZETARIS_ORG_ID, and rerun `python3 agent.py <name>`. Until then, the packet truthfully says the integration was mock-tested.

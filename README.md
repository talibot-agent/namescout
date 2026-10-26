# NameScout: the brand-clearance agent that can explain why

Open Agent Hackathon 2026, Track 02 ("The Agent That Can Explain Why"). Built by Tali, an AI agent, for Mykel Nelson.

Founders pick a product name, then find out weeks later that the .com, the handles, an app or a live trademark already belong to someone else. NameScout checks independent public sources in parallel and returns a verdict (LIKELY CLEAR / CAUTION / AVOID). Every reason in the verdict cites the evidence that produced it ([E#], with source and UTC time). Sources that would not answer are labelled "unconfirmed" and never counted as available.

- **Evidence:** RDAP (IANA bootstrap) or WHOIS for domains; GitHub, Reddit and YouTube handles; the Apple App Store (iTunes Search API); USPTO tmsearch.
- **Reasoning:** explicit, auditable scoring rules. An exact live trademark adds 40, a registered .com adds 25, and so on.
- **Explanation:** a deterministic cited explanation. An optional LLM (NVIDIA Nemotron via `LLM_BASE_URL`, `LLM_API_KEY` and `LLM_MODEL`) can rewrite it in plain English, but its output is rejected unless every citation exists and every original citation is kept. This guards against hallucinated reasons.
- **Output:** JSON plus an HTML report whose citations link to the evidence table.

```
python3 agent.py notion zqvoralyn   # writes reports/<name>.json and .html
python3 -m pytest -q
```

It makes read-only lookups only and never registers or reserves anything. Trademark results are a starting point, not legal advice.

## Requirements
Python 3.9+ standard library only (pytest for tests). No API keys are needed; the LLM narration is optional.

## Sample reports
- [reports/notion.html](reports/notion.html): AVOID, 100/100 (live USPTO mark, App Store apps, notion.com taken)
- [reports/linear.html](reports/linear.html): AVOID, 100/100
- [reports/zqvoralyn.html](reports/zqvoralyn.html): LIKELY CLEAR, 0/100

The trademark evidence comes from the public USPTO Trademark Search backend (`tmsearch.uspto.gov/prod-stage-v1-0-0/tmsearch`), with live marks listed first.

## AI authorship
The code, tests, README and reports were written by Tali, an autonomous AI agent (Grok Bot), working for Mykel Nelson. A human picked the project and reviewed it.
